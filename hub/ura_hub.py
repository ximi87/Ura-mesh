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
    "node_sync":           (True, None, None),  # announce the nodes this radio knows to the linked hubs (not only live traffic)
    "node_sync_hours":     (6, 1, 48),         # ... each node again every N hours
    "node_sync_gap_s":     (15, 2, 600),       # ... one node every N seconds (keeps the air free)
    "node_sync_age_h":     (24, 1, 168),       # ... only nodes heard within the last N hours
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

# ───────────────────────── logs + program control ─────────────────────────
import logging.handlers, sys
STARTED = time.time()
LOG_NAME = "ura-hub"


def log_setup(data_dir):
    """Besides the console (journal), keep the log in files in the data folder: 5 × 1 MB, newest first."""
    d = os.path.join(data_dir, "logs")
    os.makedirs(d, exist_ok=True)
    h = logging.handlers.RotatingFileHandler(os.path.join(d, LOG_NAME + ".log"), maxBytes=1_000_000, backupCount=4, encoding="utf-8")
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logging.getLogger().addHandler(h)


def log_files(data_dir):
    d = os.path.join(data_dir, "logs")
    names = [LOG_NAME + ".log"] + [f"{LOG_NAME}.log.{i}" for i in range(1, 5)]
    return [{"name": n, "size": os.path.getsize(os.path.join(d, n)), "mtime": int(os.path.getmtime(os.path.join(d, n)))}
            for n in names if os.path.exists(os.path.join(d, n))]


def log_tail(data_dir, lines=500, level="", q=""):
    """The newest `lines` log lines (across the rotated files), optionally only warnings/errors or matching text."""
    d = os.path.join(data_dir, "logs")
    want = {"warning": (" WARNING ", " ERROR ", " CRITICAL "), "error": (" ERROR ", " CRITICAL ")}.get(level)
    q = (q or "").lower()
    out = []
    for f in log_files(data_dir):
        try:
            with open(os.path.join(d, f["name"]), encoding="utf-8", errors="replace") as fh:
                chunk = fh.read().splitlines()
        except OSError:
            continue
        sel = [l for l in chunk if (not want or any(w in l for w in want)) and (not q or q in l.lower())]
        out = sel + out
        if len(out) >= lines:
            break
    return out[-lines:]


def program_action(action, before=None):
    """restart: the program starts itself again (same process, new code); stop: it ends and stays stopped
    (exit status 64 — the systemd unit has RestartPreventExitStatus=64). The computer is not touched."""
    def go():
        time.sleep(1)
        try:
            if before:
                before()
        except Exception:
            pass
        logging.getLogger().info("program %s by the operator", "restarting" if action == "restart" else "stopped")
        for h in logging.getLogger().handlers:
            h.flush()
        if action == "restart":
            os.execv(sys.executable, sys.orig_argv)
        os._exit(64)
    threading.Thread(target=go, daemon=True).start()


REACH_ANY = 7                 # "anywhere": the longest chain a packet can make (8 links)
RULE_DEFAULT = {"on": True, "public": True, "groups": [], "private": True, "positions": True, "mc": True,
                # multi-hop, decided by each hub for itself:
                "reach": 0,           # send:    how many hubs BEYOND this peer my packets may travel (0 = stop there,
                                      #          REACH_ANY = as far as the other hubs allow)
                "onward_to": [],      # send:    which of this peer's links my packets may continue on (first step)
                "transit": True,      # send:    I pass other hubs' packets on to this peer (if transit is on)
                "from_beyond": True}  # receive: accept packets that started at hubs beyond this peer
MC_RULE_DEFAULT = {"on": True, "adverts": True, "public": True, "private": True, "groups": [],
                   "other_groups": False,   # channels of other people (unknown to this radio) — off, like Meshtastic
                   "other": True,           # traceroute, control packets
                   "reach": 0,              # send: how many hubs BEYOND this partner my MeshCore packets may travel
                   "transit": True,         # send: I pass other hubs' MeshCore packets on to this partner (if MeshCore transit is on)
                   "from_beyond": True}     # receive: accept MeshCore packets that started at hubs beyond this partner
