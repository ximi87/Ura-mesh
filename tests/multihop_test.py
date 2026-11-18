"""Multi-hop test: test server + hubs A, B, C (no radios, URA_TEST_INJECT=1).
Chain A-B-C: transit off at B -> stops; transit on -> reaches C with origin A. Triangle: no loop, no duplicates."""
import json, os, random, ssl, subprocess, sys, time, urllib.request, http.cookiejar
from meshtastic.protobuf import mqtt_pb2
T = "/tmp/ura-mh"; PW = "TestPass123"
S = "https://127.0.0.1:8189"; HUBS = {"A": 8187, "B": 8186, "C": 8185}
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
    subprocess.run(f"for p in 8189 8188 8187 8186 8185; do pid=$(ss -ltnp \"sport = :$p\" | grep -oP 'pid=\\K[0-9]+' | head -1); [ -n \"$pid\" ] && kill $pid; done; rm -rf {T}/d*; sleep 1", shell=True)
    subprocess.Popen(f"cd /tmp/ura-t/server && URA_DATA={T}/ds URA_PORT=8188 URA_WEB_PORT=8189 setsid nohup python3 -u ura_server.py > {T}/server.log 2>&1 < /dev/null &", shell=True)
    for n, port in HUBS.items():
        subprocess.Popen(f"cd /tmp/ura-t/hub && URA_TEST_INJECT=1 URA_DATA={T}/d{n} URA_WEB_PORT={port} setsid nohup /opt/fleet/venv/bin/python -u ura_hub.py > {T}/hub{n}.log 2>&1 < /dev/null &", shell=True)
    time.sleep(5)
os.makedirs(T, exist_ok=True); start()
s = client(S); s("/api/setup", {"password": PW})
h, ids = {}, {}
for i, (n, port) in enumerate(HUBS.items()):
    c = client(f"https://127.0.0.1:{port}"); c("/api/setup", {"password": PW}); h[n] = c
    c("/api/hub", {"hub": {"name": "Hub " + n, "email": f"{n}@example.org", "country": "XX", "city": n * 2, "lat": 40 + i, "lon": 10 + i}})
    fp = c("/api/server/check", {"address": "127.0.0.1:8188"})["fingerprint"]
    c("/api/server/trust", {"address": "127.0.0.1:8188", "fingerprint": fp})
    ids[n] = c("/api/server/join", {})["hub_id"]
for n in HUBS: s(f"/api/admin/hub/{ids[n]}/approve", {})
time.sleep(4)
def link(x, y):
    h[x]("/api/links/request", {"to": ids[y]}); time.sleep(1.5)
    lk = [l for l in h[y]("/api/status")["links"] if l["peer"] == ids[x]][0]
    h[y]("/api/links/accept", {"link": lk["id"]}); time.sleep(1.5)
link("A", "B"); link("B", "C")
check("chain links active", all(l["state"] == "active" for l in h["B"]("/api/status")["links"]))
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
h["B"]("/api/hub", {"transit": {"enabled": True, "max_hops": 3}}); time.sleep(1)
# 1) origin A has NOT allowed onward (default) -> stops at B even though B allows transit
inject("A")
check("A->B arrives at B", recv("B", "A") == 1)
check("origin ticked nothing: nothing reaches C", recv("C", "B") == 0)
# 2) B publishes its offer list; origin A ticks C in it -> reaches C
time.sleep(2)
offer = [x for x in h["A"]("/api/status")["directory"] if x["id"] == ids["B"]][0]["rules"].get("transit_to", [])
check("B offers C to A (published list)", ids["C"] in offer)
rules("A", "B", send={"onward_to": [ids["C"]]}); time.sleep(1)
inject("A")
check("origin ticked C: packet reaches C via B", recv("C", "B") == 1)
check("B counted it as transit", peers("B").get(ids["C"], {}).get("transit") == 1)
# 3) receiving hub C refuses packets from beyond B
rules("C", "B", receive={"from_beyond": False}); time.sleep(1)
inject("A")
check("receiver refuses packets from further away", blocked("C", "B", "from_beyond") == 1)
rules("C", "B", receive={"from_beyond": True})
# 4) transit hub B does not pass others' packets towards C
rules("B", "C", send={"transit": False}); time.sleep(1)
before = recv("C", "B"); inject("A")
check("transit hub refuses transit on that link", recv("C", "B") == before and blocked_send("B", "C", "transit_off") >= 1)
rules("B", "C", send={"transit": True})
# 5) B's transit switched off entirely
h["B"]("/api/hub", {"transit": {"enabled": False, "max_hops": 3}}); time.sleep(1)
before = recv("C", "B"); inject("A")
check("transit off at B: nothing passes", recv("C", "B") == before)
pub = s("/api/public/hub/" + ids["A"])["hub"]["rules"]
check("A publishes its destination list", any(v["send"].get("onward_to") for v in (pub or {}).get("links", {}).values()))
# 6) triangle A-B-C-A, everything allowed: each hub gets the packet exactly once, origin never gets it back
link("A", "C")
for n in HUBS:
    h[n]("/api/hub", {"transit": {"enabled": True, "max_hops": 3}})
    for m in HUBS:
        if m != n: rules(n, m, send={"onward_to": [ids[x] for x in HUBS if x not in (n, m)]})
time.sleep(1)
before = {n: sum(recv(n, m) for m in HUBS if m != n) for n in HUBS}
inject("A"); time.sleep(3)
after = {n: sum(recv(n, m) for m in HUBS if m != n) for n in HUBS}
check("triangle: B and C each receive the packet exactly once", after["B"] - before["B"] == 1 and after["C"] - before["C"] == 1)
check("triangle: the origin A never gets its own packet back", after["A"] - before["A"] == 0)
subprocess.run("for p in 8189 8188 8187 8186 8185; do pid=$(ss -ltnp \"sport = :$p\" | grep -oP 'pid=\\K[0-9]+' | head -1); [ -n \"$pid\" ] && kill $pid; done", shell=True)
fails = [n for n, ok in results if not ok]
print(f"\n{len(results) - len(fails)}/{len(results)} passed"); sys.exit(1 if fails else 0)
