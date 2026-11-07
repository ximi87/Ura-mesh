#!/usr/bin/env python3
"""ura-mesh-client — one point of Ura (Albanian for "bridge").

Sits next to a group's radio (Meshtastic and/or MeshCore). Messages heard on a *linked*
channel are relayed to the ura-mesh-server; messages from other approved points arrive from
the server and are put on the air here, through a rate-limited queue so local users are not
disturbed. Channel 0 (the local public channel) is never linked.

Privacy (see SPEC.md): message text is never stored or shown. Only statistics per point are
kept: counts, times, networks, rooms.

Admin page + statistics dashboard on WEB_PORT (default 8091). Settings: DATA_DIR/config.json.
"""
import asyncio
import hashlib
import json
import logging
import os
import re
import secrets
import sqlite3
import ssl
import sys
import time
import urllib.parse
import uuid
from collections import deque

import aiohttp
from aiohttp import web
from pubsub import pub

import meshtastic.serial_interface
import meshtastic.tcp_interface
from meshtastic import BROADCAST_ADDR
from meshtastic.protobuf import mesh_pb2, portnums_pb2
from meshcore import EventType, MeshCore

import auth
import config

log = logging.getLogger("ura-client")

VERSION = "0.4"
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
STATS_DB = os.path.join(config.DATA_DIR, "stats.db")
SETUP_CODE_PATH = os.path.join(config.DATA_DIR, "setup-code.txt")

LIMITS = {"mt": 200, "mc": 130}            # bytes on air
NET_NAMES = {"mt": "Meshtastic", "mc": "MeshCore"}
URA_PREFIX = re.compile(r"^\[(?:[A-Z]{2}|Ura)\] ")  # text a Ura point put on the air (relay or notice)
RF_QUEUE_MAX = 20
FEEDBACK_WAIT = 600        # seconds to wait for "heard" reports from other points
ACK_WAIT = 120             # seconds to wait for the radio to report an implicit ACK
NOTICE_EVERY = 600         # same notice to the same person / channel at most every 10 min
DM_WAIT = 300              # seconds to wait for the other places to answer a private message
POS_EVERY = 300            # send rounded positions every 5 min (if the checklist allows it)
POS_MAX_AGE = 7200         # only radios heard in the last 2 hours
DM_RE = re.compile(r"^@([^\s/]{1,40})(?:/(\S{1,40}))?\s+(.+)$", re.S)
DM_HELP = "Ura: to write to someone at another place, send me: @Name your message"
REACT = {"heard": "\u2705", "unconfirmed": "\U0001F4E1", "failed": "\u274C"}   # ✅ 📡 ❌
PUBLIC_ROOM = config.PUBLIC_ROOM
KEEP_DAYS = 90


def clip(text, limit):
    b = text.encode()
    return text if len(b) <= limit else b[: limit - 3].decode(errors="ignore") + "..."


def norm_fp(fp):
    """'AB:CD:…' or 'abcd…' → 64 lowercase hex characters ('' if not a SHA-256 fingerprint)."""
    h = re.sub(r"[^0-9a-fA-F]", "", fp or "").lower()
    return h if len(h) == 64 else ""


def pretty_fp(fp):
    h = norm_fp(fp)
    return ":".join(h[i:i + 2] for i in range(0, 64, 2)).upper() if h else ""


async def fetch_fingerprint(url):
    """Connect once without checking anything and read the server certificate's SHA-256 (trust on first use,
    confirmed by a human comparing it with the server admin page)."""
    u = urllib.parse.urlsplit(url)
    if u.scheme != "https" or not u.hostname:
        raise ValueError("the address must start with https://")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    reader, writer = await asyncio.wait_for(
        asyncio.open_connection(u.hostname, u.port or 443, ssl=ctx, server_hostname=u.hostname), 10)
    try:
        der = writer.get_extra_info("ssl_object").getpeercert(binary_form=True)
    finally:
        writer.close()
    return hashlib.sha256(der).hexdigest()


def clean_url(url):
    url = (url or "").strip().rstrip("/")
    if not re.match(r"^https?://[^/\s]+$", url):
        raise ValueError("server address must look like https://host:port")
    return url


def list_serial_ports():
    by_id = {}
    d = "/dev/serial/by-id"
    if os.path.isdir(d):
        for name in os.listdir(d):
            by_id[os.path.realpath(os.path.join(d, name))] = os.path.join(d, name)
    out = []
    try:
        from serial.tools import list_ports
        for p in list_ports.comports():
            if p.hwid not in (None, "n/a"):
                out.append({"path": by_id.get(p.device, p.device), "device": p.device,
                            "description": p.description or ""})
    except Exception as e:
        log.warning("listing serial ports failed: %s", e)
    return out


class Stats:
    """Counters per point. Never stores message text or person names."""

    def __init__(self, path):
        self.con = sqlite3.connect(path)
        self.con.execute("""CREATE TABLE IF NOT EXISTS events (
            ts REAL, kind TEXT, net TEXT, room TEXT, point_id TEXT, point_name TEXT, cc TEXT, info TEXT)""")
        self.con.execute("CREATE INDEX IF NOT EXISTS events_ts ON events(ts)")
        self.con.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
        # when public-channel measuring began (a silent channel must still count as measured time)
        self.con.execute("INSERT OR IGNORE INTO meta VALUES ('public_measure_since', ?)", (str(time.time()),))
        self.con.commit()

    def add(self, kind, net=None, room=None, point_id=None, point_name=None, cc=None, info=None):
        self.con.execute("INSERT INTO events VALUES (?,?,?,?,?,?,?,?)",
                         (time.time(), kind, net, room, point_id, point_name, cc, info))
        self.con.commit()

    def add_threadsafe(self, loop, kind, **kw):
        """For callbacks from the Meshtastic thread: sqlite is used from the event loop only."""
        loop.call_soon_threadsafe(lambda: self.add(kind, **kw))

    def public_rate(self, hours=24):
        """Average messages per hour heard on the local public channel(s) — no text, just a count."""
        since = time.time() - hours * 3600
        began = float(self.con.execute("SELECT value FROM meta WHERE key='public_measure_since'").fetchone()[0])
        first = self.con.execute("SELECT MIN(ts) FROM events WHERE kind='public_heard'").fetchone()[0]
        began = min(began, first) if first else began
        n = self.con.execute("SELECT COUNT(*) FROM events WHERE kind='public_heard' AND ts>=?", (since,)).fetchone()[0]
        measured = min(hours, (time.time() - began) / 3600)
        return {"per_hour": round(n / max(measured, 1), 2), "measured_hours": round(measured, 1), "count": n}

    def prune(self):
        self.con.execute("DELETE FROM events WHERE ts < ?", (time.time() - KEEP_DAYS * 86400,))
        self.con.commit()

    def summary(self, hours):
        since = time.time() - hours * 3600
        q = lambda sql, *a: self.con.execute(sql, (since,) + a).fetchall()
        totals = dict(q("SELECT kind, COUNT(*) FROM events WHERE ts>=? GROUP BY kind"))
        points = {}
        for pid, name, cc, kind, n, last in q(
                """SELECT point_id, MAX(point_name), MAX(cc), kind, COUNT(*), MAX(ts) FROM events
                   WHERE ts>=? AND point_id IS NOT NULL AND kind IN ('remote_in','sent_to','heard_remote')
                   GROUP BY point_id, kind"""):
            p = points.setdefault(pid, {"id": pid, "name": name, "cc": cc, "in": 0, "out": 0, "heard": 0,
                                        "last": 0})
            p[{"remote_in": "in", "sent_to": "out", "heard_remote": "heard"}[kind]] += n
            p["last"] = max(p["last"], last)
            p["name"], p["cc"] = name or p["name"], cc or p["cc"]
        nets = {}
        for net, kind, n in q("SELECT net, kind, COUNT(*) FROM events WHERE ts>=? AND net IS NOT NULL "
                              "GROUP BY net, kind"):
            nets.setdefault(net, {})[kind] = n
        refused = dict(q("SELECT info, COUNT(*) FROM events WHERE ts>=? AND kind='refused' GROUP BY info"))
        dropped = dict(q("SELECT info, COUNT(*) FROM events WHERE ts>=? AND kind='rf_drop' GROUP BY info"))
        bucket = 3600 if hours <= 48 else 86400
        series = {}
        for b, kind, n in q(f"""SELECT CAST(ts/{bucket} AS INTEGER)*{bucket}, kind, COUNT(*) FROM events
                                WHERE ts>=? AND kind IN ('local_in','remote_in') GROUP BY 1, 2"""):
            series.setdefault(b, {"t": b, "local_in": 0, "remote_in": 0})[kind] = n
        return {"hours": hours, "bucket": bucket, "totals": totals,
                "points": sorted(points.values(), key=lambda p: -(p["in"] + p["out"])),
                "nets": nets, "refused": refused, "dropped": dropped,
                "series": sorted(series.values(), key=lambda s: s["t"])}