DEFAULT_CONFIG = {
    "hub": {"name": "", "email": "", "country": "", "city": "", "lat": None, "lon": None, "description": "",
            "location_mode": "radio"},            # radio = follow the connected radio's position, manual = typed in
    "server": {"address": "", "fingerprint": "", "hub_id": "", "key": "", "status": "", "web_port": 8443},
    "radios": [],                 # [{"id","net":"mt","transport":"serial|tcp","address","enabled"}]
    "airtime": {"pct_hour": 10.0, "pct_day": 0.0},        # Meshtastic radio: limit for packets from links
    "airtime_mc": {"pct_hour": 10.0, "pct_day": 0.0},     # MeshCore radio: its own limit
    "defaults": {"send": dict(RULE_DEFAULT), "receive": dict(RULE_DEFAULT),
                 "mc": {"send": dict(MC_RULE_DEFAULT), "receive": dict(MC_RULE_DEFAULT)}},
    "rules": {},                  # peer hub id -> {"send": {...}, "receive": {...}}
    "share_positions_on_map": True,
    "setup_skipped": False,       # the operator chose to set up without the step-by-step wizard
    "setup_done": False,          # every wizard step was done once: the wizard no longer opens by itself
    "transit": {"enabled": False, "max_hops": 2},   # Meshtastic: pass traffic between my linked hubs (multi-hop)
    "transit_mc": {"enabled": False, "max_hops": 2},  # MeshCore: the same, decided separately
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
            if r.get("mc"):
                out["mc"] = copy.deepcopy(r["mc"])           # MeshCore rules of this link (own block)
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

    def peers(self):
        with self.lock:
            return set(self.map.values())

    def drop_peer(self, peer):
        """Forget every node that came from this hub; returns their ids."""
        with self.lock:
            gone = [n for n, p in self.map.items() if p == peer]
            for n in gone:
                del self.map[n]
            self.save()
        return gone

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


def channel_code(name, psk):
    """The one-byte channel code ("hash") radios put in every packet: XOR of the name and of the key.
    Two radios read each other's channel only when name AND key are the same — i.e. the same code."""
    h = 0
    for b in name.encode():
        h ^= b
    for b in expand_psk(bytes(psk)) or b"":
        h ^= b
    return h


def parse_channel_link(url):
    """Meshtastic share link / QR text (https://meshtastic.org/e/#...) -> ChannelSet."""
    from meshtastic.protobuf import apponly_pb2
    frag = str(url or "").strip().split("#", 1)[-1].strip()
    if not frag:
        raise ValueError("channel_link")
    cs = apponly_pb2.ChannelSet()
    try:
        cs.ParseFromString(base64.urlsafe_b64decode(frag + "=" * (-len(frag) % 4)))
    except Exception:
        raise ValueError("channel_link")
    if not cs.settings:
        raise ValueError("channel_link")
    return cs


def _decodes(key, pkt):
    try:
        d = mesh_pb2.Data()
        d.ParseFromString(decrypt_packet(key, pkt.id, getattr(pkt, "from"), pkt.encrypted))
        return d.portnum or None
    except Exception:
        return None


def classify(data, channels):
    """Return {channel, public, private, kind, size, code} for a ServiceEnvelope, or None if invalid.
    channels: Radio.channel_keys() — {name: [{"key", "public", "code"}]}. Like the radios, the channel is found by
    its code (in every encrypted packet), not only by its name: two channels may share a name."""
    env = mqtt_pb2.ServiceEnvelope()
    try:
        env.ParseFromString(data)
    except Exception:
        return None
    pkt = env.packet
    out = {"channel": env.channel_id, "public": False, "private": env.channel_id == "PKI",
           "sender": f"!{getattr(pkt, 'from'):08x}",
           "kind": "unknown", "size": len(pkt.encrypted) if pkt.HasField("encrypted") else len(pkt.decoded.payload) + 4}
    cands = [] if out["private"] else list(channels.get(env.channel_id) or [])
    if pkt.channel and cands:                    # the packet's channel code picks the channel (and its key)
        cands = [c for c in cands if c["code"] == pkt.channel] or None
    if cands is None:
        out["unreadable"] = True                 # a channel of that name exists here, but with another key
        return out
    port, ch = None, None
    if pkt.HasField("decoded"):
        port, ch = pkt.decoded.portnum, (cands[0] if cands else None)
    else:
        for c in cands:
            if c["key"] and (port := _decodes(c["key"], pkt)):
                ch = c
                break
        if cands and ch is None:
            out["unreadable"] = True             # same channel name, but this radio's key does not open it
            return out
    if ch:
        out["public"], out["code"] = ch["public"], ch["code"]
    if port is None:
        return out
    out["kind"] = KIND.get(port, "other")
    if port == portnums_pb2.PortNum.ROUTING_APP and ch and ch.get("key") and pkt.HasField("encrypted"):
        try:                                     # an answer about a message: say what it is (e.g. the key problem)
            d = mesh_pb2.Data(); d.ParseFromString(decrypt_packet(ch["key"], pkt.id, getattr(pkt, "from"), pkt.encrypted))
            rt = mesh_pb2.Routing(); rt.ParseFromString(d.payload)
            if rt.WhichOneof("variant") == "error_reason":
                out["routing"] = mesh_pb2.Routing.Error.Name(rt.error_reason)
                out["to"] = f"!{pkt.to:08x}"
        except Exception:
            pass
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
        self.found = {}                   # what was really found on the port when it is not a Meshtastic radio
        self.stop = False
        self.stats = {}                   # what the radio reports about its own reception
        self.own_fix = None               # the radio's own position at full precision
        self.topic_root = None            # MQTT topic root the radio uses (learned from its uplinks)
        self.last_rx = time.time()        # last time the radio sent the hub anything at all
        self.watchdog = []                # times the watchdog had to act (7 days)
        self.wd_events = []               # what it found and did: [{time, stage, finding}]
        self.wd_stage, self.wd_at = 0, 0  # 0 normal, 1 fresh USB session tried, 2 radio restarted
        self.last_pkt = time.time()       # last live packet/proxy message (not the config dump at connect)
        self.unknown_ch = {}              # channel code -> {"count", "last", "senders"}: heard but cannot read
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
            if "/2/" in (proxymessage.topic or ""):
                self.topic_root = proxymessage.topic.split("/2/")[0]      # e.g. msh/EU_868 — used for node announcements
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
                code = packet.get("channel")
                if "decoded" not in packet and code and code not in self.known_codes():
                    u = self.unknown_ch.setdefault(code, {"count": 0, "last": 0, "senders": {}})
                    u["count"] += 1
                    u["last"] = int(time.time())
                    u["senders"][packet.get("fromId") or f"!{packet.get('from', 0):08x}"] = int(time.time())
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

    def _connect_failed(self, c, e):
        """The radio did not connect: ask the port what is really there. A port that was just chosen on the
        Radio page and holds no Meshtastic radio is not kept (the page shows what was found instead)."""
        info = identify_port(c["address"])
        global radio_result
        if info["kind"] == "meshtastic":
            raise RuntimeError(str(e) or "the radio did not answer")
        if info["kind"] in ("no_answer", "busy", "missing"):   # maybe still starting: keep trying, say so
            self.found = info
            raise RuntimeError("no_answer" if info["kind"] == "no_answer" else info["kind"])
        self.found = info
        if radio_result.get("address") == c["address"] and radio_result.get("state") == "connecting":
            # just chosen and it is not a Meshtastic radio: nothing is kept
            radio_result = {"address": c["address"], "state": "refused", "found": info, "text": describe_kind(info), "t": time.time()}
            log.warning("radio not saved: %s on %s — the hub works only with a Meshtastic radio", describe_kind(info), c["address"])
            def drop(d):
                if any(x.get("net", "mt") == "mt" and x.get("address") == c["address"] for x in d["radios"]):
                    d["radios"] = [x for x in d["radios"] if x.get("net", "mt") != "mt"]
                    d["channels_saved"] = []
            cfg.update(drop)
            loop.call_soon_threadsafe(apply_radios)
        elif self.error != "not_meshtastic":
            log.warning("radio %s: %s — the hub works only with a Meshtastic radio", c["address"], describe_kind(info))
        raise RuntimeError("not_meshtastic")

    def _open(self):
        c = self.conf
        if os.environ.get("URA_TEST_RADIO"):           # tests only: a simulated radio (tests/fake_radio.py)
            import importlib.util, sys as _sys
            mod = _sys.modules.get("ura_fake_radio")    # loaded once: the simulated radio keeps its memory across reconnects
            if mod is None:
                spec = importlib.util.spec_from_file_location("ura_fake_radio", os.environ["URA_TEST_RADIO"])
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                _sys.modules["ura_fake_radio"] = mod
            if "meshcore" in c["address"] or "unknown" in c["address"]:
                self._connect_failed(c, RuntimeError("Timed out waiting for connection completion"))
            return mod.FakeInterface(c)
        if c.get("transport") == "tcp":
            host, _, port = c["address"].partition(":")
            return meshtastic.tcp_interface.TCPInterface(host, portNumber=int(port or 4403))
        if not os.path.exists(c["address"]):
            raise RuntimeError("port not present")
        try:
            return meshtastic.serial_interface.SerialInterface(c["address"], timeout=60)
        except Exception as e:
            self._connect_failed(c, e)

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
                    self.own_fix = None           # what this radio really has now, not what an earlier one had
                    self._set_fix(p)
                    log.info("radio connected: %s (%s)", self.info().get("name"), self.conf.get("address"))
                    global radio_result
                    if radio_result.get("address") == self.conf.get("address"):
                        i_ = self.info()
                        radio_result = {"address": self.conf.get("address"), "state": "connected", "t": time.time(),
                                        "found": {"kind": "meshtastic", "name": i_.get("name") or "", "id": i_.get("node_id") or "",
                                                  "hw": i_.get("hw") or "", "nodes": i_.get("nodes")}}
                    try:
                        link.kick()               # its nodes and position go to the server (and partners) at once
                    except NameError:
                        pass
                    if not cfg.get().get("channels_saved"):
                        self.save_channels()          # first radio: its channels become the hub's saved copy
                except Exception as e:
                    if str(e) != self.error:      # each new reason once: a radio that is still starting is visible in the log
                        log.warning("radio %s: not connected yet — %s (trying again)", self.conf.get("address"), e)
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
                "found": self.found if self.error in ("not_meshtastic", "no_answer", "busy") else None,
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
                              "primary": ch.role == 1, "code": channel_code(name, ch.settings.psk)})
            checks = {
                "mqtt_enabled": mc.mqtt.enabled, "proxy_to_client": mc.mqtt.proxy_to_client_enabled,
                "private_address": mc.mqtt.address == adv("mqtt_address") or bool(re.match(r"^(10|127|192\.168|172\.(1[6-9]|2\d|3[01]))\.", mc.mqtt.address or "")),
                "encryption": mc.mqtt.encryption_enabled, "ignore_mqtt_off": not lc.lora.ignore_mqtt,
                "channels_linked": all(c["uplink"] and c["downlink"] for c in chans) if chans else False,
                "debug_log_off": not lc.security.debug_log_api_enabled,
                "region_set": lc.lora.region != 0,     # a radio without a region (e.g. after a reset) does not transmit
                # without a position the node crosses the links but appears on no map: a GPS, or a fixed position
                "position_known": bool(self.own_fix) or lc.position.gps_mode == config_pb2.Config.PositionConfig.GpsMode.ENABLED,
                "position_approx": (lc.position.gps_mode == config_pb2.Config.PositionConfig.GpsMode.ENABLED or not self.own_fix
                                    or (approx(self.own_fix["lat"]) == self.own_fix["lat"] and approx(self.own_fix["lon"]) == self.own_fix["lon"])) and all(c_.settings.module_settings.position_precision <= APPROX_BITS for c_ in (ln.channels or []) if c_.role != 0)}
            base.update({"name": me.get("user", {}).get("longName"), "short": me.get("user", {}).get("shortName"),
                         "node_id": me.get("user", {}).get("id"), "hw": me.get("user", {}).get("hwModel"),
                         "firmware": getattr(md, "firmware_version", "") if md else "",
                         "role": config_pb2.Config.DeviceConfig.Role.Name(lc.device.role),
                         "preset": self._preset_name(lc), "region": config_pb2.Config.LoRaConfig.RegionCode.Name(lc.lora.region),
                         "channels": chans, "checks": checks, "ready": all(checks.values()),
                         "unknown_channels": self.unknown_channels(), "channels_match": self.channels_match(),
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

    def channel_list(self):
        """The radio's channels as [{index, role, name, psk (base64), uplink, downlink, code}] (disabled left out)."""
        with self.lock:
            iface = self.iface
        if iface is None:
            return None
        lc, out = iface.localNode.localConfig, []
        for ch in iface.localNode.channels or []:
            if ch.role == 0:
                continue
            psk = bytes(ch.settings.psk)
            out.append({"index": ch.index, "role": "PRIMARY" if ch.role == 1 else "SECONDARY", "name": ch.settings.name,
                        "psk": base64.b64encode(psk).decode(), "uplink": ch.settings.uplink_enabled,
                        "downlink": ch.settings.downlink_enabled,
                        "code": channel_code(ch.settings.name or self._preset_name(lc), psk)})
        return out

    def known_codes(self):
        return {c["code"] for c in (self.channel_list() or [])}

    def unknown_channels(self):
        """Channels this radio heard packets on in the last 24 h but cannot read (different key or name)."""
        t = time.time()
        out = []
        for code, u in list(self.unknown_ch.items()):
            if t - u["last"] > 86400:
                self.unknown_ch.pop(code, None)
                continue
            nodes = (self.iface.nodes or {}) if self.iface is not None else {}
            out.append({"code": code, "count": u["count"], "last": u["last"],
                        "senders": [{"id": i, "name": (nodes.get(i) or {}).get("user", {}).get("longName")}
                                    for i in sorted(u["senders"], key=u["senders"].get, reverse=True)[:5]]})
        return sorted(out, key=lambda x: -x["last"])

    def save_channels(self):
        """Keep a copy of the radio's channels in the hub (to restore them on a new or reset radio)."""
        cl = self.channel_list()
        if cl:
            cfg.update(lambda d: d.__setitem__("channels_saved", [{k: c[k] for k in ("index", "role", "name", "psk", "uplink", "downlink")} for c in cl]))

    def channels_match(self):
        saved, cl = cfg.get().get("channels_saved") or [], self.channel_list()
        if not saved or cl is None:
            return True
        key = lambda c: (c["index"], c["role"], c["name"], c["psk"])
        return sorted(map(key, saved)) == sorted(map(key, cl))

    def restore_channels(self):
        saved = cfg.get().get("channels_saved") or []
        if not saved:
            raise ValueError("nothing_saved")
        ln = self.iface.localNode
        want = {c["index"]: c for c in saved}
        ln.beginSettingsTransaction()
        for ch in ln.channels:
            c = want.get(ch.index)
            if c:
                ch.role = 1 if c["role"] == "PRIMARY" else 2
                ch.settings.name, ch.settings.psk = c["name"], base64.b64decode(c["psk"])
                ch.settings.uplink_enabled, ch.settings.downlink_enabled = c["uplink"], c["downlink"]
                ln.writeChannel(ch.index)
            elif ch.role != 0 and ch.index != 0:
                ch.role = 0
                ln.writeChannel(ch.index)
        ln.commitSettingsTransaction()
        log.info("saved channels written back to the radio (%d)", len(saved))

    def import_channels(self, url, primary=False):
        """Add the channels of a Meshtastic share link. `primary`: its first channel becomes channel 0."""
        cs = parse_channel_link(url)
        ln = self.iface.localNode
        have = {(c["name"], c["psk"]) for c in self.channel_list()}
        added, skipped = [], []
        ln.beginSettingsTransaction()
        for i, st in enumerate(cs.settings):
            name, psk = st.name, bytes(st.psk)
            if (name, base64.b64encode(psk).decode()) in have and not (primary and i == 0):
                skipped.append(name or "(preset name)")
                continue
            if primary and i == 0:
                ch = ln.channels[0]
                ch.role = 1
            else:
                ch = next((c for c in ln.channels if c.role == 0 and c.index > 0), None)
                if ch is None:
                    skipped.append(name or "(preset name)")
                    continue
                ch.role = 2
            ch.settings.name, ch.settings.psk = name, psk
            ch.settings.uplink_enabled = ch.settings.downlink_enabled = True   # Ura needs both
            ln.writeChannel(ch.index)
            added.append(name or "(preset name)")
        ln.commitSettingsTransaction()
        warn = ""
        lo = ln.localConfig.lora
        if cs.HasField("lora_config") and (cs.lora_config.modem_preset != lo.modem_preset or cs.lora_config.region != lo.region):
            warn = "lora_differs"
        log.info("channels added from a link: %s (skipped: %s)", added, skipped)
        return {"added": added, "skipped": skipped, "warning": warn}

    def channel_keys(self):
        """{channel name as in MQTT topics: [{"key", "public", "code"}]}. A name can belong to several channels
        (a channel without a name carries the preset name, like the main channel); the code tells them apart."""
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
            out.setdefault(name, []).append({"key": expand_psk(bytes(ch.settings.psk)), "public": self._is_public(ch.settings.psk),
                                             "code": channel_code(name, ch.settings.psk)})
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

    def sync_candidates(self):
        """Nodes this radio knows from ITS OWN mesh (not via Ura), heard recently, newest first."""
        with self.lock:
            iface = self.iface
        if iface is None:
            return []
        my, remote = iface.myInfo.my_node_num, set(origins.map)
        out = []
        for num, n in list((iface.nodesByNum or {}).items()):
            nid = (n.get("user") or {}).get("id") or f"!{num:08x}"
            if num == my or n.get("viaMqtt") or nid in remote or not (n.get("user") or {}).get("longName"):
                continue
            if not n.get("lastHeard") or time.time() - n["lastHeard"] > adv("node_sync_age_h") * 3600:
                continue
            out.append((n["lastHeard"], num))
        return [num for _, num in sorted(out, reverse=True)]

    def sync_packets(self, num):
        """A known node's node info (and its position, if it shares one) as this radio would upload it on the
        main channel — so a linked hub's radio learns the node without waiting for it to transmit."""
        with self.lock:
            iface = self.iface
        if iface is None:
            return []
        n = (iface.nodesByNum or {}).get(num) or {}
        prim = next((ch for ch in iface.localNode.channels or [] if ch.role == 1), None)
        if not n.get("user") or prim is None:
            return []
        lc = iface.localNode.localConfig
        name = prim.settings.name or self._preset_name(lc)
        key = expand_psk(bytes(prim.settings.psk))
        root = self.topic_root or ("msh/" + config_pb2.Config.LoRaConfig.RegionCode.Name(lc.lora.region))
        gw = (iface.getMyUser() or {}).get("id") or f"!{iface.myInfo.my_node_num:08x}"
        u = dict(n["user"]); u.pop("raw", None)
        parts = [(portnums_pb2.PortNum.NODEINFO_APP, ParseDict(u, mesh_pb2.User(), ignore_unknown_fields=True).SerializeToString())]
        p = n.get("position") or {}
        if p.get("latitudeI") and p.get("longitudeI"):
            parts.append((portnums_pb2.PortNum.POSITION_APP, mesh_pb2.Position(
                latitude_i=int(p["latitudeI"]), longitude_i=int(p["longitudeI"]), altitude=int(p.get("altitude") or 0),
                time=int(p.get("time") or 0), precision_bits=int(p.get("precisionBits") or 0)).SerializeToString()))
        out = []
        for port, payload in parts:
            pid = secrets.randbits(32) or 1
            plain = mesh_pb2.Data(portnum=port, payload=payload).SerializeToString()
            pkt = mesh_pb2.MeshPacket(to=0xFFFFFFFF, id=pid, channel=channel_code(name, bytes(prim.settings.psk)),
                                      hop_limit=3, hop_start=3,
                                      encrypted=decrypt_packet(key, pid, num, plain) if key else plain)   # AES-CTR both ways
            setattr(pkt, "from", num)
            env = mqtt_pb2.ServiceEnvelope(packet=pkt, channel_id=name, gateway_id=gw)
            out.append((f"{root}/2/e/{name}/{gw}", env.SerializeToString()))
        return out

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
                          "muted": ch.settings.module_settings.is_muted,
                          "key_b64": base64.b64encode(psk).decode(),
                          "code": channel_code(ch.settings.name or self._preset_name(ln.localConfig), psk) if ch.role else None})
        out["channels"] = chans
        out["channels_saved"] = cfg.get().get("channels_saved") or []
        out["channels_match"] = self.channels_match()
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
            self.save_channels()
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
        self.save_channels()

    def set_fixed(self, data):
        ln = self.iface.localNode
        if not data.get("enabled"):
            ln.removeFixedPosition()
            log.info("radio fixed position removed")
            return
        lat, lon, alt = approx(data["lat"]), approx(data["lon"]), int(float(data.get("alt") or 0))
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
            changed = False
            if ch.role != 0 and not (ch.settings.uplink_enabled and ch.settings.downlink_enabled):
                ch.settings.uplink_enabled = ch.settings.downlink_enabled = True
                changed = True
            if ch.role != 0 and ch.settings.module_settings.position_precision > APPROX_BITS:
                ch.settings.module_settings.position_precision = APPROX_BITS      # ≈ 700 m, never the exact place
                changed = True
            if changed:
                ln.writeChannel(ch.index)
        ln.commitSettingsTransaction()
        log.info("radio prepared for Ura (it restarts now)")
        # no GPS and no position of its own: give it the hub's location as fixed position (sent after the restart)
        h, f = cfg.get()["hub"], self.own_fix
        exact = f and (approx(f["lat"]) != f["lat"] or approx(f["lon"]) != f["lon"])
        if ln.localConfig.position.gps_mode != config_pb2.Config.PositionConfig.GpsMode.ENABLED and (exact or (
                not f and h.get("lat") is not None and h.get("lon") is not None)):
            lat, lon = (f["lat"], f["lon"]) if f else (float(h["lat"]), float(h["lon"]))     # set_fixed rounds it
            def later():
                for _ in range(20):               # the radio restarts after "prepare": wait until it is back (≤ 40 s)
                    time.sleep(2)
                    if self.iface is not None and self.iface is not iface:
                        break
                time.sleep(3)
                try:
                    self.set_fixed({"enabled": True, "lat": lat, "lon": lon, "alt": 0})
                except Exception as e:
                    log.warning("could not give the radio the hub's location: %s", e)
            threading.Thread(target=later, daemon=True).start()


