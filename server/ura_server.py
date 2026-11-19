#!/usr/bin/env python3
"""ura-server: public rendezvous for Ura hubs.

* Hubs connect OUT over TLS (default port 8100) and exchange JSON lines.
* The server relays mesh frames ONLY along links that both hubs accepted.
  Payloads stay encrypted; the server never decodes or stores them.
* The website (default port 8443, HTTPS) shows hubs, their nodes on a map,
  node and hub pages, link statistics, shortcodes and complaints.
  Admin: approve/remove hubs, handle complaints.

Python standard library only. Settings: environment variables (see README).
"""
import asyncio, base64, hashlib, hmac, http.server, json, logging, os, re, secrets, socketserver
import sqlite3, ssl, subprocess, threading, time, urllib.parse, urllib.request
import socket

from acme import Acme, parse_client_hello, ACME_TLS_ALPN

VERSION = "0.3.0"
DATA_DIR = os.environ.get("URA_DATA", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"))
HUB_PORT = int(os.environ.get("URA_PORT", "8100"))
WEB_PORT = int(os.environ.get("URA_WEB_PORT", "8443"))
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
COMMON_DIR = os.environ.get("URA_COMMON", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "common"))

# Every operational value is a setting (Admin → Advanced settings). Only the data folder and the two
# ports are startup options. key: (default, min, max); strings/bools have None limits.
ADV_SPEC = {
    "registrations_open":   (True, None, None),   # accept new hub registrations
    "acme_enabled":         (False, None, None),  # get a free Let's Encrypt certificate for the website
    "acme_domain":          ("", None, None),     # the website's public name, e.g. ura.example.org
    "acme_email":           ("", None, None),     # optional contact for Let's Encrypt (expiry warnings)
    "acme_staging":         (False, None, None),  # test with Let's Encrypt's staging service (not trusted by browsers)
    "project_url":          ("https://github.com/ximi87/Ura-mesh", None, None),
    "install_guide_url":    ("https://github.com/ximi87/Ura-mesh/blob/main/docs/INSTALL-HUB.md", None, None),
    "node_max_age_days":    (7, 1, 90),           # nodes older than this are not shown
    "max_nodes_per_report": (2000, 10, 20000),
    "relay_rate_per_s":     (30, 1, 1000),        # sealed boxes per second per hub (flood limit)
    "relay_burst":          (200, 1, 10000),
    "max_box_bytes":        (3000, 300, 60000),
    "stats_retention_days": (365, 7, 3650),
    "complaints_per_hour":  (5, 1, 100),          # per sender address
    "complaint_min_chars":  (10, 1, 500),
    "complaint_max_chars":  (4000, 100, 20000),
    "session_hours":        (12, 1, 720),
    "lockout_attempts":     (5, 3, 50),
    "lockout_minutes":      (15, 1, 1440),
    "password_min":         (8, 8, 64),
    "tile_upstream":        ("https://tile.openstreetmap.org/{z}/{x}/{y}.png", None, None),
    "tile_contact":         ("https://github.com/ximi87/Ura-mesh", None, None),   # sent to the tile server (its policy asks for it)
    "tile_cache_days":      (14, 1, 365),
    "tile_backoff_s":       (60, 5, 3600),
}

log = logging.getLogger("ura-server")


# ───────────────────────── database ─────────────────────────

class DB:
    def __init__(self, path):
        self.lock = threading.RLock()
        self.c = sqlite3.connect(path, check_same_thread=False)
        self.c.row_factory = sqlite3.Row
        self.c.executescript("""
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE IF NOT EXISTS hubs(
            id TEXT PRIMARY KEY, key TEXT NOT NULL, name TEXT, email TEXT, email_verified INTEGER DEFAULT 0,
            country TEXT, city TEXT, code TEXT, lat REAL, lon REAL, description TEXT,
            status TEXT DEFAULT 'pending', created INTEGER, approved INTEGER, last_seen INTEGER,
            version TEXT, rules TEXT, radios TEXT);
        CREATE TABLE IF NOT EXISTS links(
            id INTEGER PRIMARY KEY AUTOINCREMENT, a TEXT, b TEXT, requested_by TEXT,
            a_ok INTEGER DEFAULT 0, b_ok INTEGER DEFAULT 0, state TEXT DEFAULT 'pending',
            created INTEGER, activated INTEGER);
        CREATE TABLE IF NOT EXISTS nodes(
            hub TEXT, net TEXT, id TEXT, name TEXT, short TEXT, hw TEXT, role TEXT,
            lat REAL, lon REAL, alt REAL, last_heard INTEGER, hops INTEGER, updated INTEGER,
            PRIMARY KEY(hub, net, id));
        CREATE TABLE IF NOT EXISTS stats(
            src TEXT, dst TEXT, net TEXT, hour INTEGER, frames INTEGER DEFAULT 0, bytes INTEGER DEFAULT 0,
            PRIMARY KEY(src, dst, net, hour));
        CREATE TABLE IF NOT EXISTS complaints(
            id INTEGER PRIMARY KEY AUTOINCREMENT, created INTEGER, email TEXT, subject_type TEXT,
            subject_id TEXT, text TEXT, status TEXT DEFAULT 'open', resolution TEXT, updated INTEGER);
        """)
        cols = [r[1] for r in self.c.execute("PRAGMA table_info(hubs)")]
        if "pubkey" not in cols:
            self.c.execute("ALTER TABLE hubs ADD COLUMN pubkey TEXT")
        for r in self.c.execute("SELECT id, key FROM hubs WHERE key NOT LIKE 'sha256:%'").fetchall():
            self.c.execute("UPDATE hubs SET key=? WHERE id=?", (key_hash(r[1]), r[0]))   # never keep hub keys in clear
        self.c.commit()

    def q(self, sql, args=()):
        with self.lock:
            return [dict(r) for r in self.c.execute(sql, args).fetchall()]

    def one(self, sql, args=()):
        r = self.q(sql, args)
        return r[0] if r else None

    def x(self, sql, args=()):
        with self.lock:
            cur = self.c.execute(sql, args)
            self.c.commit()
            return cur

    def setting(self, key, default=None):
        r = self.one("SELECT value FROM settings WHERE key=?", (key,))
        return r["value"] if r else default

    def set_setting(self, key, value):
        self.x("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
               (key, value))


