import os, re, sys, time
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.environ.get("URA_TEST_DIR", "/tmp/ura-t")
HUBPY = os.environ.get("URA_HUB_PYTHON", "python3")
from playwright.sync_api import sync_playwright

S, A, B = "https://127.0.0.1:8199", "https://127.0.0.1:8197", "https://127.0.0.1:8196"
PW = "TestPass123"
errors, results = [], []

def check(name, cond):
    results.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name, flush=True)

def nav(p, url):
    p.goto(url); p.reload()

def new_page(ctx, label):
    p = ctx.new_page()
    p.on("pageerror", lambda e: errors.append(f"{label} pageerror: {e}"))
    p.on("console", lambda m: m.type == "error" and "tile.openstreetmap" not in m.text and "Failed to load resource" not in m.text and errors.append(f"{label} console: {m.text}"))
    return p

def setup_login(p, base):
    p.goto(base + "/#/")
    p.wait_for_selector("#pw")
    p.fill("#pw", PW); p.click("#lbtn")

def hub_register(p, base, name, country, city, lat, lon):
    setup_login(p, base)
    p.wait_for_selector("text=Server connection")
    p.goto(base + "/#/settings"); p.wait_for_selector("#hname")
    p.fill("#hname", name); p.fill("#hemail", f"{name.replace(' ','').lower()}@example.org")
    p.fill("#hcountry", country); p.fill("#hcity", city)
    p.click("#hsave"); p.wait_for_selector("#hmsg .msg.ok")
    # location card: no radio in the test -> manual position
    p.check("input[name=lmode][value=manual]"); p.fill("#hlat", str(lat)); p.fill("#hlon", str(lon))
    p.click("#locsave"); p.wait_for_selector("#locmsg .msg.ok"); time.sleep(1.8); p.wait_for_selector("#hname")
    check(f"{name}: manual location saved", p.input_value("#hlat").startswith(str(lat)[:5]))
    p.fill("#saddr", "127.0.0.1:8198"); p.click("#scheck")
    p.wait_for_selector("#strust")
    fp = p.inner_text("#sfp .mono")
    p.click("#strust"); p.wait_for_selector("#sjoin")
    # the request only goes to the trusted server shown on the page
    p.fill("#saddr", ""); p.wait_for_timeout(200)
    hidden_empty = p.locator("#sjoinbox").is_hidden() and p.locator("#sjoinwarn").is_visible()
    p.fill("#saddr", "10.9.9.9:8100"); p.wait_for_timeout(200)
    hidden_other = p.locator("#sjoinbox").is_hidden()
    refused = p.evaluate("fetch('/api/server/join', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({address: ''})}).then(r => r.json())")
    p.fill("#saddr", "127.0.0.1:8198"); p.wait_for_timeout(200)
    check(f"{name}: no registration with empty/other address (button hidden, API refuses)",
          hidden_empty and hidden_other and refused.get("error") == "not_trusted" and p.locator("#sjoin").is_visible())
    p.click("#sjoin"); p.wait_for_selector("#jmsg .msg")
    return fp, p.inner_text("#jmsg")

