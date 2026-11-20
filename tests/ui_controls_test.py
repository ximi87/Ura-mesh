"""Every control on the hub pages, clicked in a real browser: tick/untick -> Save -> the setting really
changed (hub config) -> the PARTNER's page shows it. Server + hubs A, B with simulated radios.
  URA_TEST_DIR (default /tmp/ura-uc), URA_HUB_PYTHON (python with meshtastic, for the hubs)
Needs playwright in the python that runs this file."""
import http.cookiejar, json, os, ssl, subprocess, sys, time, urllib.request
from playwright.sync_api import sync_playwright
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.environ.get("URA_TEST_DIR", "/tmp/ura-uc"); PW = "TestPass123"
HUBPY = os.environ.get("URA_HUB_PYTHON", "python3")
SH, SW = 8168, 8169
HUBS = {"A": 8167, "B": 8166}
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
results, errors = [], []


def check(name, cond, detail=""):
    results.append((name, bool(cond), str(detail)))
    print(("PASS " if cond else "FAIL ") + name + (f"  — {detail}" if detail and not cond else ""), flush=True)


def client(base):
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), urllib.request.HTTPSHandler(context=ctx))
    def call(path, body=None):
        req = urllib.request.Request(base + path, data=json.dumps(body).encode() if body is not None else None,
                                     headers={"Content-Type": "application/json"}, method="POST" if body is not None else "GET")
        try: return json.loads(op.open(req, timeout=30).read())
        except urllib.error.HTTPError as e: return json.loads(e.read() or b"{}")
    return call


def wait(cond, timeout=10):
    end = time.time() + timeout
    while time.time() < end:
        try:
            v = cond()
            if v: return v
        except Exception: pass
        time.sleep(0.4)
    return None


ports = [SH, SW] + list(HUBS.values())
subprocess.run(" ".join(f"pid=$(ss -ltnp 'sport = :{p}' | grep -oP 'pid=\\K[0-9]+' | head -1); [ -n \"$pid\" ] && kill $pid;" for p in ports) + f" sleep 1; rm -rf {T}; mkdir -p {T}", shell=True)
subprocess.Popen(f"cd {REPO}/server && URA_DATA={T}/srv URA_PORT={SH} URA_WEB_PORT={SW} setsid nohup python3 -u ura_server.py > {T}/server.log 2>&1 < /dev/null &", shell=True)
for n, port in HUBS.items():
    subprocess.Popen(f"cd {REPO}/hub && URA_TEST_INJECT=1 URA_TEST_RADIO={REPO}/tests/fake_radio.py URA_TEST_NODE={'a1' if n == 'A' else 'b2'}00000 "
                     f"URA_DATA={T}/h{n} URA_WEB_PORT={port} setsid nohup {HUBPY} -u ura_hub.py > {T}/hub{n}.log 2>&1 < /dev/null &", shell=True)
time.sleep(5)
S = client(f"https://127.0.0.1:{SW}"); S("/api/setup", {"password": PW})
h, ids = {}, {}
for n, port in HUBS.items():
    c = client(f"https://127.0.0.1:{port}"); h[n] = c; c("/api/setup", {"password": PW})
    c("/api/radio", {"radio": {"transport": "serial", "address": "/dev/fake"}})
    c("/api/hub", {"hub": {"name": "Hub " + n, "email": f"{n}@example.org", "country": "XT", "city": n * 3, "location_mode": "manual", "lat": 45, "lon": 10}})
    fp = c("/api/server/check", {"address": f"127.0.0.1:{SH}"})["fingerprint"]
    c("/api/server/trust", {"address": f"127.0.0.1:{SH}", "fingerprint": fp})
    ids[n] = c("/api/server/join", {"address": f"127.0.0.1:{SH}"})["hub_id"]
    S(f"/api/admin/hub/{ids[n]}/approve", {})
time.sleep(3)
h["A"]("/api/links/request", {"to": ids["B"]})
lk = wait(lambda: next(l for l in h["B"]("/api/status")["links"] if l["peer"] == ids["A"]))
h["B"]("/api/links/accept", {"link": lk["id"]})
wait(lambda: all(l["state"] == "active" for l in h["A"]("/api/status")["links"]))
cfgA = lambda: h["A"]("/api/config")


def page(pw, n):
    p = pw.new_context(ignore_https_errors=True, viewport={"width": 1300, "height": 1000}).new_page()
    p.on("pageerror", lambda e: errors.append(f"{n}: {e}"))
    p.goto(f"https://127.0.0.1:{HUBS[n]}/#/"); p.wait_for_selector("#pw"); p.fill("#pw", PW); p.click("#lbtn")
    p.wait_for_selector("details.secline")
    return p