db = None
loop = None
online = {}            # hub_id -> asyncio.StreamWriter
FINGERPRINT = ""


# ───────────────────────── helpers ─────────────────────────

def now():
    return int(time.time())


def adv(key):
    try:
        v = json.loads(db.setting("advanced") or "{}").get(key)
    except Exception:
        v = None
    return ADV_SPEC[key][0] if v is None else v


def clean_advanced(new):
    out, errors = {}, []
    for k, (default, lo, hi) in ADV_SPEC.items():
        if k not in new:
            continue
        v = new[k]
        try:
            v = bool(v) if isinstance(default, bool) else int(float(v)) if isinstance(default, int) else str(v).strip()[:300]
        except (TypeError, ValueError):
            errors.append(k)
            continue
        if lo is not None and not (lo <= v <= hi):
            errors.append(k)
        elif k == "tile_upstream" and not (v.startswith("https://") and all(x in v for x in ("{z}", "{x}", "{y}"))):
            errors.append(k)
        elif k == "acme_domain" and v and not re.match(r"^(?=.{4,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$", v.lower()):
            errors.append(k)
        elif k == "acme_email" and v and not EMAIL_RE.match(v):
            errors.append(k)
        elif k in ("project_url", "install_guide_url") and not re.match(r"^https://\S+$", v):
            errors.append(k)
        elif k == "tile_contact" and not re.match(r"^(https?://|mailto:)\S+$", v):
            errors.append(k)
        else:
            out[k] = v
    return out, errors


def key_hash(key):
    return "sha256:" + hashlib.sha256(str(key).encode()).hexdigest()


B64_KEY = re.compile(r"^[A-Za-z0-9+/]{43}=$")


def hash_pw(pw, salt=None):
    salt = salt or secrets.token_hex(16)
    h = hashlib.scrypt(pw.encode(), salt=salt.encode(), n=2 ** 14, r=8, p=1).hex()
    return f"{salt}${h}"


def check_pw(pw, stored):
    if not stored or "$" not in stored:
        return False
    salt, _ = stored.split("$", 1)
    return hmac.compare_digest(hash_pw(pw, salt), stored)


def clean(s, n=200):
    return str(s if s is not None else "").strip()[:n]