with sync_playwright() as pw:
    br = pw.chromium.launch()
    ctxS = br.new_context(ignore_https_errors=True); ctxA = br.new_context(ignore_https_errors=True); ctxB = br.new_context(ignore_https_errors=True)
    s, a, b = new_page(ctxS, "server"), new_page(ctxA, "hubA"), new_page(ctxB, "hubB")

    # server admin setup
    nav(s, S + "/#/admin"); s.wait_for_selector("#pw"); s.fill("#pw", PW); s.click("#lbtn")
    s.wait_for_selector("text=Waiting for approval"); check("server admin setup + login", True)
    nav(s, S + "/#/join"); s.wait_for_selector("text=Certificate fingerprint")
    server_fp = s.inner_text("dd.mono.small")

    fpA, msgA = hub_register(a, A, "Test Hub A", "XA", "AAA", 10.5, 20.5)
    check("hub A sees same fingerprint as server page", fpA.strip() == server_fp.strip())
    check("hub A join request sent", "Request sent" in msgA)
    fpB, msgB = hub_register(b, B, "Test Hub B", "XB", "BBB", 30.5, 40.5)
    check("hub B join request sent", "Request sent" in msgB)

    # duplicate code refused (hub C on fresh context against hub A's code) -> via API of server not needed; check error text path later

    nav(a, A + "/#/"); a.wait_for_selector("text=Server connection")
    check("hub shows 'waiting for approval' notice", "waiting for the administrator's approval" in a.inner_text("#app"))
    nav(s, S + "/#/admin"); s.wait_for_selector("button[data-a=approve]")
    check("admin menu badge shows 2 waiting hubs", s.inner_text("nav.menu a[href='#/admin']").strip().endswith("2"))
    check("server shows 2 pending", s.locator("button[data-a=approve]").count() == 2)
    for _ in range(2):
        s.locator("button[data-a=approve]").first.click(); time.sleep(1.2)
        s.wait_for_selector("text=Approved hubs")
    time.sleep(1)
    nav(s, S + "/#/admin"); s.wait_for_selector("text=Approved hubs (2)")
    check("admin badge gone after approval", s.locator("nav.menu .mbadge").count() == 0)
    check("both hubs approved", True)

    # hubs see each other, request + accept link
    time.sleep(3)
    nav(a, A + "/#/links"); a.wait_for_selector("text=XB-BBB")
    a.click("button[data-ask]"); time.sleep(2)
    nav(a, A + "/#/links"); a.wait_for_selector("text=waiting for XB-BBB to accept")
    check("hub A requested link", True)
    nav(b, B + "/#/links"); b.wait_for_selector("button[data-acc]")
    check("hub B sees request", "asks to link" in b.inner_text("#app"))
    b.click("button[data-acc]"); time.sleep(2)
    nav(b, B + "/#/links"); b.wait_for_selector("text=My rules for this link")
    check("link active on B", "active" in b.inner_text("#app"))
    nav(a, A + "/#/links"); a.wait_for_selector("text=My rules for this link")
    check("link active on A", True)

    # rules: A turns positions off for sending, saves; check persisted + published to B
    a.locator('input[data-dir=send][data-k=positions]').uncheck()
    check("per-link reach defaults to 'only to the partner'", a.input_value("select[data-reach]") == "0")
    a.select_option("select[data-reach]", "2")
    check("reach > 0 with no further link offered says so", a.locator("[data-reach-ticks]").is_visible() and "offers no further hubs" in a.inner_text("[data-reach-ticks]"))
    a.click("button[data-save]"); a.wait_for_selector("text=✓ Saved")
    nav(a, A + "/#/links"); a.wait_for_selector("text=My rules for this link")
    check("A send-positions rule persisted", not a.locator('input[data-dir=send][data-k=positions]').is_checked())
    check("A per-link reach persisted", a.input_value("select[data-reach]") == "2")
    time.sleep(2)
    nav(b, B + "/#/links"); b.wait_for_selector("text=Rules of XA-AAA")
    check("B sees A's published rules", "Not published" not in b.inner_text("[data-peer]"))

    # end-to-end encryption: same safety code on both hubs
    import re as _re, subprocess, os
    codeA = _re.search(r"Safety code: ([0-9 ]{23})", a.inner_text("#app"))
    nav(b, B + "/#/links"); b.wait_for_selector("text=Safety code")
    codeB = _re.search(r"Safety code: ([0-9 ]{23})", b.inner_text("#app"))
    check("both hubs show the same safety code", codeA and codeB and codeA.group(1) == codeB.group(1))
    check("link marked end-to-end encrypted", "Everything on this link is sealed" in b.inner_text("#app"))
    # key change: hub B gets a new identity (reinstall / impersonation) -> A must stop + warn
    pid = subprocess.run("ss -ltnp 'sport = :8196' | grep -oP 'pid=\\K[0-9]+' | head -1", shell=True, capture_output=True, text=True).stdout.strip()
    subprocess.run(["kill", pid]); time.sleep(1.5)
    os.remove(f"{T}/hB/identity.key")
    subprocess.Popen(f"cd {REPO}/hub && URA_DATA={T}/hB URA_WEB_PORT=8196 setsid nohup {HUBPY} -u ura_hub.py >> {T}/hubB.log 2>&1 < /dev/null &", shell=True)
    time.sleep(7)
    nav(b, B + "/#/"); b.wait_for_selector("#pw"); b.fill("#pw", PW); b.click("#lbtn"); b.wait_for_selector("text=Server connection")
    nav(a, A + "/#/links"); a.wait_for_selector("text=Safety code")
    check("A detects changed key of B", "has CHANGED" in a.inner_text("#app"))
    a.on("dialog", lambda d: d.accept())
    a.click("button[data-trust]"); time.sleep(1.5)
    nav(a, A + "/#/links"); a.wait_for_selector("text=Safety code")
    check("after trusting, link sealed again", "Everything on this link is sealed" in a.inner_text("#app"))
    nav(s, S + "/#/hubs"); s.click("table a >> text=XA-AAA"); s.wait_for_selector("text=About this hub")
    check("server hub page shows E2E", "End-to-end encryption" in s.inner_text("#app") and "yes" in s.inner_text("#app"))

    # location change after registration reaches the server
    nav(a, A + "/#/settings"); a.wait_for_selector("#hlat"); a.fill("#hlat", "10.6123"); a.click("#locsave"); a.wait_for_selector("#locmsg .msg.ok")
    time.sleep(35)
    nav(s, S + "/#/hubs"); s.click("table a >> text=XA-AAA"); s.wait_for_selector("text=About this hub")
    check("new hub location shown on server", "10.61230" in s.inner_text("#app"))

    # status + radio pages (no radio)
    nav(a, A + "/#/"); a.wait_for_selector("text=Server connection"); check("hub status page", "connected" in a.inner_text("#app"))
    nav(a, A + "/#/radio"); a.wait_for_selector("text=Radio connection"); check("hub radio page", True)

    # server public pages
    nav(s, S + "/#/"); s.wait_for_selector("#map .leaflet-control-zoom"); time.sleep(2)
    markers = s.evaluate("() => { let n = 0; mapObj.eachLayer(l => { if (l instanceof L.CircleMarker) n++; }); return n; }")
    check("home page is only the map (hub markers, no side panel)", markers >= 2 and s.locator(".hubitem").count() == 0)
    check("live traffic switch on the map", s.locator("#liveon").count() == 1)
    nav(a, A + "/#/device"); a.wait_for_selector("#app .msg")
    check("device page without radio says so", "radio" in a.inner_text("#app").lower())
    nav(s, S + "/#/hubs"); s.wait_for_selector("text=XA-AAA"); check("hubs table", "XB-BBB" in s.inner_text("#app"))
    s.click("table a >> text=XA-AAA"); s.wait_for_selector("text=About this hub"); check("hub page", "Rules this hub applies" in s.inner_text("#app"))
    nav(s, S + "/#/stats"); s.wait_for_selector("text=Traffic between hubs"); check("stats page", "Active links" in s.inner_text("#app"))
    nav(s, S + "/#/hubs"); s.wait_for_selector("text=XA-AAA"); check("hubs page explains codes", "One hub per place" in s.inner_text("#app"))
    check("no shortcodes menu", s.locator("nav.menu >> text=Shortcodes").count() == 0)
    nav(s, S + "/#/complaints"); s.wait_for_selector("#csend")
    s.fill("#cem", "x@example.org"); s.fill("#ctx", "Test complaint about interference"); s.click("#csend")
    s.wait_for_selector("#cmsg .msg.ok"); check("complaint sent", "case #1" in s.inner_text("#cmsg"))
    nav(s, S + "/#/admin"); s.wait_for_selector("select[data-cs]")
    s.select_option("select[data-cs]", "resolved"); s.fill("textarea[data-cr]", "Checked, fixed."); s.click("button[data-csave]")
    s.wait_for_selector("text=✓ Saved")
    nav(s, S + "/#/complaints"); s.wait_for_selector("text=Checked, fixed."); check("complaint resolution public", "resolved" in s.inner_text("#app"))

    # advanced settings: hub (valid value persists, invalid rejected + marked)
    def adv_open(pg): pg.wait_for_selector("[data-adv=password_min]", state="attached"); pg.click("#advform [data-all='1']")
    nav(a, A + "/#/settings"); adv_open(a)
    check("hub advanced settings in sections", a.locator("details.adv-group").count() >= 5)
    a.fill("[data-adv=node_max_age_days]", "5")
    check("changed value marked + counted in its section", a.locator("[data-adv-row=node_max_age_days].changed").count() == 1
          and "1" in a.locator("details.adv-group:has([data-adv=node_max_age_days]) .adv-changed").inner_text())
    a.click("[data-adv-row=clock_sync] .switch span")
    check("dependent field greyed out", a.locator("[data-adv=clock_sync_min]").is_disabled())
    a.click("[data-reset=clock_sync]")
    check("reset to default", a.locator("[data-adv=clock_sync]").is_checked() and not a.locator("[data-adv=clock_sync_min]").is_disabled())
    a.click("#advsave"); a.wait_for_selector("#advmsg .msg.ok")
    nav(a, A + "/#/settings"); adv_open(a)
    check("hub advanced value persisted", a.input_value("[data-adv=node_max_age_days]") == "5")
    adv_open(a); a.fill("[data-adv=keepalive_s]", "1"); a.click("#advform [data-all='0']"); a.click("#advsave"); a.wait_for_selector("#advmsg .msg.bad")
    check("hub advanced invalid value rejected + marked (its section opens)", a.locator("[data-adv-row=keepalive_s].invalid").count() == 1
          and a.locator("[data-adv-row=keepalive_s]").is_visible())
    nav(a, A + "/#/settings"); adv_open(a)
    check("hub invalid value not stored", a.input_value("[data-adv=keepalive_s]") == "30")
    # advanced settings: server
    nav(s, S + "/#/admin"); adv_open(s)
    s.click("[data-adv-row=registrations_open] .switch span"); s.fill("[data-adv=stats_retention_days]", "30"); s.click("#advsave"); s.wait_for_selector("#advmsg .msg.ok")
    info = s.evaluate("fetch('/api/public/info').then(r => r.json())")
    check("server registrations closed", info["registrations_open"] is False)
    nav(s, S + "/#/admin"); adv_open(s)
    check("server advanced persisted", s.input_value("[data-adv=stats_retention_days]") == "30")
    s.click("[data-reset=registrations_open]"); s.click("#advsave"); s.wait_for_selector("#advmsg .msg.ok")
    s.fill("[data-adv=tile_upstream]", "http://evil/x"); s.click("#advsave"); s.wait_for_selector("#advmsg .msg.bad")
    check("server rejects non-https tile source", True)

    # login lockout after 5 wrong passwords (fresh browser context)
    lc = br.new_context(ignore_https_errors=True); lp = new_page(lc, "lock")
    for i in range(6):
        lp.goto(B + "/#/"); lp.reload(); lp.wait_for_selector("#pw"); lp.fill("#pw", "wrong-%d" % i); lp.click("#lbtn"); lp.wait_for_selector("#lmsg .msg")
    check("login locked after 5 failures", "Too many wrong passwords" in lp.inner_text("#lmsg"))
    lc.close()

    # language switch
    nav(s, S + "/#/hubs"); s.wait_for_selector(".lang button[data-l=sq]"); s.click(".lang button[data-l=sq]")
    s.wait_for_selector("text=Hub-et e regjistruar"); check("server Albanian", True)
    s.screenshot(path=f"{T}/shot_server_map_sq.png", full_page=True)
    nav(a, A + "/#/"); a.click(".lang button[data-l=sq]"); a.wait_for_selector("text=Lidhja me serverin"); check("hub Albanian", True)
    a.screenshot(path=f"{T}/shot_hub_status_sq.png", full_page=True)
    a.click(".lang button[data-l=en]")
    nav(b, B + "/#/links"); b.wait_for_selector("text=My rules"); b.screenshot(path=f"{T}/shot_hub_links.png", full_page=True)
    s.click(".lang button[data-l=en]"); nav(s, S + "/#/hub/" + "x"); time.sleep(1)

    # removal: admin removes hub B -> link gone at A
    nav(s, S + "/#/admin"); s.wait_for_selector("button[data-a=remove]")
    s.on("dialog", lambda d: d.accept())
    s.locator("button[data-a=remove][data-code='XB-BBB']").click(); time.sleep(4)
    nav(a, A + "/#/links"); a.wait_for_selector("text=Other hubs on the server")
    check("after removal A has no links", "No links yet" in a.inner_text("#app"))
    nav(b, B + "/#/settings"); b.wait_for_selector("text=Registration"); check("B shows removed", "removed" in b.inner_text("#app"))
    br.close()

print("\nJS errors:", len(errors))
for e in errors: print("  ", e)
fails = [n for n, ok in results if not ok]
print(f"\n{len(results)-len(fails)}/{len(results)} passed")
sys.exit(1 if fails or errors else 0)
