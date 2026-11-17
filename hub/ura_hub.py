#!/usr/bin/env python3
"""ura-hub: on-site bridge between a local mesh radio and other Ura hubs.

* The radio (Meshtastic, MQTT "proxy to client") hands every packet it would
  publish to MQTT to the hub over USB/IP, still encrypted.
* The hub applies ITS OWN rules per link (direction, public group, groups,
  private messages, positions, airtime) and passes allowed packets to
  ura-server, which delivers them only to hubs that accepted the link.
* Packets from linked hubs go back into the radio as MQTT downlink. With the
  Ura firmware patch the radio puts them on air as normal LoRa packets.
* Website (HTTPS, default port 8091) for the hub owner: status, links and
  rules, radio, settings. Everything is configured there; nothing is hard-coded.

Needs the `meshtastic` Python package (already present with the Meshtastic CLI).
"""
import asyncio, base64, copy, glob, hashlib, hmac, http.server, json, logging, math, os, re, secrets
import signal, socketserver, ssl, subprocess, threading, time, urllib.parse

from pubsub import pub
import meshtastic.serial_interface, meshtastic.tcp_interface
from google.protobuf.json_format import ParseDict
from meshtastic.protobuf import mesh_pb2, mqtt_pb2, portnums_pb2, config_pb2

from meshcrypto import expand_psk, decrypt_packet

VERSION = "0.2.0"
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("URA_DATA", os.path.join(HERE, "data"))
WEB_PORT = int(os.environ.get("URA_WEB_PORT", "8091"))
WEB_DIR = os.path.join(HERE, "web")
COMMON_DIR = os.environ.get("URA_COMMON", os.path.join(os.path.dirname(HERE), "common"))
CONFIG = os.path.join(DATA_DIR, "config.json")
URA_MQTT_ADDRESS = "127.0.0.1"          # private => firmware passes every packet; never contacted (proxy mode)
NODES_EVERY = 300

log = logging.getLogger("ura-hub")

RULE_DEFAULT = {"on": True, "public": True, "groups": [], "private": True, "positions": True}
DEFAULT_CONFIG = {
    "hub": {"name": "", "email": "", "country": "", "city": "", "lat": None, "lon": None, "description": ""},
    "server": {"address": "", "fingerprint": "", "hub_id": "", "key": "", "status": ""},
    "radios": [],                 # [{"id","net":"mt","transport":"serial|tcp","address","enabled"}]
    "airtime": {"pct_hour": 10.0, "pct_day": 0.0},
    "defaults": {"send": dict(RULE_DEFAULT), "receive": dict(RULE_DEFAULT)},
    "rules": {},                  # peer hub id -> {"send": {...}, "receive": {...}}
    "share_positions_on_map": True,
    "web_password": None,
}


# ───────────────────────── config ─────────────────────────

class Config:
    def __init__(self):
        self.lock = threading.RLock()
        self.data = copy.deepcopy(DEFAULT_CONFIG)
        if os.path.exists(CONFIG):
            with open(CONFIG) as f:
                self._merge(self.data, json.load(f))

    @staticmethod
    def _merge(base, new):
        for k, v in new.items():
            if isinstance(v, dict) and isinstance(base.get(k), dict) and base[k]:
                Config._merge(base[k], v)
            else:
                base[k] = v

    def get(self):
        with self.lock:
            return copy.deepcopy(self.data)

    def update(self, fn):
        with self.lock:
            fn(self.data)
            tmp = CONFIG + ".tmp"
            with open(tmp, "w") as f:
                json.dump(self.data, f, indent=1)
            os.chmod(tmp, 0o600)
            os.replace(tmp, CONFIG)

    def rules_for(self, peer):
        with self.lock:
            r = self.data["rules"].get(peer)
            if r is None:
                r = copy.deepcopy(self.data["defaults"])
            out = {"send": dict(RULE_DEFAULT), "receive": dict(RULE_DEFAULT)}
            for d in ("send", "receive"):
                out[d].update(r.get(d) or {})
            return out


cfg: Config = None
loop: asyncio.AbstractEventLoop = None


# ───────────────────────── counters ─────────────────────────

class Counters:
    def __init__(self):
        self.lock = threading.Lock()
        self.g = {"heard": 0, "uplinked": 0, "sent": 0, "received": 0, "to_radio": 0}
        self.peer = {}          # peer -> {"sent", "received", "blocked_send": {reason: n}, "blocked_recv": {...}}
        self.airtime = []       # [(time, seconds)]
        self.started = time.time()

    def add(self, key, n=1):
        with self.lock:
            self.g[key] = self.g.get(key, 0) + n

    def p(self, peer):
        return self.peer.setdefault(peer, {"sent": 0, "received": 0, "blocked_send": {}, "blocked_recv": {}})

    def peer_add(self, peer, key, reason=None):
        with self.lock:
            p = self.p(peer)
            if reason:
                p[key][reason] = p[key].get(reason, 0) + 1
            else:
                p[key] += 1

    def air_used(self, window):
        t = time.time()
        with self.lock:
            self.airtime = [(a, s) for a, s in self.airtime if t - a < 86400]
            return sum(s for a, s in self.airtime if t - a < window)

    def air_add(self, seconds):
        with self.lock:
            self.airtime.append((time.time(), seconds))

    def snapshot(self):
        with self.lock:
            return {"global": dict(self.g), "peers": copy.deepcopy(self.peer), "since": self.started}


