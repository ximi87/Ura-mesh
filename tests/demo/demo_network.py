#!/usr/bin/env python3
"""Demo network for screenshots and presentations: a set of made-up hubs around the world talking the
real Ura hub protocol to a (test) ura-server — registration, approval, links, rules, nodes and a
steady stream of (random, meaningless) sealed boxes so the live map and statistics have something
to show. Not a hub implementation: no radio, no real traffic.

  python3 demo_network.py https://127.0.0.1:8299 127.0.0.1:8298 <admin-password> [history-db-path]
"""
import asyncio, base64, json, math, os, random, sqlite3, ssl, sys, time, urllib.request, http.cookiejar

WEB, HUB, PW = sys.argv[1], sys.argv[2], sys.argv[3]
DB = sys.argv[4] if len(sys.argv) > 4 else None
random.seed(7)

HUBS = [  # code, name, lat, lon, number of nodes
    ("XA-MTN", "Mountain mesh", 47.27, 11.39, 34), ("XB-HBR", "Harbour mesh", 53.55, 9.99, 41),
    ("XC-CTY", "City mesh", 40.42, -3.70, 28), ("XD-VAL", "Valley mesh", 41.88, -87.63, 37),
    ("XE-ISL", "Island mesh", -33.87, 151.21, 22), ("XF-DST", "Desert mesh", 25.20, 55.27, 18),
    ("XG-LAK", "Lake mesh", -1.29, 36.82, 25),
]
LINKS = [("XA-MTN", "XB-HBR"), ("XB-HBR", "XC-CTY"), ("XC-CTY", "XD-VAL"), ("XA-MTN", "XF-DST"),
         ("XF-DST", "XG-LAK"), ("XG-LAK", "XE-ISL"), ("XB-HBR", "XD-VAL"), ("XF-DST", "XE-ISL")]
ADJ = {}
for a, b in LINKS:
    ADJ.setdefault(a, set()).add(b); ADJ.setdefault(b, set()).add(a)

ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), urllib.request.HTTPSHandler(context=ctx))