def enqueue(q, item):
    """Packets from the radio wait here while the server is unreachable; above "queue_max" the oldest go."""
    while q.qsize() >= adv("queue_max"):
        q.get_nowait()
    q.put_nowait(item)


radios = {}       # radio id -> Radio
radio_queue: asyncio.Queue = None


def drop_from_cache(iface, node_id=None):
    """The meshtastic library keeps its own copy of the radio's node list; after the radio forgets a node (or
    all), remove it there too — otherwise the pages keep showing it until the next reconnect."""
    me = iface.myInfo.my_node_num
    for num in list((iface.nodesByNum or {}).keys()):
        nid = (iface.nodesByNum[num].get("user") or {}).get("id") or f"!{num:08x}"
        if num != me and (node_id is None or nid == node_id or num == int(node_id.lstrip("!"), 16)):
            iface.nodesByNum.pop(num, None)
            if iface.nodes:
                iface.nodes.pop(nid, None)


APPROX_BITS = 15             # Meshtastic channel position precision for the hub radio's own position (≈ 700 m)
APPROX_DECIMALS = 2          # a hub radio's location is approximate: 0.01° ≈ 1 km — never more exact


def approx(v):
    return None if v in (None, "") else round(float(v), APPROX_DECIMALS)


def forget_peer(peer, everything=False, wait=False):
    """A link ended (or the hub left the server): delete everything about that partner, as if the link never
    existed — its rules, its pinned end-to-end key, its counters, and its nodes on our radio (their names and
    keys; a node that was reset meanwhile is then learned fresh). `everything`: no link is left, so all remote
    nodes go, also those whose origin is unknown."""
    cfg.update(lambda d: (d["rules"].pop(peer, None), d["peer_keys"].pop(peer, None)))
    with counters.lock:
        counters.peer.pop(peer, None)
    gone = origins.drop_peer(peer)
    mc_keys = [n[3:] for n in gone if n.startswith("mc:")]
    nodes = [n for n in gone if not n.startswith("mc:")]
    if mc_keys:
        mc_remote_keys.difference_update(mc_keys)
        def mc_forget():
            mr = mc_radio()
            if mr is None or mr.ser is None:
                return
            done, left = mr.remove_contacts([k for k in mc_keys if k in mr.contacts])
            log.info("link to %s ended: %d MeshCore contact(s) from it deleted from the radio%s", peer, done,
                     f" ({len(left)} could not be deleted)" if left else "")
        threading.Thread(target=mc_forget, daemon=True).start()
    r = mt_radio()
    def radio_forget():
        # The radio silently skips delete commands that come too fast (seen live: 31 of 51 at 0.3 s): send them
        # 2 s apart, then re-read the node list from the radio (fresh USB session) and repeat what is left.
        ids = set(nodes)
        if r is not None and r.iface is not None and everything:
            ids |= {n.get("user", {}).get("id") or f"!{num:08x}" for num, n in list((r.iface.nodesByNum or {}).items())
                    if n.get("viaMqtt") and num != r.iface.myInfo.my_node_num}
        total = left = 0
        for round_ in range(3):
            if r is None or r.iface is None:
                break
            known = set((r.iface.nodes or {}).keys())
            pending = [nid for nid in ids if nid in known]
            if round_ == 0:
                total = len(pending)
            left = len(pending)
            if not pending:
                break
            for nid in pending:
                try:
                    r.iface.localNode.removeNode(nid)
                    drop_from_cache(r.iface, nid)
                except Exception as e:
                    log.warning("could not remove node %s from the radio: %s", nid, e)
                time.sleep(2)
            iface = r.iface                       # check: read the node list again from the radio
            r._drop(iface, "re-reading the node list after deleting nodes", False)
            for _ in range(60):
                time.sleep(1)
                if r.iface is not None and r.iface is not iface:
                    break
            time.sleep(2)
        if r is not None and r.iface is not None:
            left = len([nid for nid in ids if nid in set((r.iface.nodes or {}).keys())])
        log.info("link to %s ended: its rules, key and %d remote node(s) on the radio were deleted%s", peer, total - left,
                 f" ({left} could not be deleted)" if left else " (checked on the radio)")
    if wait:
        radio_forget()
    else:
        threading.Thread(target=radio_forget, daemon=True).start()


# ───────────────────────── factory reset ─────────────────────────
reset_state = {}           # progress of a running factory reset, shown on the page


def factory_reset():
    """Delete everything this hub knows and start again as if just installed: leave the server (it deletes this
    hub, its links, statistics and nodes), remove the partners' nodes from the radio, delete settings, password,
    keys, node memory, logs and map cache, then restart in first-start mode. The website certificate stays
    (it holds no data; the browser would only warn again)."""
    import shutil
    def step(text):
        reset_state.setdefault("steps", []).append(text)
        log.info("factory reset: %s", text)
    reset_state.clear(); reset_state.update(running=True, steps=[])
    c = cfg.get()
    if c["server"]["hub_id"]:
        try:
            told = run_coro(server_leave(), timeout=25)
        except Exception:
            told = False
        step("server told: this hub, its links, statistics and nodes deleted there" if told
             else "server could not be reached — it removes this hub when the administrator does")
    peers = set(c["rules"]) | set(c["peer_keys"]) | origins.peers()
    if mt_radio() is not None and mt_radio().iface is not None:
        step("removing the partners' nodes from the radio (2 s each, then checked on the radio)…")
        for peer in peers or {""}:
            forget_peer(peer, everything=True, wait=True)
        step("partners' nodes removed from the radio")
    elif peers:
        step("no radio connected: its node list was not touched")
    def wipe():
        for r in list(radios.values()) + list(mc_radios.values()):
            r.close()
        for name in os.listdir(DATA_DIR):
            p_ = os.path.join(DATA_DIR, name)
            if name in ("web.crt", "web.key"):
                continue
            if name in ("logs", "tiles") and os.path.isdir(p_):
                shutil.rmtree(p_, ignore_errors=True)
            elif name.startswith(("config", "origins", "identity")) and os.path.isfile(p_):
                os.remove(p_)
        for h_ in list(logging.getLogger().handlers):          # the old log file is gone: start a new one
            if isinstance(h_, logging.handlers.RotatingFileHandler):
                logging.getLogger().removeHandler(h_); h_.close()
        log_setup(DATA_DIR)
        logging.getLogger().info("factory reset done: settings, password, keys, node memory, logs and map cache deleted")
    step("deleting settings, password, keys, node memory, logs and map cache; restarting…")
    program_action("restart", wipe)


# ───────────────────────── what is on a serial port ─────────────────────────
_ident_cache = {}
radio_result = {}          # outcome of the last "Save" on the Radio page: connecting / connected / refused


def usb_label(path):
    """Maker / model of the USB device behind a port, as the computer reports it (no guessing)."""
    real = os.path.realpath(path)
    dev = os.path.basename(real)
    base = f"/sys/class/tty/{dev}/device"
    for up in ("..", "../..", "../../.."):
        d = os.path.normpath(os.path.join(os.path.realpath(base), up))
        try:
            m = open(os.path.join(d, "manufacturer")).read().strip() if os.path.exists(os.path.join(d, "manufacturer")) else ""
            p = open(os.path.join(d, "product")).read().strip() if os.path.exists(os.path.join(d, "product")) else ""
        except OSError:
            continue
        if m or p:
            return " ".join(x for x in (m, p) if x)
    return ""


def ident_key(path):
    if os.environ.get("URA_TEST_RADIO") and path.startswith("/dev/fake"):
        return (path, 0, 0)
    try:
        st = os.stat(os.path.realpath(path))
        return (path, st.st_rdev, st.st_ctime)
    except OSError:
        return None


def identify_port(path, timeout=20.0):
    """Ask the device on a serial port what it is, by talking to it:
    {"kind": "meshtastic"|"meshcore"|"unknown"|"busy"|"missing", "name", "id", "hw"}.
    Meshtastic answers its own framed handshake (0x94 0xC3 …) with its node number and name; a MeshCore
    companion answers its "app start" frame (<…) with its name. Anything else is "unknown"."""
    if os.environ.get("URA_TEST_RADIO") and path.startswith("/dev/fake"):     # tests: simulated ports
        kind = "meshcore" if "meshcore" in path else "unknown" if "unknown" in path else "meshtastic"
        out = {"kind": kind, "name": {"meshcore": "Sim-MeshCore", "unknown": ""}.get(kind, "Sim-Radio"), "id": "", "hw": ""}
        if kind != "unknown":
            _ident_cache[ident_key(path)] = out
        return out
    if not os.path.exists(path):
        return {"kind": "missing", "name": "", "id": "", "hw": ""}
    try:
        st = os.stat(os.path.realpath(path))
        key = (path, st.st_rdev, st.st_ctime)
    except OSError:
        key = None
    if key and key in _ident_cache:
        return _ident_cache[key]
    import serial, termios
    out = {"kind": "no_answer", "name": "", "id": "", "hw": ""}
    got_bytes = False
    try:
        with open(path) as f:                          # like the Meshtastic library: do not reset the board on close
            a = termios.tcgetattr(f)
            a[2] &= ~termios.HUPCL
            termios.tcsetattr(f, termios.TCSAFLUSH, a)
        s = serial.Serial(path, 115200, timeout=0.3, write_timeout=1, exclusive=True)
    except Exception as e:
        busy = "busy" in str(e).lower() or "lock" in str(e).lower() or "Resource temporarily" in str(e)
        return {"kind": "busy" if busy else "unknown", "name": "", "id": "", "hw": "", "error": str(e)}
    try:
        time.sleep(0.3)
        s.reset_input_buffer()
        # MeshCore companion: CMD_APP_START → RESP_SELF_INFO (code 5), name at the end
        pl = bytes([1, 3]) + b"\0" * 6 + b"ura"
        s.write(b"<" + len(pl).to_bytes(2, "little") + pl)
        buf, end = b"", time.time() + 1.5
        while time.time() < end:
            buf += s.read(256)
            got_bytes = got_bytes or bool(buf)
            i = buf.find(b">")
            if i >= 0 and len(buf) >= i + 3:
                n = int.from_bytes(buf[i + 1:i + 3], "little")
                if len(buf) >= i + 3 + n:
                    p = buf[i + 3:i + 3 + n]
                    if p and p[0] == 5 and len(p) >= 58:
                        out = {"kind": "meshcore", "name": p[58:].split(b"\0")[0].decode("utf-8", "replace"),
                               "id": p[4:10].hex(), "hw": ""}
                    break
        if out["kind"] == "no_answer":
            # Meshtastic: ToRadio{want_config_id} → FromRadio my_info, node_info(s), metadata …
            cid = secrets.randbelow(1 << 31) or 1
            tr = mesh_pb2.ToRadio(want_config_id=cid).SerializeToString()
            s.reset_input_buffer()
            s.write(b"\x94\xc3" + len(tr).to_bytes(2, "big") + tr)
            buf, me, end = b"", None, time.time() + timeout
            while time.time() < end:
                chunk = s.read(512)
                got_bytes = got_bytes or bool(chunk)
                buf += chunk
                while True:
                    i = buf.find(b"\x94\xc3")
                    if i < 0 or len(buf) < i + 4:
                        buf = buf[i:] if i >= 0 else buf[-1:]
                        break
                    n = int.from_bytes(buf[i + 2:i + 4], "big")
                    if n > 512:
                        buf = buf[i + 2:]
                        continue
                    if len(buf) < i + 4 + n:
                        buf = buf[i:]
                        break
                    fr = mesh_pb2.FromRadio()
                    try:
                        fr.ParseFromString(buf[i + 4:i + 4 + n])
                    except Exception:
                        fr = None
                    buf = buf[i + 4 + n:]
                    if fr is None:
                        continue
                    w = fr.WhichOneof("payload_variant")
                    if w == "my_info":
                        me = fr.my_info.my_node_num
                        out.update(kind="meshtastic", id=f"!{me:08x}")
                    elif w == "node_info" and me is not None and fr.node_info.num == me:
                        out.update(name=fr.node_info.user.long_name, hw=mesh_pb2.HardwareModel.Name(fr.node_info.user.hw_model))
                    elif w == "config_complete_id":
                        end = 0
                if out["kind"] == "meshtastic" and out["name"]:
                    break
    except Exception as e:
        out["error"] = str(e)
    finally:
        try:
            s.close()
        except Exception:
            pass
    if out["kind"] == "no_answer" and got_bytes:
        out["kind"] = "unknown"                       # it talks, but neither Meshtastic nor MeshCore
    if key and out["kind"] in ("meshtastic", "meshcore"):   # a replugged device gets a new key and is asked again
        _ident_cache[key] = out
    return out


def describe_kind(info):
    """One line for messages and the log: what was found on the port."""
    k, nm = info.get("kind"), info.get("name") or ""
    if k == "meshtastic":
        return f"Meshtastic radio “{nm}” {info.get('id', '')}".strip()
    if k == "meshcore":
        return f"MeshCore radio “{nm}”"
    if k == "busy":
        return "port in use by another program"
    if k == "missing":
        return "nothing plugged in"
    if k == "no_answer":
        return "no answer from the device"
    return "not recognised as a radio"


