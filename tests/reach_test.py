"""Per-link reach test: chain A-B-C-D (+ E linked to A). The origin decides PER LINK how far its packets go
and through which of the partner's links (no radios, URA_TEST_INJECT=1)."""
import json, os, random, ssl, subprocess, sys, time, urllib.request, http.cookiejar
from meshtastic.protobuf import mqtt_pb2
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.environ.get("URA_TEST_DIR", "/tmp/ura-reach"); PW = "TestPass123"
HUBPY = os.environ.get("URA_HUB_PYTHON", sys.executable)
S = "https://127.0.0.1:8179"; HUBS = {"A": 8177, "B": 8176, "C": 8175, "D": 8174, "E": 8173}
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
results = []
def check(name, cond): results.append((name, bool(cond))); print(("PASS " if cond else "FAIL ") + name, flush=True)
def client(base):
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), urllib.request.HTTPSHandler(context=ctx))
    def call(path, body=None):
        req = urllib.request.Request(base + path, data=json.dumps(body).encode() if body is not None else None,
                                     headers={"Content-Type": "application/json"}, method="POST" if body is not None else "GET")
        try: return json.loads(op.open(req, timeout=30).read())
        except urllib.error.HTTPError as e: return json.loads(e.read())
    return call
def start():
    subprocess.run(f"for p in 8179 8178 8177 8176 8175 8174 8173; do pid=$(ss -ltnp \"sport = :$p\" | grep -oP 'pid=\\K[0-9]+' | head -1); [ -n \"$pid\" ] && kill $pid; done; rm -rf {T}/d*; sleep 1", shell=True)
    subprocess.Popen(f"cd {REPO}/server && URA_DATA={T}/ds URA_PORT=8178 URA_WEB_PORT=8179 setsid nohup python3 -u ura_server.py > {T}/server.log 2>&1 < /dev/null &", shell=True)
    for n, port in HUBS.items():
        subprocess.Popen(f"cd {REPO}/hub && URA_TEST_INJECT=1 URA_DATA={T}/d{n} URA_WEB_PORT={port} setsid nohup {HUBPY} -u ura_hub.py > {T}/hub{n}.log 2>&1 < /dev/null &", shell=True)
    time.sleep(5)
os.makedirs(T, exist_ok=True); start()
s = client(S); s("/api/setup", {"password": PW})
h, ids = {}, {}
for i, (n, port) in enumerate(HUBS.items()):
    c = client(f"https://127.0.0.1:{port}"); c("/api/setup", {"password": PW}); h[n] = c
    c("/api/hub", {"hub": {"name": "Hub " + n, "email": f"{n}@example.org", "country": "XX", "city": n * 2, "lat": 40 + i, "lon": 10 + i}})
    fp = c("/api/server/check", {"address": "127.0.0.1:8178"})["fingerprint"]
    c("/api/server/trust", {"address": "127.0.0.1:8178", "fingerprint": fp})
    ids[n] = c("/api/server/join", {"address": "127.0.0.1:8178"})["hub_id"]
for n in HUBS: s(f"/api/admin/hub/{ids[n]}/approve", {})
time.sleep(4)
def link(x, y):
    h[x]("/api/links/request", {"to": ids[y]}); time.sleep(1.5)
    lk = [l for l in h[y]("/api/status")["links"] if l["peer"] == ids[x]][0]
    h[y]("/api/links/accept", {"link": lk["id"]}); time.sleep(1.5)
link("A", "B"); link("B", "C"); link("C", "D"); link("A", "E")
check("links active", all(l["state"] == "active" for n in HUBS for l in h[n]("/api/status")["links"]))
def envelope():
    env = mqtt_pb2.ServiceEnvelope(); env.channel_id = "PKI"; env.gateway_id = "!00000001"
    setattr(env.packet, "from", random.randint(1, 2**31)); env.packet.to = 0xFFFFFFFF; env.packet.id = random.randint(1, 2**31)
    env.packet.encrypted = os.urandom(40); env.packet.hop_limit = 3; env.packet.hop_start = 3
    return env.SerializeToString(), getattr(env.packet, "from")
