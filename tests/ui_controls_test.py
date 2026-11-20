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
HUBS = {"A": 8167, "B": 8166, "C": 8165}
NODE = {"A": "a1", "B": "b2", "C": "c3"}
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
    subprocess.Popen(f"cd {REPO}/hub && URA_TEST_INJECT=1 URA_TEST_RADIO={REPO}/tests/fake_radio.py URA_TEST_NODE={NODE[n]}00000 "
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
    p.on("dialog", lambda d: d.accept())          # "really end this link?" etc. -> yes, like the operator
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


def pki_packet(sender):
    """A private-message ServiceEnvelope, encoded by hand (no protobuf library needed here)."""
    import struct, random as rnd
    f32 = lambda field, v: bytes([(field << 3) | 5]) + struct.pack("<I", v)
    ln = lambda field, b: bytes([(field << 3) | 2, len(b)]) + b
    pkt = f32(1, sender) + f32(2, 0x12345678) + ln(5, os.urandom(40)) + f32(6, rnd.randint(1, 2**31))
    return ln(1, pkt) + ln(2, b"PKI") + ln(3, b"!a1000000")


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
    # ── link requests by click: ask, decline, cancel, accept, end ──
    import base64
    c_ = page(br, "C")
    linked = lambda x, y: [l for l in h[x]("/api/status")["links"] if l["peer"] == ids[y]]
    go(b, "B", "links", "#hubdir button[data-ask]")
    b.locator(f"#hubdir button[data-ask='{ids['C']}']").click()
    check("Links/'Ask for a link' click -> C gets the request", wait(lambda: linked("C", "B"), 8))
    go(c_, "C", "links", "button[data-acc]")
    c_.locator(".reqrow button[data-rm]").click()
    check("Links/'Decline' click -> request gone on both hubs", wait(lambda: not linked("C", "B") and not linked("B", "C"), 8))
    go(b, "B", "links", "#hubdir button[data-ask]")
    b.locator(f"#hubdir button[data-ask='{ids['C']}']").click(); wait(lambda: linked("C", "B"), 8)
    go(b, "B", "links", ".reqrow button[data-rm]")
    b.locator(".reqrow button[data-rm]").click()
    check("Links/'Cancel request' click -> gone on both hubs", wait(lambda: not linked("C", "B") and not linked("B", "C"), 8))
    go(b, "B", "links", "#hubdir button[data-ask]")
    b.locator(f"#hubdir button[data-ask='{ids['C']}']").click(); wait(lambda: linked("C", "B"), 8)
    go(c_, "C", "links", "button[data-acc]"); c_.click("button[data-acc]")
    check("Links/'Accept' click -> link active on both hubs", wait(lambda: linked("B", "C") and linked("B", "C")[0]["state"] == "active" and linked("C", "B")[0]["state"] == "active", 8))

    # ── onward tick boxes: B offers C to A ──
    h["B"]("/api/hub", {"transit": {"enabled": True, "max_hops": 3}}); time.sleep(2)
    go(a, "A", "links", "details.linkbox[data-link]"); box = open_link(a)
    box.locator("select[data-reach]").select_option("1")
    tick = box.locator(f"input[data-onward='{ids['C']}']")
    if check("Links/how far: B's offer of C shown as a tick box", tick.count() == 1):
        tick.check(); box.locator(f"button[data-save='{ids['B']}']").click(); a.wait_for_timeout(700)
        r = cfgA()["rules"][ids["B"]]["send"]
        check("Links/onward tick C + 1 hub further: saved", r["reach"] == 1 and r["onward_to"] == [ids["C"]], r)

    # ── changed end-to-end key -> 'Trust new key' button ──
    pc = HUBS["C"]
    subprocess.run(f"pid=$(ss -ltnp 'sport = :{pc}' | grep -oP 'pid=\\K[0-9]+' | head -1); kill $pid; sleep 1; rm -f {T}/hC/identity.key", shell=True)
    subprocess.Popen(f"cd {REPO}/hub && URA_TEST_INJECT=1 URA_TEST_RADIO={REPO}/tests/fake_radio.py URA_TEST_NODE=c300000 "
                     f"URA_DATA={T}/hC URA_WEB_PORT={pc} setsid nohup {HUBPY} -u ura_hub.py >> {T}/hubC.log 2>&1 < /dev/null &", shell=True)
    check("B notices C's new key", wait(lambda: linked("B", "C") and linked("B", "C")[0]["e2e"]["state"] == "changed", 25))
    go(b, "B", "links", f"details.linkbox[data-peer='{ids['C']}']")
    d = b.locator(f"details.linkbox[data-peer='{ids['C']}']")
    if not d.evaluate("e => e.open"): d.locator("xpath=./summary").click()
    btn = d.locator(f"button[data-trust='{ids['C']}']")
    if check("Links/'Trust new key' button shown", btn.count() == 1):
        btn.click()
        check("Links/'Trust new key' click -> key accepted", wait(lambda: linked("B", "C")[0]["e2e"]["state"] == "ok", 8))
    go(b, "B", "links", f"details.linkbox[data-peer='{ids['C']}']")
    d = b.locator(f"details.linkbox[data-peer='{ids['C']}']")
    if not d.evaluate("e => e.open"): d.locator("xpath=./summary").click()
    d.locator("button[data-rm]").click()
    check("Links/'End link' click -> gone on both hubs, A-B kept", wait(lambda: not linked("B", "C") and linked("B", "A"), 8))

    # ── Status page: older nodes, remote nodes grouped by hub ──
    go(a, "A", "", "#localtable")
    before = a.locator("#localtable").inner_text()
    a.check("#showold"); a.wait_for_timeout(800)
    check("Status/'show older nodes' tick -> the 30-day-old node appears", "Old node" not in before and "Old node" in a.locator("#localtable").inner_text())
    h["A"]("/api/test/inject", {"topic": "msh/EU_868/2/e/PKI/!a1000000", "data": base64.b64encode(pki_packet(0x5eed1234)).decode()})
    wait(lambda: any(x["id"] == "!5eed1234" for x in h["B"]("/api/nodes")), 8)
    go(b, "B", "", "details.secline"); open_sec(b, "remote"); b.wait_for_timeout(400)
    rtxt = b.locator("details.secline[data-sec='remote']").inner_text()
    check("Status/remote nodes grouped under the hub they came from (XT-AAA)", "XT-AAA" in rtxt and "5eed1234" in rtxt, rtxt[:300])

    # ── Radio page: diagnostics + prepare by click ──
    go(a, "A", "radio", "details.secline"); open_sec(a, "diag")
    a.fill("#dgnode", "!0a100001"); a.click("button[data-dg='dm']")
    out = wait(lambda: (lambda t_: t_ if t_ and "…" not in t_ and "Waiting" not in t_ else None)(a.locator("#dgout").inner_text()), 20)
    check("Radio/Diagnostics 'private message' click -> delivered", out and a.locator("#dgout .msg.ok").count() == 1, out)
    a.fill("#dgnode", "!0a100001"); a.click("button[data-dg='trace']")
    out = wait(lambda: (lambda t_: t_ if "→" in t_ else None)(a.locator("#dgout").inner_text()), 20)
    check("Radio/Diagnostics 'traceroute' click -> route shown", out and "Neighbour two" in out, out)
    h["A"]("/api/radio/section", {"kind": "module", "section": "mqtt", "values": {"enabled": False}})
    go(a, "A", "radio", "details.secline"); open_sec(a, "state")
    if check("Radio/'Prepare radio for Ura' button shown when not ready", a.locator("#prep").count() == 1):
        a.click("#prep")
        check("Radio/'Prepare' click -> radio ready again", wait(lambda: h["A"]("/api/status")["radio"]["ready"], 10))

    # ── Device settings: channel edit + fixed position by click ──
    go(a, "A", "device", "details.secline"); open_sec(a, "ch1")
    a.fill("details[data-sec='ch1'] [data-c='name']", "Team2"); a.click("details[data-sec='ch1'] button[data-chsave]"); a.wait_for_timeout(800)
    check("Device/channel name edited by click -> written to radio", any(x["call"] == "writeChannel" and x["index"] == 1 and x["name"] == "Team2" for x in h["A"]("/api/test/radio")["calls"]))
    go(a, "A", "device", "details.secline"); open_sec(a, "fixed")
    a.check("#fxon"); a.fill("#fxlat", "43.21"); a.fill("#fxlon", "12.34"); a.click("#fxsave"); a.wait_for_selector("#fxmsg .msg")
    check("Device/fixed position by click -> written to radio", any(x["call"] == "setFixedPosition" and abs(x["lat"] - 43.21) < 1e-6 for x in h["A"]("/api/test/radio")["calls"]))
    br.close()

subprocess.run(" ".join(f"pid=$(ss -ltnp 'sport = :{p}' | grep -oP 'pid=\\K[0-9]+' | head -1); [ -n \"$pid\" ] && kill $pid;" for p in ports), shell=True)
bad = [r for r in results if not r[1]]
print(f"\nJS errors: {len(errors)} {errors[:3]}\n{len(results) - len(bad)}/{len(results)} passed")
sys.exit(1 if bad or errors else 0)
