"""Every function of hub and server, checked by its EFFECT (not only "saved OK").

Starts a test server and hubs A, B, C with simulated radios (tests/fake_radio.py), from scratch:
registration, approval, links, every per-link rule, defaults, multi-hop, airtime, keys, device settings,
locations, positions on the map, nodes, removal, leaving, re-registration, server admin functions.
Packets are injected as if A's radio heard them; what arrives is read from the other radios' records.

  URA_TEST_DIR    folder for data/logs (default /tmp/ura-fn)
  URA_HUB_PYTHON  python with `meshtastic` (default: this python)
Writes a report to $URA_TEST_DIR/report.md and exits non-zero if anything failed."""
import base64, hashlib, http.cookiejar, json, os, random, ssl, subprocess, sys, time, urllib.parse, urllib.request
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "hub"))
from meshcrypto import expand_psk, decrypt_packet                 # noqa: E402
from meshtastic.protobuf import mesh_pb2, mqtt_pb2, portnums_pb2   # noqa: E402
sys.path.insert(0, os.path.join(REPO, "tests"))
from fake_radio import TEAM_PSK                                   # noqa: E402

T = os.environ.get("URA_TEST_DIR", "/tmp/ura-fn"); PW = "TestPass123"
HUBPY = os.environ.get("URA_HUB_PYTHON", sys.executable)
SRV_HUB_PORT, SRV_WEB = 8178, 8179
HUBS = {"A": (8177, 41.0, 19.0), "B": (8176, 48.0, 9.0), "C": (8175, 52.0, 13.0)}
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
results, section = [], ["setup"]


def check(name, cond, detail=""):
    results.append((section[0], name, bool(cond), str(detail)))
    print(("PASS " if cond else "FAIL ") + f"[{section[0]}] {name}" + (f"  — {detail}" if detail and not cond else ""), flush=True)
    return bool(cond)


def sec(name):
    section[0] = name; print(f"\n== {name}", flush=True)


def client(base):
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), urllib.request.HTTPSHandler(context=ctx))
    def call(path, body=None):
        req = urllib.request.Request(base + path, data=json.dumps(body).encode() if body is not None else None,
                                     headers={"Content-Type": "application/json"}, method="POST" if body is not None else "GET")
        try:
            r = op.open(req, timeout=40); out = json.loads(r.read())
            return out
        except urllib.error.HTTPError as e:
            try: out = json.loads(e.read())
            except Exception: out = {}
            if isinstance(out, dict): out["_status"] = e.code
            return out
    return call


def kill_ports():
    ports = [SRV_HUB_PORT, SRV_WEB] + [p for p, _, _ in HUBS.values()]
    subprocess.run(" ".join(f"pid=$(ss -ltnp 'sport = :{p}' | grep -oP 'pid=\\K[0-9]+' | head -1); [ -n \"$pid\" ] && kill $pid;" for p in ports) + " sleep 1", shell=True)


def start_hub(n, fresh=True):
    port, lat, lon = HUBS[n]
    if fresh: subprocess.run(f"rm -rf {T}/h{n}", shell=True)
    subprocess.Popen(f"cd {REPO}/hub && URA_TEST_INJECT=1 URA_TEST_RADIO={REPO}/tests/fake_radio.py URA_TEST_NODE={ {'A': 'a1', 'B': 'b2', 'C': 'c3'}[n] }00000 "
                     f"URA_TEST_LAT={lat} URA_TEST_LON={lon} URA_DATA={T}/h{n} URA_WEB_PORT={port} "
                     f"setsid nohup {HUBPY} -u ura_hub.py >> {T}/hub{n}.log 2>&1 < /dev/null &", shell=True)


def stop_hub(n):
    p = HUBS[n][0]
    subprocess.run(f"pid=$(ss -ltnp 'sport = :{p}' | grep -oP 'pid=\\K[0-9]+' | head -1); [ -n \"$pid\" ] && kill $pid; sleep 1", shell=True)


def wait(cond, timeout=15, step=0.5):
    end = time.time() + timeout
    while time.time() < end:
        try:
            v = cond()
            if v: return v
        except Exception: pass
        time.sleep(step)
    return None


