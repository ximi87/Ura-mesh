"""Screenshots of the demo network for the GitHub documentation (docs/img).
Needs: demo_network.py against a test server on 8298/8299, and demo_hub.py run against a radio-less hub on 8187."""
import os
from playwright.sync_api import sync_playwright
S = os.environ.get("URA_DEMO_SERVER_WEB", "https://127.0.0.1:8299")
H = os.environ.get("URA_DEMO_HUB", "https://127.0.0.1:8187")
OUT = os.environ.get("URA_DEMO_OUT", "/tmp/ura-demo/img")
os.makedirs(OUT, exist_ok=True); errs = []
J = dict(type="jpeg", quality=82)
with sync_playwright() as pw:
    br = pw.chromium.launch()
    p = br.new_context(ignore_https_errors=True, viewport={"width": 1400, "height": 860}).new_page()
    p.on("pageerror", lambda e: errs.append(str(e)))
    p.goto(S + "/#/"); p.wait_for_selector("#liveon"); p.wait_for_timeout(9000)
    for _ in range(40):
        n = p.evaluate("() => { let n = 0; mapObj.eachLayer(l => { if (l instanceof L.CircleMarker && !l.options.interactive) n++; }); return n; }")
        if n >= 2: break
        p.wait_for_timeout(300)
    p.screenshot(path=f"{OUT}/map-world.jpg", **J)
    p.evaluate("() => { mapObj.setView([53.55, 9.99], 10); }"); p.wait_for_timeout(5000)
    p.evaluate("""() => { let best = null, bd = 1e9; const c = L.latLng(53.62, 9.93); mapObj.eachLayer(l => { if (l instanceof L.CircleMarker && l.options.radius === 6) { const d = l.getLatLng().distanceTo(c); if (d < bd) { bd = d; best = l; } } }); if (best) best.openPopup(); }""")
    p.wait_for_timeout(1500); p.screenshot(path=f"{OUT}/map-nodes.jpg", **J)
    p.goto(S + "/#/hubs"); p.reload(); p.wait_for_selector("text=XB-HBR"); p.click("table a >> text=XB-HBR")
    p.wait_for_selector("text=About this hub"); p.wait_for_timeout(5000)
    p.screenshot(path=f"{OUT}/server-hub.jpg", full_page=True, clip={"x": 0, "y": 0, "width": 1400, "height": 1180}, **J)
    p.goto(S + "/#/stats"); p.reload(); p.wait_for_selector("text=Traffic between hubs"); p.wait_for_timeout(1500)
    p.screenshot(path=f"{OUT}/server-stats.jpg", full_page=True, clip={"x": 0, "y": 0, "width": 1400, "height": 1100}, **J)
    q = br.new_context(ignore_https_errors=True, viewport={"width": 1400, "height": 860}).new_page()
    q.on("pageerror", lambda e: errs.append(str(e)))
    q.goto(H + "/#/"); q.wait_for_selector("#pw"); q.fill("#pw", "DemoHub-123"); q.click("#lbtn"); q.wait_for_selector("text=Server connection")
    q.goto(H + "/#/links"); q.reload(); q.wait_for_selector("select[data-reach]"); q.wait_for_timeout(1000)
    q.screenshot(path=f"{OUT}/hub-links.jpg", full_page=True, **J)
    q.goto(H + "/#/settings"); q.reload(); q.wait_for_selector("#tron"); q.add_style_tag(content="header.top{position:static !important}"); q.wait_for_timeout(800)
    q.locator("#tron").locator("xpath=ancestor::div[contains(@class,'card')][1]").screenshot(path=f"{OUT}/hub-settings.jpg", **J)
    q.click("#advform details[data-group='adv.g.radio'] summary"); q.click("#advform details[data-group='adv.g.server'] summary")
    q.fill("[data-adv=keepalive_s]", "45"); q.wait_for_timeout(300)
    q.locator("#advform").locator("xpath=ancestor::div[contains(@class,'card')][1]").screenshot(path=f"{OUT}/hub-advanced.jpg", **J)
    br.close()
print("errors", errs)