def mt_radio():
    for r in radios.values():
        return r
    return None


# ───────────────────────── radio (MeshCore companion) ─────────────────────────
MC_ADV_TYPES = {0: "none", 1: "companion", 2: "repeater", 3: "room", 4: "sensor"}
MC_PAYLOAD = {0: "request", 1: "response", 2: "text", 3: "ack", 4: "advert", 5: "group text", 6: "group data", 7: "anon request",
              8: "path", 9: "trace", 10: "multipart", 11: "control", 15: "raw"}


class McRadio:
    """A MeshCore radio with companion firmware on USB. It speaks its own serial protocol: frames "<" + length (2
    bytes, little endian) + payload to the radio, ">" + length + payload back. For now the hub only READS: who the
    radio is (name, key, radio settings, firmware), its contacts and channels, and every raw packet it hears
    (PUSH_CODE_LOG_RX_DATA) — those are what will be carried over the links."""

    def __init__(self, conf):
        import collections, queue as _q
        self.conf, self.lock, self.req_lock = conf, threading.Lock(), threading.Lock()
        self.ser, self.stop, self.error, self.connected_at, self.found = None, False, "", 0, {}
        self.self_info, self.device, self.contacts, self.channels = {}, {}, {}, []
        self.rx = collections.deque(maxlen=5000)       # (time, route, payload type, length, snr, rssi)
        self.resp = _q.Queue()
        self.contacts_dirty, self.last_contacts = False, 0
        self.air = collections.deque(maxlen=5000)      # (time, seconds on air) of packets Ura put on air
        self.sync_sent, self.sync_partners, self.sync_last = {}, set(), 0   # adverts announced over the links
        self.messages, self.msg_waiting = collections.deque(maxlen=100), True  # what this radio itself received
        threading.Thread(target=self._run, daemon=True).start()

    # ── serial link ──
    def _open(self):
        import serial, termios
        path = self.conf["address"]
        if not os.path.exists(path):
            raise RuntimeError("port not present")
        with open(path) as f:                          # do not reset the board when the port closes
            a = termios.tcgetattr(f); a[2] &= ~termios.HUPCL; termios.tcsetattr(f, termios.TCSAFLUSH, a)
        return serial.Serial(path, 115200, timeout=0.3, write_timeout=2, exclusive=True)

    def _send(self, payload):
        self.ser.write(b"<" + len(payload).to_bytes(2, "little") + payload)

    def _reader(self, ser):
        buf = b""
        while not self.stop and self.ser is ser:
            try:
                chunk = ser.read(512)
            except Exception:
                break
            buf += chunk
            while True:
                i = buf.find(b">")
                if i < 0:
                    buf = b""
                    break
                if len(buf) < i + 3:
                    buf = buf[i:]
                    break
                n = int.from_bytes(buf[i + 1:i + 3], "little")
                if n == 0 or n > 300:
                    buf = buf[i + 1:]
                    continue
                if len(buf) < i + 3 + n:
                    buf = buf[i:]
                    break
                frame, buf = buf[i + 3:i + 3 + n], buf[i + 3 + n:]
                try:
                    self._frame(frame)
                except Exception as e:
                    log.warning("MeshCore radio: bad frame (%s)", e)
        if self.ser is ser and not self.stop:
            with self.lock:
                self.ser = None
            self.error = "connection lost"
            log.warning("MeshCore radio %s: connection lost", self.conf.get("address"))
        try:
            ser.close()
        except Exception:
            pass

    def _frame(self, f):
        code = f[0]
        if code == 0x88 and len(f) > 3:                 # a raw packet the radio heard
            h = f[3]
            self.rx.append((time.time(), h & 3, (h >> 2) & 0x0F, len(f) - 3, (f[1] - 256 if f[1] > 127 else f[1]) / 4,
                            f[2] - 256 if f[2] > 127 else f[2]))
            self.last_rx = time.time()
            try:
                mc_send_to_peers(bytes(f[3:]))
            except Exception as e:
                log.warning("MeshCore packet not passed on: %s", e)
        elif code in (0x80, 0x8A):                      # an advert: a node (re)announced itself
            self.contacts_dirty = True
        elif code == 0x83:                              # a message for this radio is waiting
            self.msg_waiting = True
        elif code < 0x80:
            self.resp.put(f)                            # an answer to our request

    def _request(self, payload, until, timeout=4.0):
        """Send a command, collect answer frames until `until(frame)` is true (or ERR / timeout)."""
        import queue as _q
        with self.req_lock:
            while not self.resp.empty():
                self.resp.get_nowait()
            self._send(payload)
            out, end = [], time.time() + timeout
            while time.time() < end:
                try:
                    f = self.resp.get(timeout=max(0.05, end - time.time()))
                except _q.Empty:
                    break
                out.append(f)
                if f[0] == 1 or until(f):
                    break
            return out

    # ── reading the radio ──
    def _read_self(self):
        f = next((x for x in self._request(bytes([1, 3]) + b"\0" * 6 + b"ura-hub", lambda x: x[0] == 5) if x[0] == 5), None)
        if not f or len(f) < 58:
            raise RuntimeError("no_answer")
        le = lambda a, b, signed=False: int.from_bytes(f[a:b], "little", signed=signed)
        self.self_info = {"adv_type": MC_ADV_TYPES.get(f[1], f[1]), "tx_power": f[2], "max_tx_power": f[3],
                          "public_key": f[4:36].hex(), "lat": le(36, 40, True) / 1e6, "lon": le(40, 44, True) / 1e6,
                          "advert_location": f[45], "manual_add": f[47], "multi_acks": f[44], "telemetry_byte": f[46],
                          "freq_mhz": le(48, 52) / 1000, "bw_khz": le(52, 56) / 1000, "sf": f[56], "cr": f[57],
                          "name": f[58:].split(b"\0")[0].decode("utf-8", "replace")}
        d = next((x for x in self._request(bytes([22, 3]), lambda x: x[0] == 13) if x[0] == 13), None)
        if d and len(d) >= 80:
            self.device = {"fw_code": d[1], "max_contacts": d[2] * 2, "max_channels": d[3],
                           "build": d[8:20].split(b"\0")[0].decode(), "model": d[20:60].split(b"\0")[0].decode(),
                           "firmware": d[60:80].split(b"\0")[0].decode(),
                           "client_repeat": d[80] if len(d) > 80 else None}

    def _read_contacts(self):
        frames = self._request(bytes([4]), lambda x: x[0] == 4, timeout=8)
        out = {}
        for f in frames:
            if f[0] != 3 or len(f) < 148:
                continue
            le = lambda a, b, signed=False: int.from_bytes(f[a:b], "little", signed=signed)
            key = f[1:33].hex()
            out[key] = {"key": key, "type": MC_ADV_TYPES.get(f[33], f[33]), "path_len": f[35] if f[35] != 255 else None,
                        "name": f[100:132].split(b"\0")[0].decode("utf-8", "replace"),
                        "last_advert": le(132, 136), "lat": le(136, 140, True) / 1e6 or None, "lon": le(140, 144, True) / 1e6 or None}
        self.contacts, self.last_contacts, self.contacts_dirty = out, time.time(), False

    def _read_channels(self):
        out = []
        for idx in range((self.device or {}).get("max_channels") or 8):
            f = next((x for x in self._request(bytes([31, idx]), lambda x: x[0] in (18, 1), timeout=2) if x[0] == 18), None)
            if f and len(f) >= 50:
                name = f[2:34].split(b"\0")[0].decode("utf-8", "replace")
                if name or any(f[34:50]):
                    out.append({"index": idx, "name": name or "(no name)", "hash": hashlib.sha256(bytes(f[34:50])).digest()[0],
                                "public": f[34:50].hex() == "8b3387e9c5cdea6ac9e5edbaa115cd72"})   # MeshCore's well-known Public key
        self.channels = out

    def _run(self):
        global mc_result
        while not self.stop:
            if self.ser is None and self.conf.get("enabled", True):
                try:
                    ser = self._open()
                    with self.lock:
                        self.ser = ser
                    threading.Thread(target=self._reader, args=(ser,), daemon=True).start()
                    time.sleep(0.3)
                    self._read_self()
                    self.error, self.connected_at, self.found = "", time.time(), {}
                    self._read_contacts()
                    self._read_channels()
                    log.info("MeshCore radio connected: %s (%s, %s) — %d contacts, %d channels", self.self_info.get("name"),
                             self.device.get("model"), self.device.get("firmware"), len(self.contacts), len(self.channels))
                    if mc_result.get("address") == self.conf.get("address"):
                        mc_result = {"address": self.conf["address"], "state": "connected", "t": time.time(),
                                     "found": {"kind": "meshcore", "name": self.self_info.get("name"), "contacts": len(self.contacts)}}
                except Exception as e:
                    with self.lock:
                        ser, self.ser = self.ser, None
                    if ser:
                        try:
                            ser.close()
                        except Exception:
                            pass
                    msg = str(e)
                    if msg == "no_answer":                 # the port is there, but no MeshCore companion answered
                        info = identify_port(self.conf["address"])
                        self.found, msg = info, ("not_meshcore" if info["kind"] not in ("no_answer", "busy") else info["kind"])
                        if mc_result.get("address") == self.conf.get("address") and mc_result.get("state") == "connecting" \
                                and info["kind"] in ("meshtastic", "unknown"):
                            mc_result = {"address": self.conf["address"], "state": "refused", "found": info,
                                         "text": describe_kind(info), "t": time.time()}
                            log.warning("MeshCore radio not saved: %s on %s", describe_kind(info), self.conf["address"])
                            cfg.update(lambda d: d.__setitem__("radios", [x for x in d["radios"] if x.get("net") != "mc"]))
                            loop.call_soon_threadsafe(apply_radios)
                    if self.error != msg and msg != "port not present":
                        log.warning("MeshCore radio %s: %s", self.conf.get("address"), msg)
                    self.error = msg
            elif self.ser is not None and (self.contacts_dirty or time.time() - self.last_contacts > 300):
                try:
                    self._read_contacts()
                except Exception:
                    pass
            if self.ser is not None and self.self_info and self.msg_waiting:
                try:
                    self._read_messages()
                except Exception as e:
                    log.warning("MeshCore messages not read: %s", e)
            if self.ser is not None and self.self_info:
                try:
                    self._sync_step()
                except Exception as e:
                    log.warning("MeshCore advert announcement failed: %s", e)
            time.sleep(3)

    def _read_messages(self):
        """Messages addressed to this radio (private) or on its channels: kept for the MeshCore page."""
        self.msg_waiting = False
        for _ in range(30):
            f = next((x for x in self._request(bytes([10]), lambda x: x[0] in (16, 17, 7, 8, 10), timeout=3) if x[0] in (16, 17, 7, 8, 10)), None)
            if f is None or f[0] == 10:
                return
            if f[0] == 16 and len(f) >= 16:
                pre = f[4:10].hex()
                who = next((c["name"] for k, c in self.contacts.items() if k.startswith(pre)), pre)
                m = {"kind": "private", "from": who, "hops": None if f[10] == 255 else f[10] & 63,
                     "sent": int.from_bytes(f[12:16], "little"), "text": f[16 + (4 if f[11] == 2 else 0):].decode("utf-8", "replace")}
            elif f[0] == 17 and len(f) >= 11:
                ch = next((c["name"] for c in self.channels if c["index"] == f[4]), f"#{f[4]}")
                txt = f[11:].decode("utf-8", "replace")
                who, _, body = txt.partition(": ")
                m = {"kind": "channel", "channel": ch, "from": who if body else "", "text": body or txt,
                     "hops": None if f[5] == 255 else f[5] & 63, "sent": int.from_bytes(f[7:11], "little")}
            else:
                continue
            m["received"] = int(time.time())
            self.messages.append(m)
            log.info("MeshCore radio received a %s message from %s (%s hops)", m["kind"] if m["kind"] == "private" else "channel " + m["channel"],
                     m["from"] or "?", m["hops"] if m["hops"] is not None else "direct")

    def nodes(self, share_positions):
        """For the server map: this radio and the contacts it knows from ITS OWN mesh (not those that came over Ura)."""
        if not self.self_info:
            return []
        si, t = self.self_info, time.time()
        out = [{"id": si.get("public_key", "")[:12], "name": si.get("name"), "short": "", "hw": (self.device or {}).get("model"),
                "role": si.get("adv_type"), "lat": (si.get("lat") or None) if share_positions else None,
                "lon": (si.get("lon") or None) if share_positions else None, "alt": None, "last_heard": int(t), "hops": 0, "own": True}]
        for c in self.contacts.values():
            if mc_is_remote(c["key"]) or not c.get("last_advert") or t - c["last_advert"] > adv("node_max_age_days") * 86400:
                continue
            out.append({"id": c["key"][:12], "name": c["name"], "short": "", "hw": "", "role": c["type"],
                        "lat": c["lat"] if share_positions else None, "lon": c["lon"] if share_positions else None, "alt": None,
                        "last_heard": min(int(t), c["last_advert"]), "hops": c.get("path_len"), "own": False})
        return out

    def export(self, key_hex=None):
        """The radio's own advert (no key) or a contact's advert, as the raw signed packet (CMD_EXPORT_CONTACT)."""
        fr = self._request(bytes([17]) + (bytes.fromhex(key_hex) if key_hex else b""), lambda x: x[0] in (11, 1))
        f = next((x for x in fr if x[0] == 11), None)
        return bytes(f[1:]) if f and len(f) > 3 else None

    def _sync_step(self):
        """A hub radio does not hear its own adverts, and quiet nodes do not advertise while a link is up: so the
        radio's own advert and those of the contacts it knows FROM ITS OWN MESH are announced to the linked hubs —
        one every "node_sync_gap_s" s, each again every "node_sync_hours" h, everything again when a partner returns."""
        if not adv("node_sync") or time.time() - self.sync_last < max(2, adv("node_sync_gap_s")):
            return
        self.sync_last = time.time()
        online = {h["id"] for h in link.directory if h.get("online")}
        partners = {p for p in active_peers() if p in online and mc_rule(p, "send").get("on", True) and mc_rule(p, "send").get("adverts", True)}
        if partners - self.sync_partners:
            self.sync_sent.clear()
        self.sync_partners = partners
        if not partners:
            return
        due = []
        if time.time() - self.sync_sent.get("self", 0) > adv("node_sync_hours") * 3600:
            due.append("self")
        for c in sorted(self.contacts.values(), key=lambda x: -(x.get("last_advert") or 0)):
            if mc_is_remote(c["key"]) or not c.get("last_advert") or time.time() - c["last_advert"] > adv("node_sync_age_h") * 3600:
                continue
            if time.time() - self.sync_sent.get(c["key"], 0) > adv("node_sync_hours") * 3600:
                due.append(c["key"])
        if not due:
            return
        k = due[0]
        raw = self.export(None if k == "self" else k)
        self.sync_sent[k] = time.time()
        if raw:
            mc_send_to_peers(raw, announce=self.self_info.get("name") if k == "self" else (self.contacts.get(k) or {}).get("name"))

    def close(self):
        self.stop = True
        with self.lock:
            ser, self.ser = self.ser, None
        if ser:
            try:
                ser.close()
            except Exception:
                pass

    def _ok(self, payload, timeout=4.0):
        if self.ser is None:
            raise RuntimeError("no_radio")
        fr = self._request(payload, lambda x: x[0] in (0, 1), timeout)
        if not fr or fr[-1][0] != 0:
            raise RuntimeError("the radio refused the command")

    def remove_contacts(self, keys):
        """Delete contacts from the radio (CMD_REMOVE_CONTACT), then read the list again from the radio."""
        done = 0
        for k in keys:
            try:
                self._ok(bytes([15]) + bytes.fromhex(k))
                done += 1
            except Exception:
                pass
            time.sleep(0.4)
        try:
            self._read_contacts()
        except Exception:
            pass
        left = [k for k in keys if k in self.contacts]
        return done, left

    def send_raw(self, raw):
        """Put a packet from a linked hub on air unchanged (CMD_SEND_RAW_PACKET, normal priority)."""
        self._ok(bytes([65, 1]) + raw)
        self.air.append((time.time(), time_on_air(len(raw) + 2, self.self_info.get("sf") or 8, self.self_info.get("bw_khz") or 62.5,
                                                   (self.self_info.get("cr") or 8))))

    def air_used(self, seconds):
        t = time.time()
        return sum(a for ts, a in list(self.air) if t - ts < seconds)

    def prepare(self, name=None):
        """For Ura: an approximate location (the hub's), shared in the radio's adverts; the hub radio does not repeat
        packets itself (Ura carries them); optionally a new name. Then the radio announces itself once."""
        si = self.self_info
        if name:
            self._ok(bytes([8]) + name.encode("utf-8")[:31])
        h = cfg.get()["hub"]
        lat = approx(si.get("lat")) if si.get("lat") else None
        lon = approx(si.get("lon")) if si.get("lon") else None
        if h.get("lat") is not None and h.get("lon") is not None:
            lat, lon = approx(h["lat"]), approx(h["lon"])
        if lat is not None and lon is not None:
            self._ok(bytes([14]) + int(lat * 1e6).to_bytes(4, "little", signed=True) + int(lon * 1e6).to_bytes(4, "little", signed=True))
        self._ok(bytes([38, si.get("manual_add", 0), si.get("telemetry_byte", 0), 1, si.get("multi_acks", 0)]))   # share location
        self._read_self()
        self._ok(bytes([7, 1]))                          # advert, flooded: the mesh learns name + location
        log.info("MeshCore radio prepared for Ura: %s, location %s, %s (shared in adverts)", self.self_info.get("name"), lat, lon)

    def set_settings(self, v):
        """MeshCore → Device settings: name, radio (frequency, bandwidth, SF, CR), power, location sharing.
        Radio settings apply at once; the hub radio never repeats packets itself (Ura carries them)."""
        si = self.self_info
        if v.get("name"):
            self._ok(bytes([8]) + str(v["name"]).strip().encode("utf-8")[:31])
        if any(k in v for k in ("freq_mhz", "bw_khz", "sf", "cr")):
            f = int(round(float(v.get("freq_mhz", si.get("freq_mhz"))) * 1000))
            bw = int(round(float(v.get("bw_khz", si.get("bw_khz"))) * 1000))
            sf, cr = int(v.get("sf", si.get("sf"))), int(v.get("cr", si.get("cr")))
            if not (150000 <= f <= 2500000 and 7000 <= bw <= 500000 and 5 <= sf <= 12 and 5 <= cr <= 8):
                raise ValueError("radio")
            self._ok(bytes([11]) + f.to_bytes(4, "little") + bw.to_bytes(4, "little") + bytes([sf, cr, 0]))
        if "tx_power" in v:
            pw = int(v["tx_power"])
            if not -9 <= pw <= int(si.get("max_tx_power") or 22):
                raise ValueError("tx_power")
            self._ok(bytes([12, pw & 0xFF]))
        if "share_location" in v:
            self._ok(bytes([38, si.get("manual_add", 0), si.get("telemetry_byte", 0), 1 if v["share_location"] else 0, si.get("multi_acks", 0)]))
        self._read_self()
        log.info("MeshCore radio settings changed by the operator: %s", ", ".join(sorted(v)))

    def checks(self):
        si, d = self.self_info, self.device
        return {"position_known": bool(si.get("lat") or si.get("lon")),
                "position_approx": bool(si.get("lat") or si.get("lon")) and approx(si.get("lat")) == si.get("lat") and approx(si.get("lon")) == si.get("lon"),
                "position_shared": si.get("advert_location") == 1,
                "no_repeat": not d.get("client_repeat")}

    def info(self):
        t = time.time()
        rx = [x for x in list(self.rx) if t - x[0] < 3600]
        by_type = {}
        for x in rx:
            k = MC_PAYLOAD.get(x[2], f"type {x[2]}")
            by_type[k] = by_type.get(k, 0) + 1
        out = {"id": self.conf.get("id"), "net": "mc", "transport": "serial", "address": self.conf.get("address"),
               "connected": self.ser is not None and bool(self.self_info) and not self.error, "error": self.error,
               "found": self.found if self.error in ("not_meshcore", "no_answer", "busy") else None,
               "rx_hour": len(rx), "rx_by_type": by_type, "last_rx": int(rx[-1][0]) if rx else None,
               "rx_snr": round(sum(x[4] for x in rx[-50:]) / len(rx[-50:]), 1) if rx else None}
        if out["connected"]:
            ck = self.checks()
            out.update(self.self_info, device=self.device, channels=self.channels, contacts=len(self.contacts), checks=ck, ready=all(ck.values()))
        return out