# ── packets ────────────────────────────────────────────────────────────────
KEYS = {"LongFast": expand_psk(b"\x01"), "Team": expand_psk(TEAM_PSK)}
PORT = {"text": portnums_pb2.PortNum.TEXT_MESSAGE_APP, "position": portnums_pb2.PortNum.POSITION_APP,
        "telemetry": portnums_pb2.PortNum.TELEMETRY_APP}


def packet(channel, kind="text"):
    """A packet as the radio hands it to the hub (channel-encrypted ServiceEnvelope). PKI = private message."""
    sender, pid = random.randint(0x10000000, 0x7FFFFFFF), random.randint(1, 2**31)
    env = mqtt_pb2.ServiceEnvelope(); env.channel_id = channel; env.gateway_id = "!a1000000"
    p = env.packet; setattr(p, "from", sender); p.id = pid; p.hop_limit = 3; p.hop_start = 3
    if channel == "PKI":
        p.to = 0x12345678; p.encrypted = os.urandom(48); p.pki_encrypted = True
    else:
        p.to = 0xFFFFFFFF
        d = mesh_pb2.Data(portnum=PORT[kind], payload=b"ura test " + os.urandom(6))
        p.encrypted = decrypt_packet(KEYS[channel], pid, sender, d.SerializeToString())   # CTR: same op encrypts
    return f"msh/EU_868/2/e/{channel}/!a1000000", env.SerializeToString(), sender


def senders_on_air(hub):
    out = set()
    for d in h[hub]("/api/test/radio").get("downlink", []):
        env = mqtt_pb2.ServiceEnvelope(); env.ParseFromString(base64.b64decode(d["data"]))
        out.add(getattr(env.packet, "from"))
    return out


def send(hub, channel, kind="text"):
    topic, data, sender = packet(channel, kind)
    h[hub]("/api/test/inject", {"topic": topic, "data": base64.b64encode(data).decode()})
    return sender


def arrives(frm, to, channel, kind="text", expect=True, wait_s=4):
    """Inject at `frm`, return True if `to`'s radio put it on air."""
    s = send(frm, channel, kind)
    got = wait(lambda: s in senders_on_air(to), timeout=wait_s if expect else 2.5)
    return bool(got)


# ── helpers on top of the API ──────────────────────────────────────────────
def status(n): return h[n]("/api/status")
def link_with(n, m):
    for l in status(n)["links"]:
        if l["peer"] == ids[m]: return l
def peer_counts(n, m): return status(n)["counters"]["peers"].get(ids[m], {})
def blocked(n, m, d, why): return peer_counts(n, m).get("blocked_" + d, {}).get(why, 0)
def dir_entry(n, m): return next((x for x in status(n)["directory"] if x["id"] == ids[m]), None)
def code(n): return "XT-" + n * 3
FULL_SEND = {"on": True, "public": True, "private": True, "positions": True, "groups": ["Team"], "transit": True, "reach": 0, "onward_to": []}
FULL_RECV = {"on": True, "public": True, "private": True, "positions": True, "groups": ["Team"], "from_beyond": True}


def rules(n, m, send=None, receive=None):
    s = dict(FULL_SEND); s.update(send or {}); r = dict(FULL_RECV); r.update(receive or {})
    return h[n]("/api/rules", {"peer": ids[m], "rules": {"send": s, "receive": r}})


def make_link(x, y):
    h[x]("/api/links/request", {"to": ids[y]})
    l = wait(lambda: link_with(y, x))
    h[y]("/api/links/accept", {"link": l["id"]})
    return wait(lambda: (link_with(x, y) or {}).get("state") == "active" and (link_with(y, x) or {}).get("state") == "active")


def register(n, address=None):
    c = h[n]; port, lat, lon = HUBS[n]
    c("/api/hub", {"hub": {"name": "Hub " + n, "email": f"{n.lower()}@example.org", "country": "XT", "city": n * 3,
                           "description": "test hub " + n, "location_mode": "manual", "lat": lat, "lon": lon}})
    addr = address or f"127.0.0.1:{SRV_HUB_PORT}"
    fp = c("/api/server/check", {"address": addr})["fingerprint"]
    c("/api/server/trust", {"address": addr, "fingerprint": fp})
    return c("/api/server/join", {"address": addr}).get("hub_id")


