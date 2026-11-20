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
import signal, socketserver, ssl, subprocess, threading, time, urllib.parse, urllib.request

from pubsub import pub
import meshtastic.serial_interface, meshtastic.tcp_interface
from google.protobuf.json_format import ParseDict
from meshtastic.protobuf import mesh_pb2, mqtt_pb2, portnums_pb2, config_pb2

from meshcrypto import expand_psk, decrypt_packet, new_private, x25519_public, link_keys, safety_code, seal, open_box

VERSION = "0.3.0"
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("URA_DATA", os.path.join(HERE, "data"))
WEB_PORT = int(os.environ.get("URA_WEB_PORT", "8091"))
WEB_DIR = os.path.join(HERE, "web")
COMMON_DIR = os.environ.get("URA_COMMON", os.path.join(os.path.dirname(HERE), "common"))
CONFIG = os.path.join(DATA_DIR, "config.json")

# Every operational value is a setting (website: Settings → Advanced). Only the data folder and the
# web port are startup options. key: (default, min, max)  — numbers; strings/bools have None limits.
ADV_SPEC = {
    "node_max_age_days":   (7, 1, 90),        # a node counts as "heard here" if heard within N days
    "nodes_report_min":    (10, 1, 120),      # full node report to the server at least every N minutes
    "nodes_check_s":       (60, 10, 3600),    # look for node changes every N seconds
    "location_follow_m":   (50, 5, 5000),     # follow the radio only when it moved more than N metres
    "location_check_s":    (30, 10, 3600),
    "clock_sync":          (True, None, None),
    "clock_sync_min":      (60, 5, 1440),
    "mqtt_address":        ("127.0.0.1", None, None),   # set by "Prepare radio"; must be a private IP
    "replay_window_s":     (600, 60, 3600),   # reject sealed boxes older than this / remember nonces this long
    "session_hours":       (12, 1, 720),
    "lockout_attempts":    (5, 3, 50),
    "lockout_minutes":     (15, 1, 1440),
    "password_min":        (8, 8, 64),
    "server_retry_s":      (5, 2, 600),
    "refused_retry_s":     (120, 10, 3600),
    "keepalive_s":         (30, 5, 300),
    "server_timeout_s":    (120, 30, 900),
    "queue_max":           (1000, 50, 20000), # packets kept while the server is unreachable
    "tile_source":         ("server", None, None),       # server = via the Ura server, then OpenStreetMap; or a URL with {z}/{x}/{y}
    "tile_cache_days":     (14, 1, 365),
    "tile_backoff_s":      (60, 5, 3600),
    "page_refresh_s":      (30, 5, 600),
    "diag_timeout_s":      (120, 10, 600),    # how long Diagnostics waits for an answer
    "radio_watchdog_min":  (10, 0, 240),      # radio silent this long -> restart it (0 = off); see Radio._keep_open
}

log = logging.getLogger("ura-hub")

REACH_ANY = 7                 # "anywhere": the longest chain a packet can make (8 links)
RULE_DEFAULT = {"on": True, "public": True, "groups": [], "private": True, "positions": True,
                # multi-hop, decided by each hub for itself:
                "reach": 0,           # send:    how many hubs BEYOND this peer my packets may travel (0 = stop there,
                                      #          REACH_ANY = as far as the other hubs allow)
                "onward_to": [],      # send:    which of this peer's links my packets may continue on (first step)
                "transit": True,      # send:    I pass other hubs' packets on to this peer (if transit is on)
                "from_beyond": True}  # receive: accept packets that started at hubs beyond this peer
DEFAULT_CONFIG = {
    "hub": {"name": "", "email": "", "country": "", "city": "", "lat": None, "lon": None, "description": "",
            "location_mode": "radio"},            # radio = follow the connected radio's position, manual = typed in
    "server": {"address": "", "fingerprint": "", "hub_id": "", "key": "", "status": "", "web_port": 8443},
    "radios": [],                 # [{"id","net":"mt","transport":"serial|tcp","address","enabled"}]
    "airtime": {"pct_hour": 10.0, "pct_day": 0.0},
    "defaults": {"send": dict(RULE_DEFAULT), "receive": dict(RULE_DEFAULT)},
    "rules": {},                  # peer hub id -> {"send": {...}, "receive": {...}}
    "share_positions_on_map": True,
    "transit": {"enabled": False, "max_hops": 2},   # pass traffic between my linked hubs (multi-hop)
    "advanced": {k: v[0] for k, v in ADV_SPEC.items()},
    "peer_keys": {},              # peer hub id -> pinned end-to-end public key (base64)
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


def adv(key):
    """Current value of an advanced setting (falls back to its default)."""
    v = cfg.get()["advanced"].get(key) if cfg else None
    return ADV_SPEC[key][0] if v is None else v


def clean_advanced(new):
    """Validate a posted advanced-settings dict against ADV_SPEC. Returns (values, errors)."""
    out, errors = {}, []
    for k, (default, lo, hi) in ADV_SPEC.items():
        if k not in new:
            continue
        v = new[k]
        try:
            if isinstance(default, bool):
                v = bool(v)
            elif isinstance(default, int):
                v = int(float(v))
            elif isinstance(default, float):
                v = float(v)
            else:
                v = str(v).strip()[:300]
        except (TypeError, ValueError):
            errors.append(k)
            continue
        if lo is not None and not (lo <= v <= hi):
            errors.append(k)
            continue
        if k == "mqtt_address" and not re.match(r"^(10|127|192\.168|172\.(1[6-9]|2\d|3[01]))\.\d+\.\d+(\.\d+)?$", v):
            errors.append(k)
            continue
        if k == "tile_source" and v != "server" and not (v.startswith("https://") and "{z}" in v and "{x}" in v and "{y}" in v):
            errors.append(k)
            continue
        out[k] = v
    return out, errors


# ───────────────────────── end-to-end identity ─────────────────────────

class Identity:
    """This hub's X25519 key pair. The public key is published through the server; the
    private key never leaves this computer (data/identity.key, mode 600)."""

    def __init__(self):
        path = os.path.join(DATA_DIR, "identity.key")
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(new_private())
            os.chmod(path, 0o600)
        self.private = open(path, "rb").read()
        self.public = x25519_public(self.private)
        self.public_b64 = base64.b64encode(self.public).decode()
        self._keys = {}

    def peer_key(self, peer):
        """(pubkey_b64, state): state ok | new | changed | missing."""
        h = next((x for x in link.directory if x["id"] == peer), None)
        cur = (h or {}).get("pubkey")
        pinned = cfg.get()["peer_keys"].get(peer)
        if not cur:
            return None, "missing"
        if pinned is None:
            return cur, "new"
        return cur, "ok" if pinned == cur else "changed"

    def pin_new(self):
        """Pin the key of every active link we have not seen before (trust on first use)."""
        for l in link.links:
            if l["state"] == "active":
                cur, state = self.peer_key(l["peer"])
                if state == "new":
                    cfg.update(lambda d: d["peer_keys"].__setitem__(l["peer"], cur))
                    log.info("pinned end-to-end key of %s", l["peer"])

    def keys_for(self, peer):
        cur, state = self.peer_key(peer)
        if state == "new":
            self.pin_new()
            cur, state = self.peer_key(peer)
        if state != "ok":
            return None, state
        k = self._keys.get(cur)
        if k is None:
            k = self._keys[cur] = link_keys(self.private, self.public, base64.b64decode(cur))
        return k, "ok"

    def safety(self, peer):
        cur, state = self.peer_key(peer)
        return {"code": safety_code(self.public, base64.b64decode(cur)) if cur else None, "state": state}


identity: Identity = None


class Origins:
    """Which linked hub a remote node came from (learned from packets), for the status page."""

    def __init__(self):
        self.path = os.path.join(DATA_DIR, "origins.json")
        self.lock = threading.Lock()
        try:
            self.map = json.load(open(self.path))
        except Exception:
            self.map = {}
        self.dirty, self.saved = 0, 0

    def note(self, node_id, peer):
        with self.lock:
            if self.map.get(node_id) != peer:
                self.map[node_id] = peer
                self.dirty += 1
            if self.dirty and (self.dirty > 20 or time.time() - self.saved > 60 or not os.path.exists(self.path)):
                self.save()

    def save(self):
        tmp = self.path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self.map, f)
        os.replace(tmp, self.path)
        self.dirty, self.saved = 0, time.time()

    def get(self, node_id):
        return self.map.get(node_id)


