/* ura-server website */
"use strict";

Ura.add({
  "site.title": { en: "server", sq: "server" },
  "nav.map": { en: "Map", sq: "Harta" }, "nav.hubs": { en: "Hubs", sq: "Hub-et" },
  "nav.stats": { en: "Statistics", sq: "Statistika" },
  "nav.join": { en: "Register a hub", sq: "Regjistro një hub" }, "nav.complaints": { en: "Complaints", sq: "Ankesat" },
  "nav.admin": { en: "Admin", sq: "Admin" },
  "foot": { en: "Ura links separate Meshtastic and MeshCore networks over the internet. The server only lets hubs find each other and counts traffic; traffic between hubs is end-to-end encrypted, so it cannot read or store messages. Every rule lives in the hubs.",
            sq: "Ura lidh rrjete të ndara Meshtastic dhe MeshCore përmes internetit. Serveri vetëm i ndihmon hub-et të gjejnë njëri-tjetrin dhe numëron trafikun; trafiku ndërmjet hub-eve është i enkriptuar skaj-më-skaj, ndaj ai nuk mund të lexojë apo ruajë mesazhe. Çdo rregull ndodhet te hub-et." },
  "map.title": { en: "Hubs and nodes", sq: "Hub-et dhe nyjet" },
  "map.legend.hub": { en: "Hub (on-site bridge)", sq: "Hub (ura në vend)" },
  "map.legend.node": { en: "Node heard by a hub", sq: "Nyje e dëgjuar nga një hub" },
  "map.legend.link": { en: "Active link", sq: "Lidhje aktive" },
  "map.nohubs": { en: "No hub is registered yet.", sq: "Ende nuk ka asnjë hub të regjistruar." },
  "adv.g.reg": { en: "Registration and links", sq: "Regjistrimi dhe lidhjet" },
  "adv.g.cert": { en: "Certificate (Let's Encrypt)", sq: "Certifikata (Let's Encrypt)" },
  "adv.g.traffic": { en: "Nodes and traffic", sq: "Nyjet dhe trafiku" },
  "adv.g.complaints": { en: "Complaints", sq: "Ankesat" },
  "adv.g.security": { en: "Security and login", sq: "Siguria dhe hyrja" },
  "adv.g.tiles": { en: "Map tiles", sq: "Pllakat e hartës" },
  "adv.registrations_open": { en: "Accept new hub registrations", sq: "Prano regjistrime të reja hub-esh" },
  "adv.node_max_age_days": { en: "Show nodes heard within (days)", sq: "Shfaq nyjet e dëgjuara brenda (ditë)" },
  "adv.max_nodes_per_report": { en: "Max. nodes accepted per hub report", sq: "Maks. nyje të pranuara për raport hub-i" },
  "adv.relay_rate_per_s": { en: "Flood limit: sealed boxes per second per hub", sq: "Kufiri i vërshimit: kuti të mbyllura për sekondë për hub" },
  "adv.relay_burst": { en: "Flood limit: short burst allowed", sq: "Kufiri i vërshimit: shpërthim i shkurtër i lejuar" },
  "adv.max_box_bytes": { en: "Largest sealed box relayed (bytes)", sq: "Kutia më e madhe e kaluar (bajt)" },
  "adv.stats_retention_days": { en: "Keep statistics for (days)", sq: "Mbaj statistikat për (ditë)" },
  "adv.complaints_per_hour": { en: "Complaints per sender address per hour", sq: "Ankesa për adresë dërguesi në orë" },
  "adv.complaint_min_chars": { en: "Shortest complaint text (characters)", sq: "Teksti më i shkurtër i ankesës (karaktere)" },
  "adv.complaint_max_chars": { en: "Longest complaint text (characters)", sq: "Teksti më i gjatë i ankesës (karaktere)" },
  "adv.session_hours": { en: "Admin stays logged in for (hours)", sq: "Administratori qëndron i identifikuar për (orë)" },
  "adv.lockout_attempts": { en: "Lock out an address after wrong passwords", sq: "Blloko një adresë pas fjalëkalimesh të gabuara" },
  "adv.lockout_minutes": { en: "Lockout lasts (minutes)", sq: "Bllokimi zgjat (minuta)" },
  "adv.password_min": { en: "Minimum password length", sq: "Gjatësia minimale e fjalëkalimit" },
  "adv.tile_upstream": { en: "Map tile source (https URL with {z}/{x}/{y})", sq: "Burimi i pllakave të hartës (URL https me {z}/{x}/{y})" },
  "adv.tile_contact": { en: "Contact sent to the tile server (its policy requires one)", sq: "Kontakti i dërguar te serveri i pllakave (rregullat e tij e kërkojnë)" },
  "adv.tile_cache_days": { en: "Keep map tiles for (days)", sq: "Mbaj pllakat e hartës për (ditë)" },
  "adv.tile_backoff_s": { en: "After a failed tile download, pause for (seconds)", sq: "Pas një shkarkimi të dështuar, prit për (sekonda)" },
  "map.nodes_on": { en: "{n} nodes (heard in the last {d} days)", sq: "{n} nyje (dëgjuar në {d} ditët e fundit)" },
  "map.nopos": { en: "{n} nodes have no position and are not on the map.", sq: "{n} nyje nuk kanë pozicion dhe nuk shfaqen në hartë." },
  "hubs.title": { en: "Registered hubs", sq: "Hub-et e regjistruar" },
  "hubs.where": { en: "Place", sq: "Vendi" }, "hubs.links": { en: "Linked with", sq: "I lidhur me" },
  "hub.title": { en: "Hub {code}", sq: "Hub {code}" },
  "hub.about": { en: "About this hub", sq: "Për këtë hub" },
  "hub.registered": { en: "Registered", sq: "Regjistruar" }, "hub.last_seen": { en: "Last seen", sq: "Parë së fundi" },
  "rule.onward": { en: "How far its packets may go (multi-hop)", sq: "Sa larg mund të shkojnë paketat e tij (shumë-hop)" },
  "reach.0": { en: "stop at this hub", sq: "ndalojnë te ky hub" }, "reach.n": { en: "up to {n} hub(s) further", sq: "deri në {n} hub më tej" },
  "reach.any": { en: "anywhere", sq: "kudo" },
  "rule.transit": { en: "Passes other hubs' packets on", sq: "Kalon paketat e hub-eve të tjerë" },
  "rule.from_beyond": { en: "Accepts packets from hubs further away", sq: "Pranon paketa nga hub-e më larg" },
  "live.on": { en: "Live traffic", sq: "Trafiku drejtpërdrejt" },
  "live.count": { en: "{n} packets since you opened the map", sq: "{n} paketa që kur hapët hartën" },
  "hubs.codes": { en: "Code = country (ISO code, 2–3 letters) + place (2–3 letters chosen by the operator), written XX-YY. One hub per place, so a code always names exactly one hub. Remote nodes appear in your Meshtastic/MeshCore app like any other node — to message one, open it and choose “Send message”.",
                  sq: "Kodi = shteti (kodi ISO, 2–3 shkronja) + vendi (2–3 shkronja të zgjedhura nga operatori), shkruar XX-YY. Një hub për vend, ndaj një kod tregon gjithmonë saktësisht një hub. Nyjet në distancë shfaqen në aplikacionin tuaj Meshtastic/MeshCore si çdo nyje tjetër — për t'i shkruar, hapeni dhe zgjidhni “Dërgo mesazh”." },
  "hub.transit": { en: "Passes traffic between its linked hubs (multi-hop)", sq: "Kalon trafikun ndërmjet hub-eve të lidhur (shumë-hop)" },
  "hub.transit_to": { en: "offered towards {n} linked hub(s)", sq: "ofruar drejt {n} hub-eve të lidhur" },
  "hub.transit.on": { en: "yes, up to {n} hops", sq: "po, deri në {n} kalime" },
  "hub.e2e": { en: "End-to-end encryption", sq: "Enkriptim skaj-më-skaj" },
  "hub.e2e.hint": { en: "traffic between hubs is sealed; this server cannot read it", sq: "trafiku ndërmjet hub-eve është i mbyllur; ky server nuk mund ta lexojë" },
  "a.locked": { en: "Too many wrong passwords. Try again in 15 minutes.", sq: "Shumë fjalëkalime të gabuara. Provoni përsëri pas 15 minutash." },
  "hub.version": { en: "Software", sq: "Programi" }, "hub.radios": { en: "Radios", sq: "Radiot" },
  "hub.rules": { en: "Rules this hub applies (public)", sq: "Rregullat që zbaton ky hub (publike)" },
  "hub.rules.none": { en: "The hub has not published its rules yet.", sq: "Hub-i nuk i ka publikuar ende rregullat." },
  "hub.rules.default": { en: "Default for new links", sq: "Parazgjedhja për lidhjet e reja" },
  "hub.traffic30": { en: "Traffic in the last 30 days", sq: "Trafiku në 30 ditët e fundit" },
  "hub.sent_to": { en: "sent to {x}", sq: "dërguar te {x}" }, "hub.recv_from": { en: "received from {x}", sq: "marrë nga {x}" },
  "hub.complaints": { en: "Complaints about this hub", sq: "Ankesat për këtë hub" },
  "hub.complain": { en: "Report a problem with this hub", sq: "Raporto një problem me këtë hub" },
  "node.title": { en: "Node {name}", sq: "Nyja {name}" },
  "node.on_hub": { en: "Heard by hub", sq: "Dëgjuar nga hub-i" },
  "node.reach": { en: "Reachable from", sq: "E arritshme nga" },
  "node.reach.hint": { en: "Hubs linked with this node's hub. Their users can see and message this node, within the rules of both hubs.",
                       sq: "Hub-et e lidhur me hub-in e kësaj nyjeje. Përdoruesit e tyre mund ta shohin dhe t'i shkruajnë kësaj nyjeje, brenda rregullave të të dy hub-eve." },
  "node.complain": { en: "Report a problem with this node", sq: "Raporto një problem me këtë nyje" },
  "stats.title": { en: "Traffic between hubs", sq: "Trafiku ndërmjet hub-eve" },
  "stats.hint": { en: "Packets passed along each link. Counts only — the server never sees message content.",
                  sq: "Paketat e kaluara në secilën lidhje. Vetëm numra — serveri nuk e sheh kurrë përmbajtjen e mesazheve." },
  "stats.range": { en: "Period", sq: "Periudha" }, "stats.24h": { en: "24 hours", sq: "24 orë" },
  "stats.7d": { en: "7 days", sq: "7 ditë" }, "stats.30d": { en: "30 days", sq: "30 ditë" },
  "stats.total": { en: "Total", sq: "Gjithsej" }, "stats.none": { en: "No traffic in this period.", sq: "Nuk ka trafik në këtë periudhë." },
  "stats.links_active": { en: "Active links", sq: "Lidhje aktive" }, "stats.hubs_online": { en: "Hubs online", sq: "Hub-e në linjë" },
  "stats.nodes": { en: "Nodes seen", sq: "Nyje të para" }, "stats.packets": { en: "Packets", sq: "Paketa" },
  "join.title": { en: "Register a hub", sq: "Regjistro një hub" },
  "join.intro": { en: "A hub is a small computer (mini PC or Raspberry Pi) next to a Meshtastic or MeshCore radio. It connects out to this server — no port forwarding needed at your site.",
                  sq: "Hub-i është një kompjuter i vogël (mini PC ose Raspberry Pi) pranë një radioje Meshtastic ose MeshCore. Ai lidhet me këtë server nga brenda — nuk nevojitet hapje portash në vendin tuaj." },
  "join.s1": { en: "Install ura-hub on the computer and connect your radio (USB, Wi-Fi/IP or Bluetooth).", sq: "Instaloni ura-hub në kompjuter dhe lidhni radion (USB, Wi-Fi/IP ose Bluetooth)." },
  "join.s2": { en: "Open the hub's own page, enter this server's address and check the fingerprint below.", sq: "Hapni faqen e hub-it, vendosni adresën e këtij serveri dhe kontrolloni gjurmën më poshtë." },
  "join.s3": { en: "Fill in the hub name, your e-mail address, the country and place code and the hub's location, then send the request.",
               sq: "Plotësoni emrin e hub-it, adresën tuaj të e-mail-it, kodin e shtetit dhe të vendit dhe vendndodhjen e hub-it, pastaj dërgoni kërkesën." },
  "join.s4": { en: "The administrator checks the request. Once approved, your hub and its nodes appear on the map. No traffic flows yet.",
               sq: "Administratori e kontrollon kërkesën. Pasi të miratohet, hub-i juaj dhe nyjet e tij shfaqen në hartë. Ende nuk kalon trafik." },
  "join.s5": { en: "Ask another hub for a link. Traffic starts only when both hubs accept, and each hub's own rules always apply.",
               sq: "Kërkoni lidhje me një hub tjetër. Trafiku nis vetëm kur të dy hub-et pranojnë, dhe rregullat e secilit hub zbatohen gjithmonë." },
  "join.guide": { en: "Install guide", sq: "Udhëzuesi i instalimit" },
  "join.project": { en: "Source code & documentation", sq: "Kodi burimor & dokumentacioni" },
  "join.closed": { en: "This server does not accept new hubs at the moment.", sq: "Ky server nuk pranon hub-e të reja për momentin." },
  "foot.project": { en: "Ura is open source", sq: "Ura është me kod të hapur" },
  "le.title": { en: "Website certificate (Let's Encrypt)", sq: "Certifikata e faqes (Let's Encrypt)" },
  "le.hint": { en: "Ura can get a free, browser-trusted certificate for the website's public name itself — set it up in Advanced settings below (Let's Encrypt: on, domain, e-mail). The public port 443 must reach this website. Hubs keep using Ura's own certificate.",
               sq: "Ura mund të marrë vetë një certifikatë falas, të besuar nga shfletuesit, për emrin publik të faqes — konfigurojeni te Cilësimet e avancuara më poshtë (Let's Encrypt: aktiv, domeni, e-mail). Porta publike 443 duhet të arrijë këtë faqe. Hub-et vazhdojnë të përdorin certifikatën e vetë Ura." },
  "le.st.off": { en: "off", sq: "joaktiv" }, "le.st.ok": { en: "active", sq: "aktiv" }, "le.st.working": { en: "working…", sq: "në punë…" }, "le.st.error": { en: "error", sq: "gabim" },
  "le.cert": { en: "Certificate from {i}, valid for {d} more days (renewed automatically 30 days before).", sq: "Certifikatë nga {i}, e vlefshme edhe {d} ditë (rinovohet automatikisht 30 ditë para)." },
  "le.run": { en: "Get / renew certificate now", sq: "Merr / rinovo certifikatën tani" },
  "le.started": { en: "Started — this takes up to a minute.", sq: "Filloi — zgjat deri në një minutë." },
  "adv.acme_enabled": { en: "Let's Encrypt certificate for the website", sq: "Certifikatë Let's Encrypt për faqen" },
  "adv.acme_domain": { en: "Public name of the website (e.g. ura.example.org)", sq: "Emri publik i faqes (p.sh. ura.example.org)" },
  "adv.acme_email": { en: "E-mail for Let's Encrypt (optional, expiry warnings)", sq: "E-mail për Let's Encrypt (opsional, paralajmërime skadimi)" },
  "adv.acme_staging": { en: "Test mode (Let's Encrypt staging — not trusted by browsers)", sq: "Mënyrë testimi (Let's Encrypt staging — jo e besuar nga shfletuesit)" },
  "adv.project_url": { en: "Project page (source code, documentation)", sq: "Faqja e projektit (kodi, dokumentacioni)" },
  "adv.install_guide_url": { en: "Install guide for hub operators", sq: "Udhëzuesi i instalimit për operatorët e hub-eve" },
  "join.server": { en: "This server", sq: "Ky server" }, "join.address": { en: "Address for hubs", sq: "Adresa për hub-et" },
  "join.fp": { en: "Certificate fingerprint (SHA-256)", sq: "Gjurma e certifikatës (SHA-256)" },
  "join.email_note": { en: "Your e-mail address is only visible to the administrator. It is used for questions about your hub and for complaints.",
                       sq: "Adresa juaj e e-mail-it shihet vetëm nga administratori. Përdoret për pyetje rreth hub-it tuaj dhe për ankesat." },
  "c.title": { en: "Complaints", sq: "Ankesat" },
  "c.intro": { en: "Report misuse, interference or any other problem with a hub or node. Every case and its status is public here; your e-mail address is not shown.",
               sq: "Raportoni keqpërdorim, ndërhyrje ose çdo problem tjetër me një hub apo nyje. Çdo rast dhe statusi i tij është publik këtu; adresa juaj e e-mail-it nuk shfaqet." },
  "c.new": { en: "New complaint", sq: "Ankesë e re" }, "c.about": { en: "About", sq: "Për" },
  "c.node": { en: "Node", sq: "Nyje" },
  "c.general": { en: "General", sq: "Të përgjithshme" }, "c.subject": { en: "Hub or node (optional)", sq: "Hub-i ose nyja (opsionale)" },
  "c.email": { en: "Your e-mail address", sq: "Adresa juaj e e-mail-it" }, "c.text": { en: "What happened?", sq: "Çfarë ndodhi?" },
  "c.send": { en: "Send complaint", sq: "Dërgo ankesën" }, "c.sent": { en: "Thank you. Your complaint is case #{id}.", sq: "Faleminderit. Ankesa juaj është rasti #{id}." },
  "c.list": { en: "All cases", sq: "Të gjitha rastet" }, "c.none": { en: "No complaints so far.", sq: "Deri tani nuk ka ankesa." },
  "c.case": { en: "Case", sq: "Rasti" }, "c.date": { en: "Date", sq: "Data" }, "c.resolution": { en: "Answer", sq: "Përgjigjja" },
  "c.st.open": { en: "open", sq: "e hapur" }, "c.st.review": { en: "under review", sq: "në shqyrtim" },
  "c.st.resolved": { en: "resolved", sq: "e zgjidhur" }, "c.st.rejected": { en: "rejected", sq: "e refuzuar" },
  "err.email_required": { en: "Please enter a valid e-mail address.", sq: "Ju lutem vendosni një adresë të vlefshme e-mail-i." },
  "err.text_short": { en: "Please describe the problem (at least {n} characters).", sq: "Ju lutem përshkruani problemin (të paktën {n} karaktere)." },
  "err.too_many": { en: "Too many complaints from your address. Please try again later.", sq: "Shumë ankesa nga adresa juaj. Ju lutem provoni më vonë." },
  "a.title": { en: "Administration", sq: "Administrimi" },
  "a.pending": { en: "Waiting for approval", sq: "Në pritje të miratimit" }, "a.approved": { en: "Approved hubs", sq: "Hub-et e miratuar" },
  "a.approve": { en: "Approve", sq: "Mirato" }, "a.remove": { en: "Remove", sq: "Hiq" },
  "a.verify": { en: "Mark e-mail confirmed", sq: "Shëno e-mail-in si të konfirmuar" },
  "a.email": { en: "E-mail", sq: "E-mail" }, "a.email_ok": { en: "confirmed", sq: "konfirmuar" },
  "a.email_no": { en: "not confirmed (mail sending not set up yet)", sq: "pa konfirmuar (dërgimi i postës ende s'është konfiguruar)" },
  "a.remove_q": { en: "Remove hub {x}? Its links end and its nodes disappear from the map.", sq: "Ta heq hub-in {x}? Lidhjet e tij mbyllen dhe nyjet e tij zhduken nga harta." },
  "a.complaints": { en: "Complaints", sq: "Ankesat" }, "a.set_status": { en: "Update case", sq: "Përditëso rastin" },
  "a.nopending": { en: "No requests waiting.", sq: "Nuk ka kërkesa në pritje." },
  "a.change_pw": { en: "Change admin password", sq: "Ndrysho fjalëkalimin e administratorit" },
  "a.requested": { en: "Requested", sq: "Kërkuar" },
  "notfound": { en: "Not found.", sq: "Nuk u gjet." },
  "net.mt": { en: "Meshtastic", sq: "Meshtastic" }, "net.mc": { en: "MeshCore", sq: "MeshCore" },
});