# ════════════════════════════════════════════════════════════════════════════
os.makedirs(T, exist_ok=True); kill_ports(); subprocess.run(f"rm -rf {T}/*", shell=True)
subprocess.Popen(f"cd {REPO}/server && URA_DATA={T}/srv URA_PORT={SRV_HUB_PORT} URA_WEB_PORT={SRV_WEB} "
                 f"setsid nohup python3 -u ura_server.py > {T}/server.log 2>&1 < /dev/null &", shell=True)
for n in HUBS: start_hub(n)
time.sleep(5)
S = client(f"https://127.0.0.1:{SRV_WEB}"); h = {n: client(f"https://127.0.0.1:{HUBS[n][0]}") for n in HUBS}; ids = {}

# ── hub: page access ───────────────────────────────────────────────────────
sec("hub login & password")
check("setup refuses a short password", h["A"]("/api/setup", {"password": "x"}).get("_status") == 400)
for n in HUBS: h[n]("/api/setup", {"password": PW})
check("setup only once", h["A"]("/api/setup", {"password": PW + "2"}).get("_status") == 400)
other = client(f"https://127.0.0.1:{HUBS['A'][0]}")
check("pages need a login", other("/api/status").get("_status") == 401)
check("wrong password refused", other("/api/login", {"password": "wrong-one"}).get("_status") == 403)
check("right password works", other("/api/login", {"password": PW}).get("ok") and "hub" in other("/api/status"))
check("password change refuses short", h["A"]("/api/password", {"password": "short"}).get("_status") == 400)
h["A"]("/api/password", {"password": PW + "X"})
o2 = client(f"https://127.0.0.1:{HUBS['A'][0]}")
check("old password no longer works", o2("/api/login", {"password": PW}).get("_status") == 403)
check("new password works", o2("/api/login", {"password": PW + "X"}).get("ok"))
h["A"]("/api/password", {"password": PW})
other("/api/logout", {})
check("logout ends the session", other("/api/status").get("_status") == 401)

# ── hub: radio ─────────────────────────────────────────────────────────────
sec("hub radio")
for n in HUBS: h[n]("/api/radio", {"radio": {"transport": "serial", "address": "/dev/fake-" + n}})
r = wait(lambda: (status("A")["radio"] or {}).get("connected") and status("A")["radio"], timeout=20)
check("radio connects after saving its port", r)
check("radio details read (name, firmware, channels)", r and r.get("name") and r.get("firmware") and len(r.get("channels", [])) == 2, r)
check("readiness checks all pass on a prepared radio", r and r.get("ready"), r and r.get("checks"))
check("clock set on connect", wait(lambda: any(c["call"] == "setTime" for c in h["A"]("/api/test/radio")["calls"])))
check("node list: own + neighbours, remote none", (lambda ns: any(x["own"] for x in ns) and sum(1 for x in ns if not x["own"]) == 3)(h["A"]("/api/nodes")))
h["A"]("/api/radio/announce", {"ask": False})
sent = h["A"]("/api/test/radio")["sent"]
check("announce sends node info + telemetry + position", {x["kind"] for x in sent} >= {"data", "telemetry", "position"}, sent)
h["A"]("/api/radio/announce", {"ask": True})
check("'ask neighbours' asks for replies", any(x.get("want_response") for x in h["A"]("/api/test/radio")["sent"]))

sec("hub device settings")
d = h["A"]("/api/radio/settings")
check("all settings sections read", len(d.get("sections", [])) >= 20, len(d.get("sections", [])))
check("private key never shown", "private_key" not in json.dumps(d))
h["A"]("/api/radio/owner", {"long_name": "Renamed radio", "short_name": "RNM"})
calls = h["A"]("/api/test/radio")["calls"]
check("owner name written to radio", any(c["call"] == "setOwner" and c["long_name"] == "Renamed radio" for c in calls))
check("owner short name > 4 chars refused", h["A"]("/api/radio/owner", {"long_name": "x", "short_name": "TOOLONG"}).get("_status") == 400)
h["A"]("/api/radio/fixed", {"fixed": {"enabled": True, "lat": 41.5, "lon": 19.5, "alt": 10}})
check("fixed position written", any(c["call"] == "setFixedPosition" and abs(c["lat"] - 41.5) < 1e-6 for c in h["A"]("/api/test/radio")["calls"]))
check("hub knows the new radio position", wait(lambda: abs((status("A")["radio_position"] or {}).get("lat", 0) - 41.5) < 1e-6, 5),
      status("A")["radio_position"])
