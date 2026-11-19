"""Registration and link consistency: test server + hubs A, B, C (no radios), all linked.
- another address for the same server keeps the registration;
- ending a link ends it on the server and for both hubs, other links stay;
- a hub that forgets its registration is removed by the server with all its links, other links stay.
Env: URA_TEST_DIR (default /tmp/ura-lt), URA_HUB_PYTHON (python with `meshtastic`)."""
import json, os, ssl, subprocess, sys, time, urllib.request, http.cookiejar

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.environ.get("URA_TEST_DIR", "/tmp/ura-lt"); PW = "TestPass123"
HUBPY = os.environ.get("URA_HUB_PYTHON", sys.executable)
S = "https://127.0.0.1:8179"; HUBS = {"A": 8177, "B": 8176, "C": 8175}
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
results = []


def check(name, cond):
    results.append((name, bool(cond))); print(("PASS " if cond else "FAIL ") + name, flush=True)


def client(base):
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), urllib.request.HTTPSHandler(context=ctx))

    def call(path, body=None):
        req = urllib.request.Request(base + path, data=json.dumps(body).encode() if body is not None else None,
                                     headers={"Content-Type": "application/json"}, method="POST" if body is not None else "GET")
        try:
            return json.loads(op.open(req, timeout=40).read())
        except urllib.error.HTTPError as e:
            return json.loads(e.read())
    return call


def kill_ports():
    subprocess.run("for p in 8179 8178 8177 8176 8175; do pid=$(ss -ltnp \"sport = :$p\" | grep -oP 'pid=\\K[0-9]+' | head -1); "
                   "[ -n \"$pid\" ] && kill $pid; done; sleep 1", shell=True)


kill_ports()
subprocess.run(f"rm -rf {T}; mkdir -p {T}", shell=True)
subprocess.Popen(f"cd {REPO}/server && URA_DATA={T}/ds URA_PORT=8178 URA_WEB_PORT=8179 setsid nohup python3 -u ura_server.py > {T}/server.log 2>&1 < /dev/null &", shell=True)
for n, port in HUBS.items():
    subprocess.Popen(f"cd {REPO}/hub && URA_DATA={T}/d{n} URA_WEB_PORT={port} setsid nohup {HUBPY} -u ura_hub.py > {T}/hub{n}.log 2>&1 < /dev/null &", shell=True)
time.sleep(5)
s = client(S); s("/api/setup", {"password": PW})
h, ids = {}, {}
for i, (n, port) in enumerate(HUBS.items()):
    c = client(f"https://127.0.0.1:{port}"); c("/api/setup", {"password": PW}); h[n] = c
    c("/api/hub", {"hub": {"name": "Hub " + n, "email": f"{n}@example.org", "country": "XX", "city": n * 2, "lat": 10 + i, "lon": 20 + i}})
    fp = c("/api/server/check", {"address": "127.0.0.1:8178"})["fingerprint"]
    c("/api/server/trust", {"address": "127.0.0.1:8178", "fingerprint": fp})
    ids[n] = c("/api/server/join", {})["hub_id"]
for n in HUBS:
    s(f"/api/admin/hub/{ids[n]}/approve", {})
time.sleep(4)


def link(x, y):
    h[x]("/api/links/request", {"to": ids[y]}); time.sleep(1.5)
    lk = [l for l in h[y]("/api/status")["links"] if l["peer"] == ids[x]][0]
    h[y]("/api/links/accept", {"link": lk["id"]}); time.sleep(1.5)


def server_links():
    return {(l["a"], l["b"]): l["state"] for l in s("/api/admin/state")["links"]}


def active(x, y):
    return any(l["state"] == "active" and {l["a"], l["b"]} == {ids[x], ids[y]} for l in s("/api/admin/state")["links"])


link("A", "B"); link("B", "C"); link("A", "C")
check("three links active on the server", active("A", "B") and active("B", "C") and active("A", "C"))

# 1) another address for the same server keeps the registration
fp = h["A"]("/api/server/check", {"address": "localhost:8178"})["fingerprint"]
h["A"]("/api/server/trust", {"address": "localhost:8178", "fingerprint": fp}); time.sleep(6)
st = h["A"]("/api/status")
check("same server under another address keeps the registration", st["server"]["hub_id"] == ids["A"])
check("... and the hub reconnects with it", st["link_state"] == "connected" and st["server"]["status"] == "approved")

# 2) ending a link ends it everywhere; other links stay
lk = [l for l in h["A"]("/api/status")["links"] if l["peer"] == ids["B"]][0]
h["A"]("/api/links/remove", {"link": lk["id"]}); time.sleep(2)
check("ended link is gone on the server", not active("A", "B"))
check("ended link is gone for A and for B",
      not any(l["peer"] == ids["B"] for l in h["A"]("/api/status")["links"]) and
      not any(l["peer"] == ids["A"] for l in h["B"]("/api/status")["links"]))
check("other links stay active (A-C, B-C)", active("A", "C") and active("B", "C"))

# 3) a hub that forgets its registration: server removes it and all its links; other links stay
r = h["A"]("/api/server/forget", {}); time.sleep(2)
check("forget tells the server", r.get("server_informed") is True)
hubs = {x["id"]: x["status"] for x in s("/api/admin/state")["hubs"]}
check("server removed hub A", ids["A"] not in hubs)
check("A's link to C ended on the server and for C",
      not active("A", "C") and not any(l["peer"] == ids["A"] for l in h["C"]("/api/status")["links"]))
check("B-C stays active", active("B", "C"))
check("A no longer appears in other hubs' list",
      not any(x["id"] == ids["A"] for x in h["B"]("/api/status")["directory"]))

# 4) ending a link while the server is unreachable is refused clearly
r = h["A"]("/api/links/remove", {"link": 999})
check("ending a link without a server connection is refused", r.get("error") == "not_connected")

kill_ports()
fails = [n for n, ok in results if not ok]
print(f"\n{len(results) - len(fails)}/{len(results)} passed"); sys.exit(1 if fails else 0)