counters = Counters()


# ───────────────────────── packet inspection ─────────────────────────

POSITION_PORTS = {portnums_pb2.PortNum.POSITION_APP, portnums_pb2.PortNum.WAYPOINT_APP}
KIND = {portnums_pb2.PortNum.TEXT_MESSAGE_APP: "text", portnums_pb2.PortNum.POSITION_APP: "position",
        portnums_pb2.PortNum.WAYPOINT_APP: "position", portnums_pb2.PortNum.NODEINFO_APP: "nodeinfo",
        portnums_pb2.PortNum.TELEMETRY_APP: "telemetry", portnums_pb2.PortNum.ROUTING_APP: "routing",
        portnums_pb2.PortNum.TRACEROUTE_APP: "traceroute"}


def classify(data, channels):
    """Return {channel, public, private, kind, size} for a ServiceEnvelope, or None if invalid.
    channels: {channel_id: {"key": bytes|None, "public": bool}} from the radio."""
    env = mqtt_pb2.ServiceEnvelope()
    try:
        env.ParseFromString(data)
    except Exception:
        return None
    pkt = env.packet
    out = {"channel": env.channel_id, "public": False, "private": env.channel_id == "PKI",
           "kind": "unknown", "size": len(pkt.encrypted) if pkt.HasField("encrypted") else len(pkt.decoded.payload) + 4}
    ch = channels.get(env.channel_id)
    if ch:
        out["public"] = ch["public"]
    if pkt.HasField("decoded"):
        port = pkt.decoded.portnum
    elif ch and ch["key"] and not out["private"]:
        try:
            d = mesh_pb2.Data()
            d.ParseFromString(decrypt_packet(ch["key"], pkt.id, getattr(pkt, "from"), pkt.encrypted))
            port = d.portnum
        except Exception:
            return out
    else:
        return out
    out["kind"] = KIND.get(port, "other")
    return out


def allowed(rule, c):
    """Does a link rule (send or receive side) let this packet through? -> (bool, reason)."""
    if not rule.get("on"):
        return False, "link_off"
    if c["private"]:
        if not rule.get("private"):
            return False, "private"
    elif c["public"]:
        if not rule.get("public"):
            return False, "public"
    elif c["channel"] not in (rule.get("groups") or []):
        return False, "group"
    if c["kind"] == "position" and not rule.get("positions"):
        return False, "positions"
    return True, None


PRESETS = {  # modem preset -> (sf, bw_khz, cr)
    0: (11, 250, 5), 1: (12, 125, 8), 2: (12, 125, 8), 3: (10, 250, 5), 4: (9, 250, 5),
    5: (8, 250, 5), 6: (7, 250, 5), 7: (11, 125, 8), 8: (7, 500, 5), 9: (12, 62.5, 8), 10: (8, 62.5, 8)}


def time_on_air(size, sf, bw, cr, preamble=16):
    """LoRa time on air in seconds (explicit header, CRC on)."""
    tsym = (2 ** sf) / (bw * 1000)
    de = 1 if tsym > 0.016 else 0
    n = 8 + max(math.ceil((8 * size - 4 * sf + 28 + 16) / (4 * (sf - 2 * de))) * cr, 0)
    return (preamble + 4.25) * tsym + n * tsym


# ───────────────────────── radio (Meshtastic) ─────────────────────────