import base64
def inject(hub):
    data, sender = envelope()
    h[hub]("/api/test/inject", {"topic": "msh/EU_868/2/e/PKI/!00000001", "data": base64.b64encode(data).decode()}); time.sleep(3)
    return f"!{sender:08x}"
def peers(hub): return h[hub]("/api/status")["counters"]["peers"]
def recv(hub, frm): p = peers(hub).get(ids[frm], {}); return p.get("received", 0) + sum(p.get("blocked_recv", {}).values())
def rules(hub, peer, send=None, receive=None):
    base = {"on": True, "public": True, "private": True, "positions": True, "groups": [], "onward_to": [], "transit": True}
    rec = {"on": True, "public": True, "private": True, "positions": True, "groups": [], "from_beyond": True}
    base.update(send or {}); rec.update(receive or {})
    h[hub]("/api/rules", {"peer": ids[peer], "rules": {"send": base, "receive": rec}})
def blocked(hub, frm, why): return peers(hub).get(ids[frm], {}).get("blocked_recv", {}).get(why, 0)
def blocked_send(hub, to, why): return peers(hub).get(ids[to], {}).get("blocked_send", {}).get(why, 0)
for n in HUBS: h[n]("/api/hub", {"transit": {"enabled": True, "max_hops": 8}})
time.sleep(4)   # transit lists are published
def got(hub, frm): return recv(hub, frm)
def run(reach, ticks, label):
    rules("A", "B", send={"reach": reach, "onward_to": [ids[x] for x in ticks]}); time.sleep(1)
    b = {n: got(n, f) for n, f in (("B", "A"), ("C", "B"), ("D", "C"), ("E", "A"))}
    inject("A"); time.sleep(2)
    return {n: got(n, f) - b[n] for n, f in (("B", "A"), ("C", "B"), ("D", "C"), ("E", "A"))}
r = run(0, [], "only B")
check("reach 0 via B: arrives at B, goes no further", r["B"] == 1 and r["C"] == 0 and r["D"] == 0)
r = run(1, ["C"], "1 further")
check("reach 1 via B (C ticked): reaches C, not D", r["C"] == 1 and r["D"] == 0)
r = run(1, [], "1 further, nothing ticked")
check("reach 1 but no link of B ticked: stops at B", r["B"] == 1 and r["C"] == 0)
r = run(2, ["C"], "2 further")
check("reach 2 via B (C ticked): reaches D", r["C"] == 1 and r["D"] == 1)
r = run(7, [], "anywhere")
check("reach anywhere via B: reaches D without ticks", r["C"] == 1 and r["D"] == 1)
check("link A-E has its own rule (still reach 0): E gets it, it stays there", r["E"] == 1)
# a transit hub's own limit still wins: C passes others' packets only in chains of at most 2 hops
h["C"]("/api/hub", {"transit": {"enabled": True, "max_hops": 2}}); time.sleep(1)
r = run(7, [], "anywhere, C limits")
check("transit hub's own chain limit is respected", r["C"] == 1 and r["D"] == 0)
pub = s("/api/public/hub/" + ids["A"])["hub"]["rules"]
check("A publishes its per-link reach", any(v["send"].get("reach") == 7 for v in (pub or {}).get("links", {}).values()))
subprocess.run("for p in 8179 8178 8177 8176 8175 8174 8173; do pid=$(ss -ltnp \"sport = :$p\" | grep -oP 'pid=\\K[0-9]+' | head -1); [ -n \"$pid\" ] && kill $pid; done", shell=True)
fails = [n for n, ok in results if not ok]
print(f"\n{len(results) - len(fails)}/{len(results)} passed"); sys.exit(1 if fails else 0)