mc_radios = {}       # radio id -> McRadio
mc_result = {}       # outcome of the last "Save" on the MeshCore page: connecting / connected / refused


def mc_radio():
    for r in mc_radios.values():
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
    want_mc = {r["id"]: r for r in cfg.get()["radios"] if r.get("net") == "mc" and r.get("enabled", True)}
    for rid in list(mc_radios):
        if rid not in want_mc or mc_radios[rid].conf != want_mc[rid]:
            mc_radios.pop(rid).close()
    for rid, conf in want_mc.items():
        if rid not in mc_radios:
            mc_radios[rid] = McRadio(conf)


# ───────────────────────── server link ─────────────────────────

class Link:
    def __init__(self):
        self.state, self.detail = "not_configured", ""
        self.writer = None
        self.directory, self.links = [], []
        self.reconnect = asyncio.Event()
        self.kick_nodes = asyncio.Event()     # report nodes now (approved, reconnected, settings changed)
        self.kick_location = asyncio.Event()  # send the location now (settings changed, reconnected)
        self.map_data, self.map_event = None, asyncio.Event()     # the linked hubs and their nodes, from the server

    def public_rules(self):
        c = cfg.get()
        peers = {h["id"]: h.get("code") for h in self.directory}
        out = {"airtime": c["airtime"], "airtime_mc": c.get("airtime_mc") or {"pct_hour": 10.0, "pct_day": 0.0},
               "default": c["defaults"], "links": {}, "transit": c["transit"], "transit_to": [],
               "transit_mc": c.get("transit_mc") or {"enabled": False, "max_hops": 2}}
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
        for r in mc_radios.values():
            i = r.info()
            out.append({"net": "mc", "name": i.get("name"), "hw": (i.get("device") or {}).get("model"),
                        "firmware": (i.get("device") or {}).get("firmware"), "connected": i.get("connected")})
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
                    st = "removed" if self.detail in ("removed", "unknown_hub") else self.detail   # the server no longer has us
                    cfg.update(lambda d: d["server"].update(status=st))
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
                         asyncio.create_task(self._nodes()), asyncio.create_task(self._location()),
                         asyncio.create_task(self._node_sync())]
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
        c = cfg.get()
        # direct partners whose link is gone (a hub further away, known only as a node's origin, is not one)
        ended = (set(c["rules"]) | set(c["peer_keys"])) - now_peers - {c["server"]["hub_id"]}
        for peer in ended:
            forget_peer(peer, everything=not now_peers)
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
        if t == "map":                                   # answer to map_req: linked hubs + their nodes
            self.map_data = {"t": time.time(), "hubs": m.get("hubs") or [], "nodes": m.get("nodes") or [],
                             "offline_grey_h": m.get("offline_grey_h"), "offline_hide_days": m.get("offline_hide_days")}
            self.map_event.set()
        if t == "mesh" and m.get("net") == "mc" and m.get("box"):
            await asyncio.to_thread(mc_receive_box, m.get("from"), base64.b64decode(m["box"]))
        if t == "mesh" and m.get("net") == "ctl" and m.get("box"):
            await asyncio.to_thread(ctl_receive_box, m.get("from"), base64.b64decode(m["box"]))
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
        mc_last, mc_sig, mc_checked = 0, None, 0
        radios_sig = None
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
            rs = json.dumps(self.radio_summary(), sort_keys=True, default=str)
            if rs != radios_sig:                  # a radio (dis)connected or was renamed: the server's hub page follows
                radios_sig = rs
                await self.push_info()
            mr = mc_radio()
            if mr and mr.ser is not None and mr.self_info and time.time() - mc_checked >= adv("nodes_check_s"):
                mc_checked = time.time()
                mnodes = await asyncio.to_thread(mr.nodes, cfg.get()["share_positions_on_map"])
                msig = hashlib.sha256(json.dumps(sorted((n["id"], n["name"], n["lat"], n["lon"]) for n in mnodes), default=str).encode()).digest()
                if mnodes and (msig != mc_sig or time.time() - mc_last >= adv("nodes_report_min") * 60):
                    await self.send({"t": "nodes", "net": "mc", "nodes": mnodes})
                    mc_last, mc_sig = time.time(), msig
            if await self._sleep_or(self.kick_nodes, 10):
                checked, last_sig, mc_checked, mc_sig = 0, None, 0, None

    async def _node_sync(self):
        """Ura passes on live traffic; a node that is quiet while a link is up would stay unknown on the other side.
        So each node this radio knows from its own mesh is announced to the linked hubs: one every
        "node_sync_gap_s" seconds, each again every "node_sync_hours" hours, everything again when a partner
        (re)appears. The same link rules and the partner's airtime limit apply as for live packets."""
        sent, partners = {}, set()
        while True:
            await asyncio.sleep(max(2, adv("node_sync_gap_s")))
            r = mt_radio()
            online = {h["id"] for h in self.directory if h.get("online")}
            now_partners = set(active_peers()) & online
            if now_partners - partners:
                sent.clear()                  # a partner came (back): it gets every node
            partners = now_partners
            if not adv("node_sync") or not partners or r is None or r.iface is None:
                continue
            due = [n for n in await asyncio.to_thread(r.sync_candidates)
                   if time.time() - sent.get(n, 0) > adv("node_sync_hours") * 3600]
            if not due:
                continue
            num = due[0]
            for topic, data in await asyncio.to_thread(r.sync_packets, num):
                await asyncio.to_thread(send_to_peers, topic, data)
            sent[num] = time.time()
            log.info("node !%08x announced to the linked hubs (known to this radio, %d more to go)", num, len(due) - 1)

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
    extra = f" ({'received OK' if c['routing'] == 'NONE' else 'error ' + c['routing']}, to {c['to']})" if c.get("routing") else ""
    return f"{where} {c['kind']}{extra} from {c['sender']}"


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
    if r is None or r.iface is None:
        # no radio, or it is unplugged / reconnecting: the packet cannot be read without the radio's channels —
        # wait up to 15 s for it, otherwise say plainly why it did not go on air
        def later():
            for _ in range(15):
                time.sleep(1)
                rr = mt_radio()
                if rr is not None and rr.iface is not None:
                    return receive_from_peer(peer, topic, data, origin)
            counters.peer_add(peer, "blocked_recv", "no_radio")
            frm_ = next((h.get("code") for h in link.directory if h["id"] == peer), peer)
            log.info("from %s: packet not put on air (no radio connected to this hub)", frm_)
        threading.Thread(target=later, daemon=True).start()
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
    if ok and c.get("unreadable") and not c["private"]:
        ok, why = False, "key_differs"             # this radio has a channel of that name, with another key
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
    def put_on_air(waited=0):
        if r.downlink(topic, data):
            counters.air_add(toa)
            counters.peer_add(peer, "received")
            log.info("from %s%s %s: put on air%s", frm, via, pkt_desc(c), f" (after waiting {waited} s for the radio)" if waited else "")
            return True
        return False
    if put_on_air():
        return
    def later():                 # the radio is reconnecting (e.g. re-read after a link ended): wait for it, ≤ 15 s
        for i in range(15):
            time.sleep(1)
            if r.iface is not None and put_on_air(i + 1):
                return
        counters.peer_add(peer, "blocked_recv", "no_radio")
        log.info("from %s%s %s: not put on air (radio not connected)", frm, via, pkt_desc(c))
    threading.Thread(target=later, daemon=True).start()