class Radio:
    """One Meshtastic radio: keeps the connection open and reopens it after reboots."""

    def __init__(self, conf, queue):
        self.conf, self.queue = conf, queue
        self.iface, self.lock = None, threading.RLock()
        self.error, self.connected_at = "", 0
        self.stop = False
        pub.subscribe(self._on_proxy, "meshtastic.mqttclientproxymessage")
        pub.subscribe(self._on_lost, "meshtastic.connection.lost")
        pub.subscribe(self._on_packet, "meshtastic.receive")
        threading.Thread(target=self._keep_open, daemon=True).start()

    # events from the meshtastic library threads
    def _mine(self, interface):
        return interface is self.iface

    def _on_proxy(self, proxymessage, interface):
        if self._mine(interface) and proxymessage.data:
            counters.add("uplinked")
            loop.call_soon_threadsafe(self._enqueue, (proxymessage.topic, bytes(proxymessage.data)))

    def _enqueue(self, item):
        if self.queue.full():
            self.queue.get_nowait()
        self.queue.put_nowait(item)

    def _on_packet(self, packet, interface):
        if self._mine(interface) and packet.get("from") != interface.myInfo.my_node_num:
            counters.add("heard")

    def _on_lost(self, interface):
        with self.lock:
            if self.iface is interface:
                self.iface = None
                self.error = "connection lost"
                log.warning("radio %s: connection lost", self.conf.get("address"))
        try:
            interface.close()
        except Exception:
            pass

    def _open(self):
        c = self.conf
        if c.get("transport") == "tcp":
            host, _, port = c["address"].partition(":")
            return meshtastic.tcp_interface.TCPInterface(host, portNumber=int(port or 4403))
        ports = sorted(glob.glob(c["address"]))
        if not ports:
            raise RuntimeError("port not present")
        return meshtastic.serial_interface.SerialInterface(ports[0])

    def _keep_open(self):
        while not self.stop:
            if self.iface is None and self.conf.get("enabled", True):
                try:
                    iface = self._open()
                    with self.lock:
                        self.iface, self.error, self.connected_at = iface, "", time.time()
                    log.info("radio connected: %s (%s)", self.info().get("name"), self.conf.get("address"))
                except Exception as e:
                    self.error = str(e)
            time.sleep(5)

    def close(self):
        self.stop = True
        with self.lock:
            iface, self.iface = self.iface, None
        if iface:
            try:
                iface.close()
            except Exception:
                pass

    # information
    def info(self):
        with self.lock:
            iface = self.iface
        base = {"id": self.conf.get("id"), "net": "mt", "transport": self.conf.get("transport"),
                "address": self.conf.get("address"), "connected": iface is not None, "error": self.error}
        if iface is None:
            return base
        try:
            me = iface.getMyNodeInfo() or {}
            md = iface.metadata
            ln = iface.localNode
            lc, mc = ln.localConfig, ln.moduleConfig
            chans = []
            for ch in ln.channels or []:
                if ch.role == 0:
                    continue
                name = ch.settings.name or self._preset_name(lc)
                chans.append({"index": ch.index, "name": name, "public": self._is_public(ch.settings.psk),
                              "uplink": ch.settings.uplink_enabled, "downlink": ch.settings.downlink_enabled,
                              "primary": ch.role == 1})
            checks = {
                "mqtt_enabled": mc.mqtt.enabled, "proxy_to_client": mc.mqtt.proxy_to_client_enabled,
                "private_address": mc.mqtt.address == URA_MQTT_ADDRESS or bool(re.match(r"^(10|127|192\.168|172\.(1[6-9]|2\d|3[01]))\.", mc.mqtt.address or "")),
                "encryption": mc.mqtt.encryption_enabled, "ignore_mqtt_off": not lc.lora.ignore_mqtt,
                "channels_linked": all(c["uplink"] and c["downlink"] for c in chans) if chans else False,
                "debug_log_off": not lc.security.debug_log_api_enabled}
            base.update({"name": me.get("user", {}).get("longName"), "short": me.get("user", {}).get("shortName"),
                         "node_id": me.get("user", {}).get("id"), "hw": me.get("user", {}).get("hwModel"),
                         "firmware": getattr(md, "firmware_version", "") if md else "",
                         "role": config_pb2.Config.DeviceConfig.Role.Name(lc.device.role),
                         "preset": self._preset_name(lc), "region": config_pb2.Config.LoRaConfig.RegionCode.Name(lc.lora.region),
                         "channels": chans, "checks": checks, "ready": all(checks.values()),
                         "nodes": len(iface.nodes or {})})
        except Exception as e:
            base["error"] = f"reading radio: {e}"
        return base

    @staticmethod
    def _preset_name(lc):
        name = config_pb2.Config.LoRaConfig.ModemPreset.Name(lc.lora.modem_preset)
        return "".join(p.capitalize() for p in name.split("_"))

    @staticmethod
    def _is_public(psk):
        return len(psk) == 1 and psk[0] == 1

    def channel_keys(self):
        """{channel_id: {"key", "public"}} as the radio names channels in MQTT topics."""
        with self.lock:
            iface = self.iface
        out = {}
        if iface is None:
            return out
        lc = iface.localNode.localConfig
        for ch in iface.localNode.channels or []:
            if ch.role == 0:
                continue
            name = ch.settings.name or self._preset_name(lc)
            out[name] = {"key": expand_psk(bytes(ch.settings.psk)), "public": self._is_public(ch.settings.psk)}
        return out

    def lora_params(self):
        with self.lock:
            iface = self.iface
        if iface is None:
            return PRESETS[0]
        lo = iface.localNode.localConfig.lora
        if lo.use_preset:
            return PRESETS.get(lo.modem_preset, PRESETS[0])
        return (lo.spread_factor or 11, lo.bandwidth or 250, lo.coding_rate or 5)

    def nodes(self, share_positions):
        with self.lock:
            iface = self.iface
        if iface is None:
            return []
        out = []
        my = iface.myInfo.my_node_num
        for num, n in list((iface.nodesByNum or {}).items()):
            if n.get("viaMqtt") and num != my:
                continue                      # remote nodes belong to the hub that heard them
            u, p = n.get("user", {}), n.get("position", {})
            out.append({"id": u.get("id") or f"!{num:08x}", "name": u.get("longName"), "short": u.get("shortName"),
                        "hw": u.get("hwModel"), "role": u.get("role"),
                        "lat": p.get("latitude") if share_positions else None,
                        "lon": p.get("longitude") if share_positions else None,
                        "alt": p.get("altitude") if share_positions else None,
                        "last_heard": n.get("lastHeard") or (int(time.time()) if num == my else None),
                        "hops": n.get("hopsAway"), "own": num == my})
        return out

    def all_nodes(self):
        with self.lock:
            iface = self.iface
        if iface is None:
            return []
        my = iface.myInfo.my_node_num
        out = []
        for num, n in list((iface.nodesByNum or {}).items()):
            u, p = n.get("user", {}), n.get("position", {})
            out.append({"id": u.get("id") or f"!{num:08x}", "name": u.get("longName"), "short": u.get("shortName"),
                        "hw": u.get("hwModel"), "lat": p.get("latitude"), "lon": p.get("longitude"),
                        "last_heard": n.get("lastHeard"), "hops": n.get("hopsAway"), "snr": n.get("snr"),
                        "remote": bool(n.get("viaMqtt")) and num != my, "own": num == my})
        return out

    # actions
    def downlink(self, topic, data):
        with self.lock:
            iface = self.iface
        if iface is None:
            return False
        iface.sendMqttClientProxyMessage(topic, data)
        counters.add("to_radio")
        return True

    def announce(self, want_response=False):
        with self.lock:
            iface = self.iface
        if iface is None:
            return False
        me = dict(iface.getMyUser() or {})
        me.pop("raw", None)
        iface.sendData(ParseDict(me, mesh_pb2.User(), ignore_unknown_fields=True),
                       portNum=portnums_pb2.PortNum.NODEINFO_APP, wantResponse=want_response)
        pos = (iface.nodesByNum or {}).get(iface.myInfo.my_node_num, {}).get("position", {})
        if "latitude" in pos and "longitude" in pos:
            iface.sendPosition(pos["latitude"], pos["longitude"], pos.get("altitude", 0))
        log.info("announced own node info%s", " (asking neighbours to reply)" if want_response else "")
        return True

    def prepare(self):
        """Configure the radio for Ura in one settings transaction (one reboot)."""
        with self.lock:
            iface = self.iface
        if iface is None:
            raise RuntimeError("radio not connected")
        ln = iface.localNode
        ln.beginSettingsTransaction()
        m = ln.moduleConfig.mqtt
        m.enabled, m.proxy_to_client_enabled, m.encryption_enabled = True, True, True
        m.address, m.map_reporting_enabled = URA_MQTT_ADDRESS, False
        ln.writeConfig("mqtt")
        ln.localConfig.lora.ignore_mqtt = False
        ln.writeConfig("lora")
        if ln.localConfig.security.debug_log_api_enabled:
            ln.localConfig.security.debug_log_api_enabled = False
            ln.writeConfig("security")
        for ch in ln.channels or []:
            if ch.role != 0 and not (ch.settings.uplink_enabled and ch.settings.downlink_enabled):
                ch.settings.uplink_enabled = ch.settings.downlink_enabled = True
                ln.writeChannel(ch.index)
        ln.commitSettingsTransaction()
        log.info("radio prepared for Ura (it restarts now)")