origins: Origins = None


class SeenCache:
    """Drop replays (same box nonce) and duplicates (same packet from two routes) for 10 minutes."""

    def __init__(self):
        self.d, self.lock = {}, threading.Lock()

    def seen(self, key):
        self.ttl = adv("replay_window_s")
        t = time.time()
        with self.lock:
            if len(self.d) > 5000:
                self.d = {k: v for k, v in self.d.items() if t - v < self.ttl}
            if key in self.d and t - self.d[key] < self.ttl:
                return True
            self.d[key] = t
            return False


seen_cache = SeenCache()


# ───────────────────────── counters ─────────────────────────

class Counters:
    def __init__(self):
        self.lock = threading.Lock()
        self.g = {"heard": 0, "uplinked": 0, "sent": 0, "received": 0, "to_radio": 0, "transit": 0}
        self.last_block = {}           # peer -> reason of the last blocked packet (for the log)
        self.peer = {}          # peer -> {"sent", "received", "blocked_send": {reason: n}, "blocked_recv": {...}}
        self.airtime = []       # [(time, seconds)]
        self.started = time.time()

    def add(self, key, n=1):
        with self.lock:
            self.g[key] = self.g.get(key, 0) + n

    def p(self, peer):
        return self.peer.setdefault(peer, {"sent": 0, "received": 0, "transit": 0, "blocked_send": {}, "blocked_recv": {}})

    def peer_add(self, peer, key, reason=None):
        with self.lock:
            p = self.p(peer)
            if reason:
                p[key][reason] = p[key].get(reason, 0) + 1
                self.last_block[peer] = reason
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
           "sender": f"!{getattr(pkt, 'from'):08x}",
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
        self.stats = {}                   # what the radio reports about its own reception
        self.own_fix = None               # the radio's own position at full precision
        self.last_rx = time.time()        # last time the radio sent the hub anything at all
        self.watchdog = []                # times the watchdog had to act (7 days)
        self.wd_events = []               # what it found and did: [{time, stage, finding}]
        self.wd_stage, self.wd_at = 0, 0  # 0 normal, 1 fresh USB session tried, 2 radio restarted
        self.last_pkt = time.time()       # last live packet/proxy message (not the config dump at connect)
        self.hour_pk = self.hour_px = 0   # counts for the hourly log line
        self.hour_start = time.time()
        pub.subscribe(self._on_proxy, "meshtastic.mqttclientproxymessage")
        pub.subscribe(self._on_lost, "meshtastic.connection.lost")
        pub.subscribe(self._on_packet, "meshtastic.receive")
        threading.Thread(target=self._keep_open, daemon=True).start()

    # events from the meshtastic library threads
    def _mine(self, interface):
        return interface is self.iface

    def _on_proxy(self, proxymessage, interface):
        if self._mine(interface):
            self.last_rx = self.last_pkt = time.time()
            self.hour_px += 1
        if self._mine(interface) and proxymessage.data:
            counters.add("uplinked")
            loop.call_soon_threadsafe(self._enqueue, (proxymessage.topic, bytes(proxymessage.data)))

    def _enqueue(self, item):
        enqueue(self.queue, item)

    def _on_packet(self, packet, interface):
        if not self._mine(interface):
            return
        self.last_rx = self.last_pkt = time.time()
        self.hour_pk += 1
        if packet.get("from") != interface.myInfo.my_node_num:
            if not packet.get("viaMqtt"):
                counters.add("heard")
            return
        pos = packet.get("decoded", {}).get("position")
        if pos and pos.get("precisionBits") in (None, 0, 32):
            self._set_fix(pos)                # precise own fix (e.g. GPS); privacy-rounded copies are ignored
        tel = packet.get("decoded", {}).get("telemetry", {})
        if "deviceMetrics" in tel or "localStats" in tel:
            st = dict(self.stats)
            st.update(tel.get("deviceMetrics", {}))
            st.update(tel.get("localStats", {}))
            st["time"] = int(time.time())
            self.stats = st

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
        if os.environ.get("URA_TEST_RADIO"):           # tests only: a simulated radio (tests/fake_radio.py)
            import importlib.util
            spec = importlib.util.spec_from_file_location("fake_radio", os.environ["URA_TEST_RADIO"])
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod.FakeInterface(c)
        if c.get("transport") == "tcp":
            host, _, port = c["address"].partition(":")
            return meshtastic.tcp_interface.TCPInterface(host, portNumber=int(port or 4403))
        ports = sorted(glob.glob(c["address"]))
        if not ports:
            raise RuntimeError("port not present")
        return meshtastic.serial_interface.SerialInterface(ports[0])

    def _keep_open(self):
        time_set = 0
        while not self.stop:
            if self.iface is None and self.conf.get("enabled", True):
                try:
                    iface = self._open()
                    with self.lock:
                        self.iface, self.error, self.connected_at = iface, "", time.time()
                    self.last_rx = time.time()
                    if not self.wd_stage:
                        self.last_pkt = time.time()
                    time_set = 0
                    p = (iface.nodesByNum or {}).get(iface.myInfo.my_node_num, {}).get("position", {})
                    self._set_fix(p)
                    log.info("radio connected: %s (%s)", self.info().get("name"), self.conf.get("address"))
                except Exception as e:
                    self.error = str(e)
            # Radios without GPS/internet drift or keep an old clock; their "last heard" times and message
            # timestamps then go wrong. Give the radio this computer's clock on connect and every hour.
            if adv("clock_sync") and self.iface is not None and time.time() - time_set > adv("clock_sync_min") * 60 \
                    and time.gmtime().tm_year >= 2025:
                try:
                    self.iface.localNode.setTime(int(time.time()))
                    time_set = time.time()
                    log.info("radio clock set from this computer")
                except Exception as e:
                    log.warning("setting radio clock failed: %s", e)
                    time_set = time.time() - adv("clock_sync_min") * 60 + 300
            self._watchdog()
            time.sleep(5)

    def _wd_note(self, stage, finding, level=logging.WARNING):
        log.log(level, "radio watchdog: %s", finding)
        self.wd_events = [e for e in self.wd_events if time.time() - e["time"] < 7 * 86400][-49:] + \
                         [{"time": int(time.time()), "stage": stage, "finding": finding}]

    def _wd_probe(self, iface):
        """Where did the packets stop? Checked before touching anything."""
        out = []
        rx = getattr(iface, "_rxThread", None)
        out.append("hub reader thread " + ("alive" if rx is not None and rx.is_alive() else "DEAD"))
        try:
            out.append(f"{iface.stream.in_waiting} unread bytes from the radio")
        except Exception:
            pass
        try:
            from meshtastic import publishingThread as pt
            out.append(f"event thread {'alive' if pt.thread.is_alive() else 'DEAD'}, {pt.queue.qsize()} events waiting")
        except Exception:
            pass
        out.append(f"last packet {int(time.time() - self.last_pkt)} s ago")
        return "; ".join(out)

    def _hourly(self):
        if time.time() - self.hour_start >= 3600:
            log.info("radio last hour: %d packets, %d handed to Ura (MQTT proxy)", self.hour_pk, self.hour_px)
            self.hour_pk = self.hour_px = 0
            self.hour_start = time.time()

    def _drop(self, iface, why, reboot):
        if reboot:
            try:
                iface.localNode.reboot(3)
            except Exception as e:
                log.warning("watchdog: radio restart command failed: %s", e)
        with self.lock:
            if self.iface is iface:
                self.iface, self.error = None, why
        try:
            iface.close()
        except Exception:
            pass

    def _watchdog(self):
        """A connected radio sends its hub something at least every minute or two. If it stays silent, find out
        where it stopped and fix it with the gentlest step that works:
          1. log where the packets stop (hub's reader/event threads, unread bytes) — hub side or radio side;
          2. open a fresh USB session (no restart): fixes a radio that dropped its session with the hub;
          3. still nothing a few minutes later -> restart the radio: the radio itself had stalled.
        Every finding goes to the log and to the Status page."""
        self._hourly()
        limit = adv("radio_watchdog_min") * 60
        iface = self.iface
        if not limit or iface is None:
            return
        now = time.time()
        if self.wd_stage and self.last_pkt > self.wd_at:
            what = "a fresh USB session" if self.wd_stage == 1 else "restarting the radio"
            self._wd_note(0, f"packets flow again after {what} (silence ended {int(now - self.wd_at)} s after the step)", logging.INFO)
            self.wd_stage = 0
            return
        if self.wd_stage == 1 and now - self.wd_at > max(300, limit / 2):
            self._wd_note(2, "still silent with a fresh USB session — the radio itself stalled; restarting it. " + self._wd_probe(iface))
            self.wd_stage, self.wd_at = 2, now
            self.watchdog = [t for t in self.watchdog if now - t < 7 * 86400] + [now]
            return self._drop(iface, "restarted by the watchdog (radio stalled)", True)
        if self.wd_stage == 2 and now - self.wd_at > limit:
            self.wd_stage = 0                 # give up this round; start again from step 1 next time
        if self.wd_stage or now - self.last_pkt < limit:
            return
        self._wd_note(1, f"no packets for {int(now - self.last_pkt)} s — " + self._wd_probe(iface) + "; opening a fresh USB session")
        self.wd_stage, self.wd_at = 1, now
        self.watchdog = [t for t in self.watchdog if now - t < 7 * 86400] + [now]
        self._drop(iface, "fresh USB session opened by the watchdog", False)

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
                "address": self.conf.get("address"), "connected": iface is not None, "error": self.error,
                "silent_s": int(time.time() - self.last_pkt), "watchdog": [int(t) for t in self.watchdog],
                "watchdog_events": self.wd_events[-10:]}
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
                "private_address": mc.mqtt.address == adv("mqtt_address") or bool(re.match(r"^(10|127|192\.168|172\.(1[6-9]|2\d|3[01]))\.", mc.mqtt.address or "")),
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
            if num != my and (n.get("viaMqtt") or not n.get("lastHeard") or time.time() - n["lastHeard"] > adv("node_max_age_days") * 86400):
                continue                      # remote nodes belong to the hub that heard them; old/no time = stale memory
            u, p = n.get("user", {}), n.get("position", {})
            if num == my and self.own_fix:
                p = {"latitude": self.own_fix["lat"], "longitude": self.own_fix["lon"], "altitude": self.own_fix["alt"]}
            out.append({"id": u.get("id") or f"!{num:08x}", "name": u.get("longName"), "short": u.get("shortName"),
                        "hw": u.get("hwModel"), "role": u.get("role"),
                        "lat": p.get("latitude") if share_positions else None,
                        "lon": p.get("longitude") if share_positions else None,
                        "alt": p.get("altitude") if share_positions else None,
                        "last_heard": n.get("lastHeard") or (int(time.time()) if num == my else None),
                        "hops": n.get("hopsAway"), "own": num == my})
        return out

    def _set_fix(self, p):
        if p and p.get("latitude") is not None and p.get("longitude") is not None and not (p["latitude"] == 0 and p["longitude"] == 0):
            self.own_fix = {"lat": p["latitude"], "lon": p["longitude"], "alt": p.get("altitude")}

    def own_position(self):
        """The radio's own position at full precision. Its broadcasts are rounded by the channel's
        position precision (privacy), so those copies are not used for the hub's location."""
        return self.own_fix if self.iface is not None else None

    def all_nodes(self):
        with self.lock:
            iface = self.iface
        if iface is None:
            return []
        my = iface.myInfo.my_node_num
        out = []
        for num, n in list((iface.nodesByNum or {}).items()):
            u, p = n.get("user", {}), n.get("position", {})
            if num == my and self.own_fix:
                p = {"latitude": self.own_fix["lat"], "longitude": self.own_fix["lon"]}
            out.append({"id": u.get("id") or f"!{num:08x}", "name": u.get("longName"), "short": u.get("shortName"),
                        "hw": u.get("hwModel"), "lat": p.get("latitude"), "lon": p.get("longitude"),
                        "last_heard": n.get("lastHeard"), "hops": n.get("hopsAway"), "snr": n.get("snr"),
                        "remote": bool(n.get("viaMqtt")) and num != my, "own": num == my,
                        "origin": origins.get(u.get("id") or f"!{num:08x}")})
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
        iface.sendTelemetry()        # firmware may drop node info sent by a client; telemetry always goes out
        pos = (iface.nodesByNum or {}).get(iface.myInfo.my_node_num, {}).get("position", {})
        if "latitude" in pos and "longitude" in pos:
            iface.sendPosition(pos["latitude"], pos["longitude"], pos.get("altitude", 0))
        log.info("announced own node info%s", " (asking neighbours to reply)" if want_response else "")
        return True

    def diagnose(self, node, kind, text=""):
        """Send a test to a node from this radio and wait for the answer (Radio → Diagnostics)."""
        with self.lock:
            iface = self.iface
        if iface is None:
            raise RuntimeError("no_radio")
        if kind == "broadcast":                    # test message to a channel (group); no answer expected
            ch = int(node) if str(node).isdigit() else 0
            iface.sendText(text[:200] or "Ura test", channelIndex=ch)
            log.info("diagnostics broadcast on channel %s", ch)
            return {"answered": True, "seconds": 0, "result": "sent"}
        ev, out, sent = threading.Event(), {}, {}
        target = int(node.lstrip("!"), 16)
        wants_data = kind in ("trace", "telemetry", "position")   # a plain "received" ack is not the answer

        def on_packet(packet, interface):
            # Answers carry request_id = our packet id. Accept: a reply/ack FROM THE TARGET, or a routing
            # error from anyone (e.g. our own radio giving up). Our own radio's local "ok" ack is ignored.
            if interface is not iface or not sent.get("id"):
                return
            d = packet.get("decoded", {})
            if d.get("requestId") != sent["id"]:
                return
            reason = d.get("routing", {}).get("errorReason", "NONE") if d.get("portnum") == "ROUTING_APP" else None
            if wants_data and reason == "NONE":
                if packet.get("from") == target:
                    out["acked"] = True           # the node got the request; keep waiting for its data
                return
            if packet.get("from") == target or (reason not in (None, "NONE")):
                out["packet"] = packet
                ev.set()
        pub.subscribe(on_packet, "meshtastic.receive")
        kw = {"destinationId": node}
        try:
            if kind == "dm":
                pkt = iface.sendData(text.encode()[:200] or b"Ura test", portNum=portnums_pb2.PortNum.TEXT_MESSAGE_APP, wantAck=True, **kw)
            elif kind == "trace":
                pkt = iface.sendData(mesh_pb2.RouteDiscovery(), portNum=portnums_pb2.PortNum.TRACEROUTE_APP, wantResponse=True, hopLimit=7, **kw)
            elif kind == "telemetry":
                from meshtastic.protobuf import telemetry_pb2
                # a telemetry request must name the kind wanted, otherwise nodes do not answer
                pkt = iface.sendData(telemetry_pb2.Telemetry(device_metrics=telemetry_pb2.DeviceMetrics()),
                                     portNum=portnums_pb2.PortNum.TELEMETRY_APP, wantResponse=True, **kw)
            elif kind == "position":
                pkt = iface.sendData(mesh_pb2.Position(), portNum=portnums_pb2.PortNum.POSITION_APP, wantResponse=True, **kw)
            else:
                raise ValueError("bad_kind")
            sent["id"] = pkt.id
            t0 = time.time()
            answered = ev.wait(adv("diag_timeout_s"))
        finally:
            pub.unsubscribe(on_packet, "meshtastic.receive")
        res = {"answered": answered, "seconds": round(time.time() - t0, 1)}
        if not answered and out.get("acked"):
            res["result"] = "no_data"             # received the request, but did not send the data back
        if answered:
            d = out["packet"].get("decoded", {})
            res["from"] = out["packet"].get("fromId")
            if d.get("portnum") == "ROUTING_APP":
                reason = d.get("routing", {}).get("errorReason", "NONE")
                res["result"] = "delivered" if reason == "NONE" else reason
            elif "traceroute" in d:
                names = lambda ids: [(iface.nodesByNum.get(i, {}).get("user", {}).get("longName") or f"!{i:08x}") for i in ids]
                tr = d["traceroute"]
                res["route_to"] = names(tr.get("route", []))
                res["route_back"] = names(tr.get("routeBack", []))
                res["result"] = "route"
            elif "telemetry" in d:
                res["telemetry"] = {k: v for k, v in d["telemetry"].items() if k != "time"}
                res["result"] = "telemetry"
            elif "position" in d:
                pos = d["position"]
                res["position"] = {"lat": pos.get("latitude"), "lon": pos.get("longitude"), "alt": pos.get("altitude")}
                res["result"] = "position"
            else:
                res["result"] = d.get("portnum")
        log.info("diagnostics %s -> %s: %s", kind, node, res.get("result", "no answer"))
        return res

    # ───── programming the radio (Radio → Device settings) ─────
    HIDDEN_FIELDS = {"security.private_key"}           # never leaves the radio through Ura
    REBOOT_SECTIONS = {"device", "lora", "network", "bluetooth", "security", "position", "power", "display"}

    @staticmethod
    def _schema_of(msg, prefix=""):
        """Describe every field of a protobuf config section (built from Meshtastic's own definitions)."""
        from google.protobuf.descriptor import FieldDescriptor as F
        out = []
        for f in msg.DESCRIPTOR.fields:
            name = prefix + f.name
            repeated = f.is_repeated if hasattr(f, "is_repeated") else f.label == F.LABEL_REPEATED
            if f.type == F.TYPE_MESSAGE and not repeated:
                out += Radio._schema_of(getattr(msg, f.name), name + ".")
                continue
            kind = ("bool" if f.type == F.TYPE_BOOL else "enum" if f.type == F.TYPE_ENUM else
                    "string" if f.type == F.TYPE_STRING else "float" if f.type in (F.TYPE_FLOAT, F.TYPE_DOUBLE) else
                    "bytes" if f.type == F.TYPE_BYTES else "message" if f.type == F.TYPE_MESSAGE else "int")
            item = {"name": name, "type": kind, "repeated": repeated,
                    "readonly": repeated or kind in ("bytes", "message"),
                    "unsigned": f.type in (F.TYPE_UINT32, F.TYPE_UINT64, F.TYPE_FIXED32, F.TYPE_FIXED64)}
            if kind == "enum":
                item["options"] = [v.name for v in f.enum_type.values]
            out.append(item)
        return out

    @staticmethod
    def _get(msg, dotted):
        for part in dotted.split(".")[:-1]:
            msg = getattr(msg, part)
        return msg, dotted.split(".")[-1]

    def _section(self, kind, section):
        ln = self.iface.localNode
        root = ln.localConfig if kind == "config" else ln.moduleConfig
        if section not in [f.name for f in root.DESCRIPTOR.fields] or section == "version":
            raise ValueError("bad_section")
        return getattr(root, section)

    def settings(self):
        with self.lock:
            iface = self.iface
        if iface is None:
            raise RuntimeError("no_radio")
        ln = iface.localNode
        from google.protobuf.descriptor import FieldDescriptor as F
        out = {"sections": []}
        for kind, root in (("config", ln.localConfig), ("module", ln.moduleConfig)):
            for f in root.DESCRIPTOR.fields:
                if f.name == "version" or f.type != F.TYPE_MESSAGE:
                    continue
                sec = getattr(root, f.name)
                fields, values = [], {}
                for item in self._schema_of(sec):
                    full = f"{f.name}.{item['name']}"
                    if full in self.HIDDEN_FIELDS:
                        continue
                    m, leaf = self._get(sec, item["name"])
                    v = getattr(m, leaf)
                    if item["repeated"]:
                        v = [base64.b64encode(bytes(x)).decode() if isinstance(x, bytes) else str(x) for x in v]
                    elif item["type"] == "enum":
                        ev = m.DESCRIPTOR.fields_by_name[leaf].enum_type.values_by_number
                        v = ev[v].name if v in ev else v
                    elif item["type"] == "bytes":
                        v = base64.b64encode(bytes(v)).decode()
                    elif item["type"] == "message":
                        v = str(v)
                    fields.append(item)
                    values[item["name"]] = v
                out["sections"].append({"kind": kind, "name": f.name, "fields": fields, "values": values,
                                        "reboot": f.name in self.REBOOT_SECTIONS})
        me = iface.getMyUser() or {}
        out["owner"] = {"long_name": me.get("longName", ""), "short_name": me.get("shortName", ""),
                        "is_licensed": bool(me.get("isLicensed"))}
        chans = []
        for ch in ln.channels or []:
            psk = bytes(ch.settings.psk)
            chans.append({"index": ch.index, "role": ["DISABLED", "PRIMARY", "SECONDARY"][ch.role],
                          "name": ch.settings.name, "psk": "default" if psk == b"\x01" else "none" if not psk else base64.b64encode(psk).decode(),
                          "uplink": ch.settings.uplink_enabled, "downlink": ch.settings.downlink_enabled,
                          "position_precision": ch.settings.module_settings.position_precision,
                          "muted": ch.settings.module_settings.is_muted})
        out["channels"] = chans
        out["fixed"] = {"enabled": ln.localConfig.position.fixed_position, **(self.own_fix or {})}
        try:
            out["url"] = ln.getURL(includeAll=True)
        except Exception:
            out["url"] = ""
        return out

    def set_section(self, kind, section, values):
        """Validate and write one config section. Returns True if the radio will restart."""
        with self.lock:
            iface = self.iface
        if iface is None:
            raise RuntimeError("no_radio")
        sec = self._section(kind, section)
        schema = {i["name"]: i for i in self._schema_of(sec)}
        for name, v in values.items():
            item = schema.get(name)
            if not item or item["readonly"] or f"{section}.{name}" in self.HIDDEN_FIELDS:
                raise ValueError(f"field:{name}")
            m, leaf = self._get(sec, name)
            try:
                if item["type"] == "bool":
                    v = bool(v)
                elif item["type"] == "enum":
                    v = m.DESCRIPTOR.fields_by_name[leaf].enum_type.values_by_name[str(v)].number
                elif item["type"] == "float":
                    v = float(v)
                elif item["type"] == "int":
                    v = int(float(v))
                    if item["unsigned"] and v < 0:
                        raise ValueError
                else:
                    v = str(v)
                setattr(m, leaf, v)
            except Exception:
                raise ValueError(f"field:{name}")
        iface.localNode.writeConfig(section)
        log.info("radio settings written: %s.%s (%d fields)", kind, section, len(values))
        return section in self.REBOOT_SECTIONS

    def set_owner(self, long_name, short_name, is_licensed=False):
        long_name, short_name = str(long_name or "").strip(), str(short_name or "").strip()
        if not (1 <= len(long_name) <= 39 and 1 <= len(short_name) <= 4):
            raise ValueError("owner")
        self.iface.localNode.setOwner(long_name, short_name, is_licensed=bool(is_licensed))
        log.info("radio owner set: %s (%s)", long_name, short_name)

    def set_channel(self, data):
        ln = self.iface.localNode
        idx = int(data.get("index", -1))
        if not 0 <= idx < 8:
            raise ValueError("channel_index")
        role = str(data.get("role", "SECONDARY")).upper()
        if role == "DISABLED":
            if idx == 0:
                raise ValueError("primary_needed")
            ln.deleteChannel(idx)
            log.info("radio channel %d deleted", idx)
            return
        if (idx == 0) != (role == "PRIMARY"):
            raise ValueError("channel_role")
        name = str(data.get("name") or "").strip()
        if len(name.encode()) > 11:
            raise ValueError("channel_name")
        psk = str(data.get("psk") or "default")
        if psk == "default":
            key = b"\x01"
        elif psk == "none":
            key = b""
        elif psk == "random":
            key = os.urandom(32)
        else:
            key = base64.b64decode(psk, validate=True)
            if len(key) not in (1, 16, 32):
                raise ValueError("channel_psk")
        ch = ln.channels[idx]
        ch.role = 1 if role == "PRIMARY" else 2
        ch.settings.name, ch.settings.psk = name, key
        ch.settings.uplink_enabled = bool(data.get("uplink", True))
        ch.settings.downlink_enabled = bool(data.get("downlink", True))
        pp = int(data.get("position_precision", ch.settings.module_settings.position_precision) or 0)
        if not 0 <= pp <= 32:
            raise ValueError("position_precision")
        ch.settings.module_settings.position_precision = pp
        ch.settings.module_settings.is_muted = bool(data.get("muted", False))
        ln.writeChannel(idx)
        log.info("radio channel %d written: %s", idx, name or "(preset name)")

    def set_fixed(self, data):
        ln = self.iface.localNode
        if not data.get("enabled"):
            ln.removeFixedPosition()
            log.info("radio fixed position removed")
            return
        lat, lon, alt = float(data["lat"]), float(data["lon"]), int(float(data.get("alt") or 0))
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("position")
        ln.setFixedPosition(lat, lon, alt)
        self.own_fix = {"lat": lat, "lon": lon, "alt": alt}
        log.info("radio fixed position set: %s, %s", lat, lon)

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
        m.address, m.map_reporting_enabled = adv("mqtt_address"), False
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