const MENU = [["#/", "nav.map"], ["#/hubs", "nav.hubs"], ["#/stats", "nav.stats"],
              ["#/join", "nav.join"], ["#/complaints", "nav.complaints"], ["#/admin", "nav.admin"]];
const app = () => document.getElementById("app");
let INFO = {};
let mapObj = null;

const reachTxt = r => { const n = r.reach != null ? +r.reach : ((r.onward_to || []).length ? 1 : 0); return n === 0 ? t("reach.0") : n >= 7 ? t("reach.any") : t("reach.n", { n }); };

function hubLink(h) { return h ? `<a href="#/hub/${encodeURIComponent(h.id)}">${esc(h.code)} · ${esc(h.name)}</a>` : "–"; }
function nodeHref(n) { return `#/node/${encodeURIComponent(n.hub)}/${encodeURIComponent(n.net)}/${encodeURIComponent(n.id)}`; }
function netBadge(net) { return `<span class="badge ${net === "mc" ? "warn" : "info"}">${t("net." + net)}</span>`; }

function rulesHtml(r) {
  if (!r) return `<p class="muted">${t("hub.rules.none")}</p>`;
  const yn = v => v ? `<span class="badge ok">${t("rule.on")}</span>` : `<span class="badge bad">${t("rule.off")}</span>`;
  const one = (x) => x ? `<table><tr><th></th><th>${t("rule.send")}</th><th>${t("rule.receive")}</th></tr>
      <tr><td>${t("link")}</td><td>${yn(x.send && x.send.on)}</td><td>${yn(x.receive && x.receive.on)}</td></tr>
      <tr><td>${t("rule.public")}</td><td>${yn(x.send && x.send.public)}</td><td>${yn(x.receive && x.receive.public)}</td></tr>
      <tr><td>${t("rule.groups")}</td><td>${esc(((x.send && x.send.groups) || []).join(", ") || t("none"))}</td><td>${esc(((x.receive && x.receive.groups) || []).join(", ") || t("none"))}</td></tr>
      <tr><td>${t("rule.private")}</td><td>${yn(x.send && x.send.private)}</td><td>${yn(x.receive && x.receive.private)}</td></tr>
      <tr><td>${t("rule.positions")}</td><td>${yn(x.send && x.send.positions)}</td><td>${yn(x.receive && x.receive.positions)}</td></tr>
      <tr><td>${t("rule.onward")}</td><td>${reachTxt(x.send || {})}</td><td></td></tr>
      <tr><td>${t("rule.transit")}</td><td>${yn(x.send && x.send.transit !== false)}</td><td></td></tr>
      <tr><td>${t("rule.from_beyond")}</td><td></td><td>${yn(!x.receive || x.receive.from_beyond !== false)}</td></tr></table>` : "";
  let s = "";
  if (r.transit) s += `<p>${t("hub.transit")}: <b>${r.transit.enabled ? t("hub.transit.on", { n: r.transit.max_hops }) : t("rule.off")}</b>${(r.transit_to || []).length ? ` — ${t("hub.transit_to", { n: r.transit_to.length })}` : ""}</p>`;
  if (r.airtime) s += `<p>${t("rule.airtime")}: <b>${r.airtime.pct_hour}${t("pct_hour")}</b>${r.airtime.pct_day ? `, <b>${r.airtime.pct_day}${t("pct_day")}</b>` : ""}</p>`;
  if (r.links) for (const code in r.links) s += `<h3>${t("link")} ↔ ${esc(code)}</h3>` + one(r.links[code]);
  return s || `<p class="muted">${t("hub.rules.none")}</p>`;
}