class Client:
    def __init__(self):
        self.cfg = config.load()
        self.stats = Stats(STATS_DB)
        self.loop = None
        self.mt = None
        self.mt_id = None
        self.mc = None
        self.ws = None
        self.status = "off"            # server link: off / not joined / connecting / pending / approved / blocked / offline
        self.server_name = None
        self.rooms = []                # rooms the server offers this point
        self.limits = {}
        self.connected_since = None
        self.cert_problem = None
        self.public = {}
        self.backoff = 5
        self.pending = {}              # message id -> (room, net) for acks
        self.track = {}                # message id -> what we sent (for feedback to the local sender; no text)
        self.inbound = {}              # message id -> outcome of putting a remote message on the air here
        self.noticed = {}              # (who, reason) -> time of the last notice
        self.allowed = {}              # server owner's side of the checklist
        self.dmtrack = {}              # private message id -> who wrote it here (to answer them)
        self.mt_num = None
        self.rf_queue = deque(maxlen=RF_QUEUE_MAX)
        self.setup_code = None
        self.login_fail = {}
        self.restarting = False

    # ── settings shortcuts ───────────────────────────────────────
    @property
    def pc(self):
        return self.cfg["point"]

    @property
    def sc(self):
        return self.cfg["server"]

    def cc(self):
        return (self.pc["country"] or "XX").upper()

    def share(self, item):
        return bool((self.sc.get("share") or {}).get(item))

    def can(self, item):
        """Checklist: crosses only if this point's owner AND the server owner allow it."""
        return self.share(item) and bool(self.allowed.get(item))

    def room_for(self, net, channel):
        """Room a local channel sends to (None if not linked or its *send* switch is off)."""
        if channel == 0:
            return PUBLIC_ROOM if self.share("public") else None
        if not self.share("group"):
            return None
        key = "mt_channel" if net == "mt" else "mc_channel"
        for row in self.sc["links"]:
            if channel is not None and channel >= 0 and row.get(key) == channel:
                return row["room"] if row.get("send", True) else None
        return None

    def public_active(self):
        """The server decides (allowed + quiet enough); #Public is only offered while active."""
        return any(r["name"] == PUBLIC_ROOM for r in self.rooms) and self.server_ready()

    def room_channel(self, room, net):
        if not self.cfg["meshtastic" if net == "mt" else "meshcore"]["enabled"]:
            return None
        if room == PUBLIC_ROOM:   # paused / not allowed: nothing goes onto the local public channel
            return 0 if self.share("public") and self.public_active() else None
        if not self.share("group"):
            return None
        key = "mt_channel" if net == "mt" else "mc_channel"
        for row in self.sc["links"]:
            if row["room"] == room and row.get(key, -1) >= 0 and row.get("receive", True):
                return row[key]
        return None

    def linked_rooms(self):
        rooms = [row["room"] for row in self.sc["links"]] if self.share("group") else []
        return rooms + ([PUBLIC_ROOM] if self.share("public") else [])

    # ── relay ────────────────────────────────────────────────────
    def server_ready(self):
        return self.ws is not None and not self.ws.closed and self.status == "approved"

    async def heard(self, net, room, sender, text, origin=None):
        """Someone near us wrote on a linked channel. `origin` = where it came from on our radio (packet id,
        node id, channel) — only used to tell that person what happened, never sent to the server."""
        if URA_PREFIX.match(text):
            return   # already relayed by another Ura point — never send it back (no loops)
        origin = dict(origin or {}, net=net, room=room)
        self.stats.add("local_in", net=net, room=room)
        other = "mc" if net == "mt" else "mt"
        ch = self.room_channel(room, other)
        if ch is not None:   # both networks at this point: carry it across locally too
            self.rf_enqueue(other, ch, f"[{self.cc()}] {sender}: {text}")
        if not self.server_ready() or room not in {r["name"] for r in self.rooms}:
            self.stats.add("refused", net=net, room=room, info=f"server not available ({self.status})")
            self.feedback(origin, "failed", "Ura server not reachable, not sent")
            return
        mid = uuid.uuid4().hex
        self.pending[mid] = (room, net)
        self.track[mid] = {"origin": origin, "ts": time.time(), "points": {}, "results": {}, "done": False}
        try:
            await self.ws.send_json({"type": "msg", "id": mid, "room": room, "net": net,
                                     "sender": sender, "text": text})
        except Exception as e:
            self.pending.pop(mid, None)
            self.track.pop(mid, None)
            self.stats.add("refused", net=net, room=room, info="send failed")
            self.feedback(origin, "failed", "Ura server not reachable, not sent")
            log.warning("send to server failed: %s", e)

    async def from_server(self, f):
        """A message from another point: put it on the air on the linked channel(s), then report back
        whether a radio here confirmed it (heard / unheard / unknown / held)."""
        room = str(f.get("room") or "")
        mid = str(f.get("id") or "")
        if room not in self.linked_rooms():
            return
        fr = f.get("from") or {}
        cc = str(fr.get("country") or "XX").upper()
        self.stats.add("remote_in", room=room, point_id=fr.get("bridge_id"), point_name=fr.get("name"), cc=cc)
        line = f"[{cc}] {str(f.get('sender') or '?')[:40]}: {str(f.get('text') or '')}"
        chans = [(net, self.room_channel(room, net)) for net in ("mt", "mc")]
        chans = [(net, ch) for net, ch in chans if ch is not None]
        if not chans:
            await self.report(mid, "held", f"{self.pc['name']}: channel not open for receiving")
            return
        self.inbound[mid] = {"left": len(chans), "outcomes": [], "ts": time.time()}
        for net, ch in chans:
            self.rf_enqueue(net, ch, line, mid=mid)

    def inbound_done(self, mid, outcome, reason=None):
        """One network finished with a remote message: heard / unheard / unknown / held."""
        e = self.inbound.get(mid)
        if not e:
            return
        e["outcomes"].append((outcome, reason))
        e["left"] -= 1
        if e["left"] > 0:
            return
        self.inbound.pop(mid, None)
        kinds = [o for o, _ in e["outcomes"]]
        for best in ("heard", "unheard", "unknown"):
            if best in kinds:
                asyncio.ensure_future(self.report(mid, best))
                return
        reasons = "; ".join(sorted({r for o, r in e["outcomes"] if r}))
        asyncio.ensure_future(self.report(mid, "held", reasons or "held back"))

    async def report(self, mid, outcome, reason=None):
        if mid and self.server_ready():
            try:
                await self.ws.send_json({"type": "result", "id": mid, "outcome": outcome, "reason": reason})
            except Exception:
                pass

    def ack(self, f):
        mid = f.get("id")
        room, net = self.pending.pop(mid, (None, None))
        if room is None:
            return
        t = self.track.get(mid)
        if f.get("ok"):
            for p in f.get("to_points") or []:
                self.stats.add("sent_to", net=net, room=room, point_id=p.get("id"), point_name=p.get("name"),
                               cc=p.get("country"))
                if t:
                    t["points"][p.get("id")] = p
            if not f.get("to_points"):
                self.stats.add("sent_nobody", net=net, room=room)
                if t:
                    self.finish(mid, "failed", f"no other point is online in #{room}")
            elif t:
                self.loop.call_later(FEEDBACK_WAIT, self.finish_timeout, mid)
        else:
            reason = str(f.get("reason") or "?")[:80]
            self.stats.add("refused", net=net, room=room, info=reason[:60])
            if t:
                self.finish(mid, "failed", "not sent: " + reason)

    def result(self, f):
        """Another point reports what happened on its air with a message we sent."""
        mid = f.get("id")
        t = self.track.get(mid)
        p = f.get("point") or {}
        outcome = f.get("outcome")
        if outcome == "heard":
            self.stats.add("heard_remote", net=t["origin"]["net"] if t else None,
                           room=t["origin"]["room"] if t else None,
                           point_id=p.get("id"), point_name=p.get("name"), cc=p.get("country"))
        if not t or t["done"]:
            return
        t["results"][p.get("id")] = (outcome, f.get("reason"), p.get("name") or "?")
        if outcome == "heard":
            self.finish(mid, "heard")
        elif t["points"] and set(t["points"]) <= set(t["results"]):
            self.finish_all(mid)

    def finish_timeout(self, mid):
        t = self.track.get(mid)
        if t and not t["done"]:
            self.finish_all(mid)
        self.track.pop(mid, None)

    def finish_all(self, mid):
        """All points answered (or time is up) and nobody confirmed hearing it."""
        t = self.track[mid]
        res = t["results"].values()
        if any(o in ("unheard", "unknown") for o, _, _ in res) or len(res) < len(t["points"]):
            self.finish(mid, "unconfirmed")
        else:
            why = "; ".join(sorted({r or f"held back at {n}" for o, r, n in res}))
            self.finish(mid, "failed", "not put on the air: " + why)

    def finish(self, mid, verdict, why=None):
        t = self.track.get(mid)
        if not t or t["done"]:
            return
        t["done"] = True
        self.feedback(t["origin"], verdict, why)

    def feedback(self, origin, verdict, why=None):
        """Tell the person who wrote what happened: a reaction on their message (Meshtastic), plus a short
        direct message / channel notice when it did not go through. Never relayed (see URA_PREFIX)."""
        if not self.sc.get("notify", True) or not origin:
            return
        net, ch = origin.get("net"), origin.get("channel")
        if net == "mt" and origin.get("pkt_id") and ch is not None:
            self.rf_enqueue("mt", ch, REACT[verdict], kind="react", reply_id=origin["pkt_id"])
        if verdict != "failed" or not why:
            return
        who = origin.get("from_id") if net == "mt" else f"ch{ch}"
        key = (who, re.sub(r"[\d.]+", "#", why))   # same kind of reason → one notice per 10 min
        if time.time() - self.noticed.get(key, 0) < NOTICE_EVERY:
            return
        self.noticed[key] = time.time()
        if net == "mt" and origin.get("from_id"):
            self.rf_enqueue("mt", ch, f"Ura: {why}", kind="dm", dest=origin["from_id"])
        elif net == "mc" and ch is not None:
            self.rf_enqueue("mc", ch, f"[Ura] {why}", kind="notice")

    def air(self):
        """Airtime of our Meshtastic radio, as the radio itself reports it (percent)."""
        try:
            m = (self.mt.nodes or {}).get(self.mt_id, {}).get("deviceMetrics", {}) if self.mt else {}
        except Exception:
            m = {}
        cu, tx = m.get("channelUtilization"), m.get("airUtilTx")
        return {"ch_util": round(cu, 1) if cu is not None else None,
                "air_tx": round(tx, 1) if tx is not None else None}

    def busy(self, net):
        """Why the local channel should not get more Ura traffic now (None = fine)."""
        if net != "mt":
            return None   # MeshCore does not report airtime: only the radio limit applies
        a = self.air()
        if a["ch_util"] is not None and a["ch_util"] > self.sc["max_busy_pct"]:
            return f"{self.pc['name']} channel busy ({a['ch_util']:.0f}% > {self.sc['max_busy_pct']}%)"
        if a["air_tx"] is not None and a["air_tx"] > self.sc["max_tx_pct"]:
            return f"{self.pc['name']} radio airtime used ({a['air_tx']:.1f}% > {self.sc['max_tx_pct']}%)"
        return None

    def rf_enqueue(self, net, channel, text, kind="relay", mid=None, **extra):
        item = dict(extra, net=net, channel=channel, text=clip(text, LIMITS[net]), kind=kind, mid=mid)
        if kind not in ("relay", "pm"):   # feedback is tiny and should be timely: ahead of relayed messages, in order
            i = next((n for n, x in enumerate(self.rf_queue) if x["kind"] == "relay"), len(self.rf_queue))
            if len(self.rf_queue) == self.rf_queue.maxlen:
                return
            self.rf_queue.insert(i, item)
            return
        if len(self.rf_queue) == self.rf_queue.maxlen:   # full: drop the oldest relayed message
            old = next((i for i in self.rf_queue if i["kind"] == "relay"), self.rf_queue[0])
            self.rf_queue.remove(old)
            self.stats.add("rf_drop", net=old["net"], info="queue full")
            if old.get("mid"):
                self.inbound_done(old["mid"], "held", f"{self.pc['name']}: too many messages waiting")
        self.rf_queue.append(item)

    def mt_send_relay(self, item):
        """Broadcast with want_ack: the radio reports an implicit ACK when a neighbour repeats it (= heard)."""
        mid, done = item["mid"], []

        def settle(outcome):
            if not done:
                done.append(outcome)
                self.stats.add("rf_" + outcome, net="mt")
                self.inbound_done(mid, outcome)

        def on_resp(packet):
            err = ((packet.get("decoded") or {}).get("routing") or {}).get("errorReason", "NONE")
            self.loop.call_soon_threadsafe(settle, "heard" if err == "NONE" else "unheard")

        self.mt.sendData(item["text"].encode(), BROADCAST_ADDR, portNum=portnums_pb2.PortNum.TEXT_MESSAGE_APP,
                         wantAck=bool(mid), onResponse=on_resp if mid else None, onResponseAckPermitted=True,
                         channelIndex=item["channel"])
        if mid:
            self.loop.call_soon_threadsafe(self.loop.call_later, ACK_WAIT, settle, "unheard")

    def mt_send_react(self, item):
        p = mesh_pb2.MeshPacket()
        p.channel = item["channel"]
        p.decoded.portnum = portnums_pb2.PortNum.TEXT_MESSAGE_APP
        p.decoded.payload = item["text"].encode()
        p.decoded.reply_id = item["reply_id"]
        p.decoded.emoji = 1
        p.id = self.mt._generatePacketId()
        self.mt._sendPacket(p, BROADCAST_ADDR, wantAck=False)

    # ── public channel paused / open ─────────────────────────────
    def public_changed(self, before, now):
        """Tell the whole group once when its public-channel link pauses or opens again."""
        if not self.share("public") or before == now or not self.sc.get("notify", True):
            return
        if before == "active" and now == "too busy":
            text = "[Ura] Link to other places paused - this channel is too busy. Private messages still work."
        elif before == "too busy" and now == "active":
            text = "[Ura] Link to other places is open again."
        else:
            return
        log.info("public channel %s", "paused" if now == "too busy" else "open again")
        for net, key in (("mt", "meshtastic"), ("mc", "meshcore")):
            if self.cfg[key]["enabled"]:
                self.rf_enqueue(net, 0, text, kind="notice")

    def public_paused_notice(self, net, who, channel):
        """Someone wrote on the public channel while its link is paused: tell them (once per hour)."""
        if not self.share("public") or not self.sc.get("notify", True) or net != "mt" or not who:
            return
        if (self.public or {}).get("status") != "too busy":
            return
        key = (who, "public paused")
        if time.time() - self.noticed.get(key, 0) < 3600:
            return
        self.noticed[key] = time.time()
        self.rf_enqueue("mt", channel or 0, "Ura: the link to other places is paused (this channel is too busy). "
                        "Private messages still work: send me @Name text", kind="dm", dest=who)

    # ── private messages ─────────────────────────────────────────
    def reply_local(self, net, who, channel, text):
        """Direct message back to the person here who wrote to this point."""
        if net == "mt":
            self.rf_enqueue("mt", channel or 0, text, kind="dm", dest=who)
        else:
            self.rf_enqueue("mc", None, text, kind="dm", dest=who)

    async def dm_from_local(self, net, who, name, text, channel):
        """Someone here sent a direct message to this point's radio: '@Name text' goes to the other places."""
        if URA_PREFIX.match(text):
            return
        if not self.can("private"):
            key = (who, "private off")
            if time.time() - self.noticed.get(key, 0) > NOTICE_EVERY:
                self.noticed[key] = time.time()
                self.reply_local(net, who, channel, "Ura: private messages to other places are not enabled here.")
            return
        m = DM_RE.match(text.strip())
        if not m:
            self.reply_local(net, who, channel, DM_HELP)
            return
        to, place, body = m.group(1), m.group(2) or "", m.group(3).strip()
        if not self.server_ready():
            self.reply_local(net, who, channel, "Ura: server not reachable, not sent.")
            return
        mid = uuid.uuid4().hex
        self.dmtrack[mid] = {"net": net, "who": who, "channel": channel, "to": to, "ts": time.time(), "done": False}
        self.stats.add("dm_out", net=net, room="(private)")
        try:
            await self.ws.send_json({"type": "dm", "id": mid, "to": to, "place": place, "net": net,
                                     "sender": name[:40], "text": body})
        except Exception:
            self.dmtrack.pop(mid, None)
            self.reply_local(net, who, channel, "Ura: server not reachable, not sent.")
            return
        self.loop.call_later(DM_WAIT, self.dm_timeout, mid)

    def dm_answer(self, mid, text):
        t = self.dmtrack.get(mid)
        if t and not t["done"]:
            t["done"] = True
            self.reply_local(t["net"], t["who"], t["channel"], text)

    def dm_ack(self, f):
        if not f.get("ok"):
            self.stats.add("refused", room="(private)", info=str(f.get("reason") or "?")[:60])
            self.dm_answer(f.get("id"), "Ura: not sent: " + str(f.get("reason") or "?")[:100])

    def dm_result(self, f):
        t = self.dmtrack.get(f.get("id"))
        if not t:
            return
        p = f.get("point") or {}
        place = p.get("name") or "?"
        o = f.get("outcome")
        if o in ("delivered", "sent"):
            self.stats.add("sent_to", room="(private)", point_id=p.get("id"), point_name=p.get("name"),
                           cc=p.get("country"))
        if o == "delivered":
            self.stats.add("heard_remote", room="(private)", point_id=p.get("id"), point_name=p.get("name"),
                           cc=p.get("country"))
        self.dm_answer(f.get("id"), {
            "delivered": f"Ura: \u2713 delivered to {t['to']} at {place}",
            "sent": f"Ura: sent to {t['to']} at {place} (no confirmation yet)",
            "notfound": f"Ura: nobody called {t['to']} is heard at the other places",
        }.get(o) or "Ura: not sent: " + str(f.get("reason") or "held back")[:100])

    def dm_timeout(self, mid):
        self.dm_answer(mid, "Ura: no answer from the other places, not delivered.")
        self.dmtrack.pop(mid, None)

    def find_local(self, name):
        """A radio here with that name (Meshtastic long/short name or node id, MeshCore contact name)."""
        n = name.lower()
        if self.mt is not None:
            best = None
            for nid, node in (self.mt.nodes or {}).items():
                u = node.get("user") or {}
                if nid == self.mt_id:
                    continue
                if n in ((u.get("longName") or "").lower(), (u.get("shortName") or "").lower(), nid.lower()):
                    if best is None or (node.get("lastHeard") or 0) > (best[1].get("lastHeard") or 0):
                        best = (nid, node)
            if best:
                return "mt", best[0]
        if self.mc is not None:
            for c in (self.mc.contacts or {}).values():
                if (c.get("adv_name") or "").lower() == n:
                    return "mc", c.get("public_key", "")[:12]
        return None, None

    async def dm_from_server(self, f):
        """A private message from another place for someone here."""
        mid = str(f.get("id") or "")
        if not self.can("private"):
            await self.dm_report(mid, "held", f"{self.pc['name']}: private messages not enabled")
            return
        net, dest = self.find_local(str(f.get("to") or ""))
        if not net:
            await self.dm_report(mid, "notfound")
            return
        fr = f.get("from") or {}
        cc = str(fr.get("country") or "XX").upper()
        self.stats.add("dm_in", net=net, room="(private)", point_id=fr.get("bridge_id"),
                       point_name=fr.get("name"), cc=cc)
        self.rf_enqueue(net, 0, f"[{cc}] {str(f.get('sender') or '?')[:40]}: {str(f.get('text') or '')}",
                        kind="pm", mid=mid, dest=dest)

    async def dm_report(self, mid, outcome, reason=None):
        if mid and self.server_ready():
            try:
                await self.ws.send_json({"type": "dm_result", "id": mid, "outcome": outcome, "reason": reason})
            except Exception:
                pass

    def mt_send_pm(self, item):
        """Direct message with want_ack: an ACK from the recipient itself = delivered."""
        mid, dest, done = item["mid"], item["dest"], []
        dest_num = int(dest[1:], 16) if dest.startswith("!") else None

        def settle(outcome):
            if not done:
                done.append(outcome)
                asyncio.ensure_future(self.dm_report(mid, outcome))

        def on_resp(packet):
            err = ((packet.get("decoded") or {}).get("routing") or {}).get("errorReason", "NONE")
            ok = err == "NONE" and packet.get("from") == dest_num
            self.loop.call_soon_threadsafe(settle, "delivered" if ok else "sent")

        self.mt.sendData(item["text"].encode(), dest, portNum=portnums_pb2.PortNum.TEXT_MESSAGE_APP,
                         wantAck=True, onResponse=on_resp, onResponseAckPermitted=True,
                         channelIndex=item["channel"] or 0)
        self.loop.call_soon_threadsafe(self.loop.call_later, ACK_WAIT, settle, "sent")

    async def mc_send_pm(self, contact, item):
        try:
            r = await self.mc.commands.send_msg_with_retry(contact, item["text"])
            await self.dm_report(item["mid"], "delivered" if r is not None else "sent")
        except Exception as e:
            log.warning("MeshCore private message failed: %s", e)
            await self.dm_report(item["mid"], "held", f"{self.pc['name']}: radio error")

    # ── positions (rounded, no names, server map only) ───────────
    def positions(self):
        out, now = set(), time.time()
        if self.mt is not None:
            for node in (self.mt.nodes or {}).values():
                pos = node.get("position") or {}
                lat, lon = pos.get("latitude"), pos.get("longitude")
                if lat and lon and now - (node.get("lastHeard") or 0) < POS_MAX_AGE:
                    out.add((round(lat / 0.02) * 0.02, round(lon / 0.02) * 0.02, "mt"))
        if self.mc is not None:
            for c in (self.mc.contacts or {}).values():
                lat, lon = c.get("adv_lat"), c.get("adv_lon")
                if lat and lon and now - (c.get("last_advert") or 0) < POS_MAX_AGE:
                    out.add((round(lat / 0.02) * 0.02, round(lon / 0.02) * 0.02, "mc"))
        return [[round(a, 2), round(b, 2), n] for a, b, n in out][:500]

    async def positions_loop(self):
        while True:
            await asyncio.sleep(POS_EVERY)
            if self.server_ready() and self.can("positions"):
                try:
                    await self.ws.send_json({"type": "positions", "list": self.positions()})
                except Exception:
                    pass

    async def rf_worker(self):
        """Puts relayed messages on the air, at most rf_per_min per minute, and only while the local channel
        is not busy (airtime rule). Feedback (reactions / notices) goes first and is not counted."""
        while True:
            per_min = self.sc["rf_per_min"]
            if not self.rf_queue:
                await asyncio.sleep(1)
                continue
            item = self.rf_queue.popleft()
            net, channel, kind, mid = item["net"], item["channel"], item["kind"], item.get("mid")
            if kind in ("relay", "pm"):
                held = "radio limit is 0" if per_min <= 0 else self.busy(net)
                if held:
                    self.stats.add("rf_drop", net=net, info="channel busy" if per_min > 0 else held)
                    if mid and kind == "pm":
                        asyncio.ensure_future(self.dm_report(mid, "held", held))
                    elif mid:
                        self.inbound_done(mid, "held", held)
                    continue
            try:
                if net == "mt" and self.mt is not None:
                    if kind == "react":
                        await asyncio.to_thread(self.mt_send_react, item)
                    elif kind == "dm":
                        await asyncio.to_thread(self.mt.sendText, item["text"], item["dest"],
                                                wantAck=False, channelIndex=channel)
                    elif kind == "pm":
                        await asyncio.to_thread(self.mt_send_pm, item)
                    else:
                        await asyncio.to_thread(self.mt_send_relay, item)
                elif net == "mc" and self.mc is not None and self.mc.is_connected and kind in ("pm", "dm"):
                    contact = self.mc.get_contact_by_key_prefix(item["dest"])
                    if contact is None:
                        raise RuntimeError("contact not known")
                    if kind == "pm":
                        asyncio.ensure_future(self.mc_send_pm(contact, item))
                    else:
                        await self.mc.commands.send_msg(contact, item["text"])
                elif net == "mc" and self.mc is not None and self.mc.is_connected:
                    r = await self.mc.commands.send_chan_msg(channel, item["text"])
                    if r.type == EventType.ERROR:
                        raise RuntimeError(r.payload)
                    if mid:
                        self.inbound_done(mid, "unknown")   # MeshCore cannot tell whether anyone heard it
                else:
                    self.stats.add("rf_drop", net=net, info="radio not connected")
                    if mid and kind == "pm":
                        asyncio.ensure_future(self.dm_report(mid, "held", f"{self.pc['name']}: radio not connected"))
                    elif mid:
                        self.inbound_done(mid, "held", f"{self.pc['name']}: radio not connected")
                    continue
                self.stats.add("rf_tx" if kind == "relay" else "rf_feedback", net=net)
            except Exception as e:
                self.stats.add("rf_drop", net=net, info="radio error")
                if mid and kind == "pm":
                    asyncio.ensure_future(self.dm_report(mid, "held", f"{self.pc['name']}: radio error"))
                elif mid:
                    self.inbound_done(mid, "held", f"{self.pc['name']}: radio error")
                log.warning("transmit on %s ch%s failed: %s", net, channel, e)
            await asyncio.sleep(60 / per_min if kind in ("relay", "pm") and per_min > 0 else 3)

    # ── Meshtastic ───────────────────────────────────────────────
    def mt_on_text(self, packet, interface):
        try:
            if packet.get("fromId") == self.mt_id:
                return   # our own packets are never relayed
            channel = packet.get("channel", 0)
            if packet.get("decoded", {}).get("emoji"):
                return   # reactions (tapbacks) are never relayed or counted
            text = packet.get("decoded", {}).get("text", "")
            if packet.get("to") == self.mt_num and self.mt_num is not None:
                if text and packet.get("fromId"):
                    node = (interface.nodes or {}).get(packet["fromId"], {})
                    name = node.get("user", {}).get("longName") or packet["fromId"]
                    asyncio.run_coroutine_threadsafe(
                        self.dm_from_local("mt", packet["fromId"], name, text, channel), self.loop)
                return
            if packet.get("to") != 0xFFFFFFFF:
                return
            if channel == 0 and not URA_PREFIX.match(text):
                # count only (public-channel rule); text relayed by Ura itself is not local traffic
                self.stats.add_threadsafe(self.loop, "public_heard", net="mt")
            room = self.room_for("mt", channel)
            if room == PUBLIC_ROOM and not self.public_active():
                self.loop.call_soon_threadsafe(self.public_paused_notice, "mt", packet.get("fromId"), channel)
                return
            if room is None:
                return   # not linked
            node = interface.nodes.get(packet.get("fromId") or "", {}) if interface.nodes else {}
            sender = node.get("user", {}).get("longName") or packet.get("fromId") or "?"
            if text:
                origin = {"pkt_id": packet.get("id"), "from_id": packet.get("fromId"), "channel": channel}
                asyncio.run_coroutine_threadsafe(self.heard("mt", room, sender, text, origin), self.loop)
        except Exception:
            log.exception("mt_on_text")

    def mt_on_lost(self, interface, topic=pub.AUTO_TOPIC):
        log.warning("meshtastic connection lost")
        self.mt = None

    def mt_connect(self):
        c = self.cfg["meshtastic"]
        if c["connection"] == "serial":
            return meshtastic.serial_interface.SerialInterface(c["serial_port"])
        return meshtastic.tcp_interface.TCPInterface(c["host"])

    async def mt_keepalive(self):
        if not self.cfg["meshtastic"]["enabled"]:
            return
        pub.subscribe(self.mt_on_text, "meshtastic.receive.text")
        pub.subscribe(self.mt_on_lost, "meshtastic.connection.lost")
        while True:
            if self.mt is None:
                try:
                    self.mt = await asyncio.to_thread(self.mt_connect)
                    self.mt_id = self.mt.getMyNodeInfo()["user"]["id"]
                    self.mt_num = self.mt.myInfo.my_node_num
                    log.info("meshtastic connected as %s", self.mt_id)
                except Exception as e:
                    log.warning("meshtastic connect failed: %s", e)
                    self.mt = None
            await asyncio.sleep(30)

    # ── MeshCore ─────────────────────────────────────────────────
    async def mc_on_chan(self, event):
        p = event.payload
        raw = p.get("text", "")
        if p.get("channel_idx") == 0 and not URA_PREFIX.match(raw.partition(": ")[2] or raw):
            self.stats.add("public_heard", net="mc")   # count only (public-channel rule)
        room = self.room_for("mc", p.get("channel_idx"))
        if room == PUBLIC_ROOM and not self.public_active():
            self.public_paused_notice("mc", None, 0)
            return
        if room is None:
            return
        sender, _, text = raw.partition(": ")   # channel text arrives as "Name: msg"
        if not text:
            sender, text = "?", raw
        if text:
            await self.heard("mc", room, sender, text, {"channel": p.get("channel_idx")})

    async def mc_on_dm(self, event):
        p = event.payload
        prefix, text = p.get("pubkey_prefix"), p.get("text", "")
        if not prefix or not text or p.get("txt_type", 0) != 0:
            return
        c = self.mc.get_contact_by_key_prefix(prefix) if self.mc else None
        await self.dm_from_local("mc", prefix, (c or {}).get("adv_name") or prefix, text, None)

    async def mc_connect(self):
        c = self.cfg["meshcore"]
        if c["connection"] == "tcp":
            return await MeshCore.create_tcp(c["host"], c["tcp_port"])
        return await MeshCore.create_serial(c["serial_port"], c["baudrate"])

    async def mc_keepalive(self):
        if not self.cfg["meshcore"]["enabled"]:
            return
        while True:
            if self.mc is None or not self.mc.is_connected:
                try:
                    mc = await self.mc_connect()
                    if mc is None:
                        raise RuntimeError("no response")
                    mc.subscribe(EventType.CHANNEL_MSG_RECV, self.mc_on_chan)
                    mc.subscribe(EventType.CONTACT_MSG_RECV, self.mc_on_dm)
                    for row in self.sc["links"]:
                        if row.get("mc_channel", -1) >= 0:
                            await mc.commands.get_channel(row["mc_channel"])
                    await mc.start_auto_message_fetching()
                    self.mc = mc
                    log.info("meshcore connected: %s", mc.self_info.get("name"))
                except Exception as e:
                    log.warning("meshcore connect failed: %s", e)
                    self.mc = None
            await asyncio.sleep(30)

    # ── server link ──────────────────────────────────────────────
    def point_info(self):
        p = self.pc
        return {"name": p["name"], "country": p["country"], "city": p["city"], "lat": p["lat"], "lon": p["lon"],
                "contact": p["contact"],
                "networks": [n for n, k in (("mt", "meshtastic"), ("mc", "meshcore")) if self.cfg[k]["enabled"]]}

    def ws_url(self):
        return re.sub(r"^http", "ws", self.sc["url"].rstrip("/")) + "/link"

    def ssl_param(self, url=None, fp=None):
        """https → accept only the pinned certificate; http → no encryption (warned about on every page)."""
        url = url or self.sc["url"]
        if not url.startswith("https://"):
            return None
        h = norm_fp(fp if fp is not None else self.sc["fingerprint"])
        if not h:
            raise ValueError("no pinned certificate fingerprint — check the server certificate first")
        return aiohttp.Fingerprint(bytes.fromhex(h))

    async def frame(self, f):
        t = f.get("type")
        if t in ("welcome", "status"):
            prev = self.status
            prev_pub = (self.public or {}).get("status")
            self.status = f.get("status") or "?"
            self.allowed = f.get("allow") or {}
            self.server_name = f.get("hub")
            self.rooms = f.get("rooms") or []
            self.limits = f.get("limits") or {}
            self.public = f.get("public") or {}
            self.backoff = 5
            if prev != self.status:
                log.info("server %s: this point is %s", self.server_name, self.status)
            self.public_changed(prev_pub, self.public.get("status"))
        elif t == "error":
            self.status = "refused: " + str(f.get("reason"))
        elif t == "msg":
            await self.from_server(f)
        elif t == "ack":
            self.ack(f)
        elif t == "result":
            self.result(f)
        elif t == "dm":
            await self.dm_from_server(f)
        elif t == "dm_ack":
            self.dm_ack(f)
        elif t == "dm_result":
            self.dm_result(f)

    async def server_loop(self):
        s = self.sc
        if not s["enabled"]:
            return
        if not (s["url"] and s["point_id"] and s["key"]):
            self.status = "not joined"
            return
        async with aiohttp.ClientSession() as session:
            while True:
                if self.status in ("off", "offline"):
                    self.status = "connecting"
                try:
                    async with session.ws_connect(self.ws_url(), heartbeat=30, ssl=self.ssl_param()) as ws:
                        await ws.send_json({"type": "hello", "bridge_id": s["point_id"], "key": s["key"],
                                            "version": 1, "client": VERSION, "info": self.point_info(),
                                            "share": self.sc.get("share") or {}})
                        self.ws = ws
                        self.connected_since = time.time()
                        log.info("connected to server %s", self.ws_url())
                        async for m in ws:
                            if m.type == aiohttp.WSMsgType.TEXT:
                                try:
                                    await self.frame(json.loads(m.data))
                                except Exception:
                                    log.exception("server frame")
                            elif m.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                                break
                except aiohttp.ServerFingerprintMismatch as e:
                    self.cert_problem = ("the server presented a DIFFERENT certificate than the one pinned "
                                         f"({pretty_fp(e.got.hex())}) — not connecting")
                    self.status = "certificate mismatch"
                    log.error("certificate mismatch: expected %s got %s", pretty_fp(e.expected.hex()), pretty_fp(e.got.hex()))
                except Exception as e:
                    log.warning("server connection failed: %s", e)
                else:
                    self.cert_problem = None
                self.ws = None
                self.connected_since = None
                if self.status == "approved":
                    self.status = "offline"
                wait = 600 if self.status in ("blocked", "certificate mismatch") or self.status.startswith("refused") \
                    else self.backoff
                self.backoff = min(self.backoff * 2, 120)
                await asyncio.sleep(wait)

    async def report_loop(self):
        """Tell the server how many nodes this point hears (a number only, no names or positions)."""
        n = 0
        while True:
            await asyncio.sleep(30 if n == 0 else 60)
            if self.server_ready():
                try:
                    await self.ws.send_json({"type": "nodes", "count": self.node_count(), "shared": [],
                                             "public_rate": self.stats.public_rate(1),
                                             "share": self.sc.get("share") or {},
                                             "air": dict(self.air(), busy=self.busy("mt"))})
                except Exception:
                    pass
            if n % 60 == 0:
                self.stats.prune()
                cutoff = time.time() - 2 * FEEDBACK_WAIT
                for d in (self.track, self.inbound, self.dmtrack):
                    for k in [k for k, v in d.items() if v["ts"] < cutoff]:
                        d.pop(k, None)
            n += 1

    def node_count(self):
        n = 0
        if self.mt is not None and self.mt.nodes:
            n += max(0, len(self.mt.nodes) - 1)
        if self.mc is not None:
            n += len(self.mc.contacts or {})
        return n

    # ── web: auth ────────────────────────────────────────────────
    def logged_in(self, request):
        a = self.cfg["auth"]
        return auth.valid_session(request.cookies.get(auth.COOKIE), a["session_secret"], a["password_hash"])

    @web.middleware
    async def guard(self, request, handler):
        path = request.path
        is_api = path.startswith("/api/")
        if path.startswith("/static/"):
            return await handler(request)
        if not self.cfg["auth"]["password_hash"]:
            if path in ("/setup", "/api/setup"):
                return await handler(request)
            if is_api:
                raise web.HTTPForbidden(text="setup required")
            raise web.HTTPFound("setup")
        if path in ("/login", "/api/login") or self.logged_in(request):
            return await handler(request)
        if is_api:
            raise web.HTTPUnauthorized(text="login required")
        raise web.HTTPFound("login")

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
        a = self.cfg["auth"]
        resp.set_cookie(auth.COOKIE, auth.make_session(a["session_secret"], a["password_hash"]),
                        max_age=auth.SESSION_DAYS * 86400, httponly=True, samesite="Strict",
                        secure=request.secure)

    async def web_setup(self, request):
        body = await self.json_body(request)
        if self.cfg["auth"]["password_hash"]:
            raise web.HTTPConflict(text="already set up")
        if not secrets.compare_digest(str(body.get("code", "")).strip().upper(), self.setup_code or "-"):
            await asyncio.sleep(1)
            raise web.HTTPForbidden(text="wrong setup code — see the log or data/setup-code.txt")
        pw = body.get("password") or ""
        if len(pw) < 8:
            raise web.HTTPBadRequest(text="password must be at least 8 characters")
        self.cfg["auth"]["password_hash"] = auth.hash_password(pw)
        config.save(self.cfg)
        self.setup_code = None
        try:
            os.remove(SETUP_CODE_PATH)
        except OSError:
            pass
        resp = web.json_response({"ok": True})
        self.set_session(resp, request)
        return resp

    async def web_login(self, request):
        body = await self.json_body(request)
        ip = request.remote or "?"
        n, first = self.login_fail.get(ip, (0, time.time()))
        if time.time() - first > 900:
            n, first = 0, time.time()
        if n >= 10:
            raise web.HTTPTooManyRequests(text="too many attempts, try again in 15 minutes")
        if not auth.check_password(str(body.get("password", "")), self.cfg["auth"]["password_hash"]):
            self.login_fail[ip] = (n + 1, first)
            await asyncio.sleep(1)
            raise web.HTTPForbidden(text="wrong password")
        self.login_fail.pop(ip, None)
        resp = web.json_response({"ok": True})
        self.set_session(resp, request)
        return resp

    async def web_logout(self, request):
        resp = web.json_response({"ok": True})
        resp.del_cookie(auth.COOKIE)
        return resp

    async def web_password(self, request):
        body = await self.json_body(request)
        if not auth.check_password(str(body.get("current", "")), self.cfg["auth"]["password_hash"]):
            await asyncio.sleep(1)
            raise web.HTTPForbidden(text="current password is wrong")
        if len(body.get("new") or "") < 8:
            raise web.HTTPBadRequest(text="password must be at least 8 characters")
        self.cfg["auth"]["password_hash"] = auth.hash_password(body["new"])
        config.save(self.cfg)
        resp = web.json_response({"ok": True})
        self.set_session(resp, request)
        return resp

    # ── web: state, stats, settings ──────────────────────────────
    def state(self):
        mt, mc = self.cfg["meshtastic"], self.cfg["meshcore"]
        return {
            "version": VERSION,
            "point": {k: self.pc[k] for k in ("name", "country", "city")},
            "server": {"enabled": self.sc["enabled"], "status": self.status, "name": self.server_name,
                       "url": self.sc["url"], "encrypted": self.sc["url"].startswith("https://"),
                       "fingerprint": pretty_fp(self.sc["fingerprint"]), "cert_problem": self.cert_problem,
                       "point_id": self.sc["point_id"], "connected_since": self.connected_since,
                       "rooms": [r["name"] for r in self.rooms], "linked": self.sc["links"],
                       "limits": self.limits},
            "radios": {
                "mt": {"enabled": mt["enabled"], "connected": self.mt is not None, "id": self.mt_id},
                "mc": {"enabled": mc["enabled"], "connected": bool(self.mc and self.mc.is_connected),
                       "name": (self.mc.self_info or {}).get("name") if self.mc else None},
            },
            "nodes_heard": self.node_count(),
            "public_rate": self.stats.public_rate(1),
            "public": dict(self.public, linked=any(r["room"] == PUBLIC_ROOM for r in self.sc["links"]),
                           active=self.public_active()),
            "rf": {"per_min": self.sc["rf_per_min"], "queued": len(self.rf_queue), "queue_max": RF_QUEUE_MAX},
            "air": dict(self.air(), busy=self.busy("mt"), max_busy_pct=self.sc["max_busy_pct"],
                        max_tx_pct=self.sc["max_tx_pct"]),
            "notify": self.sc.get("notify", True),
            "checklist": {k: {"point": self.share(k), "server": bool(self.allowed.get(k)), "on": self.can(k)}
                          for k in ("group", "public", "private", "positions")},
        }

    async def web_state(self, request):
        return web.json_response(self.state())

    async def web_stats(self, request):
        try:
            hours = max(1, min(int(request.query.get("hours", "24")), 24 * KEEP_DAYS))
        except ValueError:
            hours = 24
        return web.json_response(self.stats.summary(hours))

    async def web_config_get(self, request):
        return web.json_response({"config": config.public_view(self.cfg), "serial_ports": list_serial_ports(),
                                  "data_dir": config.DATA_DIR, "state": self.state()})

    async def web_config_put(self, request):
        body = await self.json_body(request)
        try:
            new = config.apply_update(self.cfg, body)
        except ValueError as e:
            raise web.HTTPBadRequest(text=str(e))
        config.save(new)
        self.cfg = new
        log.info("settings saved, restarting")
        self.schedule_restart()
        return web.json_response({"ok": True, "restarting": True})

    async def web_ports(self, request):
        return web.json_response(list_serial_ports())

    async def web_join(self, request):
        """Ask the server to let this point join; stores the id + key it hands out."""
        body = await self.json_body(request)
        note = str(body.pop("note", "") or "")[:300]
        confirmed = norm_fp(body.pop("fingerprint", ""))
        try:
            url = clean_url((body.pop("server", None) or {}).get("url", ""))
            new = config.apply_update(self.cfg, body)
        except ValueError as e:
            raise web.HTTPBadRequest(text=str(e))
        p, s = new["point"], new["server"]
        s["url"] = url
        if url.startswith("https://"):
            if not confirmed:
                raise web.HTTPBadRequest(text="check and confirm the server certificate first")
            s["fingerprint"] = confirmed
        else:
            s["fingerprint"] = ""
        if not (s["url"] and p["name"] and p["country"]):
            raise web.HTTPBadRequest(text="enter the server address, the point name and the country code first")
        info = {"name": p["name"], "country": p["country"], "city": p["city"], "lat": p["lat"], "lon": p["lon"],
                "contact": p["contact"], "note": note,
                "networks": [n for n, k in (("mt", "meshtastic"), ("mc", "meshcore")) if new[k]["enabled"]]}
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as sess:
                async with sess.post(s["url"] + "/api/join", json=info,
                                     ssl=self.ssl_param(s["url"], s["fingerprint"])) as r:
                    if r.status != 200:
                        raise web.HTTPBadGateway(text=f"server said: {(await r.text())[:300]}")
                    data = await r.json()
        except web.HTTPException:
            raise
        except aiohttp.ServerFingerprintMismatch:
            raise web.HTTPConflict(text="the server certificate changed since you checked it — check again")
        except Exception as e:
            raise web.HTTPBadGateway(text=f"cannot reach the server: {e}")
        s["point_id"], s["key"], s["enabled"] = data["bridge_id"], data["key"], True
        config.save(new)
        self.cfg = new
        log.info("asked %s to join as %s", s["url"], data["bridge_id"])
        self.schedule_restart()
        return web.json_response({"ok": True, "point_id": data["bridge_id"]})

    async def web_check(self, request):
        """Read the certificate of a server address so the owner can compare the fingerprint."""
        body = await self.json_body(request)
        try:
            url = clean_url(body.get("url"))
        except ValueError as e:
            raise web.HTTPBadRequest(text=str(e))
        if url.startswith("http://"):
            return web.json_response({"url": url, "encrypted": False, "fingerprint": ""})
        try:
            fp = await fetch_fingerprint(url)
        except Exception as e:
            raise web.HTTPBadGateway(text=f"cannot read the certificate of {url}: {e}")
        return web.json_response({"url": url, "encrypted": True, "fingerprint": pretty_fp(fp),
                                  "same_as_pinned": fp == norm_fp(self.sc["fingerprint"])})

    async def web_trust(self, request):
        """Already joined: switch to a (new) address and pin the certificate the owner confirmed."""
        body = await self.json_body(request)
        try:
            url = clean_url(body.get("url"))
        except ValueError as e:
            raise web.HTTPBadRequest(text=str(e))
        fp = ""
        if url.startswith("https://"):
            fp = norm_fp(body.get("fingerprint"))
            if not fp:
                raise web.HTTPBadRequest(text="confirm the certificate fingerprint")
            try:
                now_fp = await fetch_fingerprint(url)
            except Exception as e:
                raise web.HTTPBadGateway(text=f"cannot read the certificate: {e}")
            if now_fp != fp:
                raise web.HTTPConflict(text="the server certificate changed since you checked it — check again")
        self.sc["url"], self.sc["fingerprint"] = url, fp
        config.save(self.cfg)
        log.info("server address %s, pinned certificate %s", url, pretty_fp(fp) or "(none, NOT encrypted)")
        self.schedule_restart()
        return web.json_response({"ok": True})

    async def web_leave(self, request):
        await self.json_body(request)
        self.sc.update(point_id="", key="", fingerprint="", enabled=False)
        config.save(self.cfg)
        self.schedule_restart()
        return web.json_response({"ok": True})

    async def web_restart(self, request):
        self.schedule_restart()
        return web.json_response({"ok": True})

    def schedule_restart(self):
        if not self.restarting:
            self.restarting = True
            asyncio.create_task(self.restart())

    async def restart(self):
        await asyncio.sleep(0.7)
        for closer in (lambda: self.ws.close() if self.ws is not None else None,
                       lambda: self.mc.disconnect() if self.mc is not None else None):
            try:
                c = closer()
                if c is not None:
                    await asyncio.wait_for(c, 3)
            except Exception:
                pass
        try:
            if self.mt is not None:
                await asyncio.wait_for(asyncio.to_thread(self.mt.close), 5)
        except Exception:
            pass
        logging.shutdown()
        os.execv(sys.executable, sys.orig_argv)

    def page(self, name):
        async def handler(request):
            resp = web.FileResponse(os.path.join(WEB_DIR, name))
            resp.headers["Cache-Control"] = "no-cache"
            return resp
        return handler

    async def start_web(self):
        app = web.Application(middlewares=[self.guard])
        r = app.router
        r.add_get("/", self.page("index.html"))
        r.add_get("/settings", self.page("settings.html"))
        r.add_get("/login", self.page("login.html"))
        r.add_get("/setup", self.page("login.html"))
        r.add_static("/static/", WEB_DIR)
        r.add_post("/api/setup", self.web_setup)
        r.add_post("/api/login", self.web_login)
        r.add_post("/api/logout", self.web_logout)
        r.add_post("/api/password", self.web_password)
        r.add_get("/api/state", self.web_state)
        r.add_get("/api/stats", self.web_stats)
        r.add_get("/api/config", self.web_config_get)
        r.add_put("/api/config", self.web_config_put)
        r.add_get("/api/serial-ports", self.web_ports)
        r.add_post("/api/join", self.web_join)
        r.add_post("/api/leave", self.web_leave)
        r.add_post("/api/server/check", self.web_check)
        r.add_post("/api/server/trust", self.web_trust)
        r.add_post("/api/restart", self.web_restart)
        runner = web.AppRunner(app, access_log=None)
        await runner.setup()
        await web.TCPSite(runner, config.WEB_HOST, config.WEB_PORT).start()
        log.info("admin page on http://%s:%s/", config.WEB_HOST, config.WEB_PORT)

    async def main(self):
        self.loop = asyncio.get_running_loop()
        if not self.cfg["auth"]["password_hash"]:
            self.setup_code = secrets.token_hex(3).upper()
            with open(SETUP_CODE_PATH, "w") as f:
                f.write(self.setup_code + "\n")
            log.warning("FIRST RUN — open http://<this-host>:%s/setup  · setup code: %s (also in %s)",
                        config.WEB_PORT, self.setup_code, SETUP_CODE_PATH)
        await self.start_web()
        for task in (self.mt_keepalive, self.mc_keepalive, self.rf_worker, self.server_loop, self.report_loop,
                     self.positions_loop):
            asyncio.create_task(task())
        await asyncio.Event().wait()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    try:
        asyncio.run(Client().main())
    except KeyboardInterrupt:
        pass