def enqueue(q, item):
    """Packets from the radio wait here while the server is unreachable; above "queue_max" the oldest go."""
    while q.qsize() >= adv("queue_max"):
        q.get_nowait()
    q.put_nowait(item)


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
        self.kick_nodes = asyncio.Event()     # report nodes now (approved, reconnected, settings changed)
        self.kick_location = asyncio.Event()  # send the location now (settings changed, reconnected)

    def public_rules(self):
        c = cfg.get()
        peers = {h["id"]: h.get("code") for h in self.directory}
        out = {"airtime": c["airtime"], "default": c["defaults"], "links": {}, "transit": c["transit"], "transit_to": []}
        for l in self.links:
            if l["state"] == "active":
                r = cfg.rules_for(l["peer"])
                out["links"][peers.get(l["peer"], l["peer_code"]) or l["peer"]] = r
                if c["transit"].get("enabled") and r["send"].get("transit", True) and r["send"].get("on"):
                    out["transit_to"].append(l["peer"])      # hubs I offer to pass other hubs' traffic to
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

    def info_payload(self):
        return {"rules": self.public_rules(), "radios": self.radio_summary(), "pubkey": identity.public_b64}

    async def push_info(self):
        await self.send({"t": "info", "info": self.info_payload()})

    async def run(self):
        while True:
            c = cfg.get()["server"]
            if not (c["address"] and c["fingerprint"] and c["hub_id"] and c["key"]):
                self.state = "not_configured" if not c["hub_id"] else self.state
                await self._wait(adv("refused_retry_s"))
                continue
            try:
                self.state, self.detail = "connecting", ""
                reader, writer = await open_server(c["address"], c["fingerprint"])
                writer.write((json.dumps({"t": "hello", "hub": c["hub_id"], "key": c["key"], "version": VERSION,
                                          "info": self.info_payload()}) + "\n").encode())
                first = json.loads(await asyncio.wait_for(reader.readline(), 15))
                if first.get("t") != "welcome":
                    self.state, self.detail = "refused", first.get("reason", "")
                    cfg.update(lambda d: d["server"].update(status=self.detail))
                    writer.close()
                    await self._wait(adv("refused_retry_s"))
                    continue
                self.writer = writer
                self.state = "connected"
                self.directory = first.get("hubs", [])
                self.set_links(first.get("links", []))
                identity.pin_new()
                cfg.update(lambda d: d["server"].update(status=first.get("status")))
                log.info("connected to server %s as %s (%s)", c["address"], c["hub_id"], first.get("status"))
                self.kick()                   # a (re)connected server gets the current nodes and location at once
                tasks = [asyncio.create_task(self._uplink()), asyncio.create_task(self._keepalive()),
                         asyncio.create_task(self._nodes()), asyncio.create_task(self._location())]
                try:
                    await self._push_info_soon()
                    last_rx = time.time()
                    while True:                   # the server answers every ping; silent longer than
                        try:                      # "server_timeout_s" (re-read every 5 s) = dead connection
                            line = await asyncio.wait_for(reader.readline(), 5)
                        except asyncio.TimeoutError:
                            if time.time() - last_rx > adv("server_timeout_s"):
                                raise ConnectionError(f"no answer from the server for {adv('server_timeout_s')} s")
                            continue
                        if not line:
                            break
                        last_rx = time.time()
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
                await self._wait(adv("refused_retry_s"))
            except Exception as e:
                self.state, self.detail = "error", str(e) or e.__class__.__name__
            self.writer = None
            await self._wait(adv("server_retry_s"))

    def set_links(self, links):
        """The server's full list of this hub's links (on connect and on every change). Keep the per-link
        rules in step with it: a new link gets its OWN copy of the defaults (changing the defaults later must
        not change existing links); rules of a link that ended — or of an old registration — are forgotten,
        so a new link with that hub starts from the defaults."""
        self.links = links
        now_peers = {l["peer"] for l in links}
        def upd(d):
            for peer in now_peers:
                if peer not in d["rules"]:
                    d["rules"][peer] = copy.deepcopy(d["defaults"])
            for peer in list(d["rules"]):
                if peer not in now_peers:
                    d["rules"].pop(peer, None)
        cfg.update(upd)

    def kick(self):
        """Report nodes and location now (from any thread)."""
        for ev in (self.kick_nodes, self.kick_location):
            loop.call_soon_threadsafe(ev.set)

    @staticmethod
    async def _sleep_or(ev, seconds):
        try:
            await asyncio.wait_for(ev.wait(), seconds)
        except asyncio.TimeoutError:
            pass
        kicked = ev.is_set()
        ev.clear()
        return kicked

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
        if t == "mesh" and m.get("net") == "mt" and m.get("box"):
            await asyncio.to_thread(receive_box, m["from"], base64.b64decode(m["box"]))
        elif t == "directory":
            self.directory = m.get("hubs", [])
            identity.pin_new()
        elif t == "links":
            self.set_links(m.get("links", []))
            identity.pin_new()
            await self.push_info()
        elif t == "peer_nodes" and m.get("hub") in active_peers():
            for nid in (m.get("ids") or [])[:3000]:
                origins.note(str(nid)[:12], m["hub"])
        elif t == "status":
            cfg.update(lambda d: d["server"].update(status=m.get("status")))
            if m.get("status") == "approved":
                await self.push_info()
                self.kick()                   # the server ignored nodes while the hub was pending

    async def _uplink(self):
        # after a reconnect (e.g. the server restarted) give the linked hubs a moment to come back before
        # sending what the radio heard meanwhile — the server cannot deliver to a hub that is not online yet
        if not radio_queue.empty():
            for _ in range(30):
                online = {h["id"] for h in self.directory if h.get("online")}
                if all(p in online for p in active_peers()):
                    break
                await asyncio.sleep(0.5)
        while True:
            topic, data = await radio_queue.get()
            await asyncio.to_thread(send_to_peers, topic, data)

    async def _keepalive(self):
        last = time.time()
        while True:                           # re-read the interval every second: a changed value applies at once
            await asyncio.sleep(1)
            if time.time() - last >= adv("keepalive_s"):
                last = time.time()
                await self.send({"t": "ping"})

    async def _nodes(self):
        """Report local nodes to the server: as soon as the radio is connected, then at least every "nodes_report_min" minutes.
        Never report while the radio is down (an empty list would wipe the hub's nodes from the map)."""
        last, last_sig, checked = 0, None, 0
        while True:
            r = mt_radio()
            if r and r.iface is not None and time.time() - checked >= adv("nodes_check_s"):
                checked = time.time()
                if cfg.get()["server"].get("status") != "approved":
                    last_sig = None           # the server ignores nodes of a pending hub: report again once approved
                nodes = await asyncio.to_thread(r.nodes, cfg.get()["share_positions_on_map"])
                sig = hashlib.sha256(json.dumps(sorted((n["id"], n["name"], n["lat"], n["lon"]) for n in nodes),
                                                default=str).encode()).digest()
                if nodes and (sig != last_sig or time.time() - last >= adv("nodes_report_min") * 60):
                    await self.send({"t": "nodes", "net": "mt", "nodes": nodes})
                    last, last_sig = time.time(), sig
            if await self._sleep_or(self.kick_nodes, 10):
                checked, last_sig = 0, None

    async def _location(self):
        """Keep the hub's map position in step: follow the radio (automatic) or the typed-in one."""
        sent = None
        while True:
            h = cfg.get()["hub"]
            r = mt_radio()
            if h.get("location_mode", "radio") == "radio" and r:
                pos = await asyncio.to_thread(r.own_position)
                if pos and (h["lat"] is None or distance_m(pos["lat"], pos["lon"], h["lat"], h["lon"]) > adv("location_follow_m")):
                    cfg.update(lambda d: d["hub"].update(lat=round(pos["lat"], 6), lon=round(pos["lon"], 6)))
                    h = cfg.get()["hub"]
                    log.info("hub position taken from the radio: %s, %s", h["lat"], h["lon"])
            cur = (h["lat"], h["lon"])
            if cur != sent and None not in cur:
                if await self.send({"t": "location", "lat": cur[0], "lon": cur[1]}):
                    sent = cur
            if await self._sleep_or(self.kick_location, adv("location_check_s")):
                sent = None                   # settings changed or reconnected: send it again