radios = {}       # radio id -> Radio
radio_queue: asyncio.Queue = None


def mt_radio():
    for r in radios.values():
        return r
    return None


def apply_radios():
    """(Re)create radio objects after a config change."""
    wanted = {r["id"]: r for r in cfg.get()["radios"] if r.get("net") == "mt" and r.get("enabled", True)}
    for rid in list(radios):
        if rid not in wanted or radios[rid].conf != wanted[rid]:
            radios.pop(rid).close()
    for rid, conf in wanted.items():
        if rid not in radios:
            radios[rid] = Radio(conf, radio_queue)


# ───────────────────────── server link ─────────────────────────

class Link:
    def __init__(self):
        self.state, self.detail = "not_configured", ""
        self.writer = None
        self.directory, self.links = [], []
        self.reconnect = asyncio.Event()

    def public_rules(self):
        c = cfg.get()
        peers = {h["id"]: h.get("code") for h in self.directory}
        out = {"airtime": c["airtime"], "default": c["defaults"], "links": {}}
        for l in self.links:
            if l["state"] == "active":
                out["links"][peers.get(l["peer"], l["peer_code"]) or l["peer"]] = cfg.rules_for(l["peer"])
        return out

    def radio_summary(self):
        out = []
        for r in radios.values():
            i = r.info()
            out.append({"net": "mt", "name": i.get("name"), "hw": i.get("hw"), "firmware": i.get("firmware"),
                        "connected": i.get("connected")})
        return out

    async def send(self, obj):
        w = self.writer
        if w is None:
            return False
        w.write((json.dumps(obj, separators=(",", ":")) + "\n").encode())
        await w.drain()
        return True

    async def push_info(self):
        await self.send({"t": "info", "info": {"rules": self.public_rules(), "radios": self.radio_summary()}})

    async def run(self):
        while True:
            c = cfg.get()["server"]
            if not (c["address"] and c["fingerprint"] and c["hub_id"] and c["key"]):
                self.state = "not_configured" if not c["hub_id"] else self.state
                await self._wait(30)
                continue
            try:
                self.state, self.detail = "connecting", ""
                reader, writer = await open_server(c["address"], c["fingerprint"])
                writer.write((json.dumps({"t": "hello", "hub": c["hub_id"], "key": c["key"], "version": VERSION,
                                          "info": {"rules": self.public_rules(), "radios": self.radio_summary()}}) + "\n").encode())
                first = json.loads(await asyncio.wait_for(reader.readline(), 15))
                if first.get("t") != "welcome":
                    self.state, self.detail = "refused", first.get("reason", "")
                    cfg.update(lambda d: d["server"].update(status=self.detail))
                    writer.close()
                    await self._wait(120)
                    continue
                self.writer = writer
                self.state = "connected"
                self.directory, self.links = first.get("hubs", []), first.get("links", [])
                cfg.update(lambda d: d["server"].update(status=first.get("status")))
                log.info("connected to server %s as %s (%s)", c["address"], c["hub_id"], first.get("status"))
                tasks = [asyncio.create_task(self._uplink()), asyncio.create_task(self._keepalive()),
                         asyncio.create_task(self._nodes())]
                try:
                    await self._push_info_soon()
                    while line := await asyncio.wait_for(reader.readline(), 120):
                        await self._on_message(json.loads(line))
                finally:
                    for tk in tasks:
                        tk.cancel()
                    self.writer = None
                    writer.close()
                self.state, self.detail = "disconnected", "server closed the connection"
            except ssl.SSLError as e:
                self.state, self.detail = "error", f"TLS: {e}"
            except FingerprintMismatch:
                self.state, self.detail = "fingerprint_mismatch", ""
                await self._wait(300)
            except Exception as e:
                self.state, self.detail = "error", str(e) or e.__class__.__name__
            self.writer = None
            await self._wait(5)

    async def _wait(self, seconds):
        self.reconnect.clear()
        try:
            await asyncio.wait_for(self.reconnect.wait(), seconds)
        except asyncio.TimeoutError:
            pass

    async def _push_info_soon(self):
        await asyncio.sleep(0)
        await self.push_info()

    async def _on_message(self, m):
        t = m.get("t")
        if t == "mesh" and m.get("net") == "mt":
            await asyncio.to_thread(receive_from_peer, m["from"], m["topic"], base64.b64decode(m["data"]))
        elif t == "directory":
            self.directory = m.get("hubs", [])
        elif t == "links":
            self.links = m.get("links", [])
            await self.push_info()
        elif t == "status":
            cfg.update(lambda d: d["server"].update(status=m.get("status")))
            if m.get("status") == "approved":
                await self.push_info()

    async def _uplink(self):
        while True:
            topic, data = await radio_queue.get()
            await asyncio.to_thread(send_to_peers, topic, data)

    async def _keepalive(self):
        while True:
            await asyncio.sleep(30)
            await self.send({"t": "ping"})

    async def _nodes(self):
        await asyncio.sleep(20)
        while True:
            r = mt_radio()
            if r:
                await self.send({"t": "nodes", "net": "mt", "nodes": r.nodes(cfg.get()["share_positions_on_map"])})
            await asyncio.sleep(NODES_EVERY)


