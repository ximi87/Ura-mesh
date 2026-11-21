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
HUBS = {"A": (8177, 41.0, 19.0), "B": (8176, 48.0, 9.0), "C": (8175, 52.0, 13.0), "D": (8174, 50.0, 8.0)}
NODE = {"A": "a1", "B": "b2", "C": "c3", "D": "d4"}
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
    subprocess.Popen(f"cd {REPO}/hub && URA_TEST_INJECT=1 URA_TEST_RADIO={REPO}/tests/fake_radio.py URA_TEST_NODE={NODE[n]}00000 URA_TEST_EXTRA_NODES={15 if n == 'D' else 0} "
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


def packet(channel, kind="text", size=6, key=None):
    """A packet as the radio hands it to the hub (channel-encrypted ServiceEnvelope). PKI = private message."""
    sender, pid = random.randint(0x10000000, 0x7FFFFFFF), random.randint(1, 2**31)
    env = mqtt_pb2.ServiceEnvelope(); env.channel_id = channel; env.gateway_id = "!a1000000"
    p = env.packet; setattr(p, "from", sender); p.id = pid; p.hop_limit = 3; p.hop_start = 3
    if channel == "PKI":
        p.to = 0x12345678; p.encrypted = os.urandom(48); p.pki_encrypted = True
    else:
        p.to = 0xFFFFFFFF
        d = mesh_pb2.Data(portnum=PORT[kind], payload=b"ura test " + os.urandom(size))
        k = key or KEYS[channel]
        p.encrypted = decrypt_packet(k, pid, sender, d.SerializeToString())   # CTR: same op encrypts
        code = 0
        for b in channel.encode() + k: code ^= b
        p.channel = code                       # like real radios: the channel code travels in every packet
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
check("node list: own + neighbours, remote none", (lambda ns: any(x["own"] for x in ns) and sum(1 for x in ns if not x["own"]) == 4)(h["A"]("/api/nodes")))
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
check("all hubs registered", all(ids.values()), ids)
st = S("/api/admin/state")
check("server lists them as pending", sum(1 for x in st["hubs"] if x["status"] == "pending") == len(HUBS))
check("public list hides pending hubs", not S("/api/public/hubs"))
check("hub shows 'pending'", wait(lambda: status("A")["server"]["status"] == "pending"))
check("pending hub cannot ask for links", (h["A"]("/api/links/request", {"to": ids["B"]}), time.sleep(1.5), not link_with("B", "A"))[2])
h["A"]("/api/hub", {"hub": {"name": "Changed"}})
check("hub details locked once registered", h["A"]("/api/config")["hub"]["name"] == "Hub A")
for n in HUBS: S(f"/api/admin/hub/{ids[n]}/approve", {})
check("approval reaches the hub at once", wait(lambda: all(status(n)["server"]["status"] == "approved" for n in HUBS), 8))
check("approved hubs public", len(S("/api/public/hubs")) == len(HUBS))
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
check("server shows the hub's radio nodes right after approval (recent only)", wait(lambda: len(pub("A")["nodes"]) == 4, 8), [x["name"] for x in pub("A")["nodes"]])
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

sec("max hops: chain A - B - C - D")
check("link C - D", make_link("C", "D"))
rules("C", "D"); rules("D", "C")
h["B"]("/api/hub", {"transit": {"enabled": True, "max_hops": 3}})
h["C"]("/api/hub", {"transit": {"enabled": True, "max_hops": 2}})
rules("A", "B", send={"reach": 7})
check("C allows 2 hops -> A's packet reaches C but not D", arrives("A", "C", "LongFast") and not arrives("A", "D", "LongFast", expect=False))
h["C"]("/api/hub", {"transit": {"enabled": True, "max_hops": 3}})
s3 = send("A", "LongFast")
check("C allows 3 hops -> A's packet reaches D (3 hubs away)", wait(lambda: s3 in senders_on_air("D"), 6))
check("D knows that node came from A (not from C)", wait(lambda: next((x for x in h["D"]("/api/nodes") if x["id"] == f"!{s3:08x}"), {}).get("origin") == ids["A"], 6),
      next((x for x in h["D"]("/api/nodes") if x["id"] == f"!{s3:08x}"), None))
rules("A", "B", send={"reach": 1, "onward_to": [ids["C"]]})
check("A allows only 1 hub beyond B -> stops at C even though C allows more", arrives("A", "C", "LongFast") and not arrives("A", "D", "LongFast", expect=False))
rules("A", "B", send={"reach": 2, "onward_to": [ids["C"]]})
check("A allows 2 hubs beyond B -> reaches D", arrives("A", "D", "LongFast"))
rules("A", "B", send={"reach": 7, "onward_to": []})
check("triangle: link A - C", make_link("A", "C"))
rules("A", "C"); rules("C", "A")
s0 = send("A", "LongFast"); time.sleep(4)
cnt = sum(1 for d in h["C"]("/api/test/radio")["downlink"] if (lambda e: (e.ParseFromString(base64.b64decode(d["data"])), getattr(e.packet, "from"))[1])(mqtt_pb2.ServiceEnvelope()) == s0)
check("triangle: C puts it on air exactly once (no duplicate, no loop)", cnt == 1, cnt)
check("C lists A's node as remote, from A", next((x for x in h["C"]("/api/nodes") if x["id"] == f"!{s0:08x}"), {}).get("origin") == ids["A"],
      next((x for x in h["C"]("/api/nodes") if x["id"] == f"!{s0:08x}"), None))
sb = send("B", "LongFast")
check("C lists B's node as remote, from B", wait(lambda: next((x for x in h["C"]("/api/nodes") if x["id"] == f"!{sb:08x}"), {}).get("origin") == ids["B"], 6))
check("remote nodes are not reported to the server as C's own", wait(lambda: f"!{s0:08x}" not in [x["id"] for x in pub("C")["nodes"]], 3))

# ── keys ───────────────────────────────────────────────────────────────────
sec("end-to-end key change")
stop_hub("C"); os.remove(f"{T}/hC/identity.key"); start_hub("C", fresh=False)
time.sleep(4); h["C"] = client(f"https://127.0.0.1:{HUBS['C'][0]}"); h["C"]("/api/login", {"password": PW})
check("hub keeps its registration and links after a restart", wait(lambda: status("C")["server"]["status"] == "approved" and link_with("C", "A"), 20))
cfgC = h["C"]("/api/config")
check("after a restart: rules only for linked hubs (welcome list applied)", set(cfgC["rules"]) == {l["peer"] for l in status("C")["links"]} == {ids["A"], ids["B"], ids["D"]}, list(cfgC["rules"]))
check("A notices C's key changed", wait(lambda: link_with("A", "C")["e2e"]["state"] == "changed", 20), link_with("A", "C")["e2e"])
check("nothing sent to C while key unconfirmed", not arrives("A", "C", "LongFast", expect=False) or blocked("A", "C", "send", "key_changed") > 0)
h["A"]("/api/links/trust_key", {"peer": ids["C"]})
wait(lambda: link_with("B", "C")["e2e"]["state"] == "changed", 10); h["B"]("/api/links/trust_key", {"peer": ids["C"]})
check("after 'trust new key' traffic flows", link_with("A", "C")["e2e"]["state"] == "ok" and arrives("A", "C", "LongFast"))

# ── ending things ──────────────────────────────────────────────────────────
sec("ending links, removing, leaving")
sa2, sb2 = send("A", "LongFast"), send("B", "LongFast")
check("before ending: C has a node from A and one from B", wait(lambda: {f"!{sa2:08x}", f"!{sb2:08x}"} <= {x["id"] for x in h["C"]("/api/nodes")}, 8))
h["A"]("/api/links/remove", {"link": link_with("A", "C")["id"]})
check("ending a link: gone on both sides", wait(lambda: not link_with("A", "C") and not link_with("C", "A")))
cA, cC = h["A"]("/api/config"), h["C"]("/api/config")
check("... A forgot C's rules and pinned key", ids["C"] not in cA["rules"] and ids["C"] not in cA["peer_keys"], (list(cA["rules"]), list(cA["peer_keys"])))
check("... C forgot A's rules and pinned key", ids["A"] not in cC["rules"] and ids["A"] not in cC["peer_keys"])
check("... C's radio forgot the nodes that came from A (checked by re-reading the radio)", wait(lambda: "checked on the radio" in open(f"{T}/hubC.log").read() and f"!{sa2:08x}" not in [x["id"] for x in h["C"]("/api/nodes")], 40),
      [x["id"] for x in h["C"]("/api/nodes") if x.get("remote")])
check("... nodes from B (still linked) stay on C's radio", f"!{sb2:08x}" in [x["id"] for x in h["C"]("/api/nodes")])
import sqlite3 as _sq
_db = _sq.connect(f"{T}/srv/ura.db")
check("... server: link and its statistics deleted", _db.execute("SELECT COUNT(*) FROM links WHERE (a=? AND b=?) OR (a=? AND b=?)", (ids["A"], ids["C"], ids["C"], ids["A"])).fetchone()[0] == 0
      and _db.execute("SELECT COUNT(*) FROM stats WHERE (src=? AND dst=?) OR (src=? AND dst=?)", (ids["A"], ids["C"], ids["C"], ids["A"])).fetchone()[0] == 0)
_db.close()
check("... other links untouched", link_with("A", "B")["state"] == "active" and link_with("B", "C")["state"] == "active")
check("... server agrees", not any({l["a"], l["b"]} == {ids["A"], ids["C"]} for l in S("/api/admin/state")["links"]))
S(f"/api/admin/hub/{ids['C']}/remove", {})
check("admin removes hub C: C told 'removed'", wait(lambda: status("C")["server"]["status"] == "removed", 10), status("C")["server"])
check("... its link at B is gone", wait(lambda: not link_with("B", "C"), 8))
check("... A-B untouched", link_with("A", "B")["state"] == "active")
check("... C gone from public list + nodes", ids["C"] not in [x["id"] for x in S("/api/public/hubs")])
def c_left():
    d_ = sqlite3.connect(f"{T}/srv/ura.db")
    n_ = sum(d_.execute(q, (ids["C"], ids["C"])).fetchone()[0] for q in (
        "SELECT COUNT(*) FROM hubs WHERE id=? OR id=?", "SELECT COUNT(*) FROM links WHERE a=? OR b=?",
        "SELECT COUNT(*) FROM stats WHERE src=? OR dst=?", "SELECT COUNT(*) FROM nodes WHERE hub=? OR hub=?"))
    d_.close()
    return n_ == 0
import sqlite3
check("... server: nothing about C left (hub, links, statistics, nodes)", wait(c_left, 8))
r = h["B"]("/api/server/forget", {})
check("B leaves the server", r.get("ok"), r)
check("... server removed B and the A-B link", wait(lambda: not any(x["id"] == ids["B"] for x in S("/api/admin/state")["hubs"]), 8))
check("... A sees the link gone", wait(lambda: not link_with("A", "B"), 8))
check("... B's settings unlocked for a new registration", not h["B"]("/api/config")["server"]["hub_id"])
check("... B's old link rules and partner keys cleared", not h["B"]("/api/config")["rules"] and not h["B"]("/api/config")["peer_keys"])
sv = h["B"]("/api/config")["server"]
check("... nothing about the server left: no address, no trusted fingerprint", not sv.get("address") and not sv.get("fingerprint") and not sv.get("key"), sv)
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

# ── more functions ─────────────────────────────────────────────────────────
import signal, sqlite3
me = lambda n: int(NODE[n] + "00000", 16)

sec("diagnostics (Radio page)")
h["A"]("/api/advanced", {"advanced": {"diag_timeout_s": 10}})
r = h["A"]("/api/diag", {"node": f"!{me('A') + 1:08x}", "kind": "dm", "text": "hi"})
check("private message: delivered, confirmed by the node itself (own radio's ack ignored)", r.get("result") == "delivered" and r.get("from") == f"!{me('A') + 1:08x}", r)
r = h["A"]("/api/diag", {"node": f"!{me('A') + 1:08x}", "kind": "trace"})
check("traceroute: route both ways", r.get("result") == "route" and r.get("route_to") == ["Neighbour two"] and r.get("route_back") == ["Neighbour two"], r)
r = h["A"]("/api/diag", {"node": f"!{me('A') + 1:08x}", "kind": "telemetry"})
check("telemetry request answered", r.get("result") == "telemetry" and r["telemetry"].get("deviceMetrics", {}).get("batteryLevel") == 88, r)
t0 = time.time(); r = h["A"]("/api/diag", {"node": f"!{me('A') + 2:08x}", "kind": "telemetry"})
check("telemetry: node only confirms, sends no data -> 'received, no data' (not 'delivered')", r.get("result") == "no_data" and r.get("answered") is False, r)
r = h["A"]("/api/diag", {"node": f"!{me('A') + 2:08x}", "kind": "position"})
check("position request answered", r.get("result") == "position" and r["position"]["lat"], r)
t0 = time.time(); r = h["A"]("/api/diag", {"node": f"!{me('A') + 50:08x}", "kind": "dm"})
check("no answer -> 'no answer' after the set waiting time (10 s)", r.get("answered") is False and 9.5 <= time.time() - t0 < 14, (r, round(time.time() - t0, 1)))
r = h["A"]("/api/diag", {"node": "", "kind": "broadcast", "channel": 1, "text": "group test"})
check("channel test message sent on the chosen channel", r.get("result") == "sent" and any(x["kind"] == "text" and x["channel"] == 1 for x in h["A"]("/api/test/radio")["sent"]), r)
check("bad node id refused", h["A"]("/api/diag", {"node": "xyz", "kind": "dm"}).get("_status") == 400)

sec("prepare radio for Ura")
h["A"]("/api/radio/section", {"kind": "module", "section": "mqtt", "values": {"enabled": False}})
check("radio with MQTT off is shown as not ready", wait(lambda: status("A")["radio"]["ready"] is False, 5), status("A")["radio"].get("checks"))
h["A"]("/api/advanced", {"advanced": {"mqtt_address": "127.0.0.2"}})
h["A"]("/api/radio/prepare", {})
w = [c for c in h["A"]("/api/test/radio")["calls"] if c["call"] == "writeConfig" and c["section"] == "mqtt"][-1]["values"]
check("prepare writes MQTT on + proxy + encryption + the set address", w.get("enabled") and w.get("proxy_to_client_enabled") and w.get("encryption_enabled") and w.get("address") == "127.0.0.2", w)
check("prepare in one transaction (one restart)", [c["call"] for c in h["A"]("/api/test/radio")["calls"]][-6:].count("commit") == 1)
check("radio ready again", wait(lambda: status("A")["radio"]["ready"], 5), status("A")["radio"].get("checks"))
h["A"]("/api/advanced", {"advanced": {"mqtt_address": "127.0.0.1"}})

sec("airtime: daily limit")
h["B"]("/api/hub", {"airtime": {"pct_hour": 0, "pct_day": 0.00001}})
check("over the daily limit -> not on air", not arrives("A", "B", "LongFast", expect=False) and blocked("B", "A", "recv", "airtime") > 0)
h["B"]("/api/hub", {"airtime": {"pct_hour": 10, "pct_day": 0}})
check("limit removed -> on air", arrives("A", "B", "LongFast"))

sec("duplicates, replays, tampering")
topic, data, snd = packet("LongFast")
for _ in range(2):
    h["A"]("/api/test/inject", {"topic": topic, "data": base64.b64encode(data).decode()}); time.sleep(0.3)
time.sleep(3)
check("same packet heard twice -> on air once", sum(1 for d in h["B"]("/api/test/radio")["downlink"]
      if (lambda e: (e.ParseFromString(base64.b64decode(d["data"])), getattr(e.packet, "from"))[1])(mqtt_pb2.ServiceEnvelope()) == snd) == 1)
h["B"]("/api/advanced", {"advanced": {"replay_window_s": 60}})
sr = send("A", "LongFast"); wait(lambda: sr in senders_on_air("B"), 5)
on_air = lambda: len(h["B"]("/api/test/radio")["downlink"])
n0, rec0 = on_air(), peer_counts("B", "A").get("received", 0)
h["B"]("/api/test/replay", {"index": -1}); time.sleep(1)
check("the same encrypted box replayed -> dropped", on_air() == n0 and peer_counts("B", "A").get("received", 0) == rec0)
bb0 = blocked("B", "A", "recv", "bad_box")
h["B"]("/api/test/replay", {"index": -1, "tamper": True}); time.sleep(1)
check("a box altered on the way -> rejected", blocked("B", "A", "recv", "bad_box") == bb0 + 1 and on_air() == n0)

sec("hub advanced settings: do they take effect")
h["A"]("/api/advanced", {"advanced": {"node_max_age_days": 2, "nodes_check_s": 10}})
check("node age 2 days -> the 3-day-old node leaves the server map", wait(lambda: "Three days" not in [x["name"] for x in pub("A")["nodes"]] and pub("A")["nodes"], 15),
      [x["name"] for x in pub("A")["nodes"]])
h["A"]("/api/advanced", {"advanced": {"node_max_age_days": 7}})
check("node age 7 days -> it is back", wait(lambda: "Three days" in [x["name"] for x in pub("A")["nodes"]], 15))
lat0, lon0 = pub("A")["hub"]["lat"], pub("A")["hub"]["lon"]
h["A"]("/api/advanced", {"advanced": {"location_follow_m": 50}})
h["A"]("/api/radio/fixed", {"fixed": {"enabled": True, "lat": lat0 + 0.00018, "lon": lon0, "alt": 10}})
time.sleep(4)
check("radio moved ~20 m, follow distance 50 m -> hub position unchanged", abs(pub("A")["hub"]["lat"] - lat0) < 1e-6, pub("A")["hub"]["lat"])
h["A"]("/api/advanced", {"advanced": {"location_follow_m": 10}})
check("follow distance 10 m -> hub follows the radio", wait(lambda: abs(pub("A")["hub"]["lat"] - (lat0 + 0.00018)) < 1e-5, 6), pub("A")["hub"]["lat"])
h["A"]("/api/advanced", {"advanced": {"clock_sync": False}})
h["A"]("/api/radio", {"radio": {"transport": "serial", "address": "/dev/fake-A2"}})
wait(lambda: status("A")["radio"]["connected"] and status("A")["radio"]["address"] == "/dev/fake-A2", 15); time.sleep(6)
check("clock sync off -> radio clock not set on connect", not any(c["call"] == "setTime" for c in h["A"]("/api/test/radio")["calls"]))
h["A"]("/api/advanced", {"advanced": {"clock_sync": True}})
h["A"]("/api/radio", {"radio": {"transport": "serial", "address": "/dev/fake-A3"}})
check("clock sync on -> radio clock set on connect", wait(lambda: any(c["call"] == "setTime" for c in h["A"]("/api/test/radio")["calls"]), 15))
# the hub asks every port what is plugged in, and keeps only a Meshtastic radio
t0_ = time.time(); pl = {x["path"]: x for x in h["A"]("/api/ports")}
check("ports: the list comes at once, without talking to the devices", time.time() - t0_ < 2 and set(pl) >= {"/dev/fake", "/dev/fake-meshcore", "/dev/fake-unknown"}, pl)
kinds = tuple(h["A"]("/api/ports?check=" + q)["kind"] for q in ("/dev/fake", "/dev/fake-meshcore", "/dev/fake-unknown"))
check("ports: checking each port says what is on it (Meshtastic / MeshCore / not a radio)", kinds == ("meshtastic", "meshcore", "unknown"), kinds)
rmc = h["A"]("/api/radio", {"radio": {"transport": "serial", "address": "/dev/fake-meshcore"}})
check("save a port known to hold a MeshCore radio -> refused at once, the answer names it as MeshCore",
      rmc.get("_status") == 400 and rmc.get("error") == "not_meshtastic" and rmc["found"]["kind"] == "meshcore" and "MeshCore" in rmc.get("text", ""), rmc)
run_ = h["A"]("/api/config")["radios"]
check("... the saved radio is unchanged and still connected", run_ and run_[0]["address"] == "/dev/fake-A3" and status("A")["radio"]["connected"], run_)
run_ = h["A"]("/api/radio", {"radio": {"transport": "serial", "address": "/dev/fake-unknown"}})
check("save a port that was not checked -> the hub tries to connect", run_.get("ok") and run_.get("state") == "connecting", run_)
res_ = wait(lambda: (lambda x: x if x.get("state") == "refused" else None)(h["A"]("/api/radio/result")), 20)
check("... it is not a Meshtastic radio -> refused, named, and nothing kept", res_ and res_["found"]["kind"] == "unknown" and h["A"]("/api/config")["radios"] == [], res_)
run_ = h["A"]("/api/radio", {"radio": {"transport": "serial", "address": "/dev/fake-A3"}})
res_ = wait(lambda: (lambda x: x if x.get("state") == "connected" else None)(h["A"]("/api/radio/result")), 20)
check("save the Meshtastic radio -> connected, the answer names it and its node count", res_ and res_["found"]["kind"] == "meshtastic" and res_["found"]["name"] and res_["found"]["nodes"], res_)
check("... its nodes are on the server map", wait(lambda: len(pub("A")["nodes"]) > 0, 15))
h["A"]("/api/radio/remove", {})
check("remove radio -> its nodes deleted from the server map too", wait(lambda: len(pub("A")["nodes"]) == 0, 10), len(pub("A")["nodes"]))
h["A"]("/api/radio", {"radio": {"transport": "serial", "address": "/dev/fake-A3"}})
check("... connect it again -> nodes back on the map", wait(lambda: len(pub("A")["nodes"]) > 0, 20))
h["B"]("/api/advanced", {"advanced": {"keepalive_s": 5}})
ls0 = pub("B")["hub"]["last_seen"]; time.sleep(7)
check("keepalive 5 s -> server sees the hub alive every 5 s", pub("B")["hub"]["last_seen"] > ls0, (ls0, pub("B")["hub"]["last_seen"]))
h["A"]("/api/advanced", {"advanced": {"password_min": 12}})
check("password minimum 12 -> 11 characters refused", h["A"]("/api/password", {"password": "Elevenchars"}).get("_status") == 400)
h["A"]("/api/advanced", {"advanced": {"password_min": 8}})
def set_cookie(base, pw):
    req = urllib.request.Request(base + "/api/login", data=json.dumps({"password": pw}).encode(), headers={"Content-Type": "application/json"})
    return urllib.request.urlopen(req, context=ctx, timeout=30).headers.get("Set-Cookie", "")
h["A"]("/api/advanced", {"advanced": {"session_hours": 2}})
check("session length 2 h -> login cookie lasts 7200 s", "Max-Age=7200" in set_cookie(f"https://127.0.0.1:{HUBS['A'][0]}", PW))
check("tile source must be an https URL with {z}/{x}/{y}", h["A"]("/api/advanced", {"advanced": {"tile_source": "http://x/{z}"}}).get("_status") == 400)
tile = lambda base: urllib.request.urlopen(urllib.request.Request(base + "/tiles/2/1/1.png"), context=ctx, timeout=30).read()
try: t1 = tile(f"https://127.0.0.1:{HUBS['A'][0]}")
except Exception as e: t1 = b""
check("map tile through hub -> server -> map server", t1[:4] == b"\x89PNG", len(t1))

sec("server advanced settings: do they take effect")
S("/api/admin/advanced", {"advanced": {"node_max_age_days": 2}}); h["D"]("/api/advanced", {"advanced": {}})
check("server node age 2 days -> D's 3-day node not shown", wait(lambda: pub("D")["nodes"] and "Three days" not in [x["name"] for x in pub("D")["nodes"]], 10),
      [x["name"] for x in pub("D")["nodes"]])
S("/api/admin/advanced", {"advanced": {"node_max_age_days": 7, "max_nodes_per_report": 10}}); h["D"]("/api/advanced", {"advanced": {}})
check("max nodes per report 10 -> D (19 nodes) shows 10", wait(lambda: len(pub("D")["nodes"]) == 10, 10), len(pub("D")["nodes"]))
S("/api/admin/advanced", {"advanced": {"max_nodes_per_report": 2000}})
S("/api/admin/advanced", {"advanced": {"relay_rate_per_s": 1, "relay_burst": 1}})
sent6 = [send("A", "LongFast") for _ in range(6)]; time.sleep(4)
got = len(set(sent6) & senders_on_air("B"))
check("flood limit 1/s -> most of 6 quick packets dropped by the server", 1 <= got <= 3, got)
S("/api/admin/advanced", {"advanced": {"relay_rate_per_s": 30, "relay_burst": 200, "max_box_bytes": 300}})
topic, data, big = packet("LongFast", size=400)
h["A"]("/api/test/inject", {"topic": topic, "data": base64.b64encode(data).decode()}); time.sleep(3)
check("max box size 300 -> a big packet is not relayed", big not in senders_on_air("B"))
S("/api/admin/advanced", {"advanced": {"max_box_bytes": 3000}})
check("max box size 3000 -> relayed", arrives("A", "B", "LongFast"))
S("/api/admin/advanced", {"advanced": {"complaints_per_hour": 1}})
check("complaints per hour 1 -> second complaint refused", S("/api/public/complaints", {"email": "y@example.org", "text": "another long enough complaint", "subject_type": "general"}).get("_status") == 429)
S("/api/admin/advanced", {"advanced": {"complaints_per_hour": 50, "complaint_max_chars": 100}})
cid = S("/api/public/complaints", {"email": "y@example.org", "text": "z" * 300, "subject_type": "general"}).get("id")
check("complaint max 100 characters -> longer text cut", any(x["id"] == cid and len(x["text"]) == 100 for x in S("/api/public/complaints")))
S("/api/admin/advanced", {"advanced": {"project_url": "https://example.org/p", "install_guide_url": "https://example.org/g"}})
inf = S("/api/public/info")
check("project + install guide links shown", inf.get("project_url") == "https://example.org/p" and inf.get("install_guide_url") == "https://example.org/g", inf)
S("/api/admin/advanced", {"advanced": {"session_hours": 3}})
check("server session 3 h -> admin cookie lasts 10800 s", "Max-Age=10800" in set_cookie(f"https://127.0.0.1:{SRV_WEB}", PW + "S"))
try: t2 = tile(f"https://127.0.0.1:{SRV_WEB}")
except Exception: t2 = b""
check("server map tile", t2[:4] == b"\x89PNG", len(t2))

sec("server restart, queue, statistics retention")
srv_pid = lambda: subprocess.run(f"ss -ltnp 'sport = :{SRV_HUB_PORT}' | grep -oP 'pid=\\K[0-9]+' | head -1", shell=True, capture_output=True, text=True).stdout.strip()
S("/api/admin/advanced", {"advanced": {"stats_retention_days": 7}})
h["A"]("/api/advanced", {"advanced": {"queue_max": 50, "server_retry_s": 3}})
os.kill(int(srv_pid()), signal.SIGTERM); time.sleep(2)
db = sqlite3.connect(f"{T}/srv/ura.db"); db.execute("INSERT INTO stats(src,dst,net,hour,frames,bytes) VALUES('old','old','mt',?,5,500)", ((int(time.time()) // 3600 - 24 * 30) * 3600,)); 
# leftovers like a server from before the clean-up rule: a removed hub, an ended link, statistics of a link that is gone
db.execute("INSERT INTO stats(src,dst,net,hour,frames,bytes) VALUES('h_gone1','h_gone2','mt',?,3,300)", (int(time.time()) // 3600 * 3600,))
hc = [r[1] for r in db.execute("PRAGMA table_info(hubs)")]
row = dict(zip(hc, db.execute("SELECT * FROM hubs LIMIT 1").fetchone())); row.update(id="h_gone1", status="removed")
db.execute(f"INSERT INTO hubs({','.join(row)}) VALUES({','.join('?' * len(row))})", tuple(row.values()))
lc = [r[1] for r in db.execute("PRAGMA table_info(links)") if r[1] != "id"]
lrow = dict(zip(lc, db.execute(f"SELECT {','.join(lc)} FROM links LIMIT 1").fetchone())); lrow.update(a="h_gone1", b="h_gone2", state="removed")
db.execute(f"INSERT INTO links({','.join(lrow)}) VALUES({','.join('?' * len(lrow))})", tuple(lrow.values()))
db.commit(); db.close()
check("hub notices the server is gone", wait(lambda: status("A")["link_state"] != "connected", 10), status("A")["link_state"])
queued = [send("A", "LongFast") for _ in range(55)]
subprocess.Popen(f"cd {REPO}/server && URA_DATA={T}/srv URA_PORT={SRV_HUB_PORT} URA_WEB_PORT={SRV_WEB} setsid nohup python3 -u ura_server.py >> {T}/server.log 2>&1 < /dev/null &", shell=True)
t0 = time.time()
check("hub reconnects within the retry time (3 s) + start-up", wait(lambda: status("A")["link_state"] == "connected", 15) and time.time() - t0 < 10, round(time.time() - t0, 1))
S = client(f"https://127.0.0.1:{SRV_WEB}"); S("/api/login", {"password": PW + "S"})
wait(lambda: status("B")["link_state"] == "connected", 15); time.sleep(6)
got = len(set(queued) & senders_on_air("B"))
check("packets heard while the server was down are delivered afterwards (queue)", got >= 40, f"{got} of 55")
check("... but no more than the queue size (50)", got <= 50, f"{got} of 55")
db = sqlite3.connect(f"{T}/srv/ura.db"); old = db.execute("SELECT COUNT(*) FROM stats WHERE src='old'").fetchone()[0]; db.close()
check("statistics older than 7 days removed", old == 0, old)
db = sqlite3.connect(f"{T}/srv/ura.db")
left = (db.execute("SELECT COUNT(*) FROM stats WHERE src='h_gone1'").fetchone()[0], db.execute("SELECT COUNT(*) FROM hubs WHERE status='removed'").fetchone()[0],
        db.execute("SELECT COUNT(*) FROM links WHERE state='removed'").fetchone()[0])
db.close()
check("server start clean-up: statistics of links that are gone, removed hubs, ended links -> all deleted", left == (0, 0, 0), left)

sec("waiting times: lockouts, replay window, watchdog, silent server")
h["A"]("/api/advanced", {"advanced": {"lockout_attempts": 3, "lockout_minutes": 1}})
S("/api/admin/advanced", {"advanced": {"lockout_attempts": 3, "lockout_minutes": 1}})
h["D"]("/api/advanced", {"advanced": {"radio_watchdog_min": 1}})
la_, ls_ = client(f"https://127.0.0.1:{HUBS['A'][0]}"), client(f"https://127.0.0.1:{SRV_WEB}")
for _ in range(3): la_("/api/login", {"password": "wrong"}); ls_("/api/login", {"password": "wrong"})
check("hub: 3 wrong passwords -> locked, even the right one", la_("/api/login", {"password": PW}).get("_status") == 429)
check("server: 3 wrong passwords -> locked, even the right one", ls_("/api/login", {"password": PW + "S"}).get("_status") == 429)
time.sleep(63)
check("hub: unlocked after 1 minute", la_("/api/login", {"password": PW}).get("ok"))
check("server: unlocked after 1 minute", ls_("/api/login", {"password": PW + "S"}).get("ok"))
bb0 = blocked("B", "A", "recv", "bad_box")
h["B"]("/api/test/replay", {"index": -1}); time.sleep(1)
check("a box older than the replay window (60 s) -> rejected", blocked("B", "A", "recv", "bad_box") == bb0 + 1)
ev = status("D")["radio"].get("watchdog_events") or []
check("watchdog: silent radio -> diagnosis + fresh USB session after 1 minute", any("fresh USB session" in e["finding"] for e in ev), ev)
h["A"]("/api/advanced", {"advanced": {"server_timeout_s": 30}})
pid = int(srv_pid()); os.kill(pid, signal.SIGSTOP)
check("server frozen (no answers) -> hub gives up after 30 s", wait(lambda: status("A")["link_state"] != "connected", 45), status("A")["link_state"])
os.kill(pid, signal.SIGCONT)
check("... and reconnects when the server answers again", wait(lambda: status("A")["link_state"] == "connected", 20))

sec("channels and keys")
from meshtastic.protobuf import apponly_pb2
def code_of(name, key):
    x = 0
    for b in name.encode() + key: x ^= b
    return x
ra = lambda: status("A")["radio"]
check("channel codes shown; public LongFast = 8", next(c for c in ra()["channels"] if c["name"] == "LongFast")["code"] == 8, ra()["channels"])
h["A"]("/api/test/fake", {"call": "hear", "args": {"code": 44, "sender": "!0abc1234"}}); time.sleep(1)
u = ra()["unknown_channels"]
check("radio hears a channel it cannot read -> shown with code + sender", u and u[0]["code"] == 44 and u[0]["senders"][0]["id"] == "!0abc1234", u)
h["A"]("/api/test/fake", {"call": "hear", "args": {"code": 8, "sender": "!0abc1235"}}); time.sleep(1)
check("a channel the radio knows is not listed", all(x["code"] != 8 for x in ra()["unknown_channels"]))
check("the hub keeps a saved copy of the radio's channels", any(c["name"] == "Team" for c in h["A"]("/api/radio/settings")["channels_saved"]))
check("saved copy = radio", ra()["channels_match"] is True)
h["A"]("/api/test/fake", {"call": "channel", "args": {"index": 1, "name": "Changed", "psk": base64.b64encode(b"k" * 16).decode()}})
check("channel changed outside the hub (phone app) -> 'differs' shown", ra()["channels_match"] is False)
h["A"]("/api/radio/channels_restore", {})
c1 = next((c for c in ra()["channels"] if c["index"] == 1), {})
check("'write the saved channels' -> radio has Team with its key again", c1.get("name") == "Team" and c1.get("code") == code_of("Team", TEAM_PSK) and ra()["channels_match"], c1)
h["A"]("/api/test/fake", {"call": "channel", "args": {"index": 1, "name": "Changed", "psk": base64.b64encode(b"k" * 16).decode()}})
h["A"]("/api/radio/channels_keep", {})
check("'keep the radio's channels' -> saved copy updated", ra()["channels_match"] and any(c["name"] == "Changed" for c in h["A"]("/api/radio/settings")["channels_saved"]))
h["A"]("/api/radio/channel", {"channel": {"index": 1, "role": "SECONDARY", "name": "Team", "psk": base64.b64encode(TEAM_PSK).decode(), "uplink": True, "downlink": True, "position_precision": 0, "muted": False}})
check("channel set from the hub -> saved copy follows", ra()["channels_match"] and any(c["name"] == "Team" for c in h["A"]("/api/radio/settings")["channels_saved"]))
cs = apponly_pb2.ChannelSet(); st = cs.settings.add(); st.name = "Club"; club_key = os.urandom(32); st.psk = club_key
cs.lora_config.modem_preset = 4; cs.lora_config.region = 3
url = "https://meshtastic.org/e/#" + base64.urlsafe_b64encode(cs.SerializeToString()).decode().rstrip("=")
r = h["A"]("/api/radio/channels_import", {"url": url})
check("channel link: channel added with its key", r.get("added") == ["Club"] and any(c["name"] == "Club" and c["code"] == code_of("Club", club_key) for c in ra()["channels"]), r)
check("... warns that the link uses another LoRa preset", r.get("warning") == "lora_differs", r)
check("... uplink + downlink on (needed by Ura)", (lambda c: c and c["uplink"] and c["downlink"])(next((c for c in ra()["channels"] if c["name"] == "Club"), None)))
check("... saved copy includes it", any(c["name"] == "Club" for c in h["A"]("/api/radio/settings")["channels_saved"]))
check("same link again -> 'already there'", h["A"]("/api/radio/channels_import", {"url": url}).get("skipped") == ["Club"])
check("not a channel link -> clear error", h["A"]("/api/radio/channels_import", {"url": "https://example.org/x"}).get("error") == "channel_link")
h["B"]("/api/radio/channel", {"channel": {"index": 1, "role": "SECONDARY", "name": "Team", "psk": base64.b64encode(b"o" * 32).decode(), "uplink": True, "downlink": True, "position_precision": 0, "muted": False}})
time.sleep(1)
check("both hubs have 'Team' with different keys -> not put on air, reason 'other key'",
      not arrives("A", "B", "Team", expect=False) and blocked("B", "A", "recv", "key_differs") > 0, peer_counts("B", "A"))
h["B"]("/api/radio/channel", {"channel": {"index": 1, "role": "SECONDARY", "name": "Team", "psk": base64.b64encode(TEAM_PSK).decode(), "uplink": True, "downlink": True, "position_precision": 0, "muted": False}})
time.sleep(1)
check("same key again -> Team passes", arrives("A", "B", "Team"))

sec("region check, forget a node")
h["A"]("/api/radio/section", {"kind": "config", "section": "lora", "values": {"region": "UNSET"}})
check("radio without a LoRa region -> not ready, 'region set' red", status("A")["radio"]["checks"].get("region_set") is False and not status("A")["radio"]["ready"], status("A")["radio"]["checks"])
h["A"]("/api/radio/section", {"kind": "config", "section": "lora", "values": {"region": "EU_868"}})
check("region set again -> ready", status("A")["radio"]["checks"].get("region_set") and status("A")["radio"]["ready"])
nid = f"!{me('A') + 1:08x}"
r = h["A"]("/api/radio/forget_node", {"node": nid})
check("forget a node -> removed from the radio's node list", r.get("ok") and not any(x["id"] == nid for x in h["A"]("/api/nodes")), r)
check("forget: bad node id refused", h["A"]("/api/radio/forget_node", {"node": "abc"}).get("error") == "bad_node")
n_sent = len(h["A"]("/api/test/radio")["sent"])
check("clear the radio's node list -> only the radio itself left", h["A"]("/api/radio/reset_nodes", {}).get("ok") and [x["own"] for x in h["A"]("/api/nodes")] == [True], h["A"]("/api/nodes"))
check("... and the neighbours are asked to answer", wait(lambda: any(x.get("want_response") for x in h["A"]("/api/test/radio")["sent"][n_sent:]), 10))
pos0 = status("A")["radio_position"]
n_calls = len(h["A"]("/api/test/radio")["calls"])
check("... the radio's own position (wiped by the radio with the list) is written back",
      pos0 and wait(lambda: any(x["call"] == "setFixedPosition" and abs(x["lat"] - pos0["lat"]) < 1e-6 for x in h["A"]("/api/test/radio")["calls"][n_calls - 5:]), 15), pos0)
h["A"]("/api/test/fake", {"call": "no_position", "reconnect": True})
check("radio without GPS and without a position -> 'has a position' red, not ready",
      wait(lambda: status("A")["radio"]["connected"] and status("A")["radio"]["checks"].get("position_known") is False, 20) and not status("A")["radio"]["ready"],
      (status("A")["radio"] or {}).get("checks"))
hub_loc = h["A"]("/api/config")["hub"]
h["A"]("/api/radio/prepare", {})
check("... 'Prepare' gives the radio the hub's location as fixed position -> ready",
      wait(lambda: any(x["call"] == "setFixedPosition" and abs(x["lat"] - hub_loc["lat"]) < 1e-6 for x in h["A"]("/api/test/radio")["calls"]), 60)
      and wait(lambda: status("A")["radio"]["checks"].get("position_known") and status("A")["radio"]["ready"], 15), (hub_loc, status("A")["radio"]["checks"]))

sec("remove the radio from the hub, connect it again")
r = h["A"]("/api/radio/remove", {})
check("'Remove this radio' -> the hub has no radio set up", r.get("ok") and h["A"]("/api/config")["radios"] == [] and wait(lambda: status("A")["radio"] is None, 8), status("A")["radio"])
check("... the saved channel copy is forgotten too", not h["A"]("/api/config").get("channels_saved"))
h["A"]("/api/radio", {"radio": {"transport": "serial", "address": "/dev/fake-A"}})
check("connected again like a new radio -> connected, ready, channels saved again", wait(lambda: (status("A")["radio"] or {}).get("connected") and status("A")["radio"]["ready"], 15)
      and h["A"]("/api/config").get("channels_saved"))

sec("two channels with the same name (a channel without a name = the preset name)")
dup_key = os.urandom(32)
for n in ("A", "B"):
    h[n]("/api/radio/channel", {"channel": {"index": 2, "role": "SECONDARY", "name": "", "psk": base64.b64encode(dup_key).decode(), "uplink": True, "downlink": True, "position_precision": 0, "muted": False}})
time.sleep(1)
check("both radios: public LongFast (code 8) + private 'LongFast' without a name", sum(1 for c in ra()["channels"] if c["name"] == "LongFast") == 2, ra()["channels"])
check("public LongFast still crosses (was broken: the second key was used)", arrives("A", "B", "LongFast"))
check("public positions still cross", arrives("A", "B", "LongFast", "position"))
def send_dup(frm):
    topic, data, snd = packet("LongFast", key=dup_key)
    h[frm]("/api/test/inject", {"topic": topic, "data": base64.b64encode(data).decode()}); return snd
sd = send_dup("A"); time.sleep(3)
check("private same-name channel, group not ticked -> blocked as group", sd not in senders_on_air("B") and blocked("A", "B", "send", "group") > 0)
rules("A", "B", send={"groups": ["Team", "LongFast"]}); rules("B", "A", receive={"groups": ["Team", "LongFast"]})
sd = send_dup("A")
check("group 'LongFast' (private) ticked on both -> crosses", wait(lambda: sd in senders_on_air("B"), 5))
for n in ("A", "B"):
    h[n]("/api/radio/channel", {"channel": {"index": 2, "role": "DISABLED"}})

sec("logs and program control")
def raw(base, path, pw):
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), urllib.request.HTTPSHandler(context=ctx))
    op.open(urllib.request.Request(base + "/api/login", data=json.dumps({"password": pw}).encode(), headers={"Content-Type": "application/json"}), timeout=30)
    r = op.open(base + path, timeout=30)
    return r.headers, r.read().decode()
lg = h["A"]("/api/logs?lines=300")
check("hub log: newest lines shown", lg.get("lines") and any("ura-hub" in l and "started" in l for l in lg["lines"]), (lg.get("lines") or [])[-3:])
check("hub log: files listed", lg.get("files") and lg["files"][0]["name"] == "ura-hub.log")
er = h["A"]("/api/logs?lines=300&level=warning")["lines"]
check("hub log: 'warnings and errors' shows only those", er and all((" WARNING " in l or " ERROR " in l or " CRITICAL " in l) for l in er), er[:2])
check("hub log: search", all("radio" in l.lower() for l in h["A"]("/api/logs?lines=300&q=radio")["lines"]))
hd, body = raw(f"https://127.0.0.1:{HUBS['A'][0]}", "/api/logs/file?name=ura-hub.log", PW)
check("hub log: download as a text file", "attachment" in hd.get("Content-Disposition", "") and "ura-hub" in body)
check("hub log: other file names refused", h["A"]("/api/logs/file?name=../config.json").get("_status") == 404)
check("server log: only for the admin", client(f"https://127.0.0.1:{SRV_WEB}")("/api/admin/logs").get("_status") == 401)
slg = S("/api/admin/logs?lines=200")
check("server log: newest lines shown", slg.get("lines") and any("ura-server" in l for l in slg["lines"]))
hd, body = raw(f"https://127.0.0.1:{SRV_WEB}", "/api/admin/logs/file?name=ura-server.log", PW + "S")
check("server log: download", "attachment" in hd.get("Content-Disposition", "") and "hubs connect" in body)
st0 = h["B"]("/api/session")["started"]
h["B"]("/api/program", {"action": "restart"})
check("hub 'Restart program' -> runs again (new start time)", wait(lambda: client(f"https://127.0.0.1:{HUBS['B'][0]}")("/api/session").get("started", st0) > st0, 30))
h["B"] = client(f"https://127.0.0.1:{HUBS['B'][0]}"); h["B"]("/api/login", {"password": PW})
check("... back on the server, link to A active, radio connected", wait(lambda: status("B")["link_state"] == "connected" and (link_with("B", "A") or {}).get("state") == "active" and status("B")["radio"]["connected"], 30))
check("... traffic flows", arrives("A", "B", "LongFast"))
h["D"]("/api/program", {"action": "stop"}); time.sleep(4)
port_open = lambda p_: subprocess.run(f"ss -ltn 'sport = :{p_}' | grep -c LISTEN", shell=True, capture_output=True, text=True).stdout.strip() != "0"
check("hub 'Stop program' -> program ended, page off", not port_open(HUBS["D"][0]))
time.sleep(6)
check("... stays stopped", not port_open(HUBS["D"][0]))
s_st0 = S("/api/admin/state")["started"]
S("/api/admin/program", {"action": "restart"})
check("server 'Restart program' -> runs again", wait(lambda: (lambda c_: (c_("/api/login", {"password": PW + "S"}), c_("/api/admin/state").get("started", s_st0))[1])(client(f"https://127.0.0.1:{SRV_WEB}")) > s_st0, 30))
S = client(f"https://127.0.0.1:{SRV_WEB}"); S("/api/login", {"password": PW + "S"})
check("... hubs reconnect by themselves", wait(lambda: status("A")["link_state"] == "connected" and status("B")["link_state"] == "connected", 30))
check("... link A - B still active", (link_with("A", "B") or {}).get("state") == "active")

# ── factory reset: hub B (registered, linked with A) -> nothing left anywhere, first-start mode ──
section[0] = "factory reset"
idB = ids["B"]
MY_KEY_B = h["B"]("/api/status")["my_key"]
r_ = h["B"]("/api/factory_reset", {"confirm": "wrong"})
check("factory reset without typing RESET -> refused", r_.get("_status") == 400)
h["B"]("/api/factory_reset", {"confirm": "RESET"})
fresh = lambda: client(f"https://127.0.0.1:{HUBS['B'][0]}")("/api/session")
check("factory reset -> the hub restarts in first-start mode (choose a password)", wait(lambda: fresh().get("setup_needed") is True, 120))
def srv_left(hid):
    d_ = sqlite3.connect(f"{T}/srv/ura.db")
    n_ = sum(d_.execute(q, (hid, hid)).fetchone()[0] for q in (
        "SELECT COUNT(*) FROM hubs WHERE id=? OR id=?", "SELECT COUNT(*) FROM links WHERE a=? OR b=?",
        "SELECT COUNT(*) FROM stats WHERE src=? OR dst=?", "SELECT COUNT(*) FROM nodes WHERE hub=? OR hub=?"))
    d_.close(); return n_
check("... server: nothing about the hub left (hub, links, statistics, nodes)", wait(lambda: srv_left(idB) == 0, 10), srv_left(idB))
check("... partner A: the link and B's rules and key are gone", wait(lambda: not link_with("A", "B") and idB not in h["A"]("/api/config")["rules"]
                                                                 and idB not in h["A"]("/api/config")["peer_keys"], 15))
left_files = sorted(os.listdir(f"{T}/hB"))
check("... hub folder: old settings, node memory, backups and map cache deleted", not any(f.startswith(("origins", "config.")) or f == "tiles" for f in left_files)
      and "config.json" not in left_files or json.load(open(f"{T}/hB/config.json")).get("web_password") is None, left_files)
logtxt = open(f"{T}/hB/logs/ura-hub.log").read() if os.path.exists(f"{T}/hB/logs/ura-hub.log") else ""
check("... old log deleted; the new log starts with the reset", "factory reset done" in logtxt and "link to" not in logtxt, logtxt[:300])
hb = client(f"https://127.0.0.1:{HUBS['B'][0]}"); hb("/api/setup", {"password": PW})
cb = hb("/api/config")
check("... after a new password: no name, no server, no radio, no rules, no keys — like a new installation",
      not cb["hub"]["name"] and not cb["server"]["address"] and not cb["server"]["fingerprint"] and cb["radios"] == [] and cb["rules"] == {} and cb["peer_keys"] == {}
      and not cb.get("setup_done") and not cb.get("setup_skipped"), cb["server"])
check("... a new end-to-end identity (old key deleted)", hb("/api/status")["my_key"] != MY_KEY_B)

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