def distance_m(lat1, lon1, lat2, lon2):
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


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


def my_id():
    return cfg.get()["server"]["hub_id"]


def send_to_peers(topic, data, path=None, exclude=(), origin_rules=None):
    """Radio -> server (path None), or passing on traffic of another hub (transit): apply each link's
    SEND rule. `path` = hubs the packet already went through (origin first); it is sealed inside the box."""
    r = mt_radio()
    c = classify(data, r.channel_keys() if r else {})
    if c is None:
        return
    own = path is None
    if own:                                            # our own radio's packet: we are the origin
        path = [my_id()]
        seen_cache.seen(b"p" + hashlib.sha256(data).digest())   # a copy coming back round a loop is dropped
    boxes = {}
    for peer in active_peers():
        if peer in exclude:
            continue
        rule = cfg.rules_for(peer)["send"]
        if not own and not rule.get("transit", True):
            counters.peer_add(peer, "blocked_send", "transit_off")
            continue
        ok, why = allowed(rule, c)
        if not ok:
            counters.peer_add(peer, "blocked_send", why)
            continue
        keys, state = identity.keys_for(peer)
        if keys is None:                               # no end-to-end key (or it changed): never send in clear
            counters.peer_add(peer, "blocked_send", "key_" + state)
            continue
        if own:      # the origin decides, PER LINK, how far its packet may go and through which of the partner's links
            reach = rule_reach(rule)                   # sealed in the box: no hub on the way can change it
            allow = [] if reach == 0 else ["*"] if reach >= REACH_ANY else list(rule.get("onward_to") or [])
            meta = {"allow": allow, "max_hops": reach + 1}
        else:
            meta = origin_rules or {}
            # the origin's tick list applies to the first step beyond its partner (path = origin, partner);
            # further away the hop limit and each hub's own transit rules decide
            if len(path) == 2 and "*" not in meta.get("allow", []) and peer not in meta.get("allow", []):
                continue                               # the origin did not allow this destination
        inner = json.dumps({"topic": topic, "data": base64.b64encode(data).decode(), "path": path, **meta}).encode()
        boxes[peer] = base64.b64encode(seal(keys, inner)).decode()
        counters.peer_add(peer, "sent" if len(path) == 1 else "transit")
    if own or boxes:
        names = {h["id"]: h.get("code") for h in link.directory}
        log.info("%s %s: sent to %s%s", "radio ->" if own else "passing on", pkt_desc(c),
                 ", ".join(names.get(x, x) for x in boxes) or "nobody",
                 "".join(f"; not to {names.get(x, x)} ({counters.last_block.get(x, '?')})" for x in active_peers() if x not in boxes and x not in exclude))
    if boxes:
        counters.add("sent" if len(path) == 1 else "transit")
        asyncio.run_coroutine_threadsafe(link.send({"t": "mesh", "net": "mt", "boxes": boxes}), loop)