CODE_RE = re.compile(r"^[A-Z]{2,3}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def tls_files():
    crt, key = os.path.join(DATA_DIR, "tls.crt"), os.path.join(DATA_DIR, "tls.key")
    if not os.path.exists(crt):
        subprocess.run(["openssl", "req", "-x509", "-newkey", "ec", "-pkeyopt", "ec_paramgen_curve:P-256",
                        "-nodes", "-days", "3650", "-subj", "/CN=ura-server", "-keyout", key, "-out", crt],
                       check=True, capture_output=True)
        os.chmod(key, 0o600)
    der = ssl.PEM_cert_to_DER_cert(open(crt).read())
    fp = hashlib.sha256(der).hexdigest().upper()
    return crt, key, ":".join(fp[i:i + 2] for i in range(0, len(fp), 2))


def link_peer(link, hub):
    return link["b"] if link["a"] == hub else link["a"]


def active_peers(hub):
    rows = db.q("SELECT * FROM links WHERE state='active' AND (a=? OR b=?)", (hub, hub))
    return {link_peer(r, hub) for r in rows}


def hub_public(h):
    return {"id": h["id"], "name": h["name"], "code": h["code"], "country": h["country"], "city": h["city"],
            "lat": h["lat"], "lon": h["lon"], "description": h["description"], "online": h["id"] in online,
            "last_seen": h["last_seen"], "approved": h["approved"], "version": h["version"],
            "rules": json.loads(h["rules"] or "null"), "radios": json.loads(h["radios"] or "[]"),
            "pubkey": h["pubkey"], "e2e": bool(h["pubkey"])}


def links_for(hub):
    out = []
    for r in db.q("SELECT * FROM links WHERE state!='removed' AND (a=? OR b=?)", (hub, hub)):
        peer = db.one("SELECT id,name,code FROM hubs WHERE id=?", (link_peer(r, hub),)) or {}
        mine_ok = r["a_ok"] if r["a"] == hub else r["b_ok"]
        peer_ok = r["b_ok"] if r["a"] == hub else r["a_ok"]
        out.append({"id": r["id"], "peer": peer.get("id"), "peer_name": peer.get("name"),
                    "peer_code": peer.get("code"), "peer_online": peer.get("id") in online,
                    "state": r["state"], "requested_by": r["requested_by"],
                    "i_accepted": bool(mine_ok), "peer_accepted": bool(peer_ok),
                    "created": r["created"], "activated": r["activated"]})
    return out


def directory():
    return [hub_public(h) for h in db.q("SELECT * FROM hubs WHERE status='approved' ORDER BY code")]


# ───────────────────────── hub connections (asyncio) ─────────────────────────

async def send(writer, obj):
    writer.write((json.dumps(obj, separators=(",", ":")) + "\n").encode())
    await writer.drain()


async def push(hub, obj):
    w = online.get(hub)
    if w:
        try:
            await send(w, obj)
        except Exception as e:
            log.warning("push to %s failed: %s", hub, e)


async def tell_and_close(hub, obj):
    """Send a last message to a hub, then close its connection."""
    w = online.get(hub)
    if w:
        await push(hub, obj)
        w.close()


async def push_links(*hubs):
    for h in hubs:
        await push(h, {"t": "links", "links": links_for(h)})


async def push_directory():
    d = directory()
    for h in list(online):
        await push(h, {"t": "directory", "hubs": d})


def from_thread(coro):
    """Run a coroutine on the asyncio loop from a web thread."""
    asyncio.run_coroutine_threadsafe(coro, loop)


_last_cleanup = 0
live_events, live_seq, live_lock = [], 0, threading.Lock()   # recent relays for the live map (no content)


def count(src, dst, net, size):
    global _last_cleanup, live_seq
    with live_lock:
        live_seq += 1
        live_events.append({"seq": live_seq, "t": round(time.time(), 2), "src": src, "dst": dst, "net": net})
        del live_events[:-500]
    hour = now() // 3600 * 3600
    if time.time() - _last_cleanup > 3600:
        _last_cleanup = time.time()
        db.x("DELETE FROM stats WHERE hour < ?", (now() - adv("stats_retention_days") * 86400,))
    db.x("""INSERT INTO stats(src,dst,net,hour,frames,bytes) VALUES(?,?,?,?,1,?)
            ON CONFLICT(src,dst,net,hour) DO UPDATE SET frames=frames+1, bytes=bytes+excluded.bytes""",
         (src, dst, net, hour, size))


def num(v):
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def store_nodes(hub, net, nodes):
    t = now()
    with db.lock:
        db.c.execute("DELETE FROM nodes WHERE hub=? AND net=?", (hub, net))
        for n in nodes[:adv("max_nodes_per_report")]:
            nid = clean(n.get("id"), 40)
            lh = n.get("last_heard")
            if not nid or (lh and t - int(lh) > adv("node_max_age_days") * 86400):
                continue
            db.c.execute("""INSERT OR REPLACE INTO nodes(hub,net,id,name,short,hw,role,lat,lon,alt,last_heard,hops,updated)
                            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                         (hub, net, nid, clean(n.get("name"), 60), clean(n.get("short"), 10), clean(n.get("hw"), 40),
                          clean(n.get("role"), 30), num(n.get("lat")), num(n.get("lon")), num(n.get("alt")),
                          int(lh) if lh else None, n.get("hops") if isinstance(n.get("hops"), int) else None, t))
        db.c.commit()


async def handle_join(msg, writer):
    """A new hub asks to register. It gets an id + key and waits for the admin's approval."""
    country, city = clean(msg.get("country"), 3).upper(), clean(msg.get("city"), 3).upper()
    email, name = clean(msg.get("email"), 120), clean(msg.get("name"), 60)
    code = f"{country}-{city}"
    err = None
    if not adv("registrations_open"):
        err = "registrations_closed"
    elif not name:
        err = "name_required"
    elif not EMAIL_RE.match(email):
        err = "email_required"
    elif not (CODE_RE.match(country) and CODE_RE.match(city)):
        err = "code_invalid"
    elif db.one("SELECT 1 FROM hubs WHERE code=? AND status!='removed'", (code,)):
        err = "code_taken"
    if err:
        await send(writer, {"t": "join_refused", "reason": err})
        return
    hub_id, key = "h_" + secrets.token_hex(6), secrets.token_hex(24)
    db.x("""INSERT INTO hubs(id,key,name,email,country,city,code,lat,lon,description,status,created)
            VALUES(?,?,?,?,?,?,?,?,?,?, 'pending', ?)""",
         (hub_id, key_hash(key), name, email, country, city, code, num(msg.get("lat")), num(msg.get("lon")),
          clean(msg.get("description"), 500), now()))
    log.info("join request %s %s (%s)", hub_id, name, code)
    await send(writer, {"t": "joined", "hub": hub_id, "key": key, "status": "pending"})


async def handle(reader, writer):
    peer = writer.get_extra_info("peername")
    hub_id = None
    try:
        line = await asyncio.wait_for(reader.readline(), 15)
        if not line.strip():
            return                                         # e.g. a hub only checking the certificate fingerprint
        first = json.loads(line)
        if first.get("t") == "join":
            await handle_join(first, writer)
            return
        h = db.one("SELECT * FROM hubs WHERE id=?", (first.get("hub"),))
        if first.get("t") != "hello" or not h or not hmac.compare_digest(h["key"], key_hash(first.get("key"))):
            await send(writer, {"t": "refused", "reason": "unknown_hub"})
            return
        if h["status"] == "removed":
            await send(writer, {"t": "refused", "reason": "removed"})
            return
        hub_id = h["id"]
        info = first.get("info") or {}
        db.x("UPDATE hubs SET last_seen=?, version=?, rules=?, radios=?, pubkey=COALESCE(?, pubkey) WHERE id=?",
             (now(), clean(first.get("version"), 20), json.dumps(info.get("rules")),
              json.dumps(info.get("radios") or []), pubkey_of(info), hub_id))
        bucket = [time.time(), float(adv("relay_burst"))]
        old = online.pop(hub_id, None)
        if old:
            old.close()
        online[hub_id] = writer
        await send(writer, {"t": "welcome", "hub": hub_id, "status": h["status"], "server_version": VERSION,
                            "hubs": directory(), "links": links_for(hub_id)})
        log.info("hub %s (%s) online from %s, status %s", hub_id, h["name"], peer, h["status"])
        for p_ in active_peers(hub_id):
            await send(writer, {"t": "peer_nodes", "hub": p_, "ids": [r["id"] for r in db.q("SELECT id FROM nodes WHERE hub=?", (p_,))]})
        await push_directory()
        while line := await reader.readline():
            msg = json.loads(line)
            t = msg.get("t")
            status = (db.one("SELECT status FROM hubs WHERE id=?", (hub_id,)) or {}).get("status")
            if t == "ping":
                db.x("UPDATE hubs SET last_seen=? WHERE id=?", (now(), hub_id))
                await send(writer, {"t": "pong"})
            elif t == "info":
                info = msg.get("info") or {}
                db.x("UPDATE hubs SET rules=?, radios=?, pubkey=COALESCE(?, pubkey) WHERE id=?",
                     (json.dumps(info.get("rules")), json.dumps(info.get("radios") or []), pubkey_of(info), hub_id))
                await push_directory()                     # other hubs see changed rules at once
            elif t == "location":
                lat, lon = num(msg.get("lat")), num(msg.get("lon"))
                if lat is not None and lon is not None and -90 <= lat <= 90 and -180 <= lon <= 180:
                    db.x("UPDATE hubs SET lat=?, lon=? WHERE id=?", (lat, lon, hub_id))
                    await push_directory()
            elif t == "leave":
                await hub_leave(hub_id)
                break
            elif status != "approved":
                continue                                   # pending hubs: no nodes, links or traffic yet
            elif t == "nodes":
                store_nodes(hub_id, clean(msg.get("net"), 4) or "mt", msg.get("nodes") or [])
                ids = [r["id"] for r in db.q("SELECT id FROM nodes WHERE hub=?", (hub_id,))]
                for peer in active_peers(hub_id):          # linked hubs learn which nodes are this hub's
                    await push(peer, {"t": "peer_nodes", "hub": hub_id, "ids": ids})
            elif t == "link_request":
                await link_request(hub_id, clean(msg.get("to"), 20))
            elif t == "link_accept":
                await link_accept(hub_id, int(msg.get("link") or 0))
            elif t == "link_remove":
                await link_remove(hub_id, int(msg.get("link") or 0))
            elif t == "leave":
                await hub_leave(hub_id)
                break
            elif t == "mesh":
                # flood limit per hub (token bucket)
                tnow = time.time()
                bucket[1] = min(adv("relay_burst"), bucket[1] + (tnow - bucket[0]) * adv("relay_rate_per_s"))
                bucket[0] = tnow
                if bucket[1] < 1:
                    continue
                bucket[1] -= 1
                # only end-to-end sealed boxes are relayed; the server cannot open them
                allowed = active_peers(hub_id)
                for dst, box in (msg.get("boxes") or {}).items():
                    if dst in allowed and dst in online and isinstance(box, str) and len(box) * 3 // 4 <= adv("max_box_bytes"):
                        await push(dst, {"t": "mesh", "net": msg.get("net"), "from": hub_id, "box": box})
                        count(hub_id, dst, msg.get("net") or "mt", len(box) * 3 // 4)
    except Exception as e:
        log.warning("hub %s connection error: %s", hub_id or peer, e)
    finally:
        if hub_id and online.get(hub_id) is writer:
            del online[hub_id]
            log.info("hub %s offline", hub_id)
            await push_directory()
        writer.close()



# Map tiles: OpenStreetMap blocks anonymous browser requests; apps must identify themselves and cache.
tile_lock = threading.Semaphore(4)
tile_down_until = 0.0                                  # after a failure, don't make pages wait for a dead upstream


def get_tile(z, x, y):
    """Return PNG bytes for a tile from the disk cache or OpenStreetMap (None if unavailable)."""
    if not (0 <= z <= 19 and 0 <= x < 2 ** z and 0 <= y < 2 ** z):
        return None
    path = os.path.join(DATA_DIR, "tiles", str(z), str(x), f"{y}.png")
    global tile_down_until
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < adv("tile_cache_days") * 86400:
        return open(path, "rb").read()
    if time.time() < tile_down_until:
        return open(path, "rb").read() if os.path.exists(path) else None
    try:
        with tile_lock:
            req = urllib.request.Request(adv("tile_upstream").format(z=z, x=x, y=y),
                                         headers={"User-Agent": f"Ura-server/{VERSION} (+{adv('tile_contact')})"})
            data = urllib.request.urlopen(req, timeout=6).read()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path + ".tmp", "wb") as f:
            f.write(data)
        os.replace(path + ".tmp", path)
        return data
    except Exception as e:
        log.warning("tile %s/%s/%s: %s (pausing %s s)", z, x, y, e, adv("tile_backoff_s"))
        tile_down_until = time.time() + adv("tile_backoff_s")
        return open(path, "rb").read() if os.path.exists(path) else None


def pubkey_of(info):
    k = (info or {}).get("pubkey")
    return k if isinstance(k, str) and B64_KEY.match(k) else None


async def hub_leave(hub):
    """A hub forgets its registration: remove it, end ALL its links (partners are told), drop its nodes.
    Every other link in the network stays as it is."""
    db.x("UPDATE hubs SET status='removed' WHERE id=?", (hub,))
    db.x("DELETE FROM nodes WHERE hub=?", (hub,))
    for r in db.q("SELECT id FROM links WHERE state!='removed' AND (a=? OR b=?)", (hub, hub)):
        await link_remove(hub, r["id"])
    log.info("hub %s left the network (registration forgotten by its operator)", hub)
    await push_directory()


async def link_request(src, dst):
    if dst == src or not db.one("SELECT id FROM hubs WHERE id=? AND status='approved'", (dst,)):
        return
    existing = db.one("SELECT * FROM links WHERE state!='removed' AND ((a=? AND b=?) OR (a=? AND b=?))",
                      (src, dst, dst, src))
    if existing:
        await link_accept(src, existing["id"])
        return
    db.x("INSERT INTO links(a,b,requested_by,a_ok,b_ok,state,created) VALUES(?,?,?,1,0,'pending',?)",
         (src, dst, src, now()))
    log.info("link requested %s -> %s", src, dst)
    await push_links(src, dst)


async def link_accept(hub, link_id):
    r = db.one("SELECT * FROM links WHERE id=? AND state!='removed'", (link_id,))
    if not r or hub not in (r["a"], r["b"]):
        return
    db.x(f"UPDATE links SET {'a_ok' if r['a'] == hub else 'b_ok'}=1 WHERE id=?", (link_id,))
    r = db.one("SELECT * FROM links WHERE id=?", (link_id,))
    if r["a_ok"] and r["b_ok"] and r["state"] != "active":
        db.x("UPDATE links SET state='active', activated=? WHERE id=?", (now(), link_id))
        log.info("link %d active (%s <-> %s)", link_id, r["a"], r["b"])
    await push_links(r["a"], r["b"])


async def link_remove(hub, link_id):
    r = db.one("SELECT * FROM links WHERE id=?", (link_id,))
    if not r or (hub is not None and hub not in (r["a"], r["b"])):
        return
    db.x("UPDATE links SET state='removed' WHERE id=?", (link_id,))
    log.info("link %d removed by %s", link_id, hub or "admin")
    await push_links(r["a"], r["b"])


# ───────────────────────── website (thread) ─────────────────────────

sessions = {}          # token -> expiry
login_fail = {}        # ip -> [failure times]
SEC_HEADERS = {"X-Frame-Options": "DENY", "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer",
               "Content-Security-Policy": "default-src 'self'; img-src 'self' data:; "
                                          "style-src 'self' 'unsafe-inline'; script-src 'self'; frame-ancestors 'none'"}
complaint_times = {}   # ip -> [times]


class Web(http.server.BaseHTTPRequestHandler):
    server_version = "ura-server"

    def log_message(self, fmt, *args):
        pass

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > 100_000:
            raise ValueError("too large")
        return json.loads(self.rfile.read(n) or b"{}") if n else {}

    def reply(self, obj, code=200, headers=None):
        data = json.dumps(obj).encode()
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
        if path in ("", "/"):
            path = "/index.html"
        root = os.path.realpath(WEB_DIR)
        if path.startswith("/common/"):
            root, path = os.path.realpath(COMMON_DIR), path[len("/common"):]
        full = os.path.realpath(os.path.join(root, path.lstrip("/")))
        if not full.startswith(root + os.sep) or not os.path.isfile(full):
            full = os.path.join(os.path.realpath(WEB_DIR), "index.html")
        ctype = {".html": "text/html; charset=utf-8", ".js": "application/javascript; charset=utf-8",
                 ".css": "text/css; charset=utf-8", ".svg": "image/svg+xml", ".png": "image/png"}.get(
            os.path.splitext(full)[1], "application/octet-stream")
        data = open(full, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-cache")
        for k, v in SEC_HEADERS.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def is_admin(self):
        m = re.search(r"ura_admin=([A-Za-z0-9_-]+)", self.headers.get("Cookie") or "")
        return bool(m and sessions.get(m.group(1), 0) > time.time())

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        p, qs = u.path, urllib.parse.parse_qs(u.query)
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
            if p == "/api/public/info":
                return self.reply({"version": VERSION, "fingerprint": FINGERPRINT, "hub_port": HUB_PORT,
                                   "password_min": adv("password_min"), "registrations_open": adv("registrations_open"),
                                   "project_url": adv("project_url"), "install_guide_url": adv("install_guide_url"),
                                   "node_max_age_days": adv("node_max_age_days"), "complaint_min_chars": adv("complaint_min_chars"),
                                   "setup_needed": db.setting("admin_pw") is None, "admin": self.is_admin()})
            if p == "/api/public/hubs":
                hubs = directory()
                counts = {r["hub"]: r["n"] for r in db.q("SELECT hub, COUNT(*) n FROM nodes GROUP BY hub")}
                for h in hubs:
                    h["nodes"] = counts.get(h["id"], 0)
                    h["links"] = [l for l in links_for(h["id"]) if l["state"] == "active"]
                return self.reply(hubs)
            if p == "/api/public/nodes":
                return self.reply(db.q("SELECT n.* FROM nodes n JOIN hubs h ON h.id=n.hub WHERE h.status='approved'"))
            m = re.match(r"^/api/public/node/([^/]+)/([^/]+)/([^/]+)$", p)
            if m:
                hub, net, nid = (urllib.parse.unquote(x) for x in m.groups())
                n = db.one("SELECT * FROM nodes WHERE hub=? AND net=? AND id=?", (hub, net, nid))
                h = db.one("SELECT * FROM hubs WHERE id=? AND status='approved'", (hub,))
                if not n or not h:
                    return self.reply({"error": "not_found"}, 404)
                links = [l for l in links_for(hub) if l["state"] == "active"]
                return self.reply({"node": n, "hub": hub_public(h), "links": links})
            m = re.match(r"^/api/public/hub/([^/]+)$", p)
            if m:
                h = db.one("SELECT * FROM hubs WHERE id=? AND status='approved'", (m.group(1),))
                if not h:
                    return self.reply({"error": "not_found"}, 404)
                since = now() - 30 * 86400
                st = db.q("""SELECT src,dst,net,SUM(frames) frames,SUM(bytes) bytes FROM stats
                             WHERE (src=? OR dst=?) AND hour>=? GROUP BY src,dst,net""", (h["id"], h["id"], since))
                return self.reply({"hub": hub_public(h), "nodes": db.q("SELECT * FROM nodes WHERE hub=?", (h["id"],)),
                                   "links": [l for l in links_for(h["id"]) if l["state"] == "active"], "stats30d": st,
                                   "complaints": db.q("""SELECT id,created,status,subject_type,subject_id FROM complaints
                                                         WHERE subject_id=? OR subject_id LIKE ? ORDER BY id DESC""",
                                                      (h["id"], h["id"] + "/%"))})
            if p == "/api/public/stats":
                hours = max(1, min(int((qs.get("hours") or ["168"])[0]), 24 * 90))
                since = now() // 3600 * 3600 - hours * 3600
                rows = db.q("SELECT src,dst,net,hour,frames,bytes FROM stats WHERE hour>=? ORDER BY hour", (since,))
                names = {h["id"]: {"name": h["name"], "code": h["code"]} for h in db.q("SELECT id,name,code FROM hubs")}
                return self.reply({"hours": hours, "since": since, "rows": rows, "hubs": names})
            if p == "/api/public/live":
                after = int((qs.get("after") or ["0"])[0] or 0)
                with live_lock:
                    ev = [e for e in live_events if e["seq"] > after and time.time() - e["t"] < 60]
                    return self.reply({"seq": live_seq, "events": ev[-200:]})
            if p == "/api/public/complaints":
                return self.reply(db.q("""SELECT id,created,subject_type,subject_id,text,status,resolution,updated
                                          FROM complaints ORDER BY id DESC LIMIT 500"""))
            if p == "/api/admin/state":
                if not self.is_admin():
                    return self.reply({"error": "login"}, 401)
                hubs = [dict(hub_public(h), email=h["email"], status=h["status"],
                             email_verified=bool(h["email_verified"]), created=h["created"])
                        for h in db.q("SELECT * FROM hubs WHERE status!='removed' ORDER BY created DESC")]
                d = (adv("acme_domain") or "").lower()
                return self.reply({"acme": dict(acme.status, cert=acme.cert_info(d) if d else None),
                                   "advanced": {k: adv(k) for k in ADV_SPEC},
                                   "advanced_spec": {k: {"default": v[0], "min": v[1], "max": v[2]} for k, v in ADV_SPEC.items()},
                                   "hubs": hubs, "links": db.q("SELECT * FROM links WHERE state!='removed'"),
                                   "complaints": db.q("SELECT * FROM complaints ORDER BY id DESC")})
            self.reply({"error": "not_found"}, 404)
        except Exception as e:
            log.exception("GET %s", p)
            self.reply({"error": str(e)}, 500)

    def do_POST(self):
        p = urllib.parse.urlparse(self.path).path
        try:
            b = self.body()
            if p == "/api/setup":
                if db.setting("admin_pw") is not None:
                    return self.reply({"error": "already_set"}, 400)
                if len(b.get("password") or "") < adv("password_min"):
                    return self.reply({"error": "password_short"}, 400)
                db.set_setting("admin_pw", hash_pw(b["password"]))
                return self.login_ok()
            if p == "/api/login":
                ip = self.client_address[0]
                login_fail[ip] = [x for x in login_fail.get(ip, []) if time.time() - x < adv("lockout_minutes") * 60]
                if len(login_fail[ip]) >= adv("lockout_attempts"):
                    return self.reply({"error": "locked"}, 429)
                time.sleep(0.5)
                if check_pw(b.get("password") or "", db.setting("admin_pw")):
                    login_fail.pop(ip, None)
                    return self.login_ok()
                login_fail[ip].append(time.time())
                log.warning("failed admin login from %s", ip)
                return self.reply({"error": "wrong_password"}, 403)
            if p == "/api/logout":
                return self.reply({"ok": True}, headers={"Set-Cookie": "ura_admin=; Max-Age=0; Path=/; Secure"})
            if p == "/api/public/complaints":
                ip = self.client_address[0]
                times = [t for t in complaint_times.get(ip, []) if time.time() - t < 3600]
                if len(times) >= adv("complaints_per_hour"):
                    return self.reply({"error": "too_many"}, 429)
                email, text = clean(b.get("email"), 120), clean(b.get("text"), adv("complaint_max_chars"))
                if not EMAIL_RE.match(email):
                    return self.reply({"error": "email_required"}, 400)
                if len(text) < adv("complaint_min_chars"):
                    return self.reply({"error": "text_short"}, 400)
                stype = b.get("subject_type") if b.get("subject_type") in ("hub", "node", "general") else "general"
                cur = db.x("""INSERT INTO complaints(created,email,subject_type,subject_id,text,status,updated)
                              VALUES(?,?,?,?,?,'open',?)""",
                           (now(), email, stype, clean(b.get("subject_id"), 80), text, now()))
                complaint_times[ip] = times + [time.time()]
                return self.reply({"ok": True, "id": cur.lastrowid})
            if not self.is_admin():
                return self.reply({"error": "login"}, 401)
            m = re.match(r"^/api/admin/hub/([^/]+)/(approve|remove|verify_email)$", p)
            if m:
                hub, action = m.groups()
                if action == "approve":
                    db.x("UPDATE hubs SET status='approved', approved=? WHERE id=?", (now(), hub))
                    from_thread(push(hub, {"t": "status", "status": "approved"}))
                elif action == "verify_email":
                    db.x("UPDATE hubs SET email_verified=1 WHERE id=?", (hub,))
                else:
                    db.x("UPDATE hubs SET status='removed' WHERE id=?", (hub,))
                    db.x("DELETE FROM nodes WHERE hub=?", (hub,))
                    for r in db.q("SELECT id FROM links WHERE state!='removed' AND (a=? OR b=?)", (hub, hub)):
                        from_thread(link_remove(None, r["id"]))
                    from_thread(tell_and_close(hub, {"t": "status", "status": "removed"}))
                from_thread(push_directory())
                return self.reply({"ok": True})
            m = re.match(r"^/api/admin/complaint/(\d+)$", p)
            if m:
                st = b.get("status")
                if st not in ("open", "review", "resolved", "rejected"):
                    return self.reply({"error": "bad_status"}, 400)
                db.x("UPDATE complaints SET status=?, resolution=?, updated=? WHERE id=?",
                     (st, clean(b.get("resolution"), 2000), now(), int(m.group(1))))
                return self.reply({"ok": True})
            if p == "/api/admin/acme/run":
                acme_kick.set()
                return self.reply({"ok": True})
            if p == "/api/admin/advanced":
                vals, errors = clean_advanced(b.get("advanced") or {})
                if errors:
                    return self.reply({"error": "invalid", "fields": errors}, 400)
                cur = json.loads(db.setting("advanced") or "{}")
                cur.update(vals)
                db.set_setting("advanced", json.dumps(cur))
                if any(k.startswith("acme_") for k in vals):
                    acme_kick.set()                    # apply certificate settings right away
                return self.reply({"ok": True})
            if p == "/api/admin/password":
                if len(b.get("password") or "") < adv("password_min"):
                    return self.reply({"error": "password_short"}, 400)
                db.set_setting("admin_pw", hash_pw(b["password"]))
                return self.reply({"ok": True})
            self.reply({"error": "not_found"}, 404)
        except Exception as e:
            log.exception("POST %s", p)
            self.reply({"error": str(e)}, 500)

    def login_ok(self):
        tok, ttl = secrets.token_urlsafe(24), adv("session_hours") * 3600
        sessions[tok] = time.time() + ttl
        return self.reply({"ok": True}, headers={
            "Set-Cookie": f"ura_admin={tok}; Max-Age={ttl}; Path=/; HttpOnly; Secure; SameSite=Strict"})


acme = None
le_ctx = {"domain": None, "ctx": None}      # Let's Encrypt context for the website's public name


def load_le_context():
    d = (adv("acme_domain") or "").lower()
    le_ctx["domain"], le_ctx["ctx"] = (d, acme.context_for(d)) if (acme and adv("acme_enabled") and d) else (None, None)


class TLSWebServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, addr, handler, ctx):
        super().__init__(addr, handler)
        self.ctx = ctx
        # visitors who use the public name get the Let's Encrypt certificate; everyone else
        # (hubs, LAN access by IP, no name) keeps Ura's own pinned certificate
        def sni(sslsock, server_name, _ctx):
            if server_name and le_ctx["ctx"] and server_name.lower() == le_ctx["domain"]:
                sslsock.context = le_ctx["ctx"]
        self.ctx.sni_callback = sni

    def finish_request(self, request, client_address):
        """Runs in the connection's own thread: peek at the ClientHello, answer Let's Encrypt's
        TLS-ALPN-01 check if that is what it is, otherwise serve the website over TLS."""
        try:
            request.settimeout(10)
            hello = request.recv(4096, socket.MSG_PEEK)
        except OSError:
            request.close()
            return
        name, alpn = parse_client_hello(hello)
        if ACME_TLS_ALPN in alpn:
            ctx = acme.challenges.get((name or "").lower()) if acme else None
            if ctx:
                try:
                    with ctx.wrap_socket(request, server_side=True) as s:
                        log.info("answered Let's Encrypt check for %s from %s", name, client_address[0])
                except (ssl.SSLError, OSError):
                    pass
            else:
                request.close()
            return
        request.settimeout(30)
        super().finish_request(self.ctx.wrap_socket(request, server_side=True, do_handshake_on_connect=False), client_address)

    def handle_error(self, request, client_address):
        import sys
        if isinstance(sys.exc_info()[1], (ssl.SSLError, ConnectionError, TimeoutError)):
            return                                         # browsers rejecting the self-signed certificate etc.
        super().handle_error(request, client_address)

    def get_request(self):
        return super().get_request()               # TLS starts in finish_request (connection thread)


acme_kick = threading.Event()


def acme_loop():
    """Get / renew the website certificate: at start, every 6 hours, and when the admin asks."""
    while True:
        try:
            load_le_context()
            d = (adv("acme_domain") or "").lower()
            if not (adv("acme_enabled") and d):
                acme.status = {"state": "off"}
            else:
                info = acme.cert_info(d)
                wrong_kind = info and (("STAGING" in info["issuer"].upper()) != bool(adv("acme_staging")))
                if info is None or info["days_left"] < 30 or wrong_kind or acme_kick.is_set():
                    acme_kick.clear()
                    acme.obtain(d, adv("acme_email"), adv("acme_staging"))
                    load_le_context()
                else:
                    acme.status = {"state": "ok", "detail": "certificate valid", **info}
        except Exception as e:
            acme.status = {"state": "error", "detail": str(e)[:500], "since": int(time.time())}
            log.warning("Let's Encrypt: %s", e)
        acme_kick.wait(6 * 3600)


def run_web(crt, key):
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.load_cert_chain(crt, key)
    srv = TLSWebServer(("0.0.0.0", WEB_PORT), Web, ctx)
    log.info("website on https://0.0.0.0:%d", WEB_PORT)
    srv.serve_forever()


async def main():
    global db, loop, FINGERPRINT
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    os.makedirs(DATA_DIR, exist_ok=True)
    db = DB(os.path.join(DATA_DIR, "ura.db"))
    loop = asyncio.get_running_loop()
    crt, key, FINGERPRINT = tls_files()
    log.info("ura-server %s, TLS fingerprint %s", VERSION, FINGERPRINT)
    global acme
    acme = Acme(DATA_DIR)
    threading.Thread(target=acme_loop, daemon=True).start()
    threading.Thread(target=run_web, args=(crt, key), daemon=True).start()
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.load_cert_chain(crt, key)
    server = await asyncio.start_server(handle, "0.0.0.0", HUB_PORT, ssl=ctx)
    log.info("hubs connect on %d", HUB_PORT)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