/* ───────── pages ───────── */

async function pageMap() {
  const [hubs, nodes] = await Promise.all([api("GET", "/api/public/hubs"), api("GET", "/api/public/nodes")]);
  app().innerHTML = `<div id="map" class="fullmap"></div>`;
  mapObj = makeMap("map");
  const color = {}, bounds = [];
  hubs.forEach((h, i) => color[h.id] = colorFor(i));
  const byId = Object.fromEntries(hubs.map(h => [h.id, h]));
  const drawn = new Set();
  hubs.forEach(h => (h.links || []).forEach(l => {
    const p = byId[l.peer], key = [h.id, l.peer].sort().join();
    if (!p || drawn.has(key) || h.lat == null || p.lat == null) return;
    drawn.add(key);
    L.polyline([[h.lat, h.lon], [p.lat, p.lon]], { color: "#0f7b6c", weight: 2, dashArray: "6 6", opacity: .7 }).addTo(mapObj);
  }));
  nodes.forEach(n => {
    if (n.lat == null || n.lon == null) return;
    const h = byId[n.hub];
    L.circleMarker([n.lat, n.lon], { radius: 6, color: "#fff", weight: 1.5, fillColor: color[n.hub] || "#666", fillOpacity: .95 })
      .bindPopup(`<b><a href="${nodeHref(n)}">${esc(n.name || n.id)}</a></b> ${esc(n.short || "")}<br>${netBadge(n.net)}<br>${t("node.on_hub")}: ${h ? `<a href="#/hub/${h.id}">${esc(h.code)}</a>` : ""}<br>${t("last_heard")}: ${ago(n.last_heard)}`)
      .addTo(mapObj);
    bounds.push([n.lat, n.lon]);
  });
  hubs.forEach(h => {
    if (h.lat == null) return;
    L.circleMarker([h.lat, h.lon], { radius: 11, color: color[h.id], weight: 3, fillColor: "#fff", fillOpacity: 1 })
      .bindPopup(`<b><a href="#/hub/${h.id}">${esc(h.code)} · ${esc(h.name)}</a></b><br>${onlineBadge(h.online)}<br>${t("map.nodes_on", { n: h.nodes, d: INFO.node_max_age_days })}`)
      .addTo(mapObj);
    bounds.push([h.lat, h.lon]);
  });
  if (bounds.length) mapObj.fitBounds(bounds, { padding: [40, 40], maxZoom: 12 });
  liveTraffic(mapObj, byId, color);
}