class FingerprintMismatch(Exception):
    pass


async def open_server(address, fingerprint):
    host, _, port = address.rpartition(":")
    ctx = ssl.create_default_context()
    ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE     # pinned by fingerprint
    reader, writer = await asyncio.wait_for(asyncio.open_connection(host, int(port), ssl=ctx), 15)
    der = writer.get_extra_info("ssl_object").getpeercert(binary_form=True)
    if fingerprint and fp_of(der) != fingerprint:
        writer.close()
        raise FingerprintMismatch()
    return reader, writer


def fp_of(der):
    h = hashlib.sha256(der).hexdigest().upper()
    return ":".join(h[i:i + 2] for i in range(0, len(h), 2))


link: Link = None


def active_peers():
    return [l["peer"] for l in link.links if l["state"] == "active"]


def send_to_peers(topic, data):
    """Radio -> server: apply each link's SEND rule."""
    r = mt_radio()
    c = classify(data, r.channel_keys() if r else {})
    if c is None:
        return
    targets = []
    for peer in active_peers():
        ok, why = allowed(cfg.rules_for(peer)["send"], c)
        if ok:
            targets.append(peer)
            counters.peer_add(peer, "sent")
        else:
            counters.peer_add(peer, "blocked_send", why)
    if targets:
        counters.add("sent")
        asyncio.run_coroutine_threadsafe(link.send({"t": "mesh", "net": "mt", "topic": topic,
                                                    "data": base64.b64encode(data).decode(), "to": targets}), loop)


