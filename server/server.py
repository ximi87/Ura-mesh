#!/usr/bin/env python3
"""ura-mesh-server — links Ura points (radio groups) worldwide.

Points (ura-mesh-client) connect out to /link over a WebSocket (see PROTOCOL.md). The server
keeps a directory of points, relays messages between points that share a room, enforces
approval, rate limits and duplicate suppression, and serves:

    /          public page: points + world map
    /admin     admin page: approve / block / limit points, rooms, relay statistics

Privacy (SPEC.md): message text is relayed in memory only and never stored, logged or shown.
The relay log keeps time, point, room, size and result.

Settings live in DATA_DIR/hub.json, everything else in DATA_DIR/hub.db.
Environment: DATA_DIR (./data), WEB_HOST (0.0.0.0), WEB_PORT (8100).
"""
import asyncio
import hashlib
import hmac
import json
import logging
import math
import os
import re
import secrets
import sqlite3
import time

from aiohttp import WSMsgType, web

import auth

log = logging.getLogger("hub")

DATA_DIR = os.path.abspath(os.environ.get("DATA_DIR", "data"))
WEB_HOST = os.environ.get("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.environ.get("WEB_PORT", "8100"))
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
SETTINGS_PATH = os.path.join(DATA_DIR, "hub.json")
DB_PATH = os.path.join(DATA_DIR, "hub.db")
SETUP_CODE_PATH = os.path.join(DATA_DIR, "setup-code.txt")

PROTOCOL_VERSION = 1
DEDUPE_SECS = 600
KEEP_DAYS = 90
ONLINE_GRACE = 90          # bridge counts as online this long after its socket drops (reconnects)

DEFAULT_SETTINGS = {
    "name": "Ura Server",
    "default_per_min": 6,      # messages per minute a bridge may send to the hub
    "max_bytes": 200,
    "min_distance_km": 20,     # one bridge per area: approved bridges closer than this are flagged (0 = off)
    "distance_strict": False,  # True: refuse join requests inside an existing bridge's area
    "auth": {"password_hash": "", "session_secret": ""},
}

CC_RE = re.compile(r"^[A-Z]{2}$")
PREFIX_RE = re.compile(r"^\[[A-Z]{2}\]\s*")


def load_settings():
    os.makedirs(DATA_DIR, exist_ok=True)
    s = json.loads(json.dumps(DEFAULT_SETTINGS))
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH) as f:
            saved = json.load(f)
        for k, v in saved.items():
            if isinstance(v, dict) and isinstance(s.get(k), dict):
                s[k].update(v)
            else:
                s[k] = v
    if not s["auth"]["session_secret"]:
        s["auth"]["session_secret"] = secrets.token_hex(32)
        save_settings(s)
    return s


def save_settings(s):
    tmp = SETTINGS_PATH + ".tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(s, f, indent=2)
    os.replace(tmp, SETTINGS_PATH)


def key_hash(key):
    return hashlib.sha256(key.encode()).hexdigest()


def text_hash(text):
    """Fingerprint for duplicate detection (relay prefix removed, case/space folded). Only the hash is kept."""
    t = PREFIX_RE.sub("", text or "")
    if PREFIX_RE.match(text or ""):
        t = t.split(": ", 1)[-1]
    return hashlib.sha256(" ".join(t.lower().split()).encode()).hexdigest()


def distance_km(a_lat, a_lon, b_lat, b_lon):
    """Great-circle distance (haversine)."""
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dp, dl = p2 - p1, math.radians(b_lon - a_lon)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(min(1.0, h)))


