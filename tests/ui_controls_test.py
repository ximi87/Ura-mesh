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
h["C"]("/api/wizard", {"skip": True})      # C has no link yet: its operator chose to set up without the wizard
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
    for r_ in ("", "links", "radio", "device", "settings", "logs", "setup"):
        a.goto(f"https://127.0.0.1:{HUBS['A']}/#/{r_}"); a.wait_for_timeout(150)
        if "nav." in a.locator("nav").first.inner_text(): break
    check("Menu never shows raw text keys (e.g. 'nav.setup') while pages change", "nav." not in a.locator("nav").first.inner_text(), a.locator("nav").first.inner_text())

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
    t0_ = time.time(); go(a, "A", "radio", "details.secline")
    check("Radio page opens at once (ports are checked afterwards)", time.time() - t0_ < 5, round(time.time() - t0_, 1))
    open_sec(a, "conn"); a.wait_for_selector("#rport option", state="attached")
    od = wait(lambda: (lambda o: o if "checking" not in "".join(v[0] for v in o.values()) else None)(
        {v: (txt, dis) for v, txt, dis in a.locator("#rport option").evaluate_all("os => os.map(o => [o.value, o.textContent, o.disabled])")}), 15)
    check("Radio/port list then says what is on each port; MeshCore and unknown cannot be chosen",
          od and "Meshtastic" in od["/dev/fake"][0] and not od["/dev/fake"][1] and "MeshCore" in od["/dev/fake-meshcore"][0] and od["/dev/fake-meshcore"][1]
          and "not recognised" in od["/dev/fake-unknown"][0] and od["/dev/fake-unknown"][1], od)
    a.select_option("#rport", "/dev/fake"); a.click("#rsave")
    out = wait(lambda: (lambda t_: t_ if "Connecting" not in t_ and t_ else None)(a.locator("#rmsg").inner_text()), 30)
    check("Radio/Save -> connects and names the Meshtastic radio it found", out and "Meshtastic" in out, out)

    # ── Device settings: channel edit + fixed position by click ──
    go(a, "A", "device", "details.secline"); open_sec(a, "ch1")
    a.fill("details[data-sec='ch1'] [data-c='name']", "Team2"); a.click("details[data-sec='ch1'] button[data-chsave]"); a.wait_for_timeout(800)
    check("Device/channel name edited by click -> written to radio", any(x["call"] == "writeChannel" and x["index"] == 1 and x["name"] == "Team2" for x in h["A"]("/api/test/radio")["calls"]))
    go(a, "A", "device", "details.secline"); open_sec(a, "fixed")
    a.check("#fxon"); a.fill("#fxlat", "43.21"); a.fill("#fxlon", "12.34"); a.click("#fxsave"); a.wait_for_selector("#fxmsg .msg")
    check("Device/fixed position by click -> written to radio", any(x["call"] == "setFixedPosition" and abs(x["lat"] - 43.21) < 1e-6 for x in h["A"]("/api/test/radio")["calls"]))
    # ── channels and keys ──
    h["A"]("/api/test/fake", {"call": "hear", "args": {"code": 44, "sender": "!0abc1234"}})
    go(a, "A", "", "details.secline")
    st_txt = a.locator("#app").inner_text()
    check("Status: 'hears packets it cannot read' warning with code 44 and the node", "cannot read" in st_txt and "44" in st_txt and "!0abc1234" in st_txt)
    h["A"]("/api/test/fake", {"call": "channel", "args": {"index": 1, "name": "Phone", "psk": base64.b64encode(b"p" * 16).decode()}})
    go(a, "A", "device", "details.secline")
    if check("Device: 'channels differ from the saved copy' with a restore button", a.locator("#chrestore").count() == 1):
        a.click("#chrestore"); a.wait_for_selector("#csmsg .msg")
        check("Device: restore click -> radio back on the saved channel", wait(lambda: h["A"]("/api/status")["radio"]["channels_match"], 8))
    go(a, "A", "device", "details.secline")
    check("Device: each channel shows its key with a copy button", a.locator("button[data-copy^='key']").count() >= 2)
    def ln_(field, b): return bytes([(field << 3) | 2, len(b)]) + b
    url = "https://meshtastic.org/e/#" + base64.urlsafe_b64encode(ln_(1, ln_(2, b"c" * 32) + ln_(3, b"Club"))).decode().rstrip("=")
    open_sec(a, "chimport"); a.fill("#chlink", url); a.click("#chimp"); a.wait_for_selector("#chimpmsg .msg")
    check("Device: 'Add channels from a link' click -> channel added", any(c["name"] == "Club" for c in h["A"]("/api/status")["radio"]["channels"]), a.locator("#chimpmsg").inner_text())
    # ── node list on the radio: forget one by picking it, clear all ──
    go(a, "A", "radio", "details.secline"); open_sec(a, "nodes")
    opts = a.locator("#fgnode option").all_inner_texts()
    if check("Radio: nodes offered by name in a list (no typing ids)", opts and "(!" in opts[0], opts[:2]):
        pick = a.locator("#fgnode option").first.get_attribute("value")
        a.click("#fgbtn"); a.wait_for_selector("#ndout .msg")
        check("Radio: 'Forget' on the picked node -> removed from the radio", any(x["call"] == "removeNode" and x["node"] == pick for x in h["A"]("/api/test/radio")["calls"]))
    go(a, "A", "radio", "details.secline"); open_sec(a, "nodes")
    a.click("#ndreset"); a.wait_for_selector("#ndout .msg")
    check("Radio: 'Clear the radio's node list' click -> cleared", any(x["call"] == "resetNodeDb" for x in h["A"]("/api/test/radio")["calls"]))

    # ── remove the radio from the hub ──
    go(a, "A", "radio", "details.secline"); open_sec(a, "conn")
    if check("Radio: 'Remove this radio from the hub' button", a.locator("#rremove").count() == 1):
        a.click("#rremove"); a.wait_for_selector("#rmsg .msg")
        check("Radio: remove click -> no radio set up in the hub", wait(lambda: h["A"]("/api/config")["radios"] == [], 5))
        go(a, "A", "radio", "details.secline")
        check("Radio: page says no radio is set up", "no radio set up" in a.locator("#app").inner_text())
        h["A"]("/api/radio", {"radio": {"transport": "serial", "address": "/dev/fake"}})
        wait(lambda: (h["A"]("/api/status")["radio"] or {}).get("connected"), 15)

    # ── logs + program control ──
    go(a, "A", "logs", "#lgbox"); a.wait_for_timeout(1500)
    check("Logs page: the hub's log lines shown", "ura-hub" in a.locator("#lgbox").inner_text())
    check("Logs page: download link for the log file", a.locator("a[data-logfile='ura-hub.log']").count() == 1)
    a.select_option("#lglevel", "error"); a.wait_for_timeout(1200)
    txt = a.locator("#lgbox").inner_text()
    check("Logs page: 'errors only' filter", all(" ERROR " in l or " CRITICAL " in l for l in txt.splitlines() if l.strip() and l.strip() != "No lines."), txt[:200])
    go(a, "A", "settings", "details.secline"); open_sec(a, "program")
    st0 = h["A"]("/api/session")["started"]
    if check("Settings: 'Program' with Restart and Stop", a.locator("#pgrestart").count() == 1 and a.locator("#pgstop").count() == 1):
        a.click("#pgrestart")
        check("Settings: 'Restart program' click -> hub restarts and the page comes back", wait(lambda: client(f"https://127.0.0.1:{HUBS['A'][0]}")("/api/session").get("started", st0) > st0, 30))
        a.wait_for_selector("details.secline", timeout=40000)
    sp = br.new_context(ignore_https_errors=True, viewport={"width": 1300, "height": 1000}).new_page()
    sp.on("pageerror", lambda e: errors.append(f"server: {e}"))
    sp.goto(f"https://127.0.0.1:{SW}/#/"); sp.wait_for_timeout(1500)
    check("Server: no Logs menu for visitors", sp.locator("a[href='#/logs']").count() == 0)
    sp.goto(f"https://127.0.0.1:{SW}/#/admin"); sp.wait_for_selector("#pw"); sp.fill("#pw", PW); sp.click("#lbtn"); sp.wait_for_selector("#sec-prog")
    check("Server: Logs in the menu for the admin", sp.locator("a[href='#/logs']").count() == 1)
    sp.click("a[href='#/logs']"); sp.wait_for_selector("#lgbox"); sp.wait_for_timeout(1500)
    check("Server Logs page: log shown", "ura-server" in sp.locator("#lgbox").inner_text())
    sp.goto(f"https://127.0.0.1:{SW}/#/admin"); sp.wait_for_selector("#sec-prog")
    if not sp.locator("#sec-prog").evaluate("e => e.open"): sp.locator("#sec-prog > summary").click()
    sp.wait_for_timeout(500)
    check("Server admin: 'Program' with Restart and Stop", sp.locator("#pgrestart").count() == 1 and sp.locator("#pgstop").count() == 1)

    # ── setup wizard: a brand-new hub set up only by clicks, step after step ──
    PD = 8164; ports.append(PD)
    subprocess.run(f"pid=$(ss -ltnp 'sport = :{PD}' | grep -oP 'pid=\\K[0-9]+' | head -1); [ -n \"$pid\" ] && kill $pid; rm -rf {T}/hD", shell=True)
    subprocess.Popen(f"cd {REPO}/hub && URA_TEST_INJECT=1 URA_TEST_RADIO={REPO}/tests/fake_radio.py URA_TEST_NODE=d400000 "
                     f"URA_DATA={T}/hD URA_WEB_PORT={PD} setsid nohup {HUBPY} -u ura_hub.py > {T}/hubD.log 2>&1 < /dev/null &", shell=True)
    hd = client(f"https://127.0.0.1:{PD}"); wait(lambda: hd("/api/session"), 15); hd("/api/setup", {"password": PW})
    d = br.new_context(ignore_https_errors=True, viewport={"width": 1300, "height": 1000}).new_page()
    d.on("pageerror", lambda e: errors.append(f"D: {e}")); d.on("dialog", lambda x: x.accept())
    d.goto(f"https://127.0.0.1:{PD}/#/"); d.wait_for_selector("#pw"); d.fill("#pw", PW); d.click("#lbtn"); d.wait_for_selector("#wz")
    check("Wizard: a new hub opens the step-by-step setup by itself, step 1 (name) current",
          "#/setup" in d.url and wait(lambda: d.locator(".wzs.cur[data-k='hub']").count() == 1, 8) and d.locator(".wzs.todo").count() == 5)
    d.wait_for_selector("#wzhn"); d.fill("#wzhn", "Hub D"); d.fill("#wzhe", "not-an-address"); d.fill("#wzhc", "XT"); d.fill("#wzhy", "DDD"); d.click("#wzhgo")
    check("Wizard step 1: a wrong e-mail is refused with a clear message", "mail" in d.locator("#wzhmsg").inner_text().lower(), d.locator("#wzhmsg").inner_text())
    d.fill("#wzhe", "d@example.org"); d.click("#wzhgo")
    check("Wizard step 1: saved -> green, step 2 (radio) opens",
          wait(lambda: d.locator(".wzs.ok[data-k='hub']").count() == 1 and d.locator(".wzs.cur[data-k='radio']").count() == 1, 10) and hd("/api/config")["hub"]["city"] == "DDD")
    check("Wizard step 2: radio type Meshtastic chosen, MeshCore shown as not yet available",
          d.locator("input[name=wztype][value=mt]").is_checked() and d.locator("input[name=wztype][value=mc]").is_disabled())
    d.wait_for_selector("#wzport option", state="attached")
    od = wait(lambda: (lambda o: o if "checking" not in "".join(x[1] for x in o) else None)(d.locator("#wzport option").evaluate_all("os => os.map(o => [o.value, o.textContent, o.disabled])")), 15)
    check("Wizard step 2: each port says what is on it; MeshCore cannot be chosen",
          od and any(v == "/dev/fake-meshcore" and dis for v, _, dis in od) and any(v == "/dev/fake" and "Meshtastic" in txt and not dis for v, txt, dis in od), od)
    d.select_option("#wzport", "/dev/fake"); d.click("#wzrgo")
    check("Wizard step 2: Connect -> 'Connected: … nodes', step green",
          wait(lambda: "Connected" in d.locator(".wzs[data-k='radio']").inner_text() or d.locator(".wzs.ok[data-k='radio']").count() == 1, 30)
          and wait(lambda: d.locator(".wzs.ok[data-k='radio']").count() == 1, 15))
    hd("/api/radio/section", {"kind": "module", "section": "mqtt", "values": {"enabled": False}})
    check("Wizard step 3 opens when the radio is not ready yet", wait(lambda: d.locator(".wzs.cur[data-k='prep']").count() == 1, 10))
    d.wait_for_selector("#wzprep"); d.click("#wzprep")
    check("Wizard step 3: Prepare -> ready, step green", wait(lambda: d.locator(".wzs.ok[data-k='prep']").count() == 1, 25))
    d.wait_for_selector("#wzsaddr"); d.fill("#wzsaddr", f"127.0.0.1:{SH}"); d.click("#wzscheck")
    d.wait_for_selector("#wzsjoin", timeout=15000)
    check("Wizard step 4: 'Check server' -> the server answered, with its fingerprint", "answered" in d.locator("#wzsmsg").inner_text())
    d.click("#wzsjoin")
    check("Wizard step 4: registration sent -> step green at once, step 5 says the approval is still awaited (no waiting in step 4)",
          wait(lambda: d.locator(".wzs.ok[data-k='server']").count() == 1 and "administrator" in d.locator(".wzs[data-k='link']").inner_text(), 15),
          d.locator(".wzs[data-k='link']").inner_text())
    check("Wizard step 5: 'Finish setup — link later' offered", d.locator("#wzfinish").count() == 1)
    idD = wait(lambda: hd("/api/config")["server"]["hub_id"], 10)
    S = client(f"https://127.0.0.1:{SW}"); S("/api/login", {"password": PW})     # the browser's admin login replaced the old session
    ap_ = S(f"/api/admin/hub/{idD}/approve", {}); check("(admin approves hub D)", ap_.get("ok"), (idD, ap_, hd("/api/config")["server"]))
    check("Wizard step 5: approved by the admin -> the other hubs appear by themselves", wait(lambda: d.locator(f"button[data-wzask='{ids['A']}']").count() == 1, 30))
    btn = f"button[data-wzask='{ids['A']}']"
    d.wait_for_selector(btn, timeout=15000)
    check("Wizard step 5: the other hubs are listed with 'Ask for a link'", d.locator(f"button[data-wzask='{ids['B']}']").count() == 1)
    d.click(btn)
    check("Wizard step 5: asked A -> 'waiting for … to accept'", wait(lambda: "waiting for" in d.locator(".wzs[data-k='link']").inner_text(), 10))
    lkD = wait(lambda: next(l for l in h["A"]("/api/status")["links"] if l["peer"] == idD))
    h["A"]("/api/links/accept", {"link": lkD["id"]})
    check("Wizard step 6: A accepted -> 'Everything works', all steps green",
          wait(lambda: d.locator(".wzs.cur[data-k='done']").count() == 1 and "Everything works" in d.locator(".wzs[data-k='done']").inner_text(), 20)
          and d.locator(".wzs.ok").count() == 5)
    d.click(f"#wzmore button[data-wzask='{ids['B']}']")
    check("Wizard 'Ready': link with more hubs -> request to B sent", wait(lambda: any(l["peer"] == idD for l in h["B"]("/api/status")["links"]), 10))
    d.click("#wzask")
    check("Wizard: 'Ask neighbours to answer' sent", wait(lambda: "Sent" in d.locator("#wzdmsg").inner_text(), 8))
    d.goto(f"https://127.0.0.1:{PD}/#/"); d.reload(); d.wait_for_selector("details.secline")
    check("Wizard: everything done -> the hub opens the status page, no wizard", d.locator("#wz").count() == 0)
    check("Wizard: done is remembered by the hub", hd("/api/session")["setup_done"] is True)
    hd("/api/radio/remove", {}); d.goto(f"https://127.0.0.1:{PD}/#/"); d.reload(); d.wait_for_selector("details.secline")
    check("Wizard: set up once -> a later problem (radio removed) shows on Status, no forced wizard", d.locator("#wz").count() == 0)
    d.goto(f"https://127.0.0.1:{PD}/#/setup"); d.wait_for_selector("#wz")
    check("Wizard from the menu: opens at the step that needs doing (radio)", wait(lambda: d.locator(".wzs.cur[data-k='radio']").count() == 1, 10))
    hd("/api/server/forget", {"force": True}); d.goto(f"https://127.0.0.1:{PD}/#/"); d.reload(); d.wait_for_selector("#wz")
    check("Wizard: hub left the server (fresh start) -> the wizard opens by itself again", "#/setup" in d.url)
    d.click("#wzskip"); d.wait_for_selector("details.secline")
    check("Wizard: 'Skip the wizard (advanced)' -> normal pages, remembered", hd("/api/session")["setup_skipped"] is True and d.locator("#wz").count() == 0)
    go_d = lambda r: (d.goto(f"https://127.0.0.1:{PD}/#/{r}"), d.reload())
    go_d("settings"); d.wait_for_selector("details.secline[data-sec='reset']", state="attached")
    d.locator("details.secline[data-sec='reset'] > summary").click()
    d.click("#frgo")
    check("Settings/Factory reset: without typing RESET -> refused with a message", "RESET" in d.locator("#frmsg").inner_text())
    d.fill("#frconfirm", "RESET"); d.click("#frgo")
    d.wait_for_selector("#pw", timeout=150000)
    check("Settings/Factory reset: click -> the hub comes back in first-start mode (new password)", hd("/api/session").get("setup_needed") is True or
          client(f"https://127.0.0.1:{PD}")("/api/session").get("setup_needed") is True)
    br.close()

subprocess.run(" ".join(f"pid=$(ss -ltnp 'sport = :{p}' | grep -oP 'pid=\\K[0-9]+' | head -1); [ -n \"$pid\" ] && kill $pid;" for p in ports), shell=True)
bad = [r for r in results if not r[1]]
print(f"\nJS errors: {len(errors)} {errors[:3]}\n{len(results) - len(bad)}/{len(results)} passed")
sys.exit(1 if bad or errors else 0)