def receive_from_peer(peer, topic, data):
    """Server -> radio: apply the RECEIVE rule for this link and the airtime limit."""
    counters.add("received")
    r = mt_radio()
    if r is None:
        counters.peer_add(peer, "blocked_recv", "no_radio")
        return
    c = classify(data, r.channel_keys())
    if c is None:
        counters.peer_add(peer, "blocked_recv", "invalid")
        return
    ok, why = allowed(cfg.rules_for(peer)["receive"], c)
    if not ok:
        counters.peer_add(peer, "blocked_recv", why)
        return
    a = cfg.get()["airtime"]
    toa = time_on_air(c["size"] + 16, *r.lora_params())
    if (a.get("pct_hour") and counters.air_used(3600) + toa > 3600 * a["pct_hour"] / 100) or \
       (a.get("pct_day") and counters.air_used(86400) + toa > 86400 * a["pct_day"] / 100):
        counters.peer_add(peer, "blocked_recv", "airtime")
        return
    if r.downlink(topic, data):
        counters.air_add(toa)
        counters.peer_add(peer, "received")
    else:
        counters.peer_add(peer, "blocked_recv", "no_radio")


# ───────────────────────── website ─────────────────────────

sessions = {}
SESSION_TTL = 12 * 3600


def hash_pw(pw, salt=None):
    salt = salt or secrets.token_hex(16)
    return f"{salt}${hashlib.scrypt(pw.encode(), salt=salt.encode(), n=2 ** 14, r=8, p=1).hex()}"


def check_pw(pw, stored):
    return bool(stored and "$" in stored and hmac.compare_digest(hash_pw(pw, stored.split("$", 1)[0]), stored))


def run_coro(coro, timeout=20):
    return asyncio.run_coroutine_threadsafe(coro, loop).result(timeout)


async def server_check(address):
    reader, writer = await open_server(address, "")
    der = writer.get_extra_info("ssl_object").getpeercert(binary_form=True)
    writer.close()
    return fp_of(der)


async def server_join(address, fingerprint, hub):
    reader, writer = await open_server(address, fingerprint)
    writer.write((json.dumps(dict(hub, t="join")) + "\n").encode())
    reply = json.loads(await asyncio.wait_for(reader.readline(), 15))
    writer.close()
    return reply


def status_payload():
    c = cfg.get()
    r = mt_radio()
    return {"version": VERSION, "hub": c["hub"], "server": {k: c["server"][k] for k in ("address", "fingerprint", "hub_id", "status")},
            "link_state": link.state, "link_detail": link.detail, "radio": r.info() if r else None,
            "counters": counters.snapshot(), "airtime": {"used_hour": counters.air_used(3600), "used_day": counters.air_used(86400),
                                                       "limits": c["airtime"]},
            "links": link.links, "directory": link.directory}