def clean_info(raw):
    """Validate the bridge description sent with join/hello."""
    if not isinstance(raw, dict):
        raise ValueError("info missing")
    name = str(raw.get("name") or "").strip()[:40]
    city = str(raw.get("city") or "").strip()[:40]
    country = str(raw.get("country") or "").strip().upper()
    if not name:
        raise ValueError("bridge name is required")
    if not CC_RE.match(country):
        raise ValueError("country must be a 2-letter code, e.g. AL, DE, US")
    lat = raw.get("lat")
    lon = raw.get("lon")
    try:
        lat = round(float(lat), 2) if lat not in (None, "") else None
        lon = round(float(lon), 2) if lon not in (None, "") else None
    except (TypeError, ValueError):
        raise ValueError("lat/lon must be numbers")
    if lat is not None and not (-90 <= lat <= 90 and -180 <= (lon or 0) <= 180):
        raise ValueError("lat/lon out of range")
    nets = [n for n in (raw.get("networks") or []) if n in ("mt", "mc")]
    return {"name": name, "city": city, "country": country, "lat": lat, "lon": lon,
            "networks": ",".join(sorted(set(nets))),
            "contact": str(raw.get("contact") or "").strip()[:80],
            "note": str(raw.get("note") or "").strip()[:300]}


class DB:
    def __init__(self, path):
        self.con = sqlite3.connect(path)
        self.con.row_factory = sqlite3.Row
        self.con.executescript("""
        CREATE TABLE IF NOT EXISTS bridges (
            id TEXT PRIMARY KEY, key_hash TEXT, name TEXT, country TEXT, city TEXT,
            lat REAL, lon REAL, networks TEXT, contact TEXT, note TEXT,
            status TEXT, created REAL, approved_at REAL, last_seen REAL,
            per_min INTEGER, node_count INTEGER DEFAULT 0, version INTEGER,
            msgs_in INTEGER DEFAULT 0, msgs_out INTEGER DEFAULT 0, ip TEXT);
        CREATE TABLE IF NOT EXISTS rooms (
            name TEXT PRIMARY KEY, description TEXT, open INTEGER DEFAULT 1, created REAL);
        CREATE TABLE IF NOT EXISTS room_members (room TEXT, bridge_id TEXT, PRIMARY KEY (room, bridge_id));
        DROP TABLE IF EXISTS messages;            -- old versions stored text; never again
        CREATE TABLE IF NOT EXISTS relay_log (
            id TEXT PRIMARY KEY, ts REAL, room TEXT, bridge_id TEXT, net TEXT, bytes INTEGER,
            delivered INTEGER, rejected TEXT);
        CREATE INDEX IF NOT EXISTS relay_log_ts ON relay_log(ts);
        CREATE TABLE IF NOT EXISTS deliveries (ts REAL, room TEXT, src TEXT, dst TEXT);
        CREATE INDEX IF NOT EXISTS deliveries_ts ON deliveries(ts);
        """)
        have = {r[1] for r in self.con.execute("PRAGMA table_info(bridges)")}
        for col, typ in (("public_rate", "REAL"), ("public_hours", "REAL"), ("client_version", "TEXT")):
            if col not in have:
                self.con.execute(f"ALTER TABLE bridges ADD COLUMN {col} {typ}")
        if not self.con.execute("SELECT 1 FROM rooms").fetchone():
            self.con.execute("INSERT INTO rooms VALUES ('Global', 'Worldwide chat for every bridge', 1, ?)",
                             (time.time(),))
        self.con.commit()

    def q(self, sql, args=()):
        return [dict(r) for r in self.con.execute(sql, args).fetchall()]

    def one(self, sql, args=()):
        r = self.con.execute(sql, args).fetchone()
        return dict(r) if r else None

    def run(self, sql, args=()):
        cur = self.con.execute(sql, args)
        self.con.commit()
        return cur


