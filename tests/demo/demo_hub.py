"""Radio-less demo hub "Forest mesh": join the demo server, link to Harbour mesh, set per-link rules."""
import json, ssl, sys, time, urllib.request, http.cookiejar
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
def client(base):
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), urllib.request.HTTPSHandler(context=ctx))
    def call(path, body=None):
        req = urllib.request.Request(base + path, data=json.dumps(body).encode() if body is not None else None,
                                     headers={"Content-Type": "application/json"}, method="POST" if body is not None else "GET")
        try: return json.loads(op.open(req, timeout=30).read())
        except urllib.error.HTTPError as e: return json.loads(e.read())
    return call
import os
h = client(os.environ.get("URA_DEMO_HUB", "https://127.0.0.1:8187")); srv = client(os.environ.get("URA_DEMO_SERVER_WEB", "https://127.0.0.1:8299"))
h("/api/setup", {"password": "DemoHub-123"}); h("/api/login", {"password": "DemoHub-123"})
h("/api/hub", {"hub": {"name": "Forest mesh", "email": "forest@example.org", "country": "XR", "city": "FOR",
                       "location_mode": "manual", "lat": 60.17, "lon": 24.94, "description": "Demo hub — Forest mesh."}})
h("/api/hub", {"transit": {"enabled": True, "max_hops": 4}})
A = os.environ.get("URA_DEMO_SERVER", "127.0.0.1:8298")
fp = h("/api/server/check", {"address": A})["fingerprint"]
h("/api/server/trust", {"address": A, "fingerprint": fp})
hid = h("/api/server/join", {"address": A})["hub_id"]; print("joined", hid)
srv("/api/login", {"password": "DemoAdmin-123"}); print("approve", srv(f"/api/admin/hub/{hid}/approve", {}))
time.sleep(5)
s = h("/api/status")
hbr = [x for x in s["directory"] if x["code"] == "XB-HBR"][0]
print("request", h("/api/links/request", {"to": hbr["id"]}))
for _ in range(20):
    time.sleep(2)
    s = h("/api/status")
    if any(l["state"] == "active" for l in s["links"]): break
hbr = [x for x in s["directory"] if x["code"] == "XB-HBR"][0]
names = {x["id"]: x["code"] for x in s["directory"]}
offered = (hbr.get("rules") or {}).get("transit_to", [])
print("HBR offers:", [names.get(i) for i in offered])
rules = {"send": {"on": True, "public": True, "private": True, "positions": True, "groups": [], "transit": True, "reach": 1,
                  "onward_to": [i for i in offered if names.get(i) in ("XA-MTN", "XC-CTY")]},
         "receive": {"on": True, "public": True, "private": True, "positions": False, "groups": [], "from_beyond": True}}
print("rules", h("/api/rules", {"peer": hbr["id"], "rules": rules}))
print("links", [(l["peer_code"], l["state"], l["e2e"]["state"]) for l in h("/api/status")["links"]])
