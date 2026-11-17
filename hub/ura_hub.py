#!/usr/bin/env python3
"""ura-hub, Meshtastic lane.

The radio runs with MQTT "proxy to client": every packet it would publish to
MQTT (its own and what it hears on LoRa, still encrypted) comes to us over
USB. We pass it to ura-server; packets from other hubs go back into the radio
as MQTT downlink, so remote nodes appear in the radio's node list exactly as
nodes from an MQTT gateway do.

Settings come from the environment (see hub.env.example).
"""
import asyncio, base64, glob, hashlib, json, logging, os, signal, ssl, threading, time

from pubsub import pub
import meshtastic.serial_interface
from google.protobuf.json_format import ParseDict
from meshtastic.protobuf import mesh_pb2, portnums_pb2

SERVER = os.environ["URA_SERVER"]                    # host:port
HUB_ID = os.environ["URA_HUB_ID"]
HUB_KEY = os.environ["URA_HUB_KEY"]
FINGERPRINT = os.environ["URA_SERVER_FP"].replace(":", "").upper()
MT_PORT = os.environ["URA_MT_PORT"]
DATA_DIR = os.environ.get("URA_DATA", os.path.dirname(os.path.abspath(__file__)))                  # e.g. /dev/serial/by-id/usb-...  (glob allowed)

log = logging.getLogger("ura-hub")
counts = {"heard": 0, "to_server": 0, "from_server": 0, "to_radio_fail": 0}


class Radio:
    """Keeps a Meshtastic serial connection open and reopens it after a reboot."""

    def __init__(self, loop, queue):
        self.loop, self.queue, self.iface, self.lock = loop, queue, None, threading.Lock()
        pub.subscribe(self._on_proxy, "meshtastic.mqttclientproxymessage")
        pub.subscribe(self._on_lost, "meshtastic.connection.lost")
        pub.subscribe(self._on_packet, "meshtastic.receive")
        if os.environ.get("URA_DEBUG"):
            pub.subscribe(self._on_log, "meshtastic.log.line")

    def _on_log(self, line, interface):
        if any(k in line for k in ("MQTT", "ebroadcast", "Ignore", "filtered", "dupe", "Lora RX", "Started Tx", "Completed sending")):
            log.info("radio log: %s", line.strip())

    def _on_packet(self, packet, interface):
        counts["heard"] += 1
        if os.environ.get("URA_DEBUG"):
            d = packet.get("decoded", {})
            log.info("rx from %s to %s port %s ch %s snr %s hops %s/%s viaMqtt %s encrypted %s",
                     packet.get("fromId"), packet.get("toId"), d.get("portnum"), packet.get("channel"),
                     packet.get("rxSnr"), packet.get("hopStart"), packet.get("hopLimit"),
                     packet.get("viaMqtt"), "encrypted" in packet)
            ls = d.get("telemetry", {}).get("localStats")
            if ls:
                log.info("radio stats: tx %s, relayed %s, relay cancelled %s, rx ok %s, rx bad %s, dupes %s",
                         ls.get("numPacketsTx"), ls.get("numTxRelay"), ls.get("numTxRelayCanceled"),
                         ls.get("numPacketsRx"), ls.get("numPacketsRxBad"), ls.get("numRxDupe"))

    def _on_proxy(self, proxymessage, interface):
        if proxymessage.data:
            self.loop.call_soon_threadsafe(self._enqueue, (proxymessage.topic, bytes(proxymessage.data)))

    def _enqueue(self, item):
        if self.queue.full():
            self.queue.get_nowait()          # server unreachable for a while: drop the oldest
        self.queue.put_nowait(item)

    def _on_lost(self, interface):
        log.warning("radio connection lost")
        with self.lock:
            if self.iface is interface:
                self.iface = None
        try:
            interface.close()
        except Exception:
            pass

    def keep_open(self):
        while True:
            if self.iface is None:
                ports = glob.glob(MT_PORT)
                if ports:
                    try:
                        iface = meshtastic.serial_interface.SerialInterface(ports[0])
                        with self.lock:
                            self.iface = iface
                        info = iface.getMyNodeInfo() or {}
                        log.info("radio connected: %s on %s", info.get("user", {}).get("longName"), ports[0])
                    except Exception as e:
                        log.warning("radio open failed: %s", e)
                else:
                    log.warning("radio port %s not present", MT_PORT)
            time.sleep(5)

    def downlink(self, topic, data):
        with self.lock:
            iface = self.iface
        if iface is None:
            counts["to_radio_fail"] += 1
            return
        iface.sendMqttClientProxyMessage(topic, data)
        if os.environ.get("URA_DEBUG"):
            log.info("to radio: %s, %d bytes", topic, len(data))

    def announce(self, want_response=False):
        """Broadcast this radio's own node info + telemetry (what it does on its own every few hours)."""
        with self.lock:
            iface = self.iface
        if iface is None:
            return
        me = dict(iface.getMyUser() or {})
        me.pop("raw", None)
        user = ParseDict(me, mesh_pb2.User(), ignore_unknown_fields=True)
        iface.sendData(user, portNum=portnums_pb2.PortNum.NODEINFO_APP, wantResponse=want_response)
        iface.sendTelemetry()
        pos = (iface.nodesByNum or {}).get(iface.myInfo.my_node_num, {}).get("position", {})
        if "latitude" in pos and "longitude" in pos:
            iface.sendPosition(pos["latitude"], pos["longitude"], pos.get("altitude", 0))
        log.info("announced own node info + telemetry%s", " (asking neighbours to reply)" if want_response else "")

    def node_summary(self):
        with self.lock:
            iface = self.iface
        if iface is None or not iface.nodes:
            return None
        nodes = list(iface.nodes.values())
        snap = [{"id": n.get("user", {}).get("id"), "name": n.get("user", {}).get("longName"),
                 "short": n.get("user", {}).get("shortName"), "lastHeard": n.get("lastHeard"),
                 "viaMqtt": n.get("viaMqtt", False), "hopsAway": n.get("hopsAway"),
                 "position": {k: n["position"][k] for k in ("latitude", "longitude") if k in n.get("position", {})}}
                for n in nodes]
        tmp = os.path.join(DATA_DIR, "nodes.json.tmp")
        with open(tmp, "w") as f:
            json.dump(sorted(snap, key=lambda x: -(x["lastHeard"] or 0)), f, indent=1)
        os.replace(tmp, os.path.join(DATA_DIR, "nodes.json"))
        return len(nodes), sum(1 for n in nodes if n.get("viaMqtt"))


