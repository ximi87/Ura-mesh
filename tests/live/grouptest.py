"""Private-group test through the hub APIs (same calls the pages make)."""
import json, os, ssl, sys, time, urllib.request, http.cookiejar
# Two live hubs that are linked with each other:
#   URA_HUB_A / URA_HUB_B  = their website URLs, URA_HUB_A_ID / URA_HUB_B_ID = their hub ids, URA_HUB_PW = password
#   usage: grouptest.py setup | check | send '{"t": ["UraTest"], "l": []}' | cleanup
T, L = os.environ["URA_HUB_A"], os.environ["URA_HUB_B"]
TID, LID = os.environ["URA_HUB_A_ID"], os.environ["URA_HUB_B_ID"]
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
def client(base):
    jar = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar), urllib.request.HTTPSHandler(context=ctx))
    def call(path, body=None, timeout=200):
        req = urllib.request.Request(base + path, data=json.dumps(body).encode() if body is not None else None,
                                     headers={"Content-Type": "application/json"}, method="POST" if body is not None else "GET")
        try:
            return json.loads(op.open(req, timeout=timeout).read())
        except urllib.error.HTTPError as e:
            return json.loads(e.read())
    call("/api/login", {"password": os.environ["URA_HUB_PW"]})
    return call
t, l = client(T), client(L)
RULE = lambda groups: {"send": {"on": True, "public": True, "private": True, "positions": True, "groups": groups},
                       "receive": {"on": True, "public": True, "private": True, "positions": True, "groups": groups}}
def peer(c, pid): return c("/api/status")["counters"]["peers"].get(pid, {})
step = sys.argv[1]
if step == "setup":
    print("tirana add ch:", t("/api/radio/channel", {"channel": {"index": 1, "role": "SECONDARY", "name": "UraTest", "psk": "random", "uplink": True, "downlink": True, "position_precision": 0}}))
    time.sleep(8)
    key = [c for c in t("/api/radio/settings")["channels"] if c["index"] == 1][0]["psk"]
    print("key length (base64 chars):", len(key))
    print("lb add ch:", l("/api/radio/channel", {"channel": {"index": 1, "role": "SECONDARY", "name": "UraTest", "psk": key, "uplink": True, "downlink": True, "position_precision": 0}}))
elif step == "check":
    print("tirana ch:", [(c["index"], c["name"], c["psk"][:8]) for c in t("/api/radio/settings")["channels"] if c["role"] != "DISABLED"])
    print("lb ch:    ", [(c["index"], c["name"], c["psk"][:8]) for c in l("/api/radio/settings")["channels"] if c["role"] != "DISABLED"])
    print("radio ready:", t("/api/status")["radio"]["ready"], l("/api/status")["radio"]["ready"])
elif step == "send":
    groups = json.loads(sys.argv[2])            # e.g. {"t": [...], "l": [...]}
    print("rules:", t("/api/rules", {"peer": LID, "rules": RULE(groups["t"])}), l("/api/rules", {"peer": TID, "rules": RULE(groups["l"])}))
    before = peer(l, TID)
    print("send:", t("/api/diag", {"kind": "broadcast", "channel": 1, "text": "Ura group test (UraTest channel)"}))
    time.sleep(15)
    after = peer(l, TID)
    print("LB before:", before); print("LB after: ", after)
    print("tirana blocked_send:", peer(t, LID).get("blocked_send"))
elif step == "cleanup":
    print("rules:", t("/api/rules", {"peer": LID, "rules": RULE([])}), l("/api/rules", {"peer": TID, "rules": RULE([])}))
    print("del:", t("/api/radio/channel", {"channel": {"index": 1, "role": "DISABLED"}}), l("/api/radio/channel", {"channel": {"index": 1, "role": "DISABLED"}}))
