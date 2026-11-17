import re, sys, time
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
    p.fill("#hcountry", country); p.fill("#hcity", city); p.fill("#hlat", str(lat)); p.fill("#hlon", str(lon))
    p.click("#hsave"); p.wait_for_selector("#hmsg .msg.ok")
    p.fill("#saddr", "127.0.0.1:8198"); p.click("#scheck")
    p.wait_for_selector("#strust")
    fp = p.inner_text("#sfp .mono")
    p.click("#strust"); p.wait_for_selector("#sjoin")
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

    fpA, msgA = hub_register(a, A, "Test Tirana", "AL", "TR", 41.3485, 19.8976)
    check("hub A sees same fingerprint as server page", fpA.strip() == server_fp.strip())
    check("hub A join request sent", "Request sent" in msgA)
    fpB, msgB = hub_register(b, B, "Test Ludwigsburg", "DE", "LB", 48.8899, 9.1488)
    check("hub B join request sent", "Request sent" in msgB)

    # duplicate code refused (hub C on fresh context against hub A's code) -> via API of server not needed; check error text path later

    nav(s, S + "/#/admin"); s.wait_for_selector("button[data-a=approve]")
    check("server shows 2 pending", s.locator("button[data-a=approve]").count() == 2)
    for _ in range(2):
        s.locator("button[data-a=approve]").first.click(); time.sleep(1.2)
        s.wait_for_selector("text=Approved hubs")
    time.sleep(1)
    nav(s, S + "/#/admin"); s.wait_for_selector("text=Approved hubs (2)")
    check("both hubs approved", True)

    # hubs see each other, request + accept link
    time.sleep(3)
    nav(a, A + "/#/links"); a.wait_for_selector("text=DE-LB")
    a.click("button[data-ask]"); time.sleep(2)
    nav(a, A + "/#/links"); a.wait_for_selector("text=waiting for DE-LB to accept")
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
    a.click("button[data-save]"); a.wait_for_selector("text=✓ Saved")
    nav(a, A + "/#/links"); a.wait_for_selector("text=My rules for this link")
    check("A send-positions rule persisted", not a.locator('input[data-dir=send][data-k=positions]').is_checked())
    time.sleep(2)
    nav(b, B + "/#/links"); b.wait_for_selector("text=Rules of AL-TR")
    check("B sees A's published rules", "Not published" not in b.inner_text("[data-peer]"))

    # status + radio pages (no radio)
    nav(a, A + "/#/"); a.wait_for_selector("text=Server connection"); check("hub status page", "connected" in a.inner_text("#app"))
    nav(a, A + "/#/radio"); a.wait_for_selector("text=Radio connection"); check("hub radio page", True)

    # server public pages
    nav(s, S + "/#/"); s.wait_for_selector(".hubitem"); check("map lists 2 hubs", s.locator(".hubitem").count() == 2)
    nav(s, S + "/#/hubs"); s.wait_for_selector("text=AL-TR"); check("hubs table", "DE-LB" in s.inner_text("#app"))
    s.click("text=AL-TR"); s.wait_for_selector("text=About this hub"); check("hub page", "Rules this hub applies" in s.inner_text("#app"))
    nav(s, S + "/#/stats"); s.wait_for_selector("text=Traffic between hubs"); check("stats page", "Active links" in s.inner_text("#app"))
    nav(s, S + "/#/codes"); s.wait_for_selector("text=AL-TR"); check("codes page", True)
    nav(s, S + "/#/complaints"); s.wait_for_selector("#csend")
    s.fill("#cem", "x@example.org"); s.fill("#ctx", "Test complaint about interference"); s.click("#csend")
    s.wait_for_selector("#cmsg .msg.ok"); check("complaint sent", "case #1" in s.inner_text("#cmsg"))
    nav(s, S + "/#/admin"); s.wait_for_selector("select[data-cs]")
    s.select_option("select[data-cs]", "resolved"); s.fill("textarea[data-cr]", "Checked, fixed."); s.click("button[data-csave]")
    s.wait_for_selector("text=✓ Saved")
    nav(s, S + "/#/complaints"); s.wait_for_selector("text=Checked, fixed."); check("complaint resolution public", "resolved" in s.inner_text("#app"))

    # language switch
    nav(s, S + "/#/"); s.wait_for_selector(".lang button[data-l=sq]"); s.click(".lang button[data-l=sq]")
    s.wait_for_selector("text=Hub-et dhe nyjet"); check("server Albanian", True)
    s.screenshot(path="/tmp/ura-t/shot_server_map_sq.png", full_page=True)
    nav(a, A + "/#/"); a.click(".lang button[data-l=sq]"); a.wait_for_selector("text=Lidhja me serverin"); check("hub Albanian", True)
    a.screenshot(path="/tmp/ura-t/shot_hub_status_sq.png", full_page=True)
    a.click(".lang button[data-l=en]")
    nav(b, B + "/#/links"); b.wait_for_selector("text=My rules"); b.screenshot(path="/tmp/ura-t/shot_hub_links.png", full_page=True)
    s.click(".lang button[data-l=en]"); nav(s, S + "/#/hub/" + "x"); time.sleep(1)

    # removal: admin removes hub B -> link gone at A
    nav(s, S + "/#/admin"); s.wait_for_selector("button[data-a=remove]")
    s.on("dialog", lambda d: d.accept())
    s.locator("button[data-a=remove][data-code='DE-LB']").click(); time.sleep(4)
    nav(a, A + "/#/links"); a.wait_for_selector("text=Other hubs on the server")
    check("after removal A has no links", "No links yet" in a.inner_text("#app"))
    nav(b, B + "/#/settings"); b.wait_for_selector("text=Registration"); check("B shows removed", "removed" in b.inner_text("#app"))
    br.close()

print("\nJS errors:", len(errors))
for e in errors: print("  ", e)
fails = [n for n, ok in results if not ok]
print(f"\n{len(results)-len(fails)}/{len(results)} passed")
sys.exit(1 if fails or errors else 0)