def pkt_desc(c):
    """Short description of a packet for the log: private / channel, kind, sender."""
    where = "private" if c["private"] else ("public " if c["public"] else "group ") + c["channel"]
    return f"{where} {c['kind']} from {c['sender']}"


def rule_reach(rule):
    """How many hubs beyond the partner my packets may go (older configs: derived from the tick list)."""
    if "reach" in rule:
        return max(0, min(REACH_ANY, int(rule.get("reach") or 0)))
    return min(REACH_ANY, int(cfg.get()["transit"].get("max_hops", 2)) - 1) if rule.get("onward_to") else 0


TEST_MODE = os.environ.get("URA_TEST_INJECT") == "1"
test_boxes = []                    # tests only: last boxes received, so a test can replay or tamper with one


def receive_box(peer, box):
    """Server -> hub: open the end-to-end box from a linked hub, drop replays/duplicates."""
    if TEST_MODE:
        test_boxes.append((peer, box))
        del test_boxes[:-50]
    keys, state = identity.keys_for(peer)
    if keys is None:
        counters.peer_add(peer, "blocked_recv", "key_" + state)
        return
    try:
        inner, nonce = open_box(keys, box, max_age=adv("replay_window_s"))
        m = json.loads(inner)
        data = base64.b64decode(m["data"])
    except Exception:
        counters.peer_add(peer, "blocked_recv", "bad_box")
        return
    path = [str(x)[:20] for x in (m.get("path") or [peer])][:16]
    if my_id() in path:                                # it went round in a circle
        counters.peer_add(peer, "blocked_recv", "loop")
        return
    if seen_cache.seen(b"n" + nonce) or seen_cache.seen(b"p" + hashlib.sha256(data).digest()):
        return
    if len(path) > 1 and not cfg.rules_for(peer)["receive"].get("from_beyond", True):
        counters.peer_add(peer, "blocked_recv", "from_beyond")
        return
    # multi-hop: pass it on only if the ORIGIN allowed it, I allow transit, and no hop limit is exceeded
    tr = cfg.get()["transit"]
    limit = min(int(tr.get("max_hops", 2)), int(m.get("max_hops") or 2))
    allow = [str(x)[:20] for x in (m.get("allow") or [])][:50]
    if allow and tr.get("enabled") and len(path) + 1 <= limit:
        send_to_peers(m["topic"], data, path=path + [my_id()], exclude=set(path) | {peer},
                      origin_rules={"allow": allow, "max_hops": int(m.get("max_hops") or 2)})
    receive_from_peer(peer, m["topic"], data, origin=path[0])