def web(path, body=None):
    req = urllib.request.Request(WEB + path, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json"}, method="POST" if body is not None else "GET")
    try:
        return json.loads(op.open(req, timeout=30).read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def rule(onward=()):
    s = {"on": True, "public": True, "groups": ["Hikers"], "private": True, "positions": True, "onward_to": list(onward), "transit": True}
    r = {"on": True, "public": True, "groups": ["Hikers"], "private": True, "positions": True, "from_beyond": True}
    return {"send": s, "receive": r}


def nodes_for(code, lat, lon, n):
    out, now = [], int(time.time())
    hw = ["HELTEC_V3", "RAK4631", "T_ECHO", "TBEAM", "STATION_G2", "HELTEC_WIRELESS_TRACKER", "WISMESH_TAG"]
    for i in range(n):
        r, a = random.uniform(0.5, 28) / 111, random.uniform(0, 2 * math.pi)
        nid = "!%08x" % random.getrandbits(32)
        name = random.choice(["Base", "Hill", "Roof", "Car", "Hiker", "Solar", "Relay", "Home", "Tower", "Boat"]) + " " + nid[-4:]
        out.append({"id": nid, "name": name, "short": nid[-4:], "hw": random.choice(hw), "role": random.choice(["CLIENT", "ROUTER", "CLIENT_MUTE"]),
                    "lat": round(lat + r * math.sin(a), 5) if random.random() > 0.15 else None,
                    "lon": round(lon + r * math.cos(a) / max(0.2, math.cos(math.radians(lat))), 5),
                    "alt": random.randint(0, 900), "last_heard": now - random.randint(30, 5 * 86400), "hops": random.randint(0, 5)})
    out.append({"id": "!%08x" % random.getrandbits(32), "name": code + " hub radio", "short": "HUB", "hw": "HELTEC_V3", "role": "CLIENT",
                "lat": lat, "lon": lon, "alt": 300, "last_heard": now, "hops": 0, "own": True})
    return out


class Hub:
    def __init__(self, code, name, lat, lon, n):
        self.code, self.name, self.lat, self.lon, self.n = code, name, lat, lon, n
        self.id = self.key = None
        self.links, self.directory = [], []
        self.pub = base64.b64encode(os.urandom(32)).decode()

    async def conn(self):
        host, port = HUB.rsplit(":", 1)
        return await asyncio.open_connection(host, int(port), ssl=ctx)

    async def send(self, w, obj):
        w.write((json.dumps(obj) + "\n").encode()); await w.drain()

    async def join(self):
        r, w = await self.conn()
        cc, pp = self.code.split("-")
        await self.send(w, {"t": "join", "name": self.name, "email": f"{pp.lower()}@example.org", "country": cc, "city": pp,
                            "lat": self.lat, "lon": self.lon, "description": f"Demo hub — {self.name}."})
        m = json.loads(await r.readline()); w.close()
        self.id, self.key = m["hub"], m["key"]

    def info(self, ids):
        active = [l for l in self.links if l["state"] == "active"]          # every active link, incl. hubs that joined later
        peers = [l["peer"] for l in active]
        return {"rules": {"airtime": {"pct_hour": 10, "pct_day": 0}, "default": rule(), "transit": {"enabled": True, "max_hops": 3},
                          "transit_to": peers,
                          "links": {l["peer_code"]: rule(onward=[p for p in peers if p != l["peer"]][:2]) for l in active}},
                "radios": [{"net": "mt", "name": self.code + " hub radio", "hw": "HELTEC_V3", "firmware": "2.7.26 + Ura", "connected": True}],
                "pubkey": self.pub}

    async def run(self, ids, everyone):
        while True:
            try:
                r, self.w = await self.conn()
                await self.send(self.w, {"t": "hello", "hub": self.id, "key": self.key, "version": "0.3.0", "info": self.info(ids)})
                hello = json.loads(await r.readline())
                self.links = hello.get("links", [])
                await self.send(self.w, {"t": "nodes", "net": "mt", "nodes": nodes_for(self.code, self.lat, self.lon, self.n)})
                for peer in ADJ.get(self.code, ()):
                    if self.code < peer:
                        await self.send(self.w, {"t": "link_request", "to": ids[peer]})
                while line := await r.readline():
                    m = json.loads(line)
                    if m.get("t") == "links":
                        self.links = m["links"]
                        for l in self.links:
                            if l["state"] != "active" and not l["i_accepted"]:
                                await self.send(self.w, {"t": "link_accept", "link": l["id"]})
                        await self.send(self.w, {"t": "info", "info": self.info(ids)})
            except Exception as e:
                print(self.code, "reconnect:", e, flush=True)
            await asyncio.sleep(3)


async def traffic(hubs, ids):
    """Random sealed-looking boxes along active links, so the live map moves."""
    by_code = {h.code: h for h in hubs}
    while True:
        a, b = random.choice(LINKS)
        if random.random() < .5:
            a, b = b, a
        h = by_code[a]
        try:
            await h.send(h.w, {"t": "mesh", "net": "mt", "boxes": {ids[b]: base64.b64encode(os.urandom(random.randint(90, 260))).decode()}})
        except Exception:
            pass
        await asyncio.sleep(random.uniform(0.3, 1.2))


def history(ids):
    """A week of hourly statistics for the charts (demo only)."""
    if not DB:
        return
    c = sqlite3.connect(DB)
    now = int(time.time()) // 3600 * 3600
    for a, b in LINKS:
        for h in range(7 * 24):
            day = 0.4 + 0.6 * max(0, math.sin((h % 24 - 6) / 24 * 2 * math.pi))
            for s, d in ((a, b), (b, a)):
                n = int(random.uniform(5, 40) * day)
                if n:
                    c.execute("INSERT OR REPLACE INTO stats(src,dst,net,hour,frames,bytes) VALUES(?,?,?,?,?,?)",
                              (ids[s], ids[d], "mt", now - h * 3600, n, n * 160))
    c.commit()


async def main():
    print(web("/api/setup", {"password": PW}) or "", web("/api/login", {"password": PW}))
    hubs = [Hub(*x) for x in HUBS]
    for h in hubs:
        await h.join()
    ids = {h.code: h.id for h in hubs}
    for h in hubs:
        web(f"/api/admin/hub/{h.id}/approve", {})
    history(ids)
    print("demo hubs:", ids, flush=True)
    tasks = [asyncio.create_task(h.run(ids, hubs)) for h in hubs]
    await asyncio.sleep(6)
    tasks.append(asyncio.create_task(traffic(hubs, ids)))
    await asyncio.gather(*tasks)

asyncio.run(main())