async def server_link(radio, queue):
    host, port = SERVER.rsplit(":", 1)
    ctx = ssl.create_default_context()
    ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE   # pinned by fingerprint below
    while True:
        try:
            reader, writer = await asyncio.open_connection(host, int(port), ssl=ctx)
            der = writer.get_extra_info("ssl_object").getpeercert(binary_form=True)
            if hashlib.sha256(der).hexdigest().upper() != FINGERPRINT:
                log.error("server certificate fingerprint does NOT match - not connecting")
                writer.close()
                await asyncio.sleep(60)
                continue
            writer.write((json.dumps({"t": "hello", "hub": HUB_ID, "key": HUB_KEY}) + "\n").encode())
            reply = json.loads(await asyncio.wait_for(reader.readline(), 15))
            if reply.get("t") != "welcome":
                log.error("server refused this hub (%s)", reply)
                writer.close()
                await asyncio.sleep(60)
                continue
            log.info("connected to server %s", SERVER)

            async def uplink():
                while True:
                    topic, data = await queue.get()
                    writer.write((json.dumps({"t": "mesh", "net": "mt", "topic": topic,
                                              "data": base64.b64encode(data).decode()}) + "\n").encode())
                    await writer.drain()
                    counts["to_server"] += 1

            async def keepalive():
                while True:
                    await asyncio.sleep(30)
                    writer.write(b'{"t":"ping"}\n')
                    await writer.drain()

            tasks = [asyncio.create_task(uplink()), asyncio.create_task(keepalive())]
            try:
                while line := await asyncio.wait_for(reader.readline(), 120):
                    msg = json.loads(line)
                    if msg.get("t") == "mesh" and msg.get("net") == "mt":
                        await asyncio.to_thread(radio.downlink, msg["topic"], base64.b64decode(msg["data"]))
                        counts["from_server"] += 1
            finally:
                for t in tasks:
                    t.cancel()
                writer.close()
            log.warning("server closed the connection")
        except Exception as e:
            log.warning("server link: %s", e)
        await asyncio.sleep(5)


async def report(radio):
    while True:
        await asyncio.sleep(60)
        s = radio.node_summary()
        log.info("radio heard %d, to server %d, from server %d, radio not ready %d; nodes %s",
                 counts["heard"], counts["to_server"], counts["from_server"], counts["to_radio_fail"],
                 f"{s[0]} ({s[1]} via bridge/MQTT)" if s else "n/a")


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    loop, queue = asyncio.get_running_loop(), asyncio.Queue(maxsize=1000)
    radio = Radio(loop, queue)
    threading.Thread(target=radio.keep_open, daemon=True).start()
    loop.add_signal_handler(signal.SIGUSR1, lambda: loop.run_in_executor(None, radio.announce))
    loop.add_signal_handler(signal.SIGUSR2, lambda: loop.run_in_executor(None, radio.announce, True))
    await asyncio.gather(server_link(radio, queue), report(radio))

if __name__ == "__main__":
    asyncio.run(main())