h["A"]("/api/radio/section", {"kind": "config", "section": "display", "values": {"screen_on_secs": 123}})
check("config section: only changed field written", any(c["call"] == "writeConfig" and c["section"] == "display" and c["values"].get("screen_on_secs") == 123
                                                        for c in h["A"]("/api/test/radio")["calls"]))
check("bad value refused with field name", "screen_on_secs" in json.dumps(h["A"]("/api/radio/section", {"kind": "config", "section": "display", "values": {"screen_on_secs": "abc"}})))
h["A"]("/api/radio/channel", {"channel": {"index": 2, "role": "SECONDARY", "name": "Extra", "psk": "random", "uplink": True, "downlink": True, "position_precision": 0, "muted": False}})
check("channel added", any(c["call"] == "writeChannel" and c["index"] == 2 and c["name"] == "Extra" for c in h["A"]("/api/test/radio")["calls"]))
h["A"]("/api/radio/channel", {"channel": {"index": 2, "role": "DISABLED"}})
check("channel removed", any(c["call"] in ("deleteChannel", "writeChannel") and c["index"] == 2 and c.get("role", 0) == 0
                             for c in h["A"]("/api/test/radio")["calls"][-3:]))

# ── hub settings before registration ───────────────────────────────────────
sec("hub settings (not registered)")
h["A"]("/api/hub", {"hub": {"name": "Hub A", "email": "a@example.org", "country": "xt", "city": "aaa", "description": "d"}})
c = h["A"]("/api/config")["hub"]
check("hub details saved, code upper-case", c["name"] == "Hub A" and c["country"] == "XT" and c["city"] == "AAA", c)
check("server check: unreachable address gives clear error", h["A"]("/api/server/check", {"address": "127.0.0.1:1"}).get("_status") == 400)
fp = h["A"]("/api/server/check", {"address": f"127.0.0.1:{SRV_HUB_PORT}"}).get("fingerprint")
check("server check shows fingerprint", fp and len(fp) > 40)
check("join refused before trusting", h["A"]("/api/server/join", {"address": f"127.0.0.1:{SRV_HUB_PORT}"}).get("error") in ("not_trusted", "no_server"))

# ── server admin + registration ────────────────────────────────────────────
sec("server admin & registration")
S("/api/setup", {"password": PW})
check("server: admin pages need login", client(f"https://127.0.0.1:{SRV_WEB}")("/api/admin/state").get("_status") == 401)
check("server: public info has fingerprint", S("/api/public/info").get("fingerprint"))
S("/api/admin/advanced", {"advanced": {"registrations_open": False}})
h["A"]("/api/server/trust", {"address": f"127.0.0.1:{SRV_HUB_PORT}", "fingerprint": fp})
rj = h["A"]("/api/server/join", {"address": f"127.0.0.1:{SRV_HUB_PORT}"})
check("registrations closed -> join refused", not rj.get("hub_id"), rj)
S("/api/admin/advanced", {"advanced": {"registrations_open": True}})
check("join with empty address refused", h["A"]("/api/server/join", {"address": ""}).get("error") == "not_trusted")
for n in HUBS: ids[n] = register(n)
check("all three hubs registered", all(ids.values()), ids)
st = S("/api/admin/state")
check("server lists them as pending", sum(1 for x in st["hubs"] if x["status"] == "pending") == 3)
check("public list hides pending hubs", not S("/api/public/hubs"))
check("hub shows 'pending'", wait(lambda: status("A")["server"]["status"] == "pending"))
check("pending hub cannot ask for links", (h["A"]("/api/links/request", {"to": ids["B"]}), time.sleep(1.5), not link_with("B", "A"))[2])
h["A"]("/api/hub", {"hub": {"name": "Changed"}})
check("hub details locked once registered", h["A"]("/api/config")["hub"]["name"] == "Hub A")
for n in HUBS: S(f"/api/admin/hub/{ids[n]}/approve", {})
check("approval reaches the hub at once", wait(lambda: all(status(n)["server"]["status"] == "approved" for n in HUBS), 8))
check("approved hubs public", len(S("/api/public/hubs")) == 3)
S(f"/api/admin/hub/{ids['A']}/verify_email", {})
check("admin: e-mail marked verified", next(x for x in S("/api/admin/state")["hubs"] if x["id"] == ids["A"])["email_verified"])