# ───────────────────────── MeshCore lane ─────────────────────────
def mc_parse(raw):
    """A raw MeshCore packet: header (route 2 bits, payload type 4 bits, version 2 bits), optional transport codes,
    path length (low 6 bits = hops, high 2 bits = hash size - 1), path, payload. Returns its identity like
    MeshCore's own packet hash (payload type + payload: the same packet repeated along other paths is the same)."""
    if len(raw) < 3:
        return None
    h = raw[0]
    route, ptype, i = h & 3, (h >> 2) & 0x0F, 1
    if route in (0, 3):
        i += 4
    if i >= len(raw):
        return None
    pl = raw[i]; i += 1
    if pl >> 6 == 3:
        return None
    i += (pl & 63) * ((pl >> 6) + 1)
    if i >= len(raw):
        return None
    payload = raw[i:]
    ident = hashlib.sha256(bytes([ptype]) + (bytes([pl]) if ptype == 9 else b"") + payload).digest()[:16]
    out = {"route": "flood" if route in (0, 1) else "direct", "type": MC_PAYLOAD.get(ptype, f"type {ptype}"), "hops": pl & 63, "id": ident}
    if ptype == 4:
        out["class"] = "adverts"
    elif ptype in (5, 6):                               # group: first payload byte = channel hash
        out["class"], ch = "group", None
        r = mc_radio()
        for c in (r.channels if r else []):
            if c.get("hash") == payload[0]:
                ch = c
                break
        if ch is None and payload[0] == MC_PUBLIC_HASH:
            ch = {"name": "Public", "public": True}
        if ch and ch.get("public"):
            out["class"] = "public"
        elif ch:
            out["group"] = ch["name"]
    elif ptype in (0, 1, 2, 3, 7, 8):
        out["class"] = "private"                        # private messages + their confirmations, paths, requests
    else:
        out["class"] = "other"                          # traceroute, control, multipart, raw
    return out


MC_PUBLIC_HASH = hashlib.sha256(bytes.fromhex("8b3387e9c5cdea6ac9e5edbaa115cd72")).digest()[0]


def mc_rule(peer, direction):
    """This link's MeshCore rule for one direction (separate from the Meshtastic rules)."""
    r = cfg.rules_for(peer)
    m = (r.get("mc") or {}).get(direction)
    if m is None:
        m = dict(MC_RULE_DEFAULT, on=bool((r.get(direction) or {}).get("mc", True)))
    return m


def mc_allowed(rule, p):
    if not rule.get("on", True):
        return False, "meshcore_off"
    k = p.get("class", "other")
    if k == "group":
        if p.get("group"):
            return (True, None) if p["group"] in (rule.get("groups") or []) else (False, "meshcore_group")
        return (True, None) if rule.get("other_groups", False) else (False, "meshcore_other_groups")
    return (True, None) if rule.get(k, True) else (False, "meshcore_" + k)


mc_remote_keys = set()     # MeshCore nodes whose adverts came over Ura (never announced back); kept in `origins` too


def mc_is_remote(key):
    """A MeshCore node that came over a link: not this hub's own (not reported, not announced back)."""
    return key in mc_remote_keys or ("mc:" + key) in origins.map
counters_mc = Counters()   # MeshCore traffic is counted on its own (Meshtastic keeps `counters`)


def mc_send_to_peers(raw, announce=None, path=None, exclude=(), max_hops=None):
    """MeshCore radio -> linked hubs: every packet the radio hears (each only once, whatever path it came by),
    sealed end-to-end per partner. Copies of packets that came FROM a partner are not sent back."""
    if len(raw) > 174:
        return
    p = mc_parse(raw)
    own = path is None
    if p is None or (own and seen_cache.seen(b"m" + p["id"])):
        return
    if own:
        path = [my_id()]
    boxes = {}
    for peer in active_peers():
        if peer in exclude:
            continue
        if not own and not mc_rule(peer, "send").get("transit", True):
            counters_mc.peer_add(peer, "blocked_send", "transit_off")
            continue
        ok, why = mc_allowed(mc_rule(peer, "send"), p)     # MeshCore rules of this link (independent of Meshtastic)
        if not ok:
            counters_mc.peer_add(peer, "blocked_send", why)
            continue
        keys, state = identity.keys_for(peer)
        if keys is None:
            counters_mc.peer_add(peer, "blocked_send", "key_" + state)
            continue
        mh = (int(mc_rule(peer, "send").get("reach") or 0) + 1) if own else int(max_hops or 2)   # the ORIGIN decides how far
        inner = json.dumps({"net": "mc", "data": base64.b64encode(raw).decode(), "path": path, "max_hops": mh}).encode()
        boxes[peer] = base64.b64encode(seal(keys, inner)).decode()
        counters_mc.peer_add(peer, "sent" if own else "transit")
    names = {h["id"]: h.get("code") for h in link.directory}
    if not own:
        if boxes:
            log.info("MeshCore passing on %s %s (from %s): sent to %s", p["route"], p["type"], names.get(path[0], path[0]), ", ".join(names.get(x, x) for x in boxes))
    elif announce:
        log.info("MeshCore advert of “%s” announced to %s", announce, ", ".join(names.get(x, x) for x in boxes) or "nobody")
    else:
        log.info("MeshCore radio -> %s %s (%d hops): sent to %s", p["route"], p["type"], p["hops"], ", ".join(names.get(x, x) for x in boxes) or "nobody")
    if boxes:
        counters_mc.add("sent" if own else "transit")
        asyncio.run_coroutine_threadsafe(link.send({"t": "mesh", "net": "mc", "boxes": boxes}), loop)


def mc_receive_box(peer, box):
    """A MeshCore packet from a linked hub: check the box, the link's receive rule and the airtime limit, then put it
    on air unchanged with this hub's MeshCore radio."""
    keys, state = identity.keys_for(peer)
    if keys is None:
        counters_mc.peer_add(peer, "blocked_recv", "key_" + state)
        return
    try:
        inner, nonce = open_box(keys, box, max_age=adv("replay_window_s"))
        m = json.loads(inner)
        raw = base64.b64decode(m["data"])
    except Exception:
        counters_mc.peer_add(peer, "blocked_recv", "bad_box")
        return
    if seen_cache.seen(b"n" + nonce):
        return
    p = mc_parse(raw)
    if p is None:
        counters_mc.peer_add(peer, "blocked_recv", "invalid")
        return
    path = [str(x)[:20] for x in (m.get("path") or [peer])][:16]
    if my_id() in path:                                 # it went round in a circle
        counters_mc.peer_add(peer, "blocked_recv", "loop")
        return
    if len(path) > 1 and not mc_rule(peer, "receive").get("from_beyond", True):
        counters_mc.peer_add(peer, "blocked_recv", "from_beyond")
        return
    frm = next((h.get("code") for h in link.directory if h["id"] == peer), peer)
    counters_mc.add("received")
    if p["type"] == "advert":                          # remember (permanently): this node lives on the other side
        try:
            i_ = 1 + (4 if (raw[0] & 3) in (0, 3) else 0)
            pl_ = raw[i_]; i_ += 1 + (pl_ & 63) * ((pl_ >> 6) + 1)
            k_ = raw[i_:i_ + 32].hex()
            mc_remote_keys.add(k_)
            origins.note("mc:" + k_, path[0] if path else peer)
        except Exception:
            pass
    if seen_cache.seen(b"m" + p["id"]):                # already heard here (it went round) -> not again
        return
    # MeshCore multi-hop: pass it on to my other links only if I allow MeshCore transit and the origin's limit allows
    tm = cfg.get().get("transit_mc") or {}
    origin_max = int(m.get("max_hops") or 1)
    if tm.get("enabled") and len(path) + 1 <= min(int(tm.get("max_hops", 2)), origin_max):
        try:
            mc_send_to_peers(raw, path=path + [my_id()], exclude=set(path) | {peer}, max_hops=origin_max)
        except Exception as e:
            log.warning("MeshCore packet not passed on: %s", e)
    r = mc_radio()
    if r is None or r.ser is None:
        counters_mc.peer_add(peer, "blocked_recv", "no_radio")
        log.info("from %s MeshCore %s: not put on air (no MeshCore radio connected)", frm, p["type"])
        return
    ok, why = mc_allowed(mc_rule(peer, "receive"), p)
    if not ok:
        counters_mc.peer_add(peer, "blocked_recv", why)
        log.info("from %s MeshCore %s: not put on air (%s)", frm, p["type"], why)
        return
    a = cfg.get().get("airtime_mc") or {"pct_hour": 10.0, "pct_day": 0.0}
    si = r.self_info
    toa = time_on_air(len(raw) + 2, si.get("sf") or 8, si.get("bw_khz") or 62.5, si.get("cr") or 8)
    if (a.get("pct_hour") and r.air_used(3600) + toa > 3600 * a["pct_hour"] / 100) or \
       (a.get("pct_day") and r.air_used(86400) + toa > 86400 * a["pct_day"] / 100):
        counters_mc.peer_add(peer, "blocked_recv", "airtime")
        log.info("from %s MeshCore %s: not put on air (airtime limit)", frm, p["type"])
        return
    try:
        r.send_raw(raw)
        counters_mc.peer_add(peer, "received")
        log.info("from %s MeshCore %s %s (%d hops): put on air", frm, p["route"], p["type"], p["hops"])
    except Exception as e:
        counters_mc.peer_add(peer, "blocked_recv", "radio_error")
        log.warning("from %s MeshCore %s: the radio did not take it (%s)", frm, p["type"], e)


# ───────────────────────── map data (home page, network overviews) ─────────────────────────
_srv_cache = {}


def server_json(path, max_age=30):
    """A public JSON page of the Ura server (same pinned certificate as the hub link), cached for a short while."""
    hit = _srv_cache.get(path)
    if hit and time.time() - hit[0] < max_age:
        return hit[1]
    srv = cfg.get()["server"]
    if not (srv["address"] and srv["fingerprint"]):
        return None
    host = srv["address"].rpartition(":")[0]
    url = f"https://{host}:{srv.get('web_port') or 8443}{path}"
    ctx = ssl.create_default_context(); ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE
    try:
        resp = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": TILE_UA}), timeout=6, context=ctx)
        if fp_of(resp.fp.raw._sock.getpeercert(binary_form=True)) != srv["fingerprint"]:
            return hit[1] if hit else None
        data = json.loads(resp.read())
        _srv_cache[path] = (time.time(), data)
        return data
    except Exception:
        return hit[1] if hit else None


async def _map_req():
    link.map_event.clear()
    if not await link.send({"t": "map_req"}):
        return False
    try:
        await asyncio.wait_for(link.map_event.wait(), 4)
        return True
    except asyncio.TimeoutError:
        return False


def map_from_server():
    """The linked hubs and their nodes as the server has them: asked over the hub connection (cached 20 s); the
    server's web page is only a fallback (older servers)."""
    md = link.map_data
    if not md or time.time() - md["t"] > 20:
        try:
            run_coro(_map_req(), timeout=6)
        except Exception:
            pass
        md = link.map_data
    if md and time.time() - md["t"] < 300:
        return md["nodes"], md["hubs"]
    return server_json("/api/public/nodes") or [], server_json("/api/public/hubs") or []


