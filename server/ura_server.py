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
import sqlite3, ssl, subprocess, threading, time, urllib.parse

VERSION = "0.2.0"
DATA_DIR = os.environ.get("URA_DATA", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"))
HUB_PORT = int(os.environ.get("URA_PORT", "8100"))
WEB_PORT = int(os.environ.get("URA_WEB_PORT", "8443"))
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
COMMON_DIR = os.environ.get("URA_COMMON", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "common"))
DEDUP_SECONDS = 600
NODE_MAX_AGE = 7 * 86400

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
seen = {}              # sha256(payload) -> time
FINGERPRINT = ""


# ───────────────────────── helpers ─────────────────────────

def now():
    return int(time.time())


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
            "rules": json.loads(h["rules"] or "null"), "radios": json.loads(h["radios"] or "[]")}


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


def duplicate(payload: bytes) -> bool:
    t = time.time()
    for k in [k for k, v in seen.items() if t - v > DEDUP_SECONDS]:
        del seen[k]
    h = hashlib.sha256(payload).digest()
    if h in seen:
        return True
    seen[h] = t
    return False


def count(src, dst, net, size):
    hour = now() // 3600 * 3600
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
        for n in nodes[:2000]:
            nid = clean(n.get("id"), 40)
            lh = n.get("last_heard")
            if not nid or (lh and t - int(lh) > NODE_MAX_AGE):
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
    if not name:
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
         (hub_id, key, name, email, country, city, code, num(msg.get("lat")), num(msg.get("lon")),
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
        if first.get("t") != "hello" or not h or not hmac.compare_digest(h["key"], str(first.get("key"))):
            await send(writer, {"t": "refused", "reason": "unknown_hub"})
            return
        if h["status"] == "removed":
            await send(writer, {"t": "refused", "reason": "removed"})
            return
        hub_id = h["id"]
        info = first.get("info") or {}
        db.x("UPDATE hubs SET last_seen=?, version=?, rules=?, radios=? WHERE id=?",
             (now(), clean(first.get("version"), 20), json.dumps(info.get("rules")),
              json.dumps(info.get("radios") or []), hub_id))
        old = online.pop(hub_id, None)
        if old:
            old.close()
        online[hub_id] = writer
        await send(writer, {"t": "welcome", "hub": hub_id, "status": h["status"], "server_version": VERSION,
                            "hubs": directory(), "links": links_for(hub_id)})
        log.info("hub %s (%s) online from %s, status %s", hub_id, h["name"], peer, h["status"])
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
                db.x("UPDATE hubs SET rules=?, radios=? WHERE id=?",
                     (json.dumps(info.get("rules")), json.dumps(info.get("radios") or []), hub_id))
                await push_directory()                     # other hubs see changed rules at once
            elif status != "approved":
                continue                                   # pending hubs: no nodes, links or traffic yet
            elif t == "nodes":
                store_nodes(hub_id, clean(msg.get("net"), 4) or "mt", msg.get("nodes") or [])
            elif t == "link_request":
                await link_request(hub_id, clean(msg.get("to"), 20))
            elif t == "link_accept":
                await link_accept(hub_id, int(msg.get("link") or 0))
            elif t == "link_remove":
                await link_remove(hub_id, int(msg.get("link") or 0))
            elif t == "mesh":
                payload = base64.b64decode(msg["data"])
                if duplicate(payload):
                    continue
                allowed = active_peers(hub_id)
                for dst in msg.get("to") or []:
                    if dst in allowed and dst in online:
                        await push(dst, {"t": "mesh", "net": msg.get("net"), "from": hub_id,
                                         "topic": msg.get("topic", ""), "data": msg["data"]})
                        count(hub_id, dst, msg.get("net") or "mt", len(payload))
    except Exception as e:
        log.warning("hub %s connection error: %s", hub_id or peer, e)
    finally:
        if hub_id and online.get(hub_id) is writer:
            del online[hub_id]
            log.info("hub %s offline", hub_id)
            await push_directory()
        writer.close()


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
complaint_times = {}   # ip -> [times]
SESSION_TTL = 12 * 3600


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
            if not p.startswith("/api/"):
                return self.static(p)
            if p == "/api/public/info":
                return self.reply({"version": VERSION, "fingerprint": FINGERPRINT, "hub_port": HUB_PORT,
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
            if p == "/api/public/complaints":
                return self.reply(db.q("""SELECT id,created,subject_type,subject_id,text,status,resolution,updated
                                          FROM complaints ORDER BY id DESC LIMIT 500"""))
            if p == "/api/admin/state":
                if not self.is_admin():
                    return self.reply({"error": "login"}, 401)
                hubs = [dict(hub_public(h), email=h["email"], status=h["status"],
                             email_verified=bool(h["email_verified"]), created=h["created"])
                        for h in db.q("SELECT * FROM hubs WHERE status!='removed' ORDER BY created DESC")]
                return self.reply({"hubs": hubs, "links": db.q("SELECT * FROM links WHERE state!='removed'"),
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
                if len(b.get("password") or "") < 8:
                    return self.reply({"error": "password_short"}, 400)
                db.set_setting("admin_pw", hash_pw(b["password"]))
                return self.login_ok()
            if p == "/api/login":
                time.sleep(0.5)
                if check_pw(b.get("password") or "", db.setting("admin_pw")):
                    return self.login_ok()
                return self.reply({"error": "wrong_password"}, 403)
            if p == "/api/logout":
                return self.reply({"ok": True}, headers={"Set-Cookie": "ura_admin=; Max-Age=0; Path=/; Secure"})
            if p == "/api/public/complaints":
                ip = self.client_address[0]
                times = [t for t in complaint_times.get(ip, []) if time.time() - t < 3600]
                if len(times) >= 5:
                    return self.reply({"error": "too_many"}, 429)
                email, text = clean(b.get("email"), 120), clean(b.get("text"), 4000)
                if not EMAIL_RE.match(email):
                    return self.reply({"error": "email_required"}, 400)
                if len(text) < 10:
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
            if p == "/api/admin/password":
                if len(b.get("password") or "") < 8:
                    return self.reply({"error": "password_short"}, 400)
                db.set_setting("admin_pw", hash_pw(b["password"]))
                return self.reply({"ok": True})
            self.reply({"error": "not_found"}, 404)
        except Exception as e:
            log.exception("POST %s", p)
            self.reply({"error": str(e)}, 500)

    def login_ok(self):
        tok = secrets.token_urlsafe(24)
        sessions[tok] = time.time() + SESSION_TTL
        return self.reply({"ok": True}, headers={
            "Set-Cookie": f"ura_admin={tok}; Max-Age={SESSION_TTL}; Path=/; HttpOnly; Secure; SameSite=Strict"})


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
    threading.Thread(target=run_web, args=(crt, key), daemon=True).start()
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.load_cert_chain(crt, key)
    server = await asyncio.start_server(handle, "0.0.0.0", HUB_PORT, ssl=ctx)
    log.info("hubs connect on %d", HUB_PORT)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