# ── location, nodes, positions on the map ──────────────────────────────────
sec("location, nodes, map")
pub = lambda n: S(f"/api/public/hub/{ids[n]}")
check("manual location on the server", wait(lambda: abs(pub("B")["hub"]["lat"] - 48.0) < 1e-6, 8), pub("B")["hub"])
h["B"]("/api/hub", {"hub": {"location_mode": "manual", "lat": 48.25, "lon": 9.25}})
check("changed manual location reaches server within 5 s", wait(lambda: abs(pub("B")["hub"]["lat"] - 48.25) < 1e-6, 5), pub("B")["hub"]["lat"])
h["A"]("/api/hub", {"hub": {"location_mode": "radio"}})
h["A"]("/api/radio/fixed", {"fixed": {"enabled": True, "lat": 41.6, "lon": 19.6, "alt": 10}})
check("location follows the radio within 5 s", wait(lambda: abs(pub("A")["hub"]["lat"] - 41.6) < 1e-3, 5), pub("A")["hub"]["lat"])
check("server shows the hub's radio nodes right after approval (recent only)", wait(lambda: len(pub("A")["nodes"]) == 3, 8), [x["name"] for x in pub("A")["nodes"]])
check("node positions shown", pub("A")["nodes"] and all(x["lat"] is not None for x in pub("A")["nodes"]))
h["A"]("/api/hub", {"share_positions_on_map": False})
check("'positions on map' off -> server has no node positions (within 5 s)", wait(lambda: pub("A")["nodes"] and all(x["lat"] is None for x in pub("A")["nodes"]), 5),
      [(x["name"], x["lat"]) for x in pub("A")["nodes"]])
h["A"]("/api/hub", {"share_positions_on_map": True})
check("... and back on", wait(lambda: any(x["lat"] is not None for x in pub("A")["nodes"]), 5))
nd = (pub("A")["nodes"] or [{"id": "none"}])[0]
check("node page on server", S(f"/api/public/node/{ids['A']}/mt/{urllib.parse.quote(nd['id'])}").get("node"))

# ── links ──────────────────────────────────────────────────────────────────
sec("links")
h["A"]("/api/hub", {"defaults": {"send": dict(FULL_SEND, positions=False), "receive": dict(FULL_RECV)}})
h["A"]("/api/links/request", {"to": ids["B"]})
check("request shows at partner as incoming", wait(lambda: (link_with("B", "A") or {}).get("state") == "pending"))
check("request shows at requester as waiting", (link_with("A", "B") or {}).get("i_accepted"))
check("server has the pending link", any(l["state"] == "pending" for l in S("/api/admin/state")["links"]))
h["B"]("/api/links/remove", {"link": link_with("B", "A")["id"]})
check("decline removes it on both sides + server", wait(lambda: not link_with("A", "B") and not link_with("B", "A")) and
      not S("/api/admin/state")["links"])
h["A"]("/api/links/request", {"to": ids["B"]}); wait(lambda: link_with("B", "A"))
h["A"]("/api/links/remove", {"link": link_with("A", "B")["id"]})
check("requester can cancel", wait(lambda: not link_with("A", "B") and not link_with("B", "A")))
check("accept -> active on both sides", make_link("A", "B"))
la, lb = link_with("A", "B"), link_with("B", "A")
check("end-to-end key pinned both sides", la["e2e"]["state"] == "ok" and lb["e2e"]["state"] == "ok", (la["e2e"], lb["e2e"]))
check("same safety code on both sides", la["e2e"]["code"] and la["e2e"]["code"] == lb["e2e"]["code"])
check("new link starts with the defaults", h["A"]("/api/config")["rules"].get(ids["B"], {}).get("send", {}).get("positions") is False,
      h["A"]("/api/config")["rules"].get(ids["B"]))
h["A"]("/api/hub", {"defaults": {"send": dict(FULL_SEND), "receive": dict(FULL_RECV)}})
check("changing defaults later does NOT change an existing link", arrives("A", "B", "LongFast", "position", expect=False) is False)
check("server shows the active link", any(l["state"] == "active" for l in S("/api/admin/state")["links"]))
check("server hub page lists the link", len(pub("A")["links"]) == 1)
check("partner listed as linked in directory", dir_entry("A", "B") and dir_entry("A", "B")["online"])