def map_payload():
    """Everything the maps show: this hub, its own nodes (from its radios, live), the linked hubs and THEIR nodes
    (as the server has them), plus a small statistic per network."""
    c = cfg.get()
    peers = set(active_peers())
    share = c["share_positions_on_map"]
    local = []
    r = mt_radio()
    if r is not None and r.iface is not None:
        for n in r.nodes(True):
            if n.get("own") or not (origins.map.get(n["id"])):
                local.append(dict(n, net="mt"))
    m = mc_radio()
    if m is not None and m.ser is not None and m.self_info:
        local += [dict(n, net="mc") for n in m.nodes(True)]
    nodes_srv, hubs_srv = map_from_server()
    remote = [n for n in nodes_srv if n.get("hub") in peers]
    partners = [{"id": h["id"], "code": h.get("code"), "name": h.get("name"), "lat": h.get("lat"), "lon": h.get("lon"),
                 "online": h.get("online"), "last_seen": h.get("last_seen")} for h in hubs_srv if h.get("id") in peers]
    pos = r.own_position() if r else None
    me = {"code": f"{c['hub']['country']}-{c['hub']['city']}", "name": c["hub"]["name"],
          "lat": c["hub"].get("lat") if c["hub"].get("lat") is not None else (pos or {}).get("lat"),
          "lon": c["hub"].get("lon") if c["hub"].get("lon") is not None else (pos or {}).get("lon")}
    g, gm = counters.snapshot()["global"], counters_mc.snapshot()["global"]
    stats = {"links": len(peers), "links_online": sum(1 for h in partners if h.get("online")),
             "mt": {"local": sum(1 for n in local if n["net"] == "mt"), "remote": sum(1 for n in remote if n.get("net") == "mt"),
                    "sent": g.get("sent", 0), "received": g.get("received", 0), "radio": bool(r and r.iface is not None)},
             "mc": {"local": sum(1 for n in local if n["net"] == "mc"), "remote": sum(1 for n in remote if n.get("net") == "mc"),
                    "sent": gm.get("sent", 0), "received": gm.get("received", 0), "radio": bool(m and m.ser is not None)},
             "share_positions": share, "server": bool(nodes_srv or hubs_srv)}
    md = link.map_data or {}
    return {"me": me, "local": local, "remote": remote, "partners": partners, "stats": stats,
            "offline_grey_h": md.get("offline_grey_h") or 24, "offline_hide_days": md.get("offline_hide_days") or 3}


# ───────────────────────── "forget my nodes" between hubs (deliberate removals only) ─────────────────────────
def forget_nodes_from(origin, net, why):
    """Delete from this hub's radio the nodes of network `net` that came from hub `origin` (and their origin records).
    Only for deliberate removals at the other side — after an outage nothing is deleted (keys stay, DMs keep working)."""
    if net == "mc":
        keys = [k[3:] for k, v in list(origins.map.items()) if v == origin and k.startswith("mc:")]
        for k in keys:
            origins.map.pop("mc:" + k, None)
            mc_remote_keys.discard(k)
        origins.save()
        mr = mc_radio()
        if keys and mr is not None and mr.ser is not None:
            def go():
                done, left = mr.remove_contacts([k for k in keys if k in mr.contacts])
                log.info("MeshCore: %d node(s) of %s deleted from the radio (%s)", done, hub_code(origin), why)
            threading.Thread(target=go, daemon=True).start()
        else:
            log.info("MeshCore: %d node record(s) of %s forgotten (%s)", len(keys), hub_code(origin), why)
        return len(keys)
    ids = [k for k, v in list(origins.map.items()) if v == origin and not k.startswith("mc:")]
    for k in ids:
        origins.map.pop(k, None)
    origins.save()
    r = mt_radio()
    if ids and r is not None and r.iface is not None:
        def go():
            done = 0
            for nid in ids:
                if r.iface is None:
                    break
                if nid in (r.iface.nodes or {}):
                    try:
                        r.iface.localNode.removeNode(nid)
                        drop_from_cache(r.iface, nid)
                        done += 1
                    except Exception as e:
                        log.warning("could not remove node %s from the radio: %s", nid, e)
                    time.sleep(2)               # the radio skips delete commands that come too fast
            log.info("Meshtastic: %d node(s) of %s deleted from the radio (%s)", done, hub_code(origin), why)
        threading.Thread(target=go, daemon=True).start()
    else:
        log.info("Meshtastic: %d node record(s) of %s forgotten (%s)", len(ids), hub_code(origin), why)
    return len(ids)


def hub_code(hid):
    return next((h.get("code") for h in link.directory if h["id"] == hid), hid)


def send_forget(net, peers=None, origin=None, path=None, why="radio removed"):
    """Tell linked hubs: forget the nodes of `net` that came from `origin` (default: this hub). Sealed end to end."""
    origin = origin or my_id()
    path = path or [my_id()]
    boxes = {}
    for peer in (peers if peers is not None else active_peers()):
        if peer in path:
            continue
        keys, state = identity.keys_for(peer)
        if keys is None:
            continue
        inner = json.dumps({"ctl": "forget_net", "net": net, "origin": origin, "path": path, "why": why}).encode()
        boxes[peer] = base64.b64encode(seal(keys, inner)).decode()
    if boxes:
        asyncio.run_coroutine_threadsafe(link.send({"t": "mesh", "net": "ctl", "boxes": boxes}), loop)
        log.info("told %s: forget the %s nodes of %s (%s)", ", ".join(hub_code(x) for x in boxes),
                 "MeshCore" if net == "mc" else "Meshtastic", hub_code(origin), why)


def ctl_receive_box(peer, box):
    """A control message from a linked hub (sealed): currently only "forget the nodes of network X from hub Y"."""
    keys, state = identity.keys_for(peer)
    if keys is None:
        return
    try:
        inner, nonce = open_box(keys, box, max_age=adv("replay_window_s"))
        m = json.loads(inner)
    except Exception:
        return
    if seen_cache.seen(b"n" + nonce) or m.get("ctl") != "forget_net" or m.get("net") not in ("mt", "mc"):
        return
    path = [str(x)[:20] for x in (m.get("path") or [peer])][:16]
    origin = str(m.get("origin") or peer)[:20]
    if my_id() in path:
        return
    forget_nodes_from(origin, m["net"], f"{hub_code(peer)}: {str(m.get('why') or '')[:60]}")
    # pass it on to hubs further away that may have the same nodes (multi-hop)
    tr = cfg.get().get("transit_mc" if m["net"] == "mc" else "transit") or {}
    if tr.get("enabled"):
        send_forget(m["net"], peers=[p_ for p_ in active_peers() if p_ != peer], origin=origin, path=path + [my_id()],
                    why=str(m.get("why") or "")[:60])


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
            "mc_radio": mc_radio().info() if mc_radio() else None,
            "mc_counters": counters_mc.snapshot(),
            "mc_airtime": {"used_hour": mc_radio().air_used(3600) if mc_radio() else 0, "used_day": mc_radio().air_used(86400) if mc_radio() else 0,
                           "limit": cfg.get().get("airtime_mc") or {"pct_hour": 10.0, "pct_day": 0.0}},
            "counters": counters.snapshot(), "airtime": {"used_hour": counters.air_used(3600), "used_day": counters.air_used(86400),
                                                       "limits": c["airtime"]},
            "links": [dict(l, e2e=identity.safety(l["peer"])) for l in link.links], "directory": link.directory,
            "my_key": safety_code(identity.public, identity.public)[:11], "radio_stats": r.stats if r else {},
            "radio_position": r.own_position() if r else None, "node_max_age_days": adv("node_max_age_days")}