class Bucket:
    """Token bucket: `per_min` tokens per minute, burst up to max(3, per_min/2)."""

    def __init__(self, per_min):
        self.set(per_min)
        self.tokens = self.cap

    def set(self, per_min):
        self.rate = max(per_min, 0) / 60.0
        self.cap = max(3.0, per_min / 2)
        self.last = time.monotonic()

    def take(self):
        now = time.monotonic()
        self.tokens = min(self.cap, getattr(self, "tokens", self.cap) + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


class Hub:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.s = load_settings()
        for old in ("public_feed", "show_nodes"):   # removed options (privacy)
            self.s.pop(old, None)
        self.db = DB(DB_PATH)
        self.conns = {}          # bridge_id -> websocket
        self.buckets = {}        # bridge_id -> Bucket
        self.seen_ids = {}       # message id -> ts
        self.seen_text = {}      # (room, normalized text) -> ts
        self.dropped_at = {}     # bridge_id -> time the socket went away
        self.setup_code = None
        self.login_fail = {}
        self.admin_sockets = set()

    # ── bridges / rooms ──────────────────────────────────────────
    def bridge(self, bid):
        return self.db.one("SELECT * FROM bridges WHERE id=?", (bid,))

    def rooms_for(self, bid):
        return self.db.q("""SELECT name, description FROM rooms
                            WHERE open=1 OR name IN (SELECT room FROM room_members WHERE bridge_id=?)
                            ORDER BY name""", (bid,))

    def room_bridges(self, room):
        r = self.db.one("SELECT open FROM rooms WHERE name=?", (room,))
        if not r:
            return set()
        if r["open"]:
            return {b["id"] for b in self.db.q("SELECT id FROM bridges WHERE status='approved'")}
        return {m["bridge_id"] for m in self.db.q(
            "SELECT m.bridge_id FROM room_members m JOIN bridges b ON b.id=m.bridge_id "
            "WHERE m.room=? AND b.status='approved'", (room,))}

    def status_frame(self, b, kind="status"):
        per_min = b["per_min"] if b["per_min"] is not None else self.s["default_per_min"]
        return {"type": kind, "status": b["status"], "hub": self.s["name"],
                "rooms": self.rooms_for(b["id"]) if b["status"] == "approved" else [],
                "limits": {"per_min": per_min, "max_bytes": self.s["max_bytes"]}}

    async def push_status(self, bid):
        b = self.bridge(bid)
        ws = self.conns.get(bid)
        if b is None:
            if ws is not None:
                await ws.close(message=b"removed")
            return
        if bid in self.buckets:
            self.buckets[bid].set(b["per_min"] if b["per_min"] is not None else self.s["default_per_min"])
        if ws is not None:
            try:
                await ws.send_json(self.status_frame(b))
                if b["status"] == "blocked":
                    await ws.close(message=b"blocked")
            except Exception:
                pass

    async def push_all_status(self):
        for bid in list(self.conns):
            await self.push_status(bid)

    def nearby(self, lat, lon, exclude=None):
        """Approved bridges inside the one-bridge-per-area radius around lat/lon, nearest first."""
        limit = self.s.get("min_distance_km") or 0
        if limit <= 0 or lat is None or lon is None:
            return []
        out = []
        for b in self.db.q("SELECT id, name, country, city, lat, lon FROM bridges "
                           "WHERE status='approved' AND lat IS NOT NULL AND lon IS NOT NULL"):
            if b["id"] == exclude:
                continue
            km = distance_km(lat, lon, b["lat"], b["lon"])
            if km < limit:
                out.append({"id": b["id"], "name": b["name"], "country": b["country"], "city": b["city"],
                            "km": round(km, 1)})
        return sorted(out, key=lambda x: x["km"])

    def area_check(self, b):
        """Problems with the one-bridge-per-area rule for a bridge row (shown to the admin)."""
        if not self.s.get("min_distance_km"):
            return {"nearby": [], "no_location": False}
        if b["lat"] is None or b["lon"] is None:
            return {"nearby": [], "no_location": True}
        return {"nearby": self.nearby(b["lat"], b["lon"], exclude=b["id"]), "no_location": False}

    def online(self, bid):
        return bid in self.conns or time.time() - self.dropped_at.get(bid, 0) < ONLINE_GRACE

    # ── relay ────────────────────────────────────────────────────
    def prune(self):
        cutoff = time.time() - DEDUPE_SECS
        for d in (self.seen_ids, self.seen_text):
            for k in [k for k, ts in d.items() if ts < cutoff]:
                d.pop(k, None)

    async def relay(self, bid, frame):
        b = self.bridge(bid)
        mid = str(frame.get("id") or "")[:64]
        room = str(frame.get("room") or "")
        text = str(frame.get("text") or "").strip()
        sender = str(frame.get("sender") or "?").strip()[:40]
        net = frame.get("net") if frame.get("net") in ("mt", "mc", "web", "tg") else "web"

        size = len(text.encode())

        def reject(reason):
            if mid:
                self.db.run("INSERT OR IGNORE INTO relay_log VALUES (?,?,?,?,?,?,?,?)",
                            (mid, time.time(), room, bid, net, size, 0, reason))
            return {"type": "ack", "id": mid, "ok": False, "to": 0, "to_points": [], "reason": reason}

        if not mid or not text:
            return reject("empty")
        if b is None or b["status"] != "approved":
            return reject("bridge not approved")
        allowed = {r["name"] for r in self.rooms_for(bid)}
        if room not in allowed:
            return reject(f"not a member of room {room!r}")
        if len(text.encode()) > self.s["max_bytes"]:
            return reject(f"longer than {self.s['max_bytes']} bytes")
        self.prune()
        if mid in self.seen_ids:
            return reject("duplicate id")
        key = (room, text_hash(text))
        if key in self.seen_text:
            self.seen_ids[mid] = time.time()
            return reject("duplicate (same text already relayed)")
        bucket = self.buckets.setdefault(bid, Bucket(b["per_min"] if b["per_min"] is not None
                                                     else self.s["default_per_min"]))
        if not bucket.take():
            return reject("rate limit")
        now = time.time()
        self.seen_ids[mid] = now
        self.seen_text[key] = now
        out = {"type": "msg", "id": mid, "room": room, "net": net, "sender": sender, "text": text, "ts": now,
               "from": {"bridge_id": bid, "name": b["name"], "country": b["country"], "city": b["city"]}}
        to_points = []
        for target in self.room_bridges(room) - {bid}:
            ws = self.conns.get(target)
            if ws is None:
                continue
            try:
                await ws.send_json(out)
                t = self.bridge(target)
                to_points.append({"id": target, "name": t["name"], "country": t["country"]})
                self.db.con.execute("UPDATE bridges SET msgs_out=msgs_out+1 WHERE id=?", (target,))
                self.db.con.execute("INSERT INTO deliveries VALUES (?,?,?,?)", (now, room, bid, target))
            except Exception as e:
                log.warning("send to %s failed: %s", target, e)
        self.db.run("UPDATE bridges SET msgs_in=msgs_in+1 WHERE id=?", (bid,))
        self.db.run("INSERT OR IGNORE INTO relay_log VALUES (?,?,?,?,?,?,?,?)",
                    (mid, now, room, bid, net, size, len(to_points), None))
        await self.admin_event({"kind": "msg", "msg": self.log_row(mid)})
        log.info("[%s] %s → %d point(s)", room, b["name"], len(to_points))
        return {"type": "ack", "id": mid, "ok": True, "to": len(to_points), "to_points": to_points}

    async def cleanup_loop(self):
        while True:
            await asyncio.sleep(3600)
            cutoff = time.time() - KEEP_DAYS * 86400
            self.db.run("DELETE FROM relay_log WHERE ts < ?", (cutoff,))
            self.db.run("DELETE FROM deliveries WHERE ts < ?", (cutoff,))

    # ── /link websocket ──────────────────────────────────────────
    async def link(self, request):
        ws = web.WebSocketResponse(heartbeat=30, max_msg_size=256 * 1024)
        await ws.prepare(request)
        bid = None
        try:
            first = await asyncio.wait_for(ws.receive(), 15)
            if first.type != WSMsgType.TEXT:
                return ws
            hello = json.loads(first.data)
            bid = str(hello.get("bridge_id") or "")
            b = self.bridge(bid) if hello.get("type") == "hello" else None
            if b is None or not hmac.compare_digest(b["key_hash"], key_hash(str(hello.get("key") or ""))):
                await ws.send_json({"type": "error", "reason": "unknown bridge or wrong key"})
                await asyncio.sleep(1)
                return ws
            if b["status"] == "blocked":
                await ws.send_json({"type": "welcome", "status": "blocked", "hub": self.s["name"],
                                    "rooms": [], "limits": {}})
                return ws
            try:
                info = clean_info(hello.get("info") or {})
                self.db.run("""UPDATE bridges SET name=?, country=?, city=?, lat=?, lon=?, networks=?,
                               contact=?, version=? WHERE id=?""",
                            (info["name"], info["country"], info["city"], info["lat"], info["lon"],
                             info["networks"], info["contact"] or b["contact"], hello.get("version"), bid))
                self.db.run("UPDATE bridges SET client_version=? WHERE id=?",
                            (str(hello.get("client") or "")[:20], bid))
            except ValueError as e:
                log.info("bridge %s sent bad info: %s", bid, e)
            old = self.conns.get(bid)
            if old is not None:
                await old.close(message=b"replaced by a new connection")
            self.conns[bid] = ws
            self.dropped_at.pop(bid, None)
            self.db.run("UPDATE bridges SET last_seen=?, ip=? WHERE id=?", (time.time(), request.remote, bid))
            b = self.bridge(bid)
            await ws.send_json(self.status_frame(b, "welcome"))
            log.info("bridge connected: %s (%s, %s) status=%s", b["name"], b["country"], bid, b["status"])
            await self.admin_event({"kind": "bridges"})
            async for m in ws:
                if m.type != WSMsgType.TEXT:
                    if m.type == WSMsgType.ERROR:
                        break
                    continue
                try:
                    frame = json.loads(m.data)
                except ValueError:
                    continue
                self.db.run("UPDATE bridges SET last_seen=? WHERE id=?", (time.time(), bid))
                t = frame.get("type")
                if t == "msg":
                    await ws.send_json(await self.relay(bid, frame))
                elif t == "nodes":
                    self.nodes_update(bid, frame)
        except (asyncio.TimeoutError, ValueError):
            pass
        finally:
            if bid and self.conns.get(bid) is ws:
                del self.conns[bid]
                self.dropped_at[bid] = time.time()
                log.info("bridge disconnected: %s", bid)
                await self.admin_event({"kind": "bridges"})
        return ws

    def nodes_update(self, bid, frame):
        try:
            count = int(frame.get("count") or 0)
        except (TypeError, ValueError):
            count = 0
        self.db.run("UPDATE bridges SET node_count=? WHERE id=?", (max(0, min(count, 100000)), bid))
        pr = frame.get("public_rate")
        if isinstance(pr, dict):
            try:
                self.db.run("UPDATE bridges SET public_rate=?, public_hours=? WHERE id=?",
                            (float(pr.get("per_hour") or 0), float(pr.get("measured_hours") or 0), bid))
            except (TypeError, ValueError):
                pass

    # ── public API ───────────────────────────────────────────────
    def public_bridges(self):
        out = []
        for b in self.db.q("SELECT * FROM bridges WHERE status='approved' ORDER BY country, name"):
            out.append({"id": b["id"], "name": b["name"], "country": b["country"], "city": b["city"],
                        "lat": b["lat"], "lon": b["lon"], "networks": (b["networks"] or "").split(",")
                        if b["networks"] else [], "online": self.online(b["id"]),
                        "last_seen": b["last_seen"], "nodes": b["node_count"],
                        "rooms": [r["name"] for r in self.rooms_for(b["id"])]})
        return out

    async def api_public(self, request):
        bridges = self.public_bridges()
        day = time.time() - 86400
        data = {"name": self.s["name"], "bridges": bridges,
                "rooms": self.db.q("SELECT name, description, open FROM rooms ORDER BY name"),
                "stats": {"bridges": len(bridges), "online": sum(b["online"] for b in bridges),
                          "countries": len({b["country"] for b in bridges}),
                          "messages_24h": self.db.one("SELECT COUNT(*) n FROM relay_log WHERE ts>? "
                                                      "AND rejected IS NULL", (day,))["n"]}}
        return web.json_response(data)

    async def api_join(self, request):
        try:
            body = await request.json()
            info = clean_info(body)
        except ValueError as e:
            raise web.HTTPBadRequest(text=str(e))
        except Exception:
            raise web.HTTPBadRequest(text="bad json")
        # very simple flood guard: max 5 pending requests per IP
        ip = request.remote
        if self.db.one("SELECT COUNT(*) n FROM bridges WHERE ip=? AND status='pending'", (ip,))["n"] >= 5:
            raise web.HTTPTooManyRequests(text="too many pending requests from your address")
        if self.s.get("min_distance_km") and self.s.get("distance_strict"):
            if info["lat"] is None or info["lon"] is None:
                raise web.HTTPBadRequest(text="this hub allows one bridge per area: please enter your bridge location")
            near = self.nearby(info["lat"], info["lon"])
            if near:
                n = near[0]
                raise web.HTTPConflict(text=f"an approved bridge already serves this area: {n['name']} "
                                            f"({n['city'] or n['country']}), {n['km']} km away. This hub allows one "
                                            f"bridge per {self.s['min_distance_km']} km — contact the hub admin.")
        bid = "b_" + secrets.token_hex(6)
        key = secrets.token_urlsafe(24)
        self.db.run("""INSERT INTO bridges (id, key_hash, name, country, city, lat, lon, networks, contact,
                       note, status, created, per_min, ip) VALUES (?,?,?,?,?,?,?,?,?,?, 'pending', ?, NULL, ?)""",
                    (bid, key_hash(key), info["name"], info["country"], info["city"], info["lat"], info["lon"],
                     info["networks"], info["contact"], info["note"], time.time(), ip))
        log.info("join request: %s (%s) from %s → %s", info["name"], info["country"], ip, bid)
        await self.admin_event({"kind": "bridges"})
        return web.json_response({"bridge_id": bid, "key": key, "status": "pending", "hub": self.s["name"]})

    # ── admin auth (same scheme as the bridge) ───────────────────
    def logged_in(self, request):
        a = self.s["auth"]
        return auth.valid_session(request.cookies.get(auth.COOKIE), a["session_secret"], a["password_hash"])

    @web.middleware
    async def guard(self, request, handler):
        p = request.path
        if not (p.startswith("/admin") or p.startswith("/api/admin")):
            return await handler(request)
        if not self.s["auth"]["password_hash"]:
            if p in ("/admin/setup", "/api/admin/setup"):
                return await handler(request)
            if p.startswith("/api/"):
                raise web.HTTPForbidden(text="setup required")
            raise web.HTTPFound("/admin/setup")
        if p in ("/admin/login", "/api/admin/login") or self.logged_in(request):
            return await handler(request)
        if p.startswith("/api/"):
            raise web.HTTPUnauthorized(text="login required")
        raise web.HTTPFound("/admin/login")

    async def json_body(self, request):
        if request.content_type != "application/json":
            raise web.HTTPUnsupportedMediaType()
        try:
            body = await request.json()
        except Exception:
            raise web.HTTPBadRequest(text="bad json")
        if not isinstance(body, dict):
            raise web.HTTPBadRequest(text="bad json")
        return body

    def set_session(self, resp, request):
        a = self.s["auth"]
        resp.set_cookie(auth.COOKIE, auth.make_session(a["session_secret"], a["password_hash"]),
                        max_age=auth.SESSION_DAYS * 86400, httponly=True, samesite="Strict",
                        secure=request.secure, path="/")

    async def admin_setup(self, request):
        body = await self.json_body(request)
        if self.s["auth"]["password_hash"]:
            raise web.HTTPConflict(text="already set up")
        if not secrets.compare_digest(str(body.get("code", "")).strip().upper(), self.setup_code or "-"):
            await asyncio.sleep(1)
            raise web.HTTPForbidden(text="wrong setup code — see the hub log or data/setup-code.txt")
        pw = body.get("password") or ""
        if len(pw) < 8:
            raise web.HTTPBadRequest(text="password must be at least 8 characters")
        self.s["auth"]["password_hash"] = auth.hash_password(pw)
        save_settings(self.s)
        self.setup_code = None
        try:
            os.remove(SETUP_CODE_PATH)
        except OSError:
            pass
        resp = web.json_response({"ok": True})
        self.set_session(resp, request)
        return resp

    async def admin_login(self, request):
        body = await self.json_body(request)
        ip = request.remote or "?"
        n, first = self.login_fail.get(ip, (0, time.time()))
        if time.time() - first > 900:
            n, first = 0, time.time()
        if n >= 10:
            raise web.HTTPTooManyRequests(text="too many attempts, try again in 15 minutes")
        if not auth.check_password(str(body.get("password", "")), self.s["auth"]["password_hash"]):
            self.login_fail[ip] = (n + 1, first)
            await asyncio.sleep(1)
            raise web.HTTPForbidden(text="wrong password")
        self.login_fail.pop(ip, None)
        resp = web.json_response({"ok": True})
        self.set_session(resp, request)
        return resp

    async def admin_logout(self, request):
        resp = web.json_response({"ok": True})
        resp.del_cookie(auth.COOKIE, path="/")
        return resp

    # ── admin API ────────────────────────────────────────────────
    def log_row(self, mid):
        return self.db.one("""SELECT m.*, b.name bridge, b.country FROM relay_log m
                              LEFT JOIN bridges b ON b.id=m.bridge_id WHERE m.id=?""", (mid,))

    async def admin_state(self, request):
        bridges = self.db.q("SELECT * FROM bridges ORDER BY created DESC")
        for b in bridges:
            b.pop("key_hash", None)
            b["online"] = b["id"] in self.conns
            b["rooms"] = [r["name"] for r in self.rooms_for(b["id"])]
            b["area"] = self.area_check(b)
        rooms = self.db.q("SELECT * FROM rooms ORDER BY name")
        for r in rooms:
            r["members"] = [m["bridge_id"] for m in self.db.q(
                "SELECT bridge_id FROM room_members WHERE room=?", (r["name"],))]
        settings = {k: v for k, v in self.s.items() if k != "auth"}
        return web.json_response({"bridges": bridges, "rooms": rooms, "settings": settings,
                                  "messages": self.db.q("""SELECT m.*, b.name bridge, b.country FROM relay_log m
                                      LEFT JOIN bridges b ON b.id=m.bridge_id ORDER BY m.ts DESC LIMIT 200""")})

    async def admin_bridge(self, request):
        bid = request.match_info["bid"]
        if not self.bridge(bid):
            raise web.HTTPNotFound(text="no such bridge")
        body = await self.json_body(request)
        action = body.get("action")
        if action in ("approve", "unblock"):
            self.db.run("UPDATE bridges SET status='approved', approved_at=COALESCE(approved_at, ?) WHERE id=?",
                        (time.time(), bid))
        elif action == "block":
            self.db.run("UPDATE bridges SET status='blocked' WHERE id=?", (bid,))
        elif action == "delete":
            self.db.run("DELETE FROM bridges WHERE id=?", (bid,))
            self.db.run("DELETE FROM room_members WHERE bridge_id=?", (bid,))
        elif action == "limit":
            v = body.get("per_min")
            per_min = None if v in (None, "") else int(v)
            if per_min is not None and not 0 <= per_min <= 600:
                raise web.HTTPBadRequest(text="per_min must be 0-600")
            self.db.run("UPDATE bridges SET per_min=? WHERE id=?", (per_min, bid))
        else:
            raise web.HTTPBadRequest(text="unknown action")
        log.info("admin: %s %s", action, bid)
        await self.push_status(bid)
        await self.admin_event({"kind": "bridges"})
        return web.json_response({"ok": True})

    async def admin_room(self, request):
        body = await self.json_body(request)
        action, name = body.get("action"), str(body.get("name") or "").strip()
        if not re.match(r"^[A-Za-z0-9][A-Za-z0-9 _-]{0,29}$", name):
            raise web.HTTPBadRequest(text="room name: letters, digits, space, - or _ (max 30)")
        if action == "save":
            self.db.run("INSERT INTO rooms (name, description, open, created) VALUES (?,?,?,?) "
                        "ON CONFLICT(name) DO UPDATE SET description=excluded.description, open=excluded.open",
                        (name, str(body.get("description") or "")[:100], 1 if body.get("open") else 0, time.time()))
            self.db.run("DELETE FROM room_members WHERE room=?", (name,))
            for bid in body.get("members") or []:
                if self.bridge(bid):
                    self.db.run("INSERT OR IGNORE INTO room_members VALUES (?,?)", (name, bid))
        elif action == "delete":
            self.db.run("DELETE FROM rooms WHERE name=?", (name,))
            self.db.run("DELETE FROM room_members WHERE room=?", (name,))
        else:
            raise web.HTTPBadRequest(text="unknown action")
        await self.push_all_status()
        return web.json_response({"ok": True})

    async def admin_settings(self, request):
        body = await self.json_body(request)
        s = self.s
        if "name" in body:
            s["name"] = str(body["name"]).strip()[:40] or "Ura Hub"
        for k in ("default_per_min", "max_bytes", "min_distance_km"):
            if k in body:
                try:
                    s[k] = int(body[k])
                except (TypeError, ValueError):
                    raise web.HTTPBadRequest(text=f"{k} must be a number")
        if not 0 <= s["default_per_min"] <= 600 or not 20 <= s["max_bytes"] <= 1000 \
                or not 0 <= s["min_distance_km"] <= 1000:
            raise web.HTTPBadRequest(text="limits out of range")
        for k in ("distance_strict",):
            if k in body:
                s[k] = bool(body[k])
        save_settings(s)
        await self.push_all_status()
        return web.json_response({"ok": True})

    async def admin_password(self, request):
        body = await self.json_body(request)
        if not auth.check_password(str(body.get("current", "")), self.s["auth"]["password_hash"]):
            await asyncio.sleep(1)
            raise web.HTTPForbidden(text="current password is wrong")
        if len(body.get("new") or "") < 8:
            raise web.HTTPBadRequest(text="password must be at least 8 characters")
        self.s["auth"]["password_hash"] = auth.hash_password(body["new"])
        save_settings(self.s)
        resp = web.json_response({"ok": True})
        self.set_session(resp, request)
        return resp

    async def admin_ws(self, request):
        ws = web.WebSocketResponse(heartbeat=30)
        await ws.prepare(request)
        self.admin_sockets.add(ws)
        try:
            async for _ in ws:
                pass
        finally:
            self.admin_sockets.discard(ws)
        return ws

    async def admin_event(self, ev):
        for ws in list(self.admin_sockets):
            try:
                await ws.send_json(ev)
            except Exception:
                self.admin_sockets.discard(ws)

    # ── startup ──────────────────────────────────────────────────
    def page(self, name):
        async def handler(request):
            resp = web.FileResponse(os.path.join(WEB_DIR, name))
            resp.headers["Cache-Control"] = "no-cache"
            return resp
        return handler

    async def main(self):
        if not self.s["auth"]["password_hash"]:
            self.setup_code = secrets.token_hex(3).upper()
            with open(SETUP_CODE_PATH, "w") as f:
                f.write(self.setup_code + "\n")
            log.warning("=" * 60)
            log.warning("FIRST RUN — open http://<this-host>:%s/admin/setup", WEB_PORT)
            log.warning("Setup code: %s   (also in %s)", self.setup_code, SETUP_CODE_PATH)
            log.warning("=" * 60)
        app = web.Application(middlewares=[self.guard])
        r = app.router
        r.add_get("/", self.page("index.html"))
        r.add_get("/admin", self.page("admin.html"))
        r.add_get("/admin/login", self.page("login.html"))
        r.add_get("/admin/setup", self.page("login.html"))
        r.add_static("/static/", WEB_DIR)
        r.add_get("/link", self.link)
        r.add_get("/api/public", self.api_public)
        r.add_post("/api/join", self.api_join)
        r.add_post("/api/admin/setup", self.admin_setup)
        r.add_post("/api/admin/login", self.admin_login)
        r.add_post("/api/admin/logout", self.admin_logout)
        r.add_post("/api/admin/password", self.admin_password)
        r.add_get("/api/admin/state", self.admin_state)
        r.add_post("/api/admin/bridge/{bid}", self.admin_bridge)
        r.add_post("/api/admin/room", self.admin_room)
        r.add_post("/api/admin/settings", self.admin_settings)
        r.add_get("/api/admin/ws", self.admin_ws)
        runner = web.AppRunner(app, access_log=None)
        await runner.setup()
        await web.TCPSite(runner, WEB_HOST, WEB_PORT).start()
        log.info("%s listening on http://%s:%s/", self.s["name"], WEB_HOST, WEB_PORT)
        asyncio.create_task(self.cleanup_loop())
        await asyncio.Event().wait()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        asyncio.run(Hub().main())
    except KeyboardInterrupt:
        pass