/* Live traffic: every packet passed between two hubs runs as a dot along their link (no content). */
let liveTimer = null;
function liveTraffic(m, byId, color) {
  clearInterval(liveTimer);
  let seq = null, running = 0;
  const box = L.control({ position: "topright" });
  box.onAdd = () => { const d = L.DomUtil.create("div", "livebox"); d.innerHTML = `<label class="check small"><input type="checkbox" id="liveon" checked> ${t("live.on")}</label><div class="small muted" id="livecount"></div>`; L.DomEvent.disableClickPropagation(d); return d; };
  box.addTo(m);
  let shown = 0;
  const run = (src, dst, c) => {
    if (running > 40) return;
    running++;
    const a = L.latLng(src.lat, src.lon), b = L.latLng(dst.lat, dst.lon), t0 = performance.now(), dur = 1800;
    const dot = L.circleMarker(a, { radius: 5, color: "#fff", weight: 1.5, fillColor: c, fillOpacity: 1, interactive: false }).addTo(m);
    const step = now => {
      const k = Math.min(1, (now - t0) / dur);
      dot.setLatLng([a.lat + (b.lat - a.lat) * k, a.lng + (b.lng - a.lng) * k]);
      if (k < 1 && mapObj === m) requestAnimationFrame(step); else { m.removeLayer(dot); running--; }
    };
    requestAnimationFrame(step);
  };
  const poll = async () => {
    if (mapObj !== m) { clearInterval(liveTimer); return; }
    try {
      const r = await api("GET", "/api/public/live?after=" + (seq == null ? 0 : seq));
      if (seq != null && $("#liveon") && $("#liveon").checked) r.events.forEach((e, i) => {
        const s = byId[e.src], d = byId[e.dst];
        if (s && d && s.lat != null && d.lat != null) { shown++; setTimeout(() => run(s, d, color[e.src] || "#0f7b6c"), i * 150); }
      });
      seq = r.seq;
      if ($("#livecount")) $("#livecount").textContent = t("live.count", { n: shown });
    } catch (e) {}
  };
  poll();
  liveTimer = setInterval(poll, 3000);
}