class Web(http.server.BaseHTTPRequestHandler):
    server_version = "ura-hub"

    def log_message(self, fmt, *args):
        pass

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}") if n else {}

    def reply(self, obj, code=200, headers=None):
        data = json.dumps(obj, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def static(self, path):
        root = os.path.realpath(WEB_DIR)
        if path in ("", "/"):
            path = "/index.html"
        if path.startswith("/common/"):
            root, path = os.path.realpath(COMMON_DIR), path[len("/common"):]
        full = os.path.realpath(os.path.join(root, path.lstrip("/")))
        if not full.startswith(root + os.sep) or not os.path.isfile(full):
            full = os.path.join(os.path.realpath(WEB_DIR), "index.html")
        ctype = {".html": "text/html; charset=utf-8", ".js": "application/javascript; charset=utf-8",
                 ".css": "text/css; charset=utf-8", ".svg": "image/svg+xml", ".png": "image/png"}.get(os.path.splitext(full)[1], "application/octet-stream")
        data = open(full, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def authed(self):
        m = re.search(r"ura_hub=([A-Za-z0-9_-]+)", self.headers.get("Cookie") or "")
        return bool(m and sessions.get(m.group(1), 0) > time.time())

    def login_ok(self):
        tok = secrets.token_urlsafe(24)
        sessions[tok] = time.time() + SESSION_TTL
        self.reply({"ok": True}, headers={"Set-Cookie": f"ura_hub={tok}; Max-Age={SESSION_TTL}; Path=/; HttpOnly; Secure; SameSite=Strict"})

    def do_GET(self):
        p = urllib.parse.urlparse(self.path).path
        try:
            if not p.startswith("/api/"):
                return self.static(p)
            if p == "/api/session":
                return self.reply({"setup_needed": not cfg.get()["web_password"], "logged_in": self.authed(), "version": VERSION})
            if not self.authed():
                return self.reply({"error": "login"}, 401)
            if p == "/api/status":
                return self.reply(status_payload())
            if p == "/api/nodes":
                r = mt_radio()
                return self.reply(r.all_nodes() if r else [])
            if p == "/api/config":
                c = cfg.get()
                c.pop("web_password", None)
                c["server"].pop("key", None)
                return self.reply(c)
            if p == "/api/ports":
                return self.reply(sorted(glob.glob("/dev/serial/by-id/*")) or sorted(glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*")))
            self.reply({"error": "not_found"}, 404)
        except Exception as e:
            log.exception("GET %s", p)
            self.reply({"error": str(e)}, 500)

    def do_PUT(self):
        self.do_POST()

    def do_POST(self):
        p = urllib.parse.urlparse(self.path).path
        try:
            b = self.body()
            if p == "/api/setup":
                if cfg.get()["web_password"]:
                    return self.reply({"error": "already_set"}, 400)
                if len(b.get("password") or "") < 8:
                    return self.reply({"error": "password_short"}, 400)
                cfg.update(lambda d: d.update(web_password=hash_pw(b["password"])))
                return self.login_ok()
            if p == "/api/login":
                time.sleep(0.5)
                if check_pw(b.get("password") or "", cfg.get()["web_password"]):
                    return self.login_ok()
                return self.reply({"error": "wrong_password"}, 403)
            if p == "/api/logout":
                return self.reply({"ok": True}, headers={"Set-Cookie": "ura_hub=; Max-Age=0; Path=/; Secure"})
            if not self.authed():
                return self.reply({"error": "login"}, 401)
            return self.action(p, b)
        except Exception as e:
            log.exception("POST %s", p)
            self.reply({"error": str(e)}, 500)

    def action(self, p, b):
        if p == "/api/password":
            if len(b.get("password") or "") < 8:
                return self.reply({"error": "password_short"}, 400)
            cfg.update(lambda d: d.update(web_password=hash_pw(b["password"])))
            return self.reply({"ok": True})
        if p == "/api/hub":
            h = b.get("hub") or {}
            def upd(d):
                for k in ("name", "email", "country", "city", "description"):
                    if k in h:
                        d["hub"][k] = str(h[k] or "").strip()[:500]
                d["hub"]["country"], d["hub"]["city"] = d["hub"]["country"].upper()[:3], d["hub"]["city"].upper()[:3]
                for k in ("lat", "lon"):
                    if k in h:
                        try:
                            d["hub"][k] = float(h[k]) if h[k] not in (None, "") else None
                        except ValueError:
                            pass
                if "share_positions_on_map" in b:
                    d["share_positions_on_map"] = bool(b["share_positions_on_map"])
                if "airtime" in b:
                    d["airtime"] = {"pct_hour": max(0.0, min(100.0, float(b["airtime"].get("pct_hour") or 0))),
                                    "pct_day": max(0.0, min(100.0, float(b["airtime"].get("pct_day") or 0)))}
                if "defaults" in b:
                    d["defaults"] = clean_rules(b["defaults"])
            cfg.update(upd)
            run_coro(link.push_info())
            return self.reply({"ok": True})
        if p == "/api/server/check":
            addr = normalize_addr(b.get("address"))
            return self.reply({"address": addr, "fingerprint": run_coro(server_check(addr))})
        if p == "/api/server/trust":
            addr, fp = normalize_addr(b.get("address")), str(b.get("fingerprint") or "").upper()
            def upd(d):
                if d["server"]["address"] != addr:
                    d["server"].update(hub_id="", key="", status="")
                d["server"].update(address=addr, fingerprint=fp)
            cfg.update(upd)
            loop.call_soon_threadsafe(link.reconnect.set)
            return self.reply({"ok": True})
        if p == "/api/server/join":
            c = cfg.get()
            h = c["hub"]
            if c["server"]["hub_id"]:
                return self.reply({"error": "already_registered"}, 400)
            reply = run_coro(server_join(c["server"]["address"], c["server"]["fingerprint"],
                                         {k: h[k] for k in ("name", "email", "country", "city", "lat", "lon", "description")}))
            if reply.get("t") != "joined":
                return self.reply({"error": reply.get("reason", "refused")}, 400)
            cfg.update(lambda d: d["server"].update(hub_id=reply["hub"], key=reply["key"], status=reply["status"]))
            loop.call_soon_threadsafe(link.reconnect.set)
            return self.reply({"ok": True, "hub_id": reply["hub"]})
        if p == "/api/server/forget":
            cfg.update(lambda d: d["server"].update(hub_id="", key="", status=""))
            loop.call_soon_threadsafe(link.reconnect.set)
            if link.writer:
                loop.call_soon_threadsafe(link.writer.close)
            return self.reply({"ok": True})
        m = re.match(r"^/api/links/(request|accept|remove)$", p)
        if m:
            kind = m.group(1)
            msg = {"t": "link_" + kind}
            if kind == "request":
                msg["to"] = b.get("to")
            else:
                msg["link"] = int(b.get("link") or 0)
            if not run_coro(link.send(msg)):
                return self.reply({"error": "not_connected"}, 400)
            return self.reply({"ok": True})
        if p == "/api/rules":
            peer = str(b.get("peer") or "")
            rules = clean_rules(b.get("rules") or {})
            cfg.update(lambda d: d["rules"].__setitem__(peer, rules))
            run_coro(link.push_info())
            return self.reply({"ok": True})
        if p == "/api/radio":
            rc = b.get("radio") or {}
            transport = "tcp" if rc.get("transport") == "tcp" else "serial"
            addr = str(rc.get("address") or "").strip()
            if not addr:
                cfg.update(lambda d: d.update(radios=[]))
            else:
                cfg.update(lambda d: d.update(radios=[{"id": "r1", "net": "mt", "transport": transport, "address": addr,
                                                       "enabled": bool(rc.get("enabled", True))}]))
            loop.call_soon_threadsafe(apply_radios)
            return self.reply({"ok": True})
        if p == "/api/radio/prepare":
            r = mt_radio()
            if not r:
                return self.reply({"error": "no_radio"}, 400)
            r.prepare()
            return self.reply({"ok": True})
        if p == "/api/radio/announce":
            r = mt_radio()
            if not r or not r.announce(bool(b.get("ask"))):
                return self.reply({"error": "no_radio"}, 400)
            return self.reply({"ok": True})
        return self.reply({"error": "not_found"}, 404)


def normalize_addr(a):
    a = str(a or "").strip()
    a = re.sub(r"^[a-z]+://", "", a).strip("/")
    if not a:
        raise ValueError("address_required")
    if ":" not in a:
        a += ":8100"
    return a


def clean_rules(r):
    out = {}
    for d in ("send", "receive"):
        x = r.get(d) or {}
        out[d] = {"on": bool(x.get("on")), "public": bool(x.get("public")), "private": bool(x.get("private")),
                  "positions": bool(x.get("positions")), "groups": [str(g)[:30] for g in (x.get("groups") or [])][:8]}
    return out


class TLSWebServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, addr, handler, ctx):
        super().__init__(addr, handler)
        self.ctx = ctx

    def handle_error(self, request, client_address):
        import sys
        if isinstance(sys.exc_info()[1], (ssl.SSLError, ConnectionError, TimeoutError)):
            return                                         # browsers rejecting the self-signed certificate etc.
        super().handle_error(request, client_address)

    def get_request(self):
        sock, addr = super().get_request()
        sock.settimeout(30)
        return self.ctx.wrap_socket(sock, server_side=True, do_handshake_on_connect=False), addr


def run_web():
    crt, key = os.path.join(DATA_DIR, "web.crt"), os.path.join(DATA_DIR, "web.key")
    if not os.path.exists(crt):
        subprocess.run(["openssl", "req", "-x509", "-newkey", "ec", "-pkeyopt", "ec_paramgen_curve:P-256", "-nodes",
                        "-days", "3650", "-subj", "/CN=ura-hub", "-keyout", key, "-out", crt], check=True, capture_output=True)
        os.chmod(key, 0o600)
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.load_cert_chain(crt, key)
    srv = TLSWebServer(("0.0.0.0", WEB_PORT), Web, ctx)
    log.info("website on https://0.0.0.0:%d", WEB_PORT)
    srv.serve_forever()


# ───────────────────────── main ─────────────────────────

async def main():
    global cfg, loop, link, radio_queue
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    os.makedirs(DATA_DIR, exist_ok=True)
    os.chmod(DATA_DIR, 0o700)
    cfg = Config()
    loop = asyncio.get_running_loop()
    radio_queue = asyncio.Queue(maxsize=1000)
    link = Link()
    apply_radios()
    threading.Thread(target=run_web, daemon=True).start()
    loop.add_signal_handler(signal.SIGUSR1, lambda: mt_radio() and loop.run_in_executor(None, mt_radio().announce))
    loop.add_signal_handler(signal.SIGUSR2, lambda: mt_radio() and loop.run_in_executor(None, mt_radio().announce, True))
    log.info("ura-hub %s started", VERSION)
    await link.run()


if __name__ == "__main__":
    asyncio.run(main())