def receive_from_peer(peer, topic, data, origin=None):
    """Server -> radio: apply the RECEIVE rule for this link and the airtime limit.
    `origin` = the hub whose radio heard it first (differs from `peer` for multi-hop traffic)."""
    counters.add("received")
    r = mt_radio()
    if r is None:
        counters.peer_add(peer, "blocked_recv", "no_radio")
        return
    c = classify(data, r.channel_keys())
    if c is None:
        counters.peer_add(peer, "blocked_recv", "invalid")
        return
    if c.get("sender"):
        origins.note(c["sender"], origin or peer)
    frm = next((h.get("code") for h in link.directory if h["id"] == peer), peer)
    via = "" if not origin or origin == peer else f" (from {next((h.get('code') for h in link.directory if h['id'] == origin), origin)})"
    ok, why = allowed(cfg.rules_for(peer)["receive"], c)
    if not ok:
        counters.peer_add(peer, "blocked_recv", why)
        log.info("from %s%s %s: not put on air (%s)", frm, via, pkt_desc(c), why)
        return
    a = cfg.get()["airtime"]
    toa = time_on_air(c["size"] + 16, *r.lora_params())
    if (a.get("pct_hour") and counters.air_used(3600) + toa > 3600 * a["pct_hour"] / 100) or \
       (a.get("pct_day") and counters.air_used(86400) + toa > 86400 * a["pct_day"] / 100):
        counters.peer_add(peer, "blocked_recv", "airtime")
        log.info("from %s%s %s: not put on air (airtime limit)", frm, via, pkt_desc(c))
        return
    if r.downlink(topic, data):
        counters.air_add(toa)
        counters.peer_add(peer, "received")
        log.info("from %s%s %s: put on air", frm, via, pkt_desc(c))
    else:
        counters.peer_add(peer, "blocked_recv", "no_radio")