async function pageHubs() {
  const hubs = await api("GET", "/api/public/hubs");
  app().innerHTML = `<div class="card"><h2>${t("hubs.title")}</h2><p class="muted small">${t("hubs.codes")}</p><div class="tablewrap"><table>
    <tr><th>${t("code")}</th><th>${t("name")}</th><th>${t("status")}</th><th>${t("nodes")} <span class="muted small">(${INFO.node_max_age_days} d)</span></th><th>${t("hubs.links")}</th><th>${t("hub.last_seen")}</th></tr>
    ${hubs.map(h => `<tr><td><a href="#/hub/${h.id}"><b>${esc(h.code)}</b></a></td><td>${esc(h.name)}</td><td>${onlineBadge(h.online)}</td>
      <td>${h.nodes}</td><td>${(h.links || []).map(l => `<a href="#/hub/${l.peer}">${esc(l.peer_code)}</a>`).join(", ") || "–"}</td><td>${h.online ? t("online") : ago(h.last_seen)}</td></tr>`).join("")
      || `<tr><td colspan="6" class="muted">${t("map.nohubs")}</td></tr>`}
    </table></div></div>`;
}

function nodesTable(nodes) {
  const rows = nodes.slice().sort((a, b) => (b.last_heard || 0) - (a.last_heard || 0));
  return `<div class="tablewrap"><table><tr><th>${t("name")}</th><th>${t("id")}</th><th>${t("network")}</th><th>${t("hardware")}</th><th>${t("position")}</th><th>${t("last_heard")}</th></tr>
    ${rows.map(n => `<tr><td><a href="${nodeHref(n)}">${esc(n.name || n.id)}</a> <span class="muted">${esc(n.short || "")}</span></td><td class="mono">${esc(n.id)}</td>
      <td>${netBadge(n.net)}</td><td>${esc(n.hw || "–")}</td><td>${fmtPos(n.lat, n.lon)}</td><td>${ago(n.last_heard)}</td></tr>`).join("")
      || `<tr><td colspan="6" class="muted">${t("none")}</td></tr>`}</table></div>`;
}