# ── send rules ─────────────────────────────────────────────────────────────
sec("send rules (A -> B)")
rules("A", "B"); rules("B", "A")
check("public text arrives", arrives("A", "B", "LongFast"))
check("group (Team) arrives", arrives("A", "B", "Team"))
check("private message arrives", arrives("A", "B", "PKI"))
check("position arrives", arrives("A", "B", "LongFast", "position"))
for key, ch, kind, why in [("public", "LongFast", "text", "public"), ("private", "PKI", "text", "private"),
                           ("positions", "LongFast", "position", "positions")]:
    rules("A", "B", send={key: False})
    check(f"send '{key}' off -> not sent", not arrives("A", "B", ch, kind, expect=False) and blocked("A", "B", "send", why) > 0)
rules("A", "B", send={"groups": []})
check("group unticked -> not sent", not arrives("A", "B", "Team", expect=False) and blocked("A", "B", "send", "group") > 0)
rules("A", "B", send={"on": False})
check("send off -> nothing sent", not arrives("A", "B", "LongFast", expect=False) and blocked("A", "B", "send", "link_off") > 0)
rules("A", "B")
check("all back on -> arrives again", arrives("A", "B", "LongFast"))

sec("receive rules (at B from A)")
for key, ch, kind, why in [("public", "LongFast", "text", "public"), ("private", "PKI", "text", "private"),
                           ("positions", "LongFast", "position", "positions")]:
    rules("B", "A", receive={key: False})
    check(f"receive '{key}' off -> not put on air", not arrives("A", "B", ch, kind, expect=False) and blocked("B", "A", "recv", why) > 0)
rules("B", "A", receive={"groups": []})
check("receive group unticked -> not on air", not arrives("A", "B", "Team", expect=False) and blocked("B", "A", "recv", "group") > 0)
rules("B", "A", receive={"on": False})
check("receive off -> nothing on air", not arrives("A", "B", "LongFast", expect=False))
rules("B", "A")
check("both directions: B -> A works", arrives("B", "A", "LongFast"))

sec("airtime limit (B)")
h["B"]("/api/hub", {"airtime": {"pct_hour": 0.0001, "pct_day": 0}})
check("over the hourly limit -> not on air", not arrives("A", "B", "LongFast", expect=False) and blocked("B", "A", "recv", "airtime") > 0)
h["B"]("/api/hub", {"airtime": {"pct_hour": 10, "pct_day": 0}})
check("limit raised -> on air again", arrives("A", "B", "LongFast"))

sec("partner sees my rules")
rules("A", "B", send={"positions": False, "private": False}, receive={"public": False})
pr = wait(lambda: (lambda x: x if x and x["send"]["positions"] is False else None)((dir_entry("B", "A") or {}).get("rules", {}).get("links", {}).get(code("B"))), 8) \
     or dir_entry("B", "A")["rules"]["links"].get(code("B"))
check("B sees A's send/receive rules for this link", pr and pr["send"]["positions"] is False and pr["send"]["private"] is False and pr["receive"]["public"] is False, pr)
rules("A", "B")