# ───────────────────────── website ─────────────────────────

sessions = {}
login_fail = {}                    # ip -> [failure times]
SEC_HEADERS = {"X-Frame-Options": "DENY", "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer",
               "Content-Security-Policy": "default-src 'self'; img-src 'self' data:; "
                                          "style-src 'self' 'unsafe-inline'; script-src 'self'; frame-ancestors 'none'"}


def locked_out(ip):
    t = time.time()
    login_fail[ip] = [x for x in login_fail.get(ip, []) if t - x < adv("lockout_minutes") * 60]
    return len(login_fail[ip]) >= adv("lockout_attempts")


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


async def server_leave():
    """Tell the server this hub leaves: over the open connection, or a short one of its own."""
    c = cfg.get()["server"]
    if not c["hub_id"]:
        return True
    if link.writer and link.state == "connected":
        await link.send({"t": "leave"})
        return True
    reader, writer = await open_server(c["address"], c["fingerprint"])
    writer.write((json.dumps({"t": "hello", "hub": c["hub_id"], "key": c["key"], "version": VERSION, "info": {}}) + "\n").encode())
    first = json.loads(await asyncio.wait_for(reader.readline(), 15))
    if first.get("t") != "welcome":
        writer.close()
        return first.get("reason") in ("unknown_hub", "removed")     # the server no longer has us anyway
    writer.write(b'{"t":"leave"}\n')
    await writer.drain()
    await asyncio.sleep(1)
    writer.close()
    return True


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
            "links": [dict(l, e2e=identity.safety(l["peer"])) for l in link.links], "directory": link.directory,
            "my_key": safety_code(identity.public, identity.public)[:11], "radio_stats": r.stats if r else {},
            "radio_position": r.own_position() if r else None, "node_max_age_days": adv("node_max_age_days")}


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
        for k, v in SEC_HEADERS.items():
            self.send_header(k, v)
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
        for k, v in SEC_HEADERS.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def authed(self):
        m = re.search(r"ura_hub=([A-Za-z0-9_-]+)", self.headers.get("Cookie") or "")
        return bool(m and sessions.get(m.group(1), 0) > time.time())

    def login_ok(self):
        tok, ttl = secrets.token_urlsafe(24), adv("session_hours") * 3600
        sessions[tok] = time.time() + ttl
        self.reply({"ok": True}, headers={"Set-Cookie": f"ura_hub={tok}; Max-Age={ttl}; Path=/; HttpOnly; Secure; SameSite=Strict"})

    def do_GET(self):
        p = urllib.parse.urlparse(self.path).path
        try:
            m = re.match(r"^/tiles/(\d+)/(\d+)/(\d+)\.png$", p)
            if m:
                data = get_tile(*map(int, m.groups()))
                if data is None:
                    return self.reply({"error": "tile_unavailable"}, 502)
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Cache-Control", "public, max-age=604800")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                return self.wfile.write(data)
            if not p.startswith("/api/"):
                return self.static(p)
            if p == "/api/session":
                return self.reply({"setup_needed": not cfg.get()["web_password"], "logged_in": self.authed(), "version": VERSION,
                                   "password_min": adv("password_min"), "page_refresh_s": adv("page_refresh_s")})
            if not self.authed():
                return self.reply({"error": "login"}, 401)
            if p == "/api/status":
                return self.reply(status_payload())
            if p == "/api/test/radio" and os.environ.get("URA_TEST_INJECT") == "1":
                r = mt_radio()
                return self.reply(r.iface.record if r and r.iface is not None and hasattr(r.iface, "record") else {})
            if p == "/api/nodes":
                r = mt_radio()
                return self.reply(r.all_nodes() if r else [])
            if p == "/api/advanced_spec":
                return self.reply({k: {"default": v[0], "min": v[1], "max": v[2]} for k, v in ADV_SPEC.items()})
            if p == "/api/config":
                c = cfg.get()
                c.pop("web_password", None)
                c["server"].pop("key", None)
                return self.reply(c)
            if p == "/api/radio/settings":
                r = mt_radio()
                if not r or r.iface is None:
                    return self.reply({"error": "no_radio"}, 400)
                return self.reply(r.settings())
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
                if len(b.get("password") or "") < adv("password_min"):
                    return self.reply({"error": "password_short"}, 400)
                cfg.update(lambda d: d.update(web_password=hash_pw(b["password"])))
                return self.login_ok()
            if p == "/api/login":
                ip = self.client_address[0]
                if locked_out(ip):
                    return self.reply({"error": "locked"}, 429)
                time.sleep(0.5)
                if check_pw(b.get("password") or "", cfg.get()["web_password"]):
                    login_fail.pop(ip, None)
                    return self.login_ok()
                login_fail.setdefault(ip, []).append(time.time())
                log.warning("failed hub login from %s", ip)
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
        if p == "/api/advanced":
            vals, errors = clean_advanced(b.get("advanced") or {})
            if errors:
                return self.reply({"error": "invalid", "fields": errors}, 400)
            cfg.update(lambda d: d["advanced"].update(vals))
            if "server_web_port" in b:
                try:
                    port = int(b["server_web_port"])
                    assert 1 <= port <= 65535
                except Exception:
                    return self.reply({"error": "invalid", "fields": ["server_web_port"]}, 400)
                cfg.update(lambda d: d["server"].update(web_port=port))
            link.kick()                       # e.g. node age / follow distance changed: report with the new values
            return self.reply({"ok": True})
        if p == "/api/password":
            if len(b.get("password") or "") < adv("password_min"):
                return self.reply({"error": "password_short"}, 400)
            cfg.update(lambda d: d.update(web_password=hash_pw(b["password"])))
            return self.reply({"ok": True})
        if p == "/api/hub":
            h = b.get("hub") or {}
            registered = bool(cfg.get()["server"]["hub_id"])
            def upd(d):
                for k in ("name", "email", "country", "city", "description"):
                    if k in h and not registered:
                        d["hub"][k] = str(h[k] or "").strip()[:500]
                if h.get("location_mode") in ("radio", "manual"):
                    d["hub"]["location_mode"] = h["location_mode"]
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
                if "transit" in b:
                    hops = int(b["transit"].get("max_hops") or 2)
                    if not 2 <= hops <= 8:
                        raise ValueError("max_hops")
                    d["transit"] = {"enabled": bool(b["transit"].get("enabled")), "max_hops": hops}
            cfg.update(upd)
            run_coro(link.push_info())
            link.kick()                       # new location / positions setting: tell the server now
            return self.reply({"ok": True})
        if p == "/api/server/check":
            addr = normalize_addr(b.get("address"))
            try:
                return self.reply({"address": addr, "fingerprint": run_coro(server_check(addr))})
            except Exception as e:           # unreachable / wrong port / not a Ura server: a normal situation, not a crash
                return self.reply({"error": "unreachable", "detail": f"{addr}: {e.__class__.__name__} {e}".strip()}, 400)
        if p == "/api/server/trust":
            addr, fp = normalize_addr(b.get("address")), str(b.get("fingerprint") or "").upper()
            def upd(d):
                # Another address for the SAME server (same fingerprint, e.g. its domain name instead of its
                # IP) keeps the registration. Only a different server (other fingerprint) starts over.
                if d["server"]["fingerprint"] and d["server"]["fingerprint"] != fp:
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
            # the request goes only to the server the operator sees on the page AND has trusted
            try:
                shown = normalize_addr(b.get("address"))
            except ValueError:
                return self.reply({"error": "not_trusted"}, 400)
            if not c["server"]["fingerprint"] or shown != c["server"]["address"]:
                return self.reply({"error": "not_trusted"}, 400)
            try:
                reply = run_coro(server_join(c["server"]["address"], c["server"]["fingerprint"],
                                             {k: h[k] for k in ("name", "email", "country", "city", "lat", "lon", "description")}))
            except FingerprintMismatch:
                return self.reply({"error": "fingerprint_mismatch"}, 400)
            except Exception as e:
                return self.reply({"error": "unreachable", "detail": f"{e.__class__.__name__} {e}".strip()}, 400)
            if reply.get("t") != "joined":
                return self.reply({"error": reply.get("reason", "refused")}, 400)
            cfg.update(lambda d: d["server"].update(hub_id=reply["hub"], key=reply["key"], status=reply["status"]))
            loop.call_soon_threadsafe(link.reconnect.set)
            return self.reply({"ok": True, "hub_id": reply["hub"]})
        if p == "/api/server/forget":
            # Tell the server first: it removes this hub and ends all its links (partners are told at once).
            told = False
            try:
                told = run_coro(server_leave(), timeout=25)
            except Exception as e:
                log.warning("could not tell the server that this hub leaves: %s", e)
            if not told and not b.get("force"):
                return self.reply({"error": "leave_not_confirmed"}, 400)
            def clear(d):                      # a fresh start: no registration, no links -> no link rules, no partner keys
                d["server"].update(hub_id="", key="", status="")
                d["rules"], d["peer_keys"] = {}, {}
            cfg.update(clear)
            loop.call_soon_threadsafe(link.reconnect.set)
            if link.writer:
                loop.call_soon_threadsafe(link.writer.close)
            log.info("registration forgotten (server informed: %s)", told)
            return self.reply({"ok": True, "server_informed": told})
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
        if p == "/api/links/trust_key":
            peer = str(b.get("peer") or "")
            cur, state = identity.peer_key(peer)
            if not cur:
                return self.reply({"error": "no_key"}, 400)
            cfg.update(lambda d: d["peer_keys"].__setitem__(peer, cur))
            log.info("operator trusted new end-to-end key of %s", peer)
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
        if p in ("/api/radio/section", "/api/radio/owner", "/api/radio/channel", "/api/radio/fixed"):
            r = mt_radio()
            if not r or r.iface is None:
                return self.reply({"error": "no_radio"}, 400)
            try:
                reboot = False
                if p == "/api/radio/section":
                    reboot = r.set_section(str(b.get("kind")), str(b.get("section")), b.get("values") or {})
                elif p == "/api/radio/owner":
                    r.set_owner(b.get("long_name"), b.get("short_name"), b.get("is_licensed"))
                elif p == "/api/radio/channel":
                    r.set_channel(b.get("channel") or {})
                else:
                    r.set_fixed(b.get("fixed") or {})
            except ValueError as e:
                return self.reply({"error": "invalid", "fields": [str(e).split(":", 1)[-1]]}, 400)
            link.kick()                       # new radio name / position: map and server follow at once
            return self.reply({"ok": True, "reboot": reboot})
        if p == "/api/radio/prepare":
            r = mt_radio()
            if not r:
                return self.reply({"error": "no_radio"}, 400)
            r.prepare()
            return self.reply({"ok": True})
        if p == "/api/test/replay" and TEST_MODE:     # tests only: feed a received box again, optionally altered
            peer, box = test_boxes[int(b.get("index", -1))]
            if b.get("tamper"):
                box = box[:40] + bytes([box[40] ^ 1]) + box[41:]
            receive_box(peer, box)
            return self.reply({"ok": True, "peer": peer})
        if p == "/api/test/inject" and os.environ.get("URA_TEST_INJECT") == "1":
            loop.call_soon_threadsafe(enqueue, radio_queue, (str(b["topic"]), base64.b64decode(b["data"])))
            return self.reply({"ok": True})
        if p == "/api/diag":
            r = mt_radio()
            if not r:
                return self.reply({"error": "no_radio"}, 400)
            node = str(b.get("node") or "")
            if b.get("kind") == "broadcast":
                node = str(int(b.get("channel") or 0))
            elif not re.match(r"^!?[0-9a-fA-F]{8}$", node):
                return self.reply({"error": "bad_node"}, 400)
            else:
                node = "!" + node.lstrip("!").lower()
            return self.reply(r.diagnose(node, str(b.get("kind")), str(b.get("text") or "")))
        if p == "/api/radio/announce":
            r = mt_radio()
            if not r or not r.announce(bool(b.get("ask"))):
                return self.reply({"error": "no_radio"}, 400)
            return self.reply({"ok": True})
        return self.reply({"error": "not_found"}, 404)


