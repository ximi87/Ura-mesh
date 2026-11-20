"""A simulated Meshtastic radio for tests (hub started with URA_TEST_RADIO=<this file>).

It looks like meshtastic's SerialInterface to the hub, so the hub's real radio code runs unchanged:
channels (#0 LongFast with the public default key, #1 "Team" with a private key shared by all fake
radios), a few local nodes with positions, every config/module section, owner, fixed position.
Everything the hub sends to the radio is recorded in `record` (read via GET /api/test/radio):
downlinked MQTT proxy messages, packets sent, settings written.
URA_TEST_NODE = this radio's node number in hex (default derived from the data folder)."""
import base64, hashlib, os, threading, time, types
from meshtastic.protobuf import channel_pb2, config_pb2, localonly_pb2, mesh_pb2

TEAM_PSK = hashlib.sha256(b"ura test team channel").digest()[:16]


class FakeNode:
    def __init__(self, iface):
        self.iface = iface
        lc, mc = localonly_pb2.LocalConfig(), localonly_pb2.LocalModuleConfig()
        lc.lora.use_preset, lc.lora.modem_preset = True, config_pb2.Config.LoRaConfig.ModemPreset.LONG_FAST
        lc.lora.region, lc.lora.ignore_mqtt = config_pb2.Config.LoRaConfig.RegionCode.EU_868, False
        lc.device.role = config_pb2.Config.DeviceConfig.Role.CLIENT
        mc.mqtt.enabled, mc.mqtt.proxy_to_client_enabled, mc.mqtt.encryption_enabled = True, True, True
        mc.mqtt.address, mc.mqtt.root = "127.0.0.1", "msh/EU_868"
        self.localConfig, self.moduleConfig = lc, mc
        self.channels = []
        for i in range(8):
            ch = channel_pb2.Channel(index=i, role=channel_pb2.Channel.Role.DISABLED)
            if i == 0:
                ch.role, ch.settings.psk = channel_pb2.Channel.Role.PRIMARY, b"\x01"
            elif i == 1:
                ch.role, ch.settings.name, ch.settings.psk = channel_pb2.Channel.Role.SECONDARY, "Team", TEAM_PSK
            if ch.role != channel_pb2.Channel.Role.DISABLED:
                ch.settings.uplink_enabled = ch.settings.downlink_enabled = True
            self.channels.append(ch)

    def _rec(self, what, **kw):
        self.iface.record["calls"].append({"call": what, "time": time.time(), **kw})

    def setTime(self, t=0): self._rec("setTime", t=t)
    def reboot(self, secs=10): self._rec("reboot", secs=secs)
    def beginSettingsTransaction(self): self._rec("begin")
    def commitSettingsTransaction(self): self._rec("commit")
    def writeChannel(self, index, adminIndex=0): self._rec("writeChannel", index=index, name=self.channels[index].settings.name,
                                                           role=int(self.channels[index].role))
    def deleteChannel(self, index): self.channels[index].role = 0; self._rec("deleteChannel", index=index)
    def getURL(self, includeAll=True): return "https://meshtastic.org/e/#TEST"

    def writeConfig(self, name):
        sec = getattr(self.localConfig, name, None) if self.localConfig.DESCRIPTOR.fields_by_name.get(name) else getattr(self.moduleConfig, name)
        from google.protobuf.json_format import MessageToDict
        self._rec("writeConfig", section=name, values=MessageToDict(sec, preserving_proto_field_name=True))

    def setOwner(self, long_name=None, short_name=None, is_licensed=False, **kw):
        u = self.iface.nodesByNum[self.iface.myInfo.my_node_num]["user"]
        if long_name: u["longName"] = long_name
        if short_name: u["shortName"] = short_name
        self._rec("setOwner", long_name=long_name, short_name=short_name)

    def setFixedPosition(self, lat, lon, alt=0):
        self.localConfig.position.fixed_position = True
        self.iface.nodesByNum[self.iface.myInfo.my_node_num]["position"] = {"latitude": lat, "longitude": lon, "altitude": alt}
        self._rec("setFixedPosition", lat=lat, lon=lon, alt=alt)

    def removeFixedPosition(self):
        self.localConfig.position.fixed_position = False
        self._rec("removeFixedPosition")


class FakeInterface:
    def __init__(self, conf=None):
        seed = os.environ.get("URA_TEST_NODE") or hashlib.sha256(os.environ.get("URA_DATA", "x").encode()).hexdigest()[:7]
        me = int(seed, 16) & 0x7FFFFFFF
        lat, lon = float(os.environ.get("URA_TEST_LAT", "45.0")), float(os.environ.get("URA_TEST_LON", "10.0"))
        self.myInfo = types.SimpleNamespace(my_node_num=me)
        self.metadata = types.SimpleNamespace(firmware_version="2.7.26-test")
        self.record = {"downlink": [], "sent": [], "calls": []}
        now = int(time.time())
        def node(num, name, dlat, dlon, heard):
            return {"num": num, "user": {"id": f"!{num:08x}", "longName": name, "shortName": name[:4], "hwModel": "HELTEC_V3"},
                    "position": {"latitude": lat + dlat, "longitude": lon + dlon, "altitude": 100}, "lastHeard": heard, "hopsAway": 0}
        self.nodesByNum = {me: node(me, "Test radio " + seed, 0, 0, now),
                           me + 1: node(me + 1, "Neighbour one", .01, .01, now - 60),
                           me + 2: node(me + 2, "Neighbour two", -.01, .02, now - 3600),
                           me + 3: node(me + 3, "Old node", .05, .05, now - 30 * 86400)}
        self.nodes = {n["user"]["id"]: n for n in self.nodesByNum.values()}
        self.localNode = FakeNode(self)
        self.isConnected = threading.Event(); self.isConnected.set()

    def getMyNodeInfo(self): return self.nodesByNum[self.myInfo.my_node_num]
    def getMyUser(self): return dict(self.nodesByNum[self.myInfo.my_node_num]["user"])

    def sendMqttClientProxyMessage(self, topic, data):
        self.record["downlink"].append({"topic": topic, "data": base64.b64encode(data).decode(), "time": time.time()})

    def sendData(self, data, destinationId="^all", portNum=0, wantResponse=False, **kw):
        self.record["sent"].append({"kind": "data", "port": int(portNum), "want_response": wantResponse})
    def sendTelemetry(self, *a, **kw): self.record["sent"].append({"kind": "telemetry"})
    def sendPosition(self, lat=0, lon=0, alt=0, *a, **kw): self.record["sent"].append({"kind": "position", "lat": lat, "lon": lon})
    def sendText(self, text, destinationId="^all", *a, **kw): self.record["sent"].append({"kind": "text", "to": destinationId})
    def close(self): self.isConnected.clear()