class Web(http.server.BaseHTTPRequestHandler):
    def handle(self):
        try:
            super().handle()
        except (BrokenPipeError, ConnectionResetError, ssl.SSLError):
            pass                                  # the browser went away while a page was being sent — nothing to report
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
                                   "started": int(STARTED), "setup_skipped": bool(cfg.get().get("setup_skipped")), "setup_done": bool(cfg.get().get("setup_done")),
                                   "password_min": adv("password_min"), "page_refresh_s": adv("page_refresh_s")})
            if not self.authed():
                return self.reply({"error": "login"}, 401)
            if p == "/api/status":
                return self.reply(status_payload())
            if p == "/api/logs":
                q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                n = max(10, min(20000, int((q.get("lines") or ["500"])[0] or 500)))
                lines = log_tail(DATA_DIR, n * 4 if q.get("net") else n, (q.get("level") or [""])[0], (q.get("q") or [""])[0])
                net = (q.get("net") or [""])[0]
                if net == "mc":                            # MeshCore lines only
                    lines = [l for l in lines if "MeshCore" in l][-n:]
                elif net == "mt":                          # everything else (Meshtastic radio, its traffic, the hub)
                    lines = [l for l in lines if "MeshCore" not in l][-n:]
                return self.reply({"files": log_files(DATA_DIR), "started": int(STARTED), "version": VERSION, "lines": lines})
            if p == "/api/logs/file":
                q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                name = (q.get("name") or [""])[0]
                if name not in [f["name"] for f in log_files(DATA_DIR)]:
                    return self.reply({"error": "not_found"}, 404)
                data = open(os.path.join(DATA_DIR, "logs", name), "rb").read()
                self.send_response(200)
                for k, v in SEC_HEADERS.items():
                    self.send_header(k, v)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Disposition", f'attachment; filename="{name}.txt"')
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                return self.wfile.write(data)
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
            if p == "/api/factory_reset":
                return self.reply(reset_state)
            if p == "/api/map":
                return self.reply(map_payload())
            if p == "/api/mc/status":
                r = mc_radio()
                return self.reply({"radio": r.info() if r else None, "result": mc_result})
            if p == "/api/mc/messages":
                r = mc_radio()
                return self.reply(list(reversed(r.messages)) if r else [])
            if p == "/api/mc/contacts":
                r = mc_radio()
                return self.reply(sorted((r.contacts.values() if r else []), key=lambda x: -(x.get("last_advert") or 0)))
            if p == "/api/radio/result":
                return self.reply(radio_result)
            if p == "/api/radio/settings":
                r = mt_radio()
                if not r or r.iface is None:
                    return self.reply({"error": "no_radio"}, 400)
                return self.reply(r.settings())
            if p == "/api/ports":
                paths = sorted(glob.glob("/dev/serial/by-id/*")) or sorted(glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*"))
                if os.environ.get("URA_TEST_RADIO"):        # tests: only simulated ports, never a real radio
                    paths = ["/dev/fake", "/dev/fake-meshcore", "/dev/fake-unknown"]
                r = mt_radio()
                live = r.conf.get("address") if r is not None and r.iface is not None else None
                mcr = mc_radio()
                mc_live = mcr.conf.get("address") if mcr is not None and mcr.ser is not None and mcr.self_info else None
                def one(path):
                    if path == mc_live:                   # the hub's MeshCore radio: from its open connection
                        return {"kind": "meshcore", "name": mcr.self_info.get("name") or "", "id": "", "hw": mcr.device.get("model") or "",
                                "in_use": True, "path": path, "dev": os.path.basename(os.path.realpath(path)), "usb": usb_label(path)}
                    if path == live:                      # the hub is using it: ask the open connection, not the port
                        i = r.info()
                        info = {"kind": "meshtastic", "name": i.get("name") or "", "id": i.get("node_id") or "", "hw": i.get("hw") or "", "in_use": True}
                    else:
                        info = identify_port(path)
                    return dict(info, path=path, dev=os.path.basename(os.path.realpath(path)), usb=usb_label(path))
                def quick(path):                          # instant: what the computer says + what is already known
                    if path in (live, mc_live):
                        return one(path)
                    known = _ident_cache.get(ident_key(path))
                    return dict(known or {"kind": None}, path=path, dev=os.path.basename(os.path.realpath(path)), usb=usb_label(path))
                if "check=" not in self.path:
                    return self.reply([quick(x) for x in paths])
                want = (urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("check") or [""])[0]
                if want not in paths:
                    return self.reply({"error": "not_found"}, 404)
                return self.reply(one(want))
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
        if p == "/api/factory_reset":
            if b.get("confirm") != "RESET":
                return self.reply({"error": "confirm"}, 400)
            ip = self.client_address[0]                  # the current hub password is required (counts like a login)
            if locked_out(ip):
                return self.reply({"error": "locked"}, 429)
            time.sleep(0.5)
            if not check_pw(str(b.get("password") or ""), cfg.get()["web_password"]):
                login_fail.setdefault(ip, []).append(time.time())
                log.warning("factory reset refused: wrong hub password (from %s)", ip)
                return self.reply({"error": "wrong_password"}, 403)
            log.info("factory reset confirmed with the hub password (from %s)", ip)
            if reset_state.get("running"):
                return self.reply({"ok": True, "already": True})
            threading.Thread(target=factory_reset, daemon=True).start()
            return self.reply({"ok": True})
        if p == "/api/wizard":                       # use / skip the setup wizard
            def upd(d):
                if "skip" in b:
                    d["setup_skipped"] = bool(b["skip"])
                if b.get("done"):
                    d["setup_done"] = True
            cfg.update(upd)
            return self.reply({"ok": True})
        if p == "/api/program":
            act = b.get("action")
            if act not in ("restart", "stop"):
                return self.reply({"error": "bad_action"}, 400)
            def release():
                for r in list(radios.values()) + list(mc_radios.values()):
                    r.close()
            program_action(act, release)
            return self.reply({"ok": True, "action": act})
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
                            d["hub"][k] = approx(h[k])          # approximate (≈ 1 km), never exact
                        except ValueError:
                            pass
                if "share_positions_on_map" in b:
                    d["share_positions_on_map"] = bool(b["share_positions_on_map"])
                for k_ in ("airtime", "airtime_mc"):
                    if k_ in b:
                        d[k_] = {"pct_hour": max(0.0, min(100.0, float(b[k_].get("pct_hour") or 0))),
                                 "pct_day": max(0.0, min(100.0, float(b[k_].get("pct_day") or 0)))}
                if "defaults" in b:
                    d["defaults"] = clean_rules(b["defaults"])
                for k_ in ("transit", "transit_mc"):
                    if k_ in b:
                        hops = int(b[k_].get("max_hops") or 2)
                        if not 2 <= hops <= 8:
                            raise ValueError("max_hops")
                        d[k_] = {"enabled": bool(b[k_].get("enabled")), "max_hops": hops}
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
            for peer in set(cfg.get()["rules"]) | set(cfg.get()["peer_keys"]) | origins.peers():
                forget_peer(peer, everything=True)      # no links left: every partner and remote node goes
            def clear(d):                      # as if this server was never used: no address, no trusted fingerprint,
                d["server"].update(address="", fingerprint="", hub_id="", key="", status="")   # no registration,
                d["rules"], d["peer_keys"] = {}, {}                                              # no links, no keys
                d["setup_done"] = False                                                          # a fresh start: wizard again
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
            before = cfg.rules_for(peer)
            was = {"mt": before["send"].get("on", True) or before["receive"].get("on", True),
                   "mc": mc_rule(peer, "send").get("on", True) or mc_rule(peer, "receive").get("on", True)}
            now_ = {"mt": rules["send"]["on"] or rules["receive"]["on"], "mc": rules["mc"]["send"]["on"] or rules["mc"]["receive"]["on"]}
            cfg.update(lambda d: d["rules"].__setitem__(peer, rules))
            for net_ in ("mt", "mc"):
                if was[net_] and not now_[net_]:          # switched off for this link: no more of that network both ways
                    send_forget(net_, peers=[peer], why=("MeshCore" if net_ == "mc" else "Meshtastic") + " switched off for this link")
                    forget_nodes_from(peer, net_, ("MeshCore" if net_ == "mc" else "Meshtastic") + " switched off for the link")
            run_coro(link.push_info())
            return self.reply({"ok": True})
        if p == "/api/radio":
            rc = b.get("radio") or {}
            transport = "tcp" if rc.get("transport") == "tcp" else "serial"
            addr = str(rc.get("address") or "").strip()
            found = None
            if addr and transport == "serial":
                r = mt_radio()
                if r is not None and r.iface is not None and r.conf.get("address") == addr:
                    found = {"kind": "meshtastic", "name": r.info().get("name") or "", "id": r.info().get("node_id") or ""}
                else:
                    k_ = ident_key(addr)
                    found = ({"kind": "missing", "name": "", "id": "", "hw": ""} if k_ is None
                             else _ident_cache.get(k_) or {"kind": "meshtastic?"})
                if found["kind"] not in ("meshtastic", "meshtastic?"):
                    log.warning("radio not saved: %s on %s — the hub works only with a Meshtastic radio", describe_kind(found), addr)
                    loop.call_soon_threadsafe(apply_radios)
                    return self.reply({"error": "not_meshtastic", "found": found, "text": describe_kind(found)}, 400)
            others = lambda d: [x for x in d["radios"] if x.get("net", "mt") != "mt"]      # a MeshCore radio stays
            if not addr:
                cfg.update(lambda d: d.update(radios=others(d)))
            else:
                cfg.update(lambda d: d.update(radios=others(d) + [{"id": "r1", "net": "mt", "transport": transport, "address": addr,
                                                                   "enabled": bool(rc.get("enabled", True))}]))
            global radio_result
            if found and found["kind"] == "meshtastic" and found.get("name") and r is not None and r.iface is not None and r.conf.get("address") == addr:
                radio_result = {"address": addr, "state": "connected", "found": found, "t": time.time()}
            elif addr and transport == "serial":
                radio_result = {"address": addr, "state": "connecting", "t": time.time()}
                found = None
            state_now = radio_result.get("state")
            loop.call_soon_threadsafe(apply_radios)
            if addr:
                log.info("radio chosen: %s — connecting", addr)
            return self.reply({"ok": True, "found": found, "state": state_now})
        if p == "/api/mc/radio":                     # choose the MeshCore radio (USB)
            addr = str((b.get("radio") or {}).get("address") or "").strip()
            if not addr:
                return self.reply({"error": "no_address"}, 400)
            r = mt_radio()
            if r is not None and r.conf.get("address") == addr:
                return self.reply({"error": "not_meshcore", "found": {"kind": "meshtastic", "name": r.info().get("name") or ""},
                                   "text": "this port is the hub's Meshtastic radio"}, 400)
            k_ = ident_key(addr)
            found = {"kind": "missing", "name": ""} if k_ is None else _ident_cache.get(k_) or {"kind": "meshcore?"}
            if found["kind"] not in ("meshcore", "meshcore?"):
                log.warning("MeshCore radio not saved: %s on %s", describe_kind(found), addr)
                return self.reply({"error": "not_meshcore", "found": found, "text": describe_kind(found)}, 400)
            global mc_result
            mc_result = {"address": addr, "state": "connecting", "t": time.time()}
            cfg.update(lambda d: d.__setitem__("radios", [x for x in d["radios"] if x.get("net") != "mc"]
                                               + [{"id": "m1", "net": "mc", "transport": "serial", "address": addr, "enabled": True}]))
            loop.call_soon_threadsafe(apply_radios)
            log.info("MeshCore radio chosen: %s — connecting", addr)
            return self.reply({"ok": True, "state": "connecting"})
        if p == "/api/mc/prepare":
            r = mc_radio()
            if r is None or r.ser is None:
                return self.reply({"error": "no_radio"}, 400)
            name = str(b.get("name") or "").strip()[:31]
            try:
                r.prepare(name or None)
            except Exception as e:
                return self.reply({"error": "radio", "detail": str(e)}, 400)
            return self.reply({"ok": True, "radio": r.info()})
        if p == "/api/mc/settings":
            r = mc_radio()
            if r is None or r.ser is None:
                return self.reply({"error": "no_radio"}, 400)
            try:
                r.set_settings(b.get("values") or {})
            except ValueError as e:
                return self.reply({"error": "invalid", "fields": [str(e)]}, 400)
            except Exception as e:
                return self.reply({"error": "radio", "detail": str(e)}, 400)
            return self.reply({"ok": True, "radio": r.info()})
        if p == "/api/mc/forget":                    # delete contacts from the MeshCore radio (they are learned again when heard)
            r = mc_radio()
            if r is None or r.ser is None:
                return self.reply({"error": "no_radio"}, 400)
            keys = [str(k).lower() for k in (b.get("keys") or []) if re.match(r"^[0-9a-fA-F]{64}$", str(k))]
            for k in keys:
                origins.map.pop("mc:" + k, None)
            origins.save()
            done, left = r.remove_contacts(keys)
            log.info("MeshCore: %d contact(s) deleted from the radio by the operator", done)
            link.kick()
            return self.reply({"ok": True, "deleted": done, "left": left})
        if p == "/api/mc/remove":                    # forget the MeshCore radio; the Meshtastic one stays
            cfg.update(lambda d: d.__setitem__("radios", [x for x in d["radios"] if x.get("net") != "mc"]))
            for k_ in [k for k in origins.map if k.startswith("mc:")]:     # what came over links for this radio goes too
                origins.map.pop(k_, None)
            origins.save()
            mc_remote_keys.clear()
            loop.call_soon_threadsafe(apply_radios)
            if link.writer is not None:
                run_coro(link.send({"t": "nodes", "net": "mc", "nodes": []}))
            send_forget("mc", why="MeshCore radio removed")
            log.info("MeshCore radio removed from the hub by the operator (its nodes on the server deleted too)")
            return self.reply({"ok": True})
        if p == "/api/radio/remove":                 # forget the radio completely; it can be connected again as new
            def clear(d):
                d["radios"] = [x for x in d["radios"] if x.get("net", "mt") != "mt"]      # only the Meshtastic radio
                d["channels_saved"] = []
            cfg.update(clear)
            with origins.lock:
                for k_ in [k for k in origins.map if not k.startswith("mc:")]:   # only the Meshtastic ones
                    origins.map.pop(k_, None)
                origins.save()
            loop.call_soon_threadsafe(apply_radios)
            if link.writer is not None:            # its nodes leave the server map too (an empty report deletes them)
                run_coro(link.send({"t": "nodes", "net": "mt", "nodes": []}))
            send_forget("mt", why="Meshtastic radio removed")
            log.info("radio removed from the hub by the operator (settings, saved channels, node origins and its nodes on the server forgotten)")
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
        if p in ("/api/radio/channels_import", "/api/radio/channels_restore", "/api/radio/channels_keep"):
            r = mt_radio()
            if not r or r.iface is None:
                return self.reply({"error": "no_radio"}, 400)
            try:
                if p.endswith("import"):
                    res = r.import_channels(b.get("url"), bool(b.get("primary")))
                    r.save_channels()
                    return self.reply({"ok": True, **res})
                if p.endswith("restore"):
                    r.restore_channels()
                else:
                    r.save_channels()
            except ValueError as e:
                return self.reply({"error": str(e)}, 400)
            return self.reply({"ok": True})
        if p == "/api/radio/prepare":
            r = mt_radio()
            if not r:
                return self.reply({"error": "no_radio"}, 400)
            r.prepare()
            r.save_channels()
            return self.reply({"ok": True})
        if p == "/api/test/fake" and TEST_MODE:        # tests only: make the simulated radio do something
            r = mt_radio()
            getattr(r.iface, "test_" + str(b.get("call")))(**(b.get("args") or {}))
            if b.get("reconnect"):
                r._drop(r.iface, "test: read the radio again", False)
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
        if p == "/api/radio/reset_nodes":            # clear the radio's node list, then let it fill up again
            r = mt_radio()
            if not r or r.iface is None:
                return self.reply({"error": "no_radio"}, 400)
            keep = dict(r.own_fix) if r.own_fix else None     # the radio forgets its own position too: write it back
            gps = r.iface.localNode.localConfig.position.gps_mode == config_pb2.Config.PositionConfig.GpsMode.ENABLED
            r.iface.localNode.resetNodeDb()
            drop_from_cache(r.iface)
            with origins.lock:
                for k_ in [k for k in origins.map if not k.startswith("mc:")]:   # only the Meshtastic ones
                    origins.map.pop(k_, None)
                origins.save()
            log.info("radio node list cleared by the operator; asking neighbours to answer")
            def refill():
                time.sleep(5)
                rr = mt_radio()
                if rr and keep and not gps:
                    try:
                        rr.set_fixed({"enabled": True, "lat": keep["lat"], "lon": keep["lon"], "alt": keep.get("alt") or 0})
                    except Exception as e:
                        log.warning("could not write the radio's position back: %s", e)
                if rr:
                    rr.announce(True)
            threading.Thread(target=refill, daemon=True).start()
            return self.reply({"ok": True})
        if p == "/api/radio/forget_node":            # e.g. a node that was reset and has a new key
            r = mt_radio()
            node = str(b.get("node") or "")
            if not r or r.iface is None:
                return self.reply({"error": "no_radio"}, 400)
            if not re.match(r"^!?[0-9a-fA-F]{8}$", node):
                return self.reply({"error": "bad_node"}, 400)
            node = "!" + node.lstrip("!").lower()
            r.iface.localNode.removeNode(node)
            drop_from_cache(r.iface, node)
            origins.map.pop(node, None)
            log.info("radio forgot node %s (it will be learned again with its current key)", node)
            return self.reply({"ok": True})
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
                  "positions": bool(x.get("positions")), "groups": [str(g)[:30] for g in (x.get("groups") or [])][:8],
                  "mc": bool(x.get("mc", True))}                  # MeshCore lane on this link
        if d == "send":
            out[d]["onward_to"] = [str(h)[:20] for h in (x.get("onward_to") or [])][:50]
            out[d]["reach"] = rule_reach(x)
            out[d]["transit"] = bool(x.get("transit", True))
        else:
            out[d]["from_beyond"] = bool(x.get("from_beyond", True))
    m = r.get("mc") or {}
    out["mc"] = {}
    for d in ("send", "receive"):
        x = m.get(d)
        if x is None:                                    # older rules: one MeshCore switch per direction
            x = dict(MC_RULE_DEFAULT, on=bool((r.get(d) or {}).get("mc", True)))
        out["mc"][d] = {k: bool(x.get(k, v)) for k, v in MC_RULE_DEFAULT.items() if k not in ("groups", "reach")}
        out["mc"][d]["groups"] = [str(g)[:32] for g in (x.get("groups") or [])][:40]
        out["mc"][d]["reach"] = max(0, min(REACH_ANY, int(x.get("reach") or 0)))
    for d in ("send", "receive"):
        out[d].pop("mc", None)
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
    log_setup(DATA_DIR)
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