TILE_UA = f"Ura-hub/{VERSION} (+https://github.com/ximi87/Ura-mesh)"
tile_lock = threading.Semaphore(4)
tile_down = {}                    # source url prefix -> time until which it is skipped after a failure


def get_tile(z, x, y):
    """Map tile from the local cache, else from the Ura server's tile cache (certificate pinned),
    else straight from OpenStreetMap. Hubs without internet still get maps through the server."""
    if not (0 <= z <= 19 and 0 <= x < 2 ** z and 0 <= y < 2 ** z):
        return None
    path = os.path.join(DATA_DIR, "tiles", str(z), str(x), f"{y}.png")
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < adv("tile_cache_days") * 86400:
        return open(path, "rb").read()
    srv = cfg.get()["server"]
    sources = []
    if adv("tile_source") != "server":
        sources.append((adv("tile_source").format(z=z, x=x, y=y), None))
    elif srv["address"] and srv["fingerprint"]:
        host = srv["address"].rpartition(":")[0]
        sources.append((f"https://{host}:{srv.get('web_port') or 8443}/tiles/{z}/{x}/{y}.png", srv["fingerprint"]))
    if adv("tile_source") == "server":
        sources.append((f"https://tile.openstreetmap.org/{z}/{x}/{y}.png", None))
    for url, fp in sources:
        src = url.split("/tiles/")[0] if "/tiles/" in url else "osm"
        if time.time() < tile_down.get(src, 0):
            continue
        try:
            with tile_lock:
                ctx = ssl.create_default_context()
                if fp:
                    ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE
                resp = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": TILE_UA}), timeout=6, context=ctx)
                if fp and fp_of(resp.fp.raw._sock.getpeercert(binary_form=True)) != fp:
                    continue
                data = resp.read()
            if not data.startswith(b"\x89PNG"):
                continue
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path + ".tmp", "wb") as f:
                f.write(data)
            os.replace(path + ".tmp", path)
            return data
        except Exception:
            tile_down[src] = time.time() + adv("tile_backoff_s")
            continue
    return open(path, "rb").read() if os.path.exists(path) else None


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
        if d == "send":
            out[d]["onward_to"] = [str(h)[:20] for h in (x.get("onward_to") or [])][:50]
            out[d]["reach"] = rule_reach(x)
            out[d]["transit"] = bool(x.get("transit", True))
        else:
            out[d]["from_beyond"] = bool(x.get("from_beyond", True))
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
    import meshcrypto
    meshcrypto._selftest() and meshcrypto._selftest_e2e()   # FIPS-197, SP 800-38A, RFC 7748 vectors; raises if broken
    cfg = Config()
    global identity, origins
    identity = Identity()
    origins = Origins()
    loop = asyncio.get_running_loop()
    radio_queue = asyncio.Queue()             # size limited by enqueue() with the current "queue_max"
    link = Link()
    apply_radios()
    threading.Thread(target=run_web, daemon=True).start()
    loop.add_signal_handler(signal.SIGUSR1, lambda: mt_radio() and loop.run_in_executor(None, mt_radio().announce))
    loop.add_signal_handler(signal.SIGUSR2, lambda: mt_radio() and loop.run_in_executor(None, mt_radio().announce, True))
    log.info("ura-hub %s started", VERSION)
    await link.run()


if __name__ == "__main__":
    asyncio.run(main())