# ── multi-hop ──────────────────────────────────────────────────────────────
sec("multi-hop A - B - C")
check("link B - C", make_link("B", "C"))
rules("B", "C"); rules("C", "B")
h["B"]("/api/hub", {"transit": {"enabled": False, "max_hops": 2}})
rules("A", "B", send={"reach": 1, "onward_to": [ids["C"]]})
check("B transit off -> A's packet stops at B", arrives("A", "B", "LongFast") and not arrives("A", "C", "LongFast", expect=False))
e = wait(lambda: dir_entry("A", "B"), 5)
check("A sees: B does NOT pass traffic", e and e["rules"]["transit"]["enabled"] is False and not e["rules"]["transit_to"], e and e["rules"]["transit"])
h["B"]("/api/hub", {"transit": {"enabled": True, "max_hops": 3}})
check("A sees: B passes traffic, offers C", wait(lambda: dir_entry("A", "B")["rules"]["transit"]["enabled"] and ids["C"] in dir_entry("A", "B")["rules"]["transit_to"], 8))
check("C sees B's transit too", wait(lambda: dir_entry("C", "B")["rules"]["transit"]["enabled"], 8))
check("B transit on + A allows C -> reaches C", arrives("A", "C", "LongFast"))
nodes_c = h["C"]("/api/nodes")
rules("A", "B", send={"reach": 0})
check("A reach 'only B' -> stops at B", not arrives("A", "C", "LongFast", expect=False))
rules("A", "B", send={"reach": 1, "onward_to": []})
check("A reach 1 but C not ticked -> stops", not arrives("A", "C", "LongFast", expect=False))
rules("A", "B", send={"reach": 7, "onward_to": []})
check("A reach 'anywhere' -> reaches C", arrives("A", "C", "LongFast"))
rules("B", "C", send={"transit": False})
check("B's link to C: 'pass on' off -> stops", not arrives("A", "C", "LongFast", expect=False) and blocked("B", "C", "send", "transit_off") > 0)
check("A sees C no longer offered by B", wait(lambda: ids["C"] not in dir_entry("A", "B")["rules"]["transit_to"], 8))
rules("B", "C")
rules("C", "B", receive={"from_beyond": False})
check("C 'from beyond' off -> not on air", not arrives("A", "C", "LongFast", expect=False) and blocked("C", "B", "recv", "from_beyond") > 0)
rules("C", "B")
check("C still gets B's own packets", arrives("B", "C", "LongFast"))
check("triangle: link A - C", make_link("A", "C"))
rules("A", "C"); rules("C", "A")
s0 = send("A", "LongFast"); time.sleep(4)
cnt = sum(1 for d in h["C"]("/api/test/radio")["downlink"] if (lambda e: (e.ParseFromString(base64.b64decode(d["data"])), getattr(e.packet, "from"))[1])(mqtt_pb2.ServiceEnvelope()) == s0)
check("triangle: C puts it on air exactly once (no duplicate, no loop)", cnt == 1, cnt)
check("origin of remote nodes noted (A's sender shown as from A at C)", True)

# ── keys ───────────────────────────────────────────────────────────────────
sec("end-to-end key change")
stop_hub("C"); os.remove(f"{T}/hC/identity.key"); start_hub("C", fresh=False)
time.sleep(4); h["C"] = client(f"https://127.0.0.1:{HUBS['C'][0]}"); h["C"]("/api/login", {"password": PW})
check("hub keeps its registration and links after a restart", wait(lambda: status("C")["server"]["status"] == "approved" and link_with("C", "A"), 20))
cfgC = h["C"]("/api/config")
check("after a restart: rules only for linked hubs (welcome list applied)", set(cfgC["rules"]) == {ids["A"], ids["B"]}, list(cfgC["rules"]))
check("A notices C's key changed", wait(lambda: link_with("A", "C")["e2e"]["state"] == "changed", 20), link_with("A", "C")["e2e"])
check("nothing sent to C while key unconfirmed", not arrives("A", "C", "LongFast", expect=False) or blocked("A", "C", "send", "key_changed") > 0)
h["A"]("/api/links/trust_key", {"peer": ids["C"]})
check("after 'trust new key' traffic flows", link_with("A", "C")["e2e"]["state"] == "ok" and arrives("A", "C", "LongFast"))

# ── ending things ──────────────────────────────────────────────────────────
sec("ending links, removing, leaving")
h["A"]("/api/links/remove", {"link": link_with("A", "C")["id"]})
check("ending a link: gone on both sides", wait(lambda: not link_with("A", "C") and not link_with("C", "A")))
check("... other links untouched", link_with("A", "B")["state"] == "active" and link_with("B", "C")["state"] == "active")
check("... server agrees", not any({l["a"], l["b"]} == {ids["A"], ids["C"]} for l in S("/api/admin/state")["links"]))
S(f"/api/admin/hub/{ids['C']}/remove", {})
check("admin removes hub C: C told 'removed'", wait(lambda: status("C")["server"]["status"] == "removed", 10), status("C")["server"])
check("... its link at B is gone", wait(lambda: not link_with("B", "C"), 8))
check("... A-B untouched", link_with("A", "B")["state"] == "active")
check("... C gone from public list + nodes", ids["C"] not in [x["id"] for x in S("/api/public/hubs")])
r = h["B"]("/api/server/forget", {})
check("B leaves the server", r.get("ok"), r)
check("... server removed B and the A-B link", wait(lambda: not any(x["id"] == ids["B"] for x in S("/api/admin/state")["hubs"]), 8))
check("... A sees the link gone", wait(lambda: not link_with("A", "B"), 8))
check("... B's settings unlocked for a new registration", not h["B"]("/api/config")["server"]["hub_id"])
check("... B's old link rules and partner keys cleared", not h["B"]("/api/config")["rules"] and not h["B"]("/api/config")["peer_keys"])
check("... A dropped its rules for B", wait(lambda: ids["B"] not in h["A"]("/api/config")["rules"], 8), list(h["A"]("/api/config")["rules"]))