def go(p, n, route, sel):
    p.goto(f"https://127.0.0.1:{HUBS[n]}/#/{route}"); p.reload(); p.wait_for_selector(sel, state="attached"); p.wait_for_timeout(800)


def open_sec(p, key):
    d = p.locator(f"details.secline[data-sec='{key}']")
    if not d.evaluate("e => e.open"): d.locator("xpath=./summary").click()


def open_link(p):
    d = p.locator("details.linkbox[data-link]").first
    if not d.evaluate("e => e.open"): d.locator("xpath=./summary").click()
    return d


def peer_table_text(p):
    return p.locator("details.linkbox[data-link]").first.locator(".linkbody").inner_text()


with sync_playwright() as pw:
    br = pw.chromium.launch()
    a, b = page(br, "A"), page(br, "B")

    # ── per-link rules on A's Links page: every tick box, saved, really changed ──
    go(a, "A", "links", "details.linkbox[data-link]"); box = open_link(a)
    for d, keys in (("send", ["on", "public", "private", "positions", "transit"]), ("receive", ["on", "public", "private", "positions", "from_beyond"])):
        for k in keys:
            go(a, "A", "links", "details.linkbox[data-link]"); box = open_link(a)
            before = cfgA()["rules"][ids["B"]][d][k]
            box.locator(f"input[data-dir='{d}'][data-k='{k}']").click()
            box.locator(f"button[data-save='{ids['B']}']").click(); a.wait_for_timeout(700)
            after = cfgA()["rules"][ids["B"]][d][k]
            check(f"Links/{d}/{k}: click + Save changes the rule ({before} -> {after})", after == (not before))
            if d == "send" and k == "positions":
                go(b, "B", "links", "details.linkbox[data-link]"); open_link(b)
                row = wait(lambda: [r for r in b.locator("details.linkbox[data-link] .linkbody table tr").all_inner_texts() if r.startswith("Positions")], 8)
                check("... partner B's page shows A no longer sends positions", row and "off" in row[0].lower(), row)
            go(a, "A", "links", "details.linkbox[data-link]"); box = open_link(a)
            box.locator(f"input[data-dir='{d}'][data-k='{k}']").click()
            box.locator(f"button[data-save='{ids['B']}']").click(); a.wait_for_timeout(700)
            check(f"Links/{d}/{k}: clicking again restores it", cfgA()["rules"][ids["B"]][d][k] == before)
    for d in ("send", "receive"):
        go(a, "A", "links", "details.linkbox[data-link]"); box = open_link(a)
        g = box.locator(f"input[data-dir='{d}'][data-g='Team']")
        if not check(f"Links/{d}: radio's group 'Team' offered as a tick box", g.count() == 1): continue
        g.click(); box.locator(f"button[data-save='{ids['B']}']").click(); a.wait_for_timeout(700)
        check(f"Links/{d}/group Team: click + Save adds it", "Team" in cfgA()["rules"][ids["B"]][d]["groups"])
    go(a, "A", "links", "details.linkbox[data-link]"); box = open_link(a)
    box.locator("select[data-reach]").select_option("7"); box.locator(f"button[data-save='{ids['B']}']").click(); a.wait_for_timeout(700)
    check("Links/how far: 'anywhere' saved", cfgA()["rules"][ids["B"]]["send"]["reach"] == 7)
    go(b, "B", "links", "details.linkbox[data-link]"); open_link(b)
    check("... partner B's page shows A's packets may go anywhere", wait(lambda: "Anywhere" in peer_table_text(b), 8))

    # ── the reported case: A turns on 'Pass traffic between my linked hubs' -> B sees it ──
    go(b, "B", "links", "details.linkbox[data-link]"); open_link(b)
    check("before: B's page says A does NOT pass traffic", "passes traffic between its linked hubs\toff" in peer_table_text(b).lower().replace(" \t", "\t")
          or "passes traffic between its linked hubs off" in " ".join(peer_table_text(b).lower().split()))
    go(a, "A", "settings", "details.secline"); open_sec(a, "limits")
    a.check("#tron"); a.fill("#trhops", "3"); a.click("#lsave"); a.wait_for_selector("#lmsg .msg")
    check("Settings/multi-hop: saved on A", cfgA()["transit"] == {"enabled": True, "max_hops": 3}, cfgA()["transit"])
    go(b, "B", "links", "details.linkbox[data-link]"); open_link(b)
    txt = wait(lambda: (lambda x: x if "passes traffic between its linked hubs on" in x else None)(" ".join(peer_table_text(b).lower().split())), 10)
    check("after: B's page says A passes traffic (max 3 hops)", txt and "max 3" in txt, " ".join(peer_table_text(b).split())[:400])

    # ── Settings page: every control saves ──
    go(a, "A", "settings", "details.secline"); open_sec(a, "limits")
    a.fill("#ahour", "7.5"); a.fill("#aday", "2"); a.uncheck("#spos"); a.click("#lsave"); a.wait_for_selector("#lmsg .msg")
    c = cfgA()
    check("Settings/airtime hour + day saved", c["airtime"] == {"pct_hour": 7.5, "pct_day": 2.0}, c["airtime"])
    check("Settings/'positions on map' off saved", c["share_positions_on_map"] is False)
    for k in ("on", "public", "private", "positions"):
        go(a, "A", "settings", "details.secline"); open_sec(a, "limits")
        before = cfgA()["defaults"]["send"][k]
        a.locator(f"#defs input[data-dir='send'][data-k='{k}']").click(); a.click("#lsave"); a.wait_for_selector("#lmsg .msg")
        check(f"Settings/defaults send {k}: saved", cfgA()["defaults"]["send"][k] == (not before))
    go(a, "A", "settings", "details.secline"); open_sec(a, "limits")
    a.uncheck("#tron"); a.click("#lsave"); a.wait_for_selector("#lmsg .msg")
    check("Settings/multi-hop off saved", cfgA()["transit"]["enabled"] is False)
    check("... airtime/positions NOT reset by that save", cfgA()["airtime"]["pct_hour"] == 7.5 and cfgA()["share_positions_on_map"] is False)
    go(a, "A", "settings", "details.secline"); open_sec(a, "loc")
    a.check("input[name=lmode][value=manual]"); a.fill("#hlat", "44.123"); a.fill("#hlon", "11.456"); a.click("#locsave"); a.wait_for_selector("#locmsg .msg")
    check("Settings/location manual saved", abs(cfgA()["hub"]["lat"] - 44.123) < 1e-6)
    check("... and on the server within 5 s", wait(lambda: abs(S(f"/api/public/hub/{ids['A']}")["hub"]["lat"] - 44.123) < 1e-6, 5))
    go(a, "A", "settings", "details.secline"); open_sec(a, "loc")
    a.check("input[name=lmode][value=radio]"); a.click("#locsave"); a.wait_for_selector("#locmsg .msg")
    check("Settings/location 'from radio' saved + follows radio", wait(lambda: cfgA()["hub"]["location_mode"] == "radio" and abs(cfgA()["hub"]["lat"] - 45.0) < 1e-3, 8), cfgA()["hub"])
    go(a, "A", "settings", "details.secline"); open_sec(a, "adv")
    a.click("#advform [data-all='1']"); a.fill("[data-adv=page_refresh_s]", "40"); a.click("#advsave"); a.wait_for_selector("#advmsg .msg")
    check("Settings/advanced value saved", cfgA()["advanced"].get("page_refresh_s") == 40)

    # ── Status / Device pages ──
    go(a, "A", "", "details.secline")
    a.click("#ann"); a.wait_for_timeout(800)
    check("Status/'Announce this radio now' sends to the radio", any(x["kind"] == "data" for x in h["A"]("/api/test/radio")["sent"]))
    go(a, "A", "device", "details.secline"); open_sec(a, "owner")
    a.fill("#olong", "Clicked name"); a.click("#osave"); a.wait_for_selector("#omsg .msg")
    check("Device/owner name written to the radio", any(x["call"] == "setOwner" and x["long_name"] == "Clicked name" for x in h["A"]("/api/test/radio")["calls"]))
    open_sec(a, "display")
    inp = a.locator("details[data-sec='display'] input[data-f='screen_on_secs']")
    inp.fill("77"); a.locator("button[data-save-sec='display']").click(); a.wait_for_timeout(800)
    check("Device/section field written to the radio", any(x["call"] == "writeConfig" and x["section"] == "display" and x["values"].get("screen_on_secs") == 77
                                                           for x in h["A"]("/api/test/radio")["calls"]))
    br.close()

subprocess.run(" ".join(f"pid=$(ss -ltnp 'sport = :{p}' | grep -oP 'pid=\\K[0-9]+' | head -1); [ -n \"$pid\" ] && kill $pid;" for p in ports), shell=True)
bad = [r for r in results if not r[1]]
print(f"\nJS errors: {len(errors)} {errors[:3]}\n{len(results) - len(bad)}/{len(results)} passed")
sys.exit(1 if bad or errors else 0)