async function pageHub(id) {
  let d;
  try { d = await api("GET", "/api/public/hub/" + encodeURIComponent(id)); } catch (e) { app().innerHTML = `<div class="card">${t("notfound")}</div>`; return; }
  const h = d.hub;
  const names = {}; d.links.forEach(l => names[l.peer] = l.peer_code);
  const traffic = d.stats30d.map(s => s.src === h.id ? `${t("hub.sent_to", { x: esc(names[s.dst] || s.dst) })}: <b>${s.frames}</b> ${t("frames")}`
                                                     : `${t("hub.recv_from", { x: esc(names[s.src] || s.src) })}: <b>${s.frames}</b> ${t("frames")}`);
  app().innerHTML = `
    <div class="spread"><h1>${t("hub.title", { code: esc(h.code) })} · ${esc(h.name)}</h1>${onlineBadge(h.online)}</div>
    <div class="grid g2">
      <div class="card"><h2>${t("hub.about")}</h2><dl class="kv">
        <dt>${t("code")}</dt><dd><b>${esc(h.code)}</b> (${esc(h.country)} · ${esc(h.city)})</dd>
        <dt>${t("position")}</dt><dd>${fmtPos(h.lat, h.lon)}</dd>
        <dt>${t("hub.registered")}</dt><dd>${dt(h.approved)}</dd>
        <dt>${t("hub.last_seen")}</dt><dd>${h.online ? t("online") : ago(h.last_seen)}</dd>
        <dt>${t("hub.version")}</dt><dd>${esc(h.version || "–")}</dd>
        <dt>${t("hub.e2e")}</dt><dd>${h.e2e ? `<span class="badge ok">🔒 ${t("yes")}</span> <span class="muted small">${t("hub.e2e.hint")}</span>` : `<span class="badge warn">${t("no")}</span>`}</dd>
        <dt>${t("hub.radios")}</dt><dd>${(h.radios || []).map(r => `${netBadge(r.net)} ${esc(r.name || "")} <span class="muted">${esc(r.hw || "")} ${esc(r.firmware || "")}</span>`).join("<br>") || "–"}</dd>
        <dt>${t("links")}</dt><dd>${d.links.map(l => `<a href="#/hub/${l.peer}">${esc(l.peer_code)} · ${esc(l.peer_name)}</a>`).join("<br>") || t("none")}</dd>
      </dl>${h.description ? `<p>${esc(h.description)}</p>` : ""}</div>
      <div class="card"><div id="hubmap" class="minimap"></div></div>
    </div>
    <div class="grid g2">
      <div class="card"><h2>${t("hub.rules")}</h2>${rulesHtml(h.rules)}</div>
      <div class="card"><h2>${t("hub.traffic30")}</h2>${traffic.length ? "<p>" + traffic.join("<br>") + "</p>" : `<p class="muted">${t("stats.none")}</p>`}
        <h3>${t("hub.complaints")}</h3>${d.complaints.length ? d.complaints.map(c => `<div>#${c.id} · ${dt(c.created)} · ${cStatus(c.status)}</div>`).join("") : `<p class="muted">${t("c.none")}</p>`}
        <p><a href="#/complaints?hub=${encodeURIComponent(h.id)}">${t("hub.complain")} →</a></p></div>
    </div>
    <div class="card"><h2>${t("nodes")} (${d.nodes.length})</h2><div id="hubnodes"></div></div>`;
  dataTable($("#hubnodes"), d.nodes, [
    { key: "name", label: t("name"), render: n => `<a href="${nodeHref(n)}">${esc(n.name || n.id)}</a> <span class="muted">${esc(n.short || "")}</span>`, sort: n => (n.name || "").toLowerCase() },
    { key: "id", label: t("id"), render: n => `<span class="mono">${esc(n.id)}</span>` },
    { key: "net", label: t("network"), render: n => netBadge(n.net) },
    { key: "hw", label: t("hardware") },
    { key: "lat", label: t("position"), render: n => fmtPos(n.lat, n.lon), sort: n => n.lat != null ? 1 : 0 },
    { key: "last_heard", label: t("last_heard"), render: n => ago(n.last_heard) }],
    { searchKeys: ["name", "short", "id", "hw"], initialSort: "last_heard" });
  const m = makeMap("hubmap", h.lat != null ? [h.lat, h.lon] : [45, 15], h.lat != null ? 10 : 4, { guard: true });
  const b = [];
  if (h.lat != null) { L.circleMarker([h.lat, h.lon], { radius: 11, color: "#0f7b6c", weight: 3, fillColor: "#fff", fillOpacity: 1 }).bindPopup(esc(h.name)).addTo(m); b.push([h.lat, h.lon]); }
  d.nodes.forEach(n => { if (n.lat != null) { L.circleMarker([n.lat, n.lon], { radius: 6, color: "#fff", weight: 1.5, fillColor: "#0f7b6c", fillOpacity: .95 }).bindPopup(`<a href="${nodeHref(n)}">${esc(n.name || n.id)}</a>`).addTo(m); b.push([n.lat, n.lon]); } });
  if (b.length > 1) m.fitBounds(b, { padding: [30, 30], maxZoom: 13 });
}

async function pageNode(hub, net, id) {
  let d;
  try { d = await api("GET", `/api/public/node/${encodeURIComponent(hub)}/${encodeURIComponent(net)}/${encodeURIComponent(id)}`); }
  catch (e) { app().innerHTML = `<div class="card">${t("notfound")}</div>`; return; }
  const n = d.node, h = d.hub;
  app().innerHTML = `
    <h1>${t("node.title", { name: esc(n.name || n.id) })}</h1>
    <div class="grid g2">
      <div class="card"><dl class="kv">
        <dt>${t("name")}</dt><dd>${esc(n.name || "–")} <span class="muted">${esc(n.short || "")}</span></dd>
        <dt>${t("id")}</dt><dd class="mono">${esc(n.id)}</dd>
        <dt>${t("network")}</dt><dd>${netBadge(n.net)}</dd>
        <dt>${t("hardware")}</dt><dd>${esc(n.hw || "–")}</dd>
        <dt>${t("role")}</dt><dd>${esc(n.role || "–")}</dd>
        <dt>${t("position")}</dt><dd>${fmtPos(n.lat, n.lon)}${n.alt != null ? ` · ${Math.round(n.alt)} m` : ""}</dd>
        <dt>${t("last_heard")}</dt><dd>${ago(n.last_heard)} <span class="muted small">${dt(n.last_heard)}</span></dd>
        <dt>${t("hops")}</dt><dd>${n.hops != null ? n.hops : "–"}</dd>
        <dt>${t("node.on_hub")}</dt><dd>${hubLink(h)} ${onlineBadge(h.online)}</dd>
        <dt>${t("node.reach")}</dt><dd>${d.links.map(l => `<a href="#/hub/${l.peer}">${esc(l.peer_code)} · ${esc(l.peer_name)}</a>`).join("<br>") || t("none")}
          <div class="hint">${t("node.reach.hint")}</div></dd>
      </dl><p><a href="#/complaints?node=${encodeURIComponent(h.id + "/" + n.id)}">${t("node.complain")} →</a></p></div>
      <div class="card"><div id="nodemap" class="minimap"></div></div>
    </div>`;
  const ctr = n.lat != null ? [n.lat, n.lon] : (h.lat != null ? [h.lat, h.lon] : [45, 15]);
  const m = makeMap("nodemap", ctr, n.lat != null ? 12 : 6, { guard: true });
  if (n.lat != null) L.circleMarker([n.lat, n.lon], { radius: 8, color: "#fff", weight: 2, fillColor: "#0f7b6c", fillOpacity: 1 }).addTo(m);
  if (h.lat != null) L.circleMarker([h.lat, h.lon], { radius: 11, color: "#0f7b6c", weight: 3, fillColor: "#fff", fillOpacity: 1 }).bindPopup(esc(h.name)).addTo(m);
}

async function pageStats() {
  const hours = +(new URLSearchParams(location.hash.split("?")[1] || "").get("h") || 168);
  const [d, hubs, nodes] = await Promise.all([api("GET", "/api/public/stats?hours=" + hours), api("GET", "/api/public/hubs"), api("GET", "/api/public/nodes")]);
  const name = id => (d.hubs[id] && d.hubs[id].code) || id;
  const pairs = {};
  // grouped by hub CODE, not internal id: a hub that registered again keeps one chart with its whole history
  d.rows.forEach(r => { const src = name(r.src), dst = name(r.dst), k = src + ">" + dst; (pairs[k] = pairs[k] || { src, dst, total: 0, hours: {} }); pairs[k].total += r.frames; pairs[k].hours[r.hour] = (pairs[k].hours[r.hour] || 0) + r.frames; });
  const bucket = hours <= 48 ? 3600 : 86400;
  const start = Math.floor(d.since / bucket) * bucket, n = Math.ceil((Date.now() / 1000 - start) / bucket);
  const labels = [...Array(n)].map((_, i) => { const x = new Date((start + i * bucket) * 1000); return bucket === 3600 ? x.getHours() + ":00" : (x.getDate() + "." + (x.getMonth() + 1)); });
  const series = k => { const v = Array(n).fill(0); for (const h in pairs[k].hours) { const i = Math.floor((h - start) / bucket); if (i >= 0 && i < n) v[i] += pairs[k].hours[h]; } return v; };
  const links = new Set(); hubs.forEach(h => (h.links || []).forEach(l => links.add([h.id, l.peer].sort().join())));
  const total = Object.values(pairs).reduce((a, p) => a + p.total, 0);
  app().innerHTML = `
    <div class="spread"><h1>${t("stats.title")}</h1><div class="row">${[24, 168, 720].map(h => `<a class="btn ${h === hours ? "primary" : ""}" href="#/stats?h=${h}">${t(h === 24 ? "stats.24h" : h === 168 ? "stats.7d" : "stats.30d")}</a>`).join("")}</div></div>
    <p class="muted">${t("stats.hint")}</p>
    <div class="grid g4">
      <div class="stat"><div class="v">${hubs.filter(h => h.online).length} / ${hubs.length}</div><div class="l">${t("stats.hubs_online")}</div></div>
      <div class="stat"><div class="v">${links.size}</div><div class="l">${t("stats.links_active")}</div></div>
      <div class="stat"><div class="v">${nodes.length}</div><div class="l">${t("stats.nodes")}</div></div>
      <div class="stat"><div class="v">${total}</div><div class="l">${t("stats.packets")}</div></div>
    </div><div id="charts" style="margin-top:1rem"></div>`;
  // one chart per link: both directions in two colours
  const linksSeen = {};
  Object.values(pairs).forEach(p => { const [a, b] = [p.src, p.dst].sort(); (linksSeen[a + "|" + b] = linksSeen[a + "|" + b] || { a, b, total: 0 }).total += p.total; });
  const lk = Object.values(linksSeen).sort((x, y) => y.total - x.total);
  const ser = (src, dst) => pairs[src + ">" + dst] ? series(src + ">" + dst) : Array(n).fill(0);
  const tot = (src, dst) => pairs[src + ">" + dst] ? pairs[src + ">" + dst].total : 0;
  $("#charts").innerHTML = lk.length ? lk.map((x, i) => `<div class="card"><div class="spread"><h2>${esc(name(x.a))} ⇄ ${esc(name(x.b))}</h2>
      <div class="legend" style="margin:0"><span><span class="dot" style="background:var(--accent)"></span>${esc(name(x.a))} → ${esc(name(x.b))}: <b>${tot(x.a, x.b)}</b></span>
      <span><span class="dot" style="background:var(--info)"></span>${esc(name(x.b))} → ${esc(name(x.a))}: <b>${tot(x.b, x.a)}</b></span></div></div>
      <div class="chart" id="ch${i}"></div></div>`).join("") : `<div class="card muted">${t("stats.none")}</div>`;
  lk.forEach((x, i) => splitBarChart($("#ch" + i), labels, ser(x.a, x.b), ser(x.b, x.a),
                                      [name(x.a) + " → " + name(x.b), name(x.b) + " → " + name(x.a)]));
}

function pageJoin() {
  const host = location.hostname;
  app().innerHTML = `<div class="grid g2"><div class="card"><h1>${t("join.title")}</h1><p>${t("join.intro")}</p>
      <p><a class="btn primary" href="${esc(INFO.install_guide_url)}" target="_blank" rel="noopener">${t("join.guide")}</a>
         <a class="btn" href="${esc(INFO.project_url)}" target="_blank" rel="noopener">${t("join.project")}</a></p>
      ${INFO.registrations_open ? "" : `<div class="msg warn">${t("join.closed")}</div>`}
      <ol class="steps"><li>${t("join.s1")}</li><li>${t("join.s2")}</li><li>${t("join.s3")}</li><li>${t("join.s4")}</li><li>${t("join.s5")}</li></ol>
      <p class="muted small">${t("join.email_note")}</p></div>
    <div class="card"><h2>${t("join.server")}</h2><dl class="kv">
      <dt>${t("join.address")}</dt><dd class="mono">${esc(host)}:${INFO.hub_port}</dd>
      <dt>${t("join.fp")}</dt><dd class="mono small">${esc(INFO.fingerprint)}</dd>
      <dt>${t("hub.version")}</dt><dd>${esc(INFO.version)}</dd></dl></div></div>`;
}

function cStatus(s) { const c = { open: "warn", review: "info", resolved: "ok", rejected: "bad" }[s] || ""; return `<span class="badge ${c}">${t("c.st." + s)}</span>`; }

async function pageComplaints() {
  const qs = new URLSearchParams(location.hash.split("?")[1] || "");
  const pre = qs.get("hub") ? ["hub", qs.get("hub")] : qs.get("node") ? ["node", qs.get("node")] : ["general", ""];
  const list = await api("GET", "/api/public/complaints");
  app().innerHTML = `<div class="grid g2">
    <div class="card"><h1>${t("c.title")}</h1><p>${t("c.intro")}</p><h2>${t("c.new")}</h2>
      <label>${t("c.about")}</label><select id="cst"><option value="general">${t("c.general")}</option><option value="hub">${t("hub")}</option><option value="node">${t("c.node")}</option></select>
      <label>${t("c.subject")}</label><input type="text" id="csi" value="${esc(pre[1])}">
      <label>${t("c.email")}</label><input type="email" id="cem">
      <label>${t("c.text")}</label><textarea id="ctx"></textarea>
      <div id="cmsg"></div><button class="primary" id="csend">${t("c.send")}</button></div>
    <div class="card"><h2>${t("c.list")}</h2>${list.length ? list.map(c => `<div class="card" style="box-shadow:none">
      <div class="spread"><b>${t("c.case")} #${c.id}</b>${cStatus(c.status)}</div>
      <div class="muted small">${dt(c.created)} · ${esc(c.subject_type)} ${esc(c.subject_id || "")}</div>
      <p>${esc(c.text)}</p>${c.resolution ? `<div class="msg info"><b>${t("c.resolution")}:</b> ${esc(c.resolution)}</div>` : ""}</div>`).join("") : `<p class="muted">${t("c.none")}</p>`}</div></div>`;
  $("#cst").value = pre[0];
  $("#csend").onclick = async () => {
    try {
      const r = await api("POST", "/api/public/complaints", { subject_type: $("#cst").value, subject_id: $("#csi").value, email: $("#cem").value, text: $("#ctx").value });
      $("#cmsg").innerHTML = `<div class="msg ok">${t("c.sent", { id: r.id })}</div>`; setTimeout(pageComplaints, 2500);
    } catch (e) { $("#cmsg").innerHTML = `<div class="msg bad">${t("err." + e.message, { n: INFO.complaint_min_chars }) !== "err." + e.message ? t("err." + e.message, { n: INFO.complaint_min_chars }) : esc(e.message)}</div>`; }
  };
}

async function pageAdmin() {
  INFO = await api("GET", "/api/public/info");
  adminBadge();
  if (INFO.setup_needed || !INFO.admin) {
    app().innerHTML = `<div class="center"><div class="card narrow"><h2>${INFO.setup_needed ? t("setup.title") : t("a.title")}</h2>
      <label>${t("password")}</label><input type="password" id="pw" autocomplete="current-password"><div class="hint">${t("password.min", { n: INFO.password_min })}</div>
      <div id="lmsg"></div><button class="primary" id="lbtn">${INFO.setup_needed ? t("setup.btn") : t("login")}</button></div></div>`;
    const go = async () => {
      try { await api("POST", INFO.setup_needed ? "/api/setup" : "/api/login", { password: $("#pw").value }); pageAdmin(); }
      catch (e) { $("#lmsg").innerHTML = `<div class="msg bad">${e.message === "wrong_password" ? t("password.wrong") : e.message === "locked" ? t("a.locked") : e.message === "password_short" ? t("password.short") : esc(e.message)}</div>`; }
    };
    $("#lbtn").onclick = go; $("#pw").onkeydown = e => { if (e.key === "Enter") go(); };
    return;
  }
  const s = await api("GET", "/api/admin/state");
  const pending = s.hubs.filter(h => h.status === "pending"), approved = s.hubs.filter(h => h.status === "approved");
  const hubRow = (h, act) => `<tr><td><b>${esc(h.code)}</b></td><td>${esc(h.name)}<div class="muted small">${esc(h.id)}</div></td>
     <td>${esc(h.email)}<div class="small">${h.email_verified ? `<span class="badge ok">${t("a.email_ok")}</span>` : `<span class="badge warn">${t("a.email_no")}</span>`}</div></td>
     <td>${fmtPos(h.lat, h.lon)}</td><td>${dt(h.created)}</td><td>${onlineBadge(h.online)}</td>
     <td class="row">${act ? `<button class="primary small" data-a="approve" data-id="${h.id}">${t("a.approve")}</button>` : ""}
       ${h.email_verified ? "" : `<button class="small" data-a="verify_email" data-id="${h.id}">${t("a.verify")}</button>`}
       <button class="danger small" data-a="remove" data-id="${h.id}" data-code="${esc(h.code)}">${t("a.remove")}</button></td></tr>`;
  const head = `<tr><th>${t("code")}</th><th>${t("name")}</th><th>${t("a.email")}</th><th>${t("position")}</th><th>${t("a.requested")}</th><th>${t("status")}</th><th></th></tr>`;
  app().innerHTML = `<div class="spread"><h1>${t("a.title")}</h1><button id="lo">${t("logout")}</button></div>
    <div class="card"><h2>${t("a.pending")} (${pending.length})</h2><div class="tablewrap"><table>${head}${pending.map(h => hubRow(h, true)).join("") || `<tr><td colspan="7" class="muted">${t("a.nopending")}</td></tr>`}</table></div></div>
    <div class="card"><h2>${t("a.approved")} (${approved.length})</h2><div class="tablewrap"><table>${head}${approved.map(h => hubRow(h, false)).join("")}</table></div></div>
    <div class="card"><h2>${t("a.complaints")}</h2>${s.complaints.map(c => `<div class="card" style="box-shadow:none">
      <div class="spread"><b>#${c.id}</b>${cStatus(c.status)}</div><div class="muted small">${dt(c.created)} · ${esc(c.email)} · ${esc(c.subject_type)} ${esc(c.subject_id || "")}</div>
      <p>${esc(c.text)}</p><div class="row"><select data-cs="${c.id}">${["open", "review", "resolved", "rejected"].map(x => `<option value="${x}" ${x === c.status ? "selected" : ""}>${t("c.st." + x)}</option>`).join("")}</select></div>
      <label>${t("c.resolution")}</label><textarea data-cr="${c.id}" style="min-height:60px">${esc(c.resolution || "")}</textarea>
      <button class="small" data-csave="${c.id}">${t("a.set_status")}</button></div>`).join("") || `<p class="muted">${t("c.none")}</p>`}</div>
    <div class="card narrow"><h2>${t("a.change_pw")}</h2><input type="password" id="npw"><div class="hint">${t("password.min", { n: INFO.password_min })}</div><div id="pmsg"></div><button id="pbtn">${t("save")}</button></div>
    <div class="card"><h2>${t("le.title")}</h2><p class="muted small">${t("le.hint")}</p>
      <p>${t("status")}: <b>${t("le.st." + (s.acme.state || "off"))}</b> ${s.acme.detail ? `<span class="muted small">— ${esc(s.acme.detail)}</span>` : ""}</p>
      ${s.acme.cert ? `<p class="small">${t("le.cert", { i: esc(s.acme.cert.issuer), d: s.acme.cert.days_left })}</p>` : ""}
      <button id="lerun">${t("le.run")}</button> <span class="muted small" id="lemsg"></span></div>
    <div class="card"><h2>${t("adv.title")}</h2><p class="muted small">${t("adv.intro")}</p><div id="advform"></div><div id="advmsg"></div><button class="primary" id="advsave">${t("save")}</button></div>`;
  $("#lerun").onclick = async () => { await api("POST", "/api/admin/acme/run", {}); $("#lemsg").textContent = t("le.started"); setTimeout(pageAdmin, 20000); };
  const af = advancedForm($("#advform"), s.advanced_spec, s.advanced, {
    groups: [["adv.g.reg", ["registrations_open", "project_url", "install_guide_url"]],
             ["adv.g.cert", ["acme_enabled", "acme_domain", "acme_email", "acme_staging"]],
             ["adv.g.traffic", ["node_max_age_days", "max_nodes_per_report", "relay_rate_per_s", "relay_burst", "max_box_bytes", "stats_retention_days"]],
             ["adv.g.complaints", ["complaints_per_hour", "complaint_min_chars", "complaint_max_chars"]],
             ["adv.g.security", ["session_hours", "lockout_attempts", "lockout_minutes", "password_min"]],
             ["adv.g.tiles", ["tile_upstream", "tile_contact", "tile_cache_days", "tile_backoff_s"]]],
    depends: { acme_domain: "acme_enabled", acme_email: "acme_enabled", acme_staging: "acme_enabled" } });
  $("#advsave").onclick = async () => {
    try { await api("POST", "/api/admin/advanced", { advanced: af.read() }); af.mark([]); INFO = {}; $("#advmsg").innerHTML = `<div class="msg ok">${t("saved")}</div>`; }
    catch (e) { af.mark((e.data && e.data.fields) || []); $("#advmsg").innerHTML = `<div class="msg bad">${t("adv.invalid")}</div>`; }
  };
  $("#lo").onclick = async () => { await api("POST", "/api/logout", {}); pageAdmin(); };
  $$("button[data-a]").forEach(b => b.onclick = async () => {
    if (b.dataset.a === "remove" && !confirm(t("a.remove_q", { x: b.dataset.code }))) return;
    b.disabled = true; b.textContent = "…";
    await api("POST", `/api/admin/hub/${b.dataset.id}/${b.dataset.a}`, {}); pageAdmin();
  });
  $$("button[data-csave]").forEach(b => b.onclick = async () => {
    const id = b.dataset.csave; b.disabled = true;
    await api("POST", "/api/admin/complaint/" + id, { status: $(`select[data-cs="${id}"]`).value, resolution: $(`textarea[data-cr="${id}"]`).value });
    b.textContent = "✓ " + t("saved"); b.disabled = false;
  });
  $("#pbtn").onclick = async () => {
    try { await api("POST", "/api/admin/password", { password: $("#npw").value }); $("#pmsg").innerHTML = `<div class="msg ok">${t("saved")}</div>`; }
    catch (e) { $("#pmsg").innerHTML = `<div class="msg bad">${t("password.min", { n: INFO.password_min })}</div>`; }
  };
}

/* ───────── router ───────── */

/* Admin menu badge: hubs waiting for approval (shown only to a logged-in administrator). */
function adminBadge() {
  const a = document.querySelector('nav.menu a[href="#/admin"]');
  if (!a) return;
  a.querySelectorAll(".mbadge").forEach(x => x.remove());
  if (INFO.pending) a.insertAdjacentHTML("beforeend", ` <span class="badge warn mbadge" title="${esc(t("a.pending"))}">${INFO.pending}</span>`);
}
setInterval(async () => { try { if (!document.hidden && INFO.admin) { INFO = await api("GET", "/api/public/info"); adminBadge(); } } catch (e) {} }, 60000);

async function route() {
  renderHeader(t("site.title"), MENU);
  if (mapObj) { mapObj.remove(); mapObj = null; }
  const parts = location.hash.replace(/^#\/?/, "").split("?")[0].split("/").map(decodeURIComponent);
  app().innerHTML = `<p class="muted">${t("loading")}</p>`;
  try {
    INFO = await api("GET", "/api/public/info");          // fresh on every page: admin state + waiting hubs
    adminBadge();
    $("#foot").innerHTML = (location.hash.replace(/^#\/?/, "") === "") ? "" :
      esc(t("foot")) + (INFO.project_url ? ` · <a href="${esc(INFO.project_url)}" target="_blank" rel="noopener">${t("foot.project")}</a>` : "");
    switch (parts[0]) {
      case "": return await pageMap();
      case "hubs": return await pageHubs();
      case "hub": return await pageHub(parts[1]);
      case "node": return await pageNode(parts[1], parts[2], parts.slice(3).join("/"));
      case "stats": return await pageStats();
      case "join": return pageJoin();
      case "complaints": return await pageComplaints();
      case "admin": return await pageAdmin();
      default: app().innerHTML = `<div class="card">${t("notfound")}</div>`;
    }
  } catch (e) { app().innerHTML = `<div class="card msg bad">${t("error")}: ${esc(e.message)}</div>`; }
}
Ura.onLang = route;
window.addEventListener("hashchange", route);
document.documentElement.lang = Ura.lang;
route();