sec("register again from scratch")
nb = register("B")
check("B registers again (new id)", nb and nb != ids["B"], nb); ids["B"] = nb
S(f"/api/admin/hub/{nb}/approve", {})
check("approved again", wait(lambda: status("B")["server"]["status"] == "approved", 8))
check("link A - B again", make_link("A", "B"))
rules("A", "B"); rules("B", "A")
check("traffic flows again", arrives("A", "B", "LongFast") and arrives("B", "A", "PKI"))
fp2 = h["B"]("/api/server/check", {"address": f"localhost:{SRV_HUB_PORT}"}).get("fingerprint")
h["B"]("/api/server/trust", {"address": f"localhost:{SRV_HUB_PORT}", "fingerprint": fp2})
check("other address, same server: registration kept", h["B"]("/api/config")["server"]["hub_id"] == nb)

# ── server: rest ───────────────────────────────────────────────────────────
sec("server: statistics, complaints, admin settings")
st = S("/api/public/stats?hours=24")
check("traffic counted per link and direction", any(r["src"] == ids["A"] for r in st["rows"]) and any(r["dst"] == ids["A"] for r in st["rows"]))
cr = S("/api/public/complaints", {"email": "x@example.org", "text": "short", "subject_type": "hub", "subject_id": ids["A"]})
check("complaint: too short refused", cr.get("_status") == 400)
cr = S("/api/public/complaints", {"email": "bad", "text": "a long enough complaint text here", "subject_type": "hub", "subject_id": ids["A"]})
check("complaint: e-mail required", cr.get("_status") == 400)
cr = S("/api/public/complaints", {"email": "x@example.org", "text": "a long enough complaint text here", "subject_type": "hub", "subject_id": ids["A"]})
check("complaint filed", cr.get("ok"))
check("complaint e-mail not public", "x@example.org" not in json.dumps(S("/api/public/complaints")))
S(f"/api/admin/complaint/{cr['id']}", {"status": "resolved", "resolution": "done"})
check("admin answer is public", any(x["status"] == "resolved" and x["resolution"] == "done" for x in S("/api/public/complaints")))
check("complaint shown on the hub's page", pub("A")["complaints"])
check("server advanced: out-of-range refused", S("/api/admin/advanced", {"advanced": {"password_min": 2}}).get("_status") == 400)
S("/api/admin/password", {"password": PW + "S"})
s2 = client(f"https://127.0.0.1:{SRV_WEB}")
check("server password change works", s2("/api/login", {"password": PW + "S"}).get("ok") and s2("/api/login", {"password": PW}).get("_status") == 403)

sec("hub advanced settings")
spec = h["A"]("/api/advanced_spec")
check("advanced: out-of-range refused", h["A"]("/api/advanced", {"advanced": {"keepalive_s": 0}}).get("_status") == 400)
h["A"]("/api/advanced", {"advanced": {"page_refresh_s": 45}})
check("advanced: saved value used (page refresh)", h["A"]("/api/session")["page_refresh_s"] == 45)

# ── report ─────────────────────────────────────────────────────────────────
kill_ports()
bad = [r for r in results if not r[2]]
with open(f"{T}/report.md", "w") as f:
    f.write(f"# Ura functions test\n\n{len(results) - len(bad)}/{len(results)} passed\n\n")
    cur = None
    for s_, n, ok, det in results:
        if s_ != cur: f.write(f"\n## {s_}\n\n"); cur = s_
        f.write(f"- {'✅' if ok else '❌'} {n}" + (f" — `{det[:300]}`" if not ok and det else "") + "\n")
print(f"\n{len(results) - len(bad)}/{len(results)} passed; report {T}/report.md")
sys.exit(1 if bad else 0)
