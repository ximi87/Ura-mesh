/* ura-hub website (owner only) */
"use strict";

Ura.add({
  "site.hub": { en: "hub", sq: "hub" },
  "nav.status": { en: "Status", sq: "Gjendja" }, "nav.links": { en: "Links & rules", sq: "Lidhjet & rregullat" },
  "nav.radio": { en: "Radio", sq: "Radio" }, "nav.settings": { en: "Settings", sq: "Cilësimet" },
  "foot.hub": { en: "This page belongs to this hub only. The Ura server cannot change anything here; every rule is decided by you.",
                sq: "Kjo faqe i përket vetëm këtij hub-i. Serveri Ura nuk mund të ndryshojë asgjë këtu; çdo rregull vendoset nga ju." },
  "login.title": { en: "Ura hub – log in", sq: "Ura hub – hyrja" },
  "st.hub": { en: "This hub", sq: "Ky hub" }, "st.server": { en: "Server connection", sq: "Lidhja me serverin" },
  "st.radio": { en: "Radio", sq: "Radio" }, "st.traffic": { en: "Traffic since start", sq: "Trafiku që nga nisja" },
  "st.airtime": { en: "Airtime used by remote packets", sq: "Koha në ajër e përdorur nga paketat e largëta" },
  "st.heard": { en: "Heard by radio", sq: "Dëgjuar nga radio" }, "st.uplinked": { en: "Given to hub", sq: "Dhënë hub-it" },
  "st.sent": { en: "Sent to linked hubs", sq: "Dërguar te hub-et e lidhur" }, "st.received": { en: "Received from hubs", sq: "Marrë nga hub-et" },
  "st.to_radio": { en: "Put on air", sq: "Nxjerrë në ajër" },
  "st.hour": { en: "last hour", sq: "ora e fundit" }, "st.day": { en: "last 24 h", sq: "24 orët e fundit" },
  "st.limit": { en: "limit {x}", sq: "kufiri {x}" }, "st.nolimit": { en: "no limit", sq: "pa kufi" },
  "st.nodes": { en: "Nodes in the radio", sq: "Nyjet në radio" },
  "st.nodes.hint": { en: "Local nodes are sent to the Ura map. Remote nodes came from linked hubs.", sq: "Nyjet lokale dërgohen në hartën e Ura. Nyjet në distancë erdhën nga hub-et e lidhur." },
  "st.announce": { en: "Announce this radio now", sq: "Njofto këtë radio tani" },
  "st.ask": { en: "Ask neighbours to answer", sq: "Kërkoju fqinjëve të përgjigjen" },
  "st.announced": { en: "Sent.", sq: "U dërgua." },
  "srv.not_configured": { en: "not set up — go to Settings", sq: "e pakonfiguruar — shkoni te Cilësimet" },
  "srv.connecting": { en: "connecting…", sq: "duke u lidhur…" }, "srv.connected": { en: "connected", sq: "e lidhur" },
  "srv.disconnected": { en: "disconnected", sq: "e shkëputur" }, "srv.error": { en: "error", sq: "gabim" },
  "srv.refused": { en: "refused by server", sq: "refuzuar nga serveri" },
  "srv.fingerprint_mismatch": { en: "certificate changed! Check it in Settings.", sq: "certifikata ka ndryshuar! Kontrollojeni te Cilësimet." },
  "reg.pending": { en: "waiting for the administrator's approval", sq: "në pritje të miratimit nga administratori" },
  "reg.approved": { en: "approved", sq: "miratuar" }, "reg.removed": { en: "removed by the administrator", sq: "hequr nga administratori" },
  "reg.none": { en: "not registered", sq: "i paregjistruar" },
  "l.dir": { en: "Other hubs on the server", sq: "Hub-et e tjera në server" },
  "l.dir.none": { en: "No other approved hub yet.", sq: "Ende nuk ka hub tjetër të miratuar." },
  "l.ask": { en: "Ask for a link", sq: "Kërko lidhje" }, "l.accept": { en: "Accept", sq: "Prano" },
  "l.remove": { en: "End link", sq: "Mbyll lidhjen" }, "l.decline": { en: "Decline", sq: "Refuzo" },
  "l.mylinks": { en: "My links", sq: "Lidhjet e mia" }, "l.none": { en: "No links yet.", sq: "Ende nuk ka lidhje." },
  "l.state.active": { en: "active", sq: "aktive" }, "l.state.pending": { en: "waiting", sq: "në pritje" },
  "l.wait_peer": { en: "waiting for {x} to accept", sq: "në pritje që {x} të pranojë" },
  "l.wait_me": { en: "{x} asks to link with you", sq: "{x} kërkon të lidhet me ju" },
  "l.remove_q": { en: "End the link with {x}? Traffic stops immediately.", sq: "Ta mbyll lidhjen me {x}? Trafiku ndalon menjëherë." },
  "l.rules": { en: "My rules for this link", sq: "Rregullat e mia për këtë lidhje" },
  "l.rules.hint": { en: "“Send” = what this hub passes to {x}. “Receive” = what this hub lets onto the air from {x}. The other hub has its own rules too.",
                    sq: "“Dërgo” = çfarë kalon ky hub te {x}. “Merr” = çfarë lejon ky hub të dalë në ajër nga {x}. Hub-i tjetër ka gjithashtu rregullat e veta." },
  "l.link_on": { en: "Link open in this direction", sq: "Lidhja e hapur në këtë drejtim" },
  "l.public.hint": { en: "the default public channel ({x})", sq: "kanali publik i parazgjedhur ({x})" },
  "l.groups.hint": { en: "Other groups (channels) of your radio. A group crosses only if the other hub accepts it too.",
                     sq: "Grupet e tjera (kanalet) e radios suaj. Një grup kalon vetëm nëse e pranon edhe hub-i tjetër." },
  "l.nogroups": { en: "Your radio has no other channels.", sq: "Radio juaj nuk ka kanale të tjera." },
  "l.peer_rules": { en: "Rules of {x} for this link", sq: "Rregullat e {x} për këtë lidhje" },
  "rx.title": { en: "What the radio hears", sq: "Çfarë dëgjon radio" },
  "rx.none": { en: "The radio has not reported its reception yet (it does so every few minutes).", sq: "Radio ende nuk ka raportuar marrjen (e bën çdo disa minuta)." },
  "rx.rx": { en: "Packets received", sq: "Paketa të marra" }, "rx.bad": { en: "Unreadable packets", sq: "Paketa të palexueshme" },
  "rx.chutil": { en: "Channel busy", sq: "Kanali i zënë" }, "rx.airtx": { en: "Own transmit time", sq: "Koha e vet e transmetimit" },
  "rx.online": { en: "{n} of {m} known nodes active in the last 2 hours", sq: "{n} nga {m} nyje të njohura aktive në 2 orët e fundit" },
  "rx.chutil.hint": { en: "“Channel busy” counts every LoRa signal the radio picks up on its frequency, including ones it cannot decode (other networks, other settings, noise).",
                      sq: "“Kanali i zënë” numëron çdo sinjal LoRa që radio kap në frekuencën e saj, përfshirë ato që nuk mund t'i deshifrojë (rrjete të tjera, cilësime të tjera, zhurmë)." },
  "rx.updated": { en: "updated", sq: "përditësuar" },
  "rx.deaf": { en: "The radio has received nothing since it started. Nobody is in range: place it higher (roof, window) or use a better antenna.",
               sq: "Radio nuk ka marrë asgjë që kur u ndez. Askush nuk është në rreze: vendoseni më lart (çati, dritare) ose përdorni një antenë më të mirë." },
  "nl.local": { en: "Heard here", sq: "Dëgjuar këtu" },
  "nl.local.hint": { en: "Nodes this radio heard itself over LoRa in the last 7 days. These are the nodes of this area; only they are sent to the Ura map.",
                     sq: "Nyjet që kjo radio i ka dëgjuar vetë përmes LoRa në 7 ditët e fundit. Këto janë nyjet e kësaj zone; vetëm ato dërgohen në hartën e Ura." },
  "nl.show_old": { en: "show {n} older / without time", sq: "shfaq {n} më të vjetra / pa kohë" },
  "nl.none_local": { en: "No node heard in the last 7 days.", sq: "Asnjë nyje e dëgjuar në 7 ditët e fundit." },
  "nl.nopos": { en: "no position set", sq: "pa pozicion" },
  "nl.remote": { en: "From linked hubs", sq: "Nga hub-et e lidhur" },
  "nl.remote.hint": { en: "Nodes that reached this radio through Ura, grouped by the hub that heard them.", sq: "Nyjet që arritën te kjo radio përmes Ura, të grupuara sipas hub-it që i dëgjoi." },
  "nl.unknown": { en: "Via bridge (origin not known, e.g. older tests)", sq: "Përmes urës (origjina e panjohur, p.sh. teste më të vjetra)" },
  "e2e.title": { en: "End-to-end encryption", sq: "Enkriptimi skaj-më-skaj" },
  "e2e.ok": { en: "🔒 Everything on this link is sealed between the two hubs. The server only passes on boxes it cannot open.",
              sq: "🔒 Gjithçka në këtë lidhje është e mbyllur ndërmjet dy hub-eve. Serveri vetëm kalon kuti që nuk mund t'i hapë." },
  "e2e.code": { en: "Safety code", sq: "Kodi i sigurisë" },
  "e2e.code.hint": { en: "Compare this code with the operator of {x} (phone, chat). If it is the same on both hubs, nobody — not even the server — sits in between.",
                     sq: "Krahasojeni këtë kod me operatorin e {x} (telefon, chat). Nëse është i njëjtë në të dy hub-et, askush — as serveri — nuk ndodhet në mes." },
  "e2e.changed": { en: "⚠️ The key of {x} has CHANGED. Traffic is stopped. This happens when that hub was reinstalled — or when someone tries to sit in between. Call the operator, compare the new safety code, and only then trust it.",
                   sq: "⚠️ Çelësi i {x} ka NDRYSHUAR. Trafiku është ndalur. Kjo ndodh kur ai hub është riinstaluar — ose kur dikush përpiqet të futet në mes. Telefononi operatorin, krahasoni kodin e ri të sigurisë dhe vetëm atëherë besojeni." },
  "e2e.trust": { en: "Codes match – trust the new key", sq: "Kodet përputhen – beso çelësin e ri" },
  "e2e.missing": { en: "⚠️ {x} has no end-to-end key yet (older software). Nothing is sent to it until it is updated.",
                   sq: "⚠️ {x} ende nuk ka çelës skaj-më-skaj (program më i vjetër). Asgjë nuk i dërgohet derisa të përditësohet." },
  "why.key_missing": { en: "no end-to-end key", sq: "pa çelës skaj-më-skaj" }, "why.key_changed": { en: "key changed", sq: "çelësi ndryshoi" },
  "why.bad_box": { en: "box could not be opened", sq: "kutia nuk u hap" },
  "err.locked": { en: "Too many wrong passwords. Try again in 15 minutes.", sq: "Shumë fjalëkalime të gabuara. Provoni përsëri pas 15 minutash." },
  "l.peer_rules.none": { en: "Not published yet.", sq: "Ende të papublikuara." },
  "l.counts": { en: "Traffic since start", sq: "Trafiku që nga nisja" },
  "l.blocked": { en: "stopped by rules", sq: "ndaluar nga rregullat" },
  "why.link_off": { en: "direction off", sq: "drejtimi joaktiv" }, "why.public": { en: "public group", sq: "grupi publik" },
  "why.group": { en: "group not allowed", sq: "grup i palejuar" }, "why.private": { en: "private message", sq: "mesazh privat" },
  "why.positions": { en: "position", sq: "pozicion" }, "why.airtime": { en: "airtime limit", sq: "kufiri i kohës në ajër" },
  "why.no_radio": { en: "radio not connected", sq: "radio e palidhur" }, "why.invalid": { en: "invalid packet", sq: "paketë e pavlefshme" },
  "l.not_connected": { en: "The hub is not connected to an approved server yet.", sq: "Hub-i ende nuk është i lidhur me një server që e ka miratuar." },
  "r.title": { en: "Radio connection", sq: "Lidhja e radios" }, "r.type": { en: "Radio type", sq: "Lloji i radios" },
  "r.transport": { en: "Connection", sq: "Lidhja" }, "r.serial": { en: "USB (serial)", sq: "USB (serial)" },
  "r.tcp": { en: "Wi-Fi / IP", sq: "Wi-Fi / IP" }, "r.ble": { en: "Bluetooth (not supported yet)", sq: "Bluetooth (ende e pambështetur)" },
  "r.port": { en: "USB port", sq: "Porta USB" }, "r.host": { en: "Address (IP or host[:port])", sq: "Adresa (IP ose host[:portë])" },
  "r.detected": { en: "Detected ports", sq: "Portat e gjetura" }, "r.none_detected": { en: "No USB radio found.", sq: "Nuk u gjet asnjë radio USB." },
  "r.mc_soon": { en: "MeshCore support comes next.", sq: "Mbështetja për MeshCore vjen së shpejti." },
  "r.state": { en: "Radio status", sq: "Gjendja e radios" }, "r.connected": { en: "connected", sq: "e lidhur" },
  "r.not_connected": { en: "not connected", sq: "e palidhur" }, "r.firmware": { en: "Firmware", sq: "Firmware" },
  "r.preset": { en: "LoRa preset", sq: "Preset LoRa" }, "r.region": { en: "Region", sq: "Rajoni" },
  "r.channels": { en: "Channels (groups)", sq: "Kanalet (grupet)" }, "r.public": { en: "public", sq: "publik" },
  "r.private_ch": { en: "private", sq: "privat" },
  "r.ready": { en: "Ready for Ura", sq: "Gati për Ura" }, "r.not_ready": { en: "Not ready for Ura", sq: "Jo gati për Ura" },
  "r.prepare": { en: "Prepare radio for Ura", sq: "Përgatit radion për Ura" },
  "r.prepare_q": { en: "The radio will be configured for Ura and restart (about 30 s). Continue?", sq: "Radio do të konfigurohet për Ura dhe do të rindizet (rreth 30 s). Të vazhdoj?" },
  "r.prepared": { en: "Done. The radio restarts now and reconnects by itself.", sq: "U krye. Radio po rindizet dhe do të rilidhet vetë." },
  "r.fw_note": { en: "The hub radio needs the Ura firmware patch so that remote packets go on air as normal packets (otherwise nodes with “Ignore MQTT” drop them).",
                 sq: "Radio e hub-it ka nevojë për patch-in e firmware-it Ura që paketat e largëta të dalin në ajër si paketa normale (përndryshe nyjet me “Ignore MQTT” i hedhin poshtë)." },
  "chk.mqtt_enabled": { en: "MQTT on", sq: "MQTT aktiv" }, "chk.proxy_to_client": { en: "MQTT through the hub (client proxy)", sq: "MQTT përmes hub-it (client proxy)" },
  "chk.private_address": { en: "MQTT address private", sq: "Adresa MQTT private" }, "chk.encryption": { en: "Packets stay encrypted", sq: "Paketat mbeten të enkriptuara" },
  "chk.ignore_mqtt_off": { en: "“Ignore MQTT” off", sq: "“Ignore MQTT” joaktiv" }, "chk.channels_linked": { en: "Channels: uplink + downlink on", sq: "Kanalet: uplink + downlink aktiv" },
  "chk.debug_log_off": { en: "Radio debug log off", sq: "Regjistri i debug-ut joaktiv" },
  "s.hub": { en: "Hub details", sq: "Të dhënat e hub-it" },
  "s.name": { en: "Hub name", sq: "Emri i hub-it" }, "s.email": { en: "Your e-mail address", sq: "Adresa juaj e e-mail-it" },
  "s.country": { en: "Country code (2–3 letters)", sq: "Kodi i shtetit (2–3 shkronja)" }, "s.city": { en: "Place code (2–3 letters)", sq: "Kodi i vendit (2–3 shkronja)" },
  "s.lat": { en: "Latitude", sq: "Gjerësia gjeografike" }, "s.lon": { en: "Longitude", sq: "Gjatësia gjeografike" },
  "s.desc": { en: "Description (public)", sq: "Përshkrimi (publik)" },
  "s.locked": { en: "Registered details are kept by the server. To change them, ask the administrator.", sq: "Të dhënat e regjistruara ruhen nga serveri. Për t'i ndryshuar, pyesni administratorin." },
  "s.server": { en: "Ura server", sq: "Serveri Ura" }, "s.address": { en: "Server address (host:port)", sq: "Adresa e serverit (host:portë)" },
  "s.check": { en: "Check server", sq: "Kontrollo serverin" }, "s.fp": { en: "Certificate fingerprint", sq: "Gjurma e certifikatës" },
  "s.fp_hint": { en: "Compare it with the fingerprint shown on the server's “Register a hub” page. Trust it only if they match.",
                 sq: "Krahasojeni me gjurmën që shfaqet në faqen “Regjistro një hub” të serverit. Besojeni vetëm nëse përputhen." },
  "s.trust": { en: "Fingerprint matches – trust this server", sq: "Gjurma përputhet – besoje këtë server" },
  "s.trusted": { en: "Trusted fingerprint", sq: "Gjurma e besuar" },
  "s.join": { en: "Send registration request", sq: "Dërgo kërkesën për regjistrim" },
  "s.joined": { en: "Request sent. Hub id {x}. Waiting for approval.", sq: "Kërkesa u dërgua. ID e hub-it {x}. Në pritje të miratimit." },
  "s.registration": { en: "Registration", sq: "Regjistrimi" },
  "s.forget": { en: "Forget registration", sq: "Harro regjistrimin" },
  "s.forget_q": { en: "Forget this hub's registration on the server? You would need to register again.", sq: "Ta harroj regjistrimin e këtij hub-i në server? Do t'ju duhet të regjistroheni përsëri." },
  "loc.title": { en: "Location of this hub", sq: "Vendndodhja e këtij hub-i" },
  "loc.hint": { en: "Where the hub is shown on the Ura map. It should be where the radio is.", sq: "Ku shfaqet hub-i në hartën e Ura. Duhet të jetë aty ku ndodhet radio." },
  "loc.radio": { en: "Take the position from the radio automatically (follows it if it moves)", sq: "Merre pozicionin nga radio automatikisht (e ndjek nëse lëviz)" },
  "loc.manual": { en: "Enter the position manually", sq: "Vendose pozicionin manualisht" },
  "loc.radio_pos": { en: "Position reported by the radio", sq: "Pozicioni i raportuar nga radio" },
  "loc.use": { en: "Use it", sq: "Përdore" },
  "loc.no_radio_pos": { en: "none — the radio has no GPS fix and no fixed position. Set a fixed position on the radio, or enter one manually here.",
                        sq: "asnjë — radio nuk ka sinjal GPS dhe as pozicion fiks. Vendosni një pozicion fiks në radio ose shkruajeni manualisht këtu." },
  "nc.title": { en: "Nodes", sq: "Nyjet" },
  "nc.map": { en: "On the Ura map", sq: "Në hartën e Ura" }, "nc.map.hint": { en: "heard here in the last 7 days, incl. this radio — same number as on the server", sq: "dëgjuar këtu në 7 ditët e fundit, përfshirë këtë radio — i njëjti numër si në server" },
  "nc.remote": { en: "From linked hubs", sq: "Nga hub-et e lidhur" },
  "nc.memory": { en: "In the radio's memory", sq: "Në kujtesën e radios" }, "nc.memory.hint": { en: "everything the radio remembers, incl. {n} older or without time", sq: "gjithçka që radio mban mend, përfshirë {n} më të vjetra ose pa kohë" },
  "s.limits": { en: "Airtime and sharing", sq: "Koha në ajër dhe ndarja" },
  "s.air_hour": { en: "Max. airtime for remote packets, % of each hour (0 = no limit)", sq: "Koha maksimale në ajër për paketat e largëta, % e çdo ore (0 = pa kufi)" },
  "s.air_day": { en: "Max. airtime, % of each day (0 = no limit)", sq: "Koha maksimale në ajër, % e çdo dite (0 = pa kufi)" },
  "s.air_hint": { en: "EU 868 MHz: the legal duty cycle is 1% or 10% depending on the sub-band. Remote packets above the limit are not put on air.",
                  sq: "BE 868 MHz: cikli ligjor i punës është 1% ose 10% sipas nën-brezit. Paketat e largëta mbi kufi nuk nxirren në ajër." },
  "s.share_pos": { en: "Show my nodes' positions on the public Ura map", sq: "Shfaq pozicionet e nyjeve të mia në hartën publike të Ura" },
  "s.defaults": { en: "Default rules for new links", sq: "Rregullat e parazgjedhura për lidhjet e reja" },
  "s.password": { en: "Change hub password", sq: "Ndrysho fjalëkalimin e hub-it" },
  "err.code_taken": { en: "This country/place code is already used by another hub.", sq: "Ky kod shteti/vendi përdoret tashmë nga një hub tjetër." },
  "err.code_invalid": { en: "Country and place code must be 2–3 letters each.", sq: "Kodi i shtetit dhe i vendit duhet të jenë 2–3 shkronja secili." },
  "err.email_required": { en: "A valid e-mail address is required.", sq: "Nevojitet një adresë e vlefshme e-mail-i." },
  "err.name_required": { en: "Please enter a hub name.", sq: "Ju lutem vendosni një emër për hub-in." },
  "err.not_connected": { en: "Not connected to the server.", sq: "Nuk jeni të lidhur me serverin." },
  "err.no_radio": { en: "No radio connected.", sq: "Asnjë radio e lidhur." },
  "err.address_required": { en: "Please enter the server address.", sq: "Ju lutem vendosni adresën e serverit." },
});

const MENU = [["#/", "nav.status"], ["#/links", "nav.links"], ["#/radio", "nav.radio"], ["#/settings", "nav.settings"]];
const app = () => document.getElementById("app");
let mapObj = null, timer = null;

function errText(e) { const k = "err." + e.message; return t(k) !== k ? t(k) : esc(e.message); }
function srvState(s) { return `srv.${s.link_state}`; }
function regText(st) { return st ? t("reg." + st) : t("reg.none"); }
function ruleRow(lbl, dir, key, rule) { return `<label class="check"><input type="checkbox" data-dir="${dir}" data-k="${key}" ${rule[key] ? "checked" : ""}> ${lbl}</label>`; }

/* ───────── status ───────── */
const LOCAL_COLOR = "#0f7b6c";
const REMOTE_COLORS = ["#2a56c6", "#c2410c", "#7c3aed", "#b91c1c", "#0e7490", "#a16207", "#be185d"];
const WEEK = 7 * 86400;
let showOld = false;

function receptionHtml(st) {
  if (!st || !st.time) return `<p class="muted">${t("rx.none")}</p>`;
  const v = (x, suf) => x == null ? "–" : (typeof x === "number" ? (Number.isInteger(x) ? x : x.toFixed(1)) : x) + (suf || "");
  const box = (x, lbl, suf) => x == null ? "" : `<div class="stat"><div class="v">${v(x, suf)}</div><div class="l">${t(lbl)}</div></div>`;
  return `<div class="grid g4">${box(st.numPacketsRx, "rx.rx")}${box(st.numPacketsRxBad, "rx.bad")}${box(st.channelUtilization, "rx.chutil", " %")}${box(st.airUtilTx, "rx.airtx", " %")}</div>
    <p class="muted small">${st.numOnlineNodes != null ? t("rx.online", { n: v(st.numOnlineNodes), m: v(st.numTotalNodes) }) + " · " : ""}${t("rx.updated")} ${ago(st.time)}</p>
    <p class="muted small">${t("rx.chutil.hint")}</p>
    ${st.numPacketsRx === 0 ? `<div class="msg warn">${t("rx.deaf")}</div>` : ""}`;
}

async function pageStatus() {
  const s = await api("GET", "/api/status");
  const nodes = await api("GET", "/api/nodes");
  const g = s.counters.global, r = s.radio, a = s.airtime;
  const pct = (used, win) => (100 * used / win).toFixed(2) + " %";
  const srvBadge = s.link_state === "connected" ? "ok" : (s.link_state === "connecting" ? "warn" : "bad");
  const now = Date.now() / 1000;
  const own = nodes.find(n => n.own);
  const localAll = nodes.filter(n => !n.own && !n.remote);
  const localRecent = localAll.filter(n => n.last_heard && now - n.last_heard < WEEK);
  const local = (showOld ? localAll : localRecent).sort((x, y) => (y.last_heard || 0) - (x.last_heard || 0));
  const hidden = localAll.length - localRecent.length;
  const codeOf = id => { const h = s.directory.find(x => x.id === id); return h ? h.code + " · " + h.name : null; };
  const groups = {};
  nodes.filter(n => n.remote).forEach(n => { const k = n.origin && codeOf(n.origin) ? n.origin : "?"; (groups[k] = groups[k] || []).push(n); });
  const gkeys = Object.keys(groups).sort((x, y) => (x === "?") - (y === "?"));
  const color = {}; gkeys.forEach((k, i) => color[k] = k === "?" ? "#8a8f98" : REMOTE_COLORS[i % REMOTE_COLORS.length]);
  const row = n => `<tr><td>${esc(n.name || "–")} <span class="muted">${esc(n.short || "")}</span></td><td class="mono small">${esc(n.id)}</td>
      <td>${ago(n.last_heard)}</td><td>${n.hops != null ? n.hops : "–"}</td><td>${n.snr != null ? n.snr + " dB" : "–"}</td><td>${n.lat != null ? "📍" : ""}</td></tr>`;
  const head = `<tr><th>${t("name")}</th><th>${t("id")}</th><th>${t("last_heard")}</th><th>${t("hops")}</th><th>SNR</th><th></th></tr>`;
  app().innerHTML = `
    <div class="grid g3">
      <div class="card"><h2>${t("st.hub")}</h2><dl class="kv">
        <dt>${t("name")}</dt><dd><b>${esc(s.hub.name || "–")}</b></dd>
        <dt>${t("code")}</dt><dd>${s.hub.country && s.hub.city ? esc(s.hub.country + "-" + s.hub.city) : "–"}</dd>
        <dt>${t("s.registration")}</dt><dd>${regText(s.server.status)}</dd></dl></div>
      <div class="card"><h2>${t("st.server")}</h2><dl class="kv">
        <dt>${t("status")}</dt><dd><span class="badge ${srvBadge}">${t(srvState(s))}</span> <span class="muted small">${esc(s.link_detail || "")}</span></dd>
        <dt>${t("s.address")}</dt><dd class="mono">${esc(s.server.address || "–")}</dd>
        <dt>${t("links")}</dt><dd>${s.links.filter(l => l.state === "active").map(l => esc(l.peer_code) + (l.e2e && l.e2e.state === "ok" ? " 🔒" : " ⚠️")).join(", ") || t("none")}</dd></dl></div>
      <div class="card"><h2>${t("st.radio")}</h2>${r ? `<dl class="kv">
        <dt>${t("status")}</dt><dd>${r.connected ? `<span class="badge ok">${t("r.connected")}</span>` : `<span class="badge bad">${t("r.not_connected")}</span> <span class="muted small">${esc(r.error || "")}</span>`}</dd>
        <dt>${t("name")}</dt><dd>${esc(r.name || "–")} <span class="muted">${esc(r.short || "")}</span></dd>
        <dt>${t("r.firmware")}</dt><dd>${esc(r.firmware || "–")}</dd>
        <dt>${t("r.ready")}</dt><dd>${r.connected ? (r.ready ? `<span class="badge ok">${t("yes")}</span>` : `<a href="#/radio" class="badge warn">${t("r.not_ready")}</a>`) : "–"}</dd></dl>`
        : `<p class="muted">${t("err.no_radio")} <a href="#/radio">${t("nav.radio")} →</a></p>`}</div>
    </div>
    <div class="grid g4">
      <div class="stat"><div class="v">${g.heard}</div><div class="l">${t("st.heard")}</div></div>
      <div class="stat"><div class="v">${g.sent}</div><div class="l">${t("st.sent")}</div></div>
      <div class="stat"><div class="v">${g.received}</div><div class="l">${t("st.received")}</div></div>
      <div class="stat"><div class="v">${g.to_radio}</div><div class="l">${t("st.to_radio")}</div></div>
    </div>
    <div class="card" style="margin-top:1rem"><h2>${t("nc.title")}</h2><div class="grid g3">
      <div class="stat"><div class="v">${localRecent.length + (own ? 1 : 0)}</div><div class="l">${t("nc.map")}<br><span class="small">${t("nc.map.hint")}</span></div></div>
      <div class="stat"><div class="v">${nodes.filter(n => n.remote).length}</div><div class="l">${t("nc.remote")}</div></div>
      <div class="stat"><div class="v">${nodes.length}</div><div class="l">${t("nc.memory")}<br><span class="small">${t("nc.memory.hint", { n: hidden })}</span></div></div></div></div>
    <div class="grid g2">
      <div class="card"><h2>${t("rx.title")}</h2>${receptionHtml(s.radio_stats)}</div>
      <div class="card"><h2>${t("st.airtime")}</h2>
        <p>${t("st.hour")}: <b>${pct(a.used_hour, 3600)}</b> (${a.limits.pct_hour ? t("st.limit", { x: a.limits.pct_hour + " %" }) : t("st.nolimit")})<br>
           ${t("st.day")}: <b>${pct(a.used_day, 86400)}</b> (${a.limits.pct_day ? t("st.limit", { x: a.limits.pct_day + " %" }) : t("st.nolimit")})</p>
        <div class="row"><button id="ann">${t("st.announce")}</button><button id="ask">${t("st.ask")}</button><span id="annmsg" class="muted"></span></div></div>
    </div>
    <div class="card"><div id="map" class="minimap" style="height:440px"></div>
      <div class="legend"><span><span class="dot" style="background:${LOCAL_COLOR}"></span>${t("nl.local")}</span>
        ${gkeys.map(k => `<span><span class="dot" style="background:${color[k]}"></span>${esc(k === "?" ? t("nl.unknown") : codeOf(k))}</span>`).join("")}</div></div>
    <div class="grid g2">
      <div class="card"><div class="spread"><h2>${t("nl.local")} (${localRecent.length})</h2>
        ${hidden ? `<label class="check small"><input type="checkbox" id="showold" ${showOld ? "checked" : ""}> ${t("nl.show_old", { n: hidden })}</label>` : ""}</div>
        <p class="muted small">${t("nl.local.hint")}</p>
        ${own ? `<p class="small">${t("st.radio")}: <b>${esc(own.name || own.id)}</b> ${own.lat != null ? "📍" : `<span class="muted">(${t("nl.nopos")})</span>`}</p>` : ""}
        <div class="tablewrap"><table>${head}${local.map(row).join("") || `<tr><td colspan="6" class="muted">${t("nl.none_local")}</td></tr>`}</table></div></div>
      <div class="card"><h2>${t("nl.remote")} (${nodes.filter(n => n.remote).length})</h2>
        <p class="muted small">${t("nl.remote.hint")}</p>
        ${gkeys.length ? gkeys.map(k => `<h3><span class="dot" style="background:${color[k]}"></span>${esc(k === "?" ? t("nl.unknown") : codeOf(k))} (${groups[k].length})</h3>
          <div class="tablewrap"><table>${head}${groups[k].sort((x, y) => (y.last_heard || 0) - (x.last_heard || 0)).map(row).join("")}</table></div>`).join("")
          : `<p class="muted">${t("none")}</p>`}</div>
    </div>`;
  const b = [];
  mapObj = makeMap("map");
  const dot = (n, c, rad) => { if (n.lat == null) return; L.circleMarker([n.lat, n.lon], { radius: rad, color: "#fff", weight: 1.5, fillColor: c, fillOpacity: .95 })
      .bindPopup(`<b>${esc(n.name || n.id)}</b> ${esc(n.short || "")}<br>${t("last_heard")}: ${ago(n.last_heard)}`).addTo(mapObj); b.push([n.lat, n.lon]); };
  local.forEach(n => dot(n, LOCAL_COLOR, 6));
  gkeys.forEach(k => groups[k].forEach(n => dot(n, color[k], 6)));
  if (own) dot(own, LOCAL_COLOR, 10);
  if (b.length) mapObj.fitBounds(b, { padding: [30, 30], maxZoom: 12 });
  if ($("#showold")) $("#showold").onchange = e => { showOld = e.target.checked; if (mapObj) { mapObj.remove(); mapObj = null; } pageStatus(); };
  const ann = async ask => { try { await api("POST", "/api/radio/announce", { ask }); $("#annmsg").textContent = t("st.announced"); } catch (e) { $("#annmsg").textContent = errText(e); } };
  $("#ann").onclick = () => ann(false); $("#ask").onclick = () => ann(true);
}

/* ───────── links ───────── */
async function pageLinks() {
  const s = await api("GET", "/api/status");
  const c = await api("GET", "/api/config");
  const r = s.radio || {};
  const chans = (r.channels || []);
  const pubName = (chans.find(x => x.public) || {}).name || "LongFast";
  const groups = chans.filter(x => !x.public).map(x => x.name);
  const ok = s.link_state === "connected" && s.server.status === "approved";
  const linked = new Set(s.links.map(l => l.peer));
  const others = s.directory.filter(h => h.id !== s.server.hub_id);
  const peerCounts = s.counters.peers;
  const rulesOf = peer => { const x = c.rules[peer] || c.defaults; return { send: Object.assign({}, x.send), receive: Object.assign({}, x.receive) }; };
  const dirCol = (peer, dir, rule) => `<div><h3>${t(dir === "send" ? "rule.send" : "rule.receive")}</h3>
      ${ruleRow(t("l.link_on"), dir, "on", rule)}
      ${ruleRow(t("rule.public") + ` <span class="muted small">${t("l.public.hint", { x: esc(pubName) })}</span>`, dir, "public", rule)}
      ${ruleRow(t("rule.private"), dir, "private", rule)}
      ${ruleRow(t("rule.positions"), dir, "positions", rule)}
      <div class="small muted" style="margin-top:.4rem">${t("rule.groups")}</div>
      ${groups.length ? groups.map(gname => `<label class="check"><input type="checkbox" data-dir="${dir}" data-g="${esc(gname)}" ${(rule.groups || []).includes(gname) ? "checked" : ""}> ${esc(gname)}</label>`).join("") : `<div class="muted small">${t("l.nogroups")}</div>`}</div>`;
  const peerRules = l => { const h = s.directory.find(x => x.id === l.peer); const pr = h && h.rules && h.rules.links && h.rules.links[s.hub.country + "-" + s.hub.city]; return pr; };
  const countsHtml = peer => { const p = peerCounts[peer]; if (!p) return `<p class="muted small">–</p>`;
    const bl = o => Object.entries(o).map(([k, v]) => `${t("why." + k)}: ${v}`).join(", ");
    return `<p class="small">${t("rule.send")}: <b>${p.sent}</b>${Object.keys(p.blocked_send).length ? ` · ${t("l.blocked")}: ${bl(p.blocked_send)}` : ""}<br>
      ${t("rule.receive")}: <b>${p.received}</b>${Object.keys(p.blocked_recv).length ? ` · ${t("l.blocked")}: ${bl(p.blocked_recv)}` : ""}</p>`; };
  const yn = v => v ? `<span class="badge ok">${t("rule.on")}</span>` : `<span class="badge bad">${t("rule.off")}</span>`;
  const prHtml = pr => !pr ? `<p class="muted small">${t("l.peer_rules.none")}</p>` :
    `<table class="small"><tr><th></th><th>${t("rule.send")}</th><th>${t("rule.receive")}</th></tr>
     ${["on", "public", "private", "positions"].map(k => `<tr><td>${t(k === "on" ? "link" : "rule." + k)}</td><td>${yn(pr.send[k])}</td><td>${yn(pr.receive[k])}</td></tr>`).join("")}
     <tr><td>${t("rule.groups")}</td><td>${esc((pr.send.groups || []).join(", ") || "–")}</td><td>${esc((pr.receive.groups || []).join(", ") || "–")}</td></tr></table>`;
  app().innerHTML = `${ok ? "" : `<div class="msg warn">${t("l.not_connected")}</div>`}
    <div class="card"><h2>${t("l.mylinks")}</h2>${s.links.length ? s.links.map(l => `
      <div class="card" style="box-shadow:none" data-link="${l.id}" data-peer="${l.peer}">
        <div class="spread"><h2 style="margin:0">${esc(l.peer_code)} · ${esc(l.peer_name)} ${onlineBadge(l.peer_online)}</h2>
          <div class="row"><span class="badge ${l.state === "active" ? "ok" : "warn"}">${t("l.state." + l.state)}</span>
          ${l.state !== "active" && !l.i_accepted ? `<button class="primary small" data-acc="${l.id}">${t("l.accept")}</button>` : ""}
          <button class="danger small" data-rm="${l.id}" data-code="${esc(l.peer_code)}">${l.state === "active" ? t("l.remove") : t("l.decline")}</button></div></div>
        ${l.state !== "active" ? `<p class="muted">${l.i_accepted ? t("l.wait_peer", { x: esc(l.peer_code) }) : t("l.wait_me", { x: esc(l.peer_code) })}</p>` : `
        <div class="msg ${l.e2e.state === "ok" ? "ok" : "bad"}" style="margin-top:.5rem"><b>${t("e2e.title")}</b><br>
          ${l.e2e.state === "ok" ? t("e2e.ok") : l.e2e.state === "changed" ? t("e2e.changed", { x: esc(l.peer_code) }) : t("e2e.missing", { x: esc(l.peer_code) })}
          ${l.e2e.code ? `<div style="margin-top:.4rem">${t("e2e.code")}: <b class="mono" style="font-size:1.1rem">${esc(l.e2e.code)}</b></div><div class="small">${t("e2e.code.hint", { x: esc(l.peer_code) })}</div>` : ""}
          ${l.e2e.state === "changed" ? `<button class="danger small" data-trust="${l.peer}" style="margin-top:.4rem">${t("e2e.trust")}</button>` : ""}</div>
        <h3>${t("l.rules")}</h3><p class="muted small">${t("l.rules.hint", { x: esc(l.peer_code) })}</p>
        <div class="grid g2">${dirCol(l.peer, "send", rulesOf(l.peer).send)}${dirCol(l.peer, "receive", rulesOf(l.peer).receive)}</div>
        <div class="row"><button class="primary" data-save="${l.peer}">${t("save")}</button><span class="muted" data-saved="${l.peer}"></span></div>
        <div class="grid g2"><div><h3>${t("l.peer_rules", { x: esc(l.peer_code) })}</h3>${prHtml(peerRules(l))}</div>
        <div><h3>${t("l.counts")}</h3>${countsHtml(l.peer)}</div></div>`}
      </div>`).join("") : `<p class="muted">${t("l.none")}</p>`}</div>
    <div class="card"><h2>${t("l.dir")}</h2><div class="tablewrap"><table>
      <tr><th>${t("code")}</th><th>${t("name")}</th><th>${t("status")}</th><th>${t("position")}</th><th></th></tr>
      ${others.map(h => `<tr><td><b>${esc(h.code)}</b></td><td>${esc(h.name)}</td><td>${onlineBadge(h.online)}</td><td>${fmtPos(h.lat, h.lon)}</td>
        <td>${linked.has(h.id) ? "" : `<button class="small" data-ask="${h.id}" ${ok ? "" : "disabled"}>${t("l.ask")}</button>`}</td></tr>`).join("")
        || `<tr><td colspan="5" class="muted">${t("l.dir.none")}</td></tr>`}</table></div></div>`;
  const act = async (path, body, btn) => { btn.disabled = true; btn.textContent = "…"; try { await api("POST", path, body); } catch (e) { alert(errText(e)); } setTimeout(pageLinks, 800); };
  $$("button[data-ask]").forEach(b => b.onclick = () => act("/api/links/request", { to: b.dataset.ask }, b));
  $$("button[data-acc]").forEach(b => b.onclick = () => act("/api/links/accept", { link: +b.dataset.acc }, b));
  $$("button[data-rm]").forEach(b => b.onclick = () => { if (confirm(t("l.remove_q", { x: b.dataset.code }))) act("/api/links/remove", { link: +b.dataset.rm }, b); });
  $$("button[data-trust]").forEach(b => b.onclick = () => act("/api/links/trust_key", { peer: b.dataset.trust }, b));
  $$("button[data-save]").forEach(b => b.onclick = async () => {
    const peer = b.dataset.save, box = b.closest("[data-peer]"), rules = { send: { groups: [] }, receive: { groups: [] } };
    $$("input[data-k]", box).forEach(i => rules[i.dataset.dir][i.dataset.k] = i.checked);
    $$("input[data-g]", box).forEach(i => { if (i.checked) rules[i.dataset.dir].groups.push(i.dataset.g); });
    b.disabled = true;
    try { await api("POST", "/api/rules", { peer, rules }); $(`[data-saved="${peer}"]`).textContent = "✓ " + t("saved"); }
    catch (e) { $(`[data-saved="${peer}"]`).textContent = errText(e); }
    b.disabled = false;
  });
}

/* ───────── radio ───────── */
async function pageRadio() {
  const [s, c, ports] = await Promise.all([api("GET", "/api/status"), api("GET", "/api/config"), api("GET", "/api/ports")]);
  const rc = c.radios[0] || { transport: "serial", address: "" }, r = s.radio;
  app().innerHTML = `<div class="grid g2">
    <div class="card"><h2>${t("r.title")}</h2>
      <label>${t("r.type")}</label><select id="rtype"><option value="mt">Meshtastic</option><option value="mc" disabled>MeshCore – ${t("r.mc_soon")}</option></select>
      <label>${t("r.transport")}</label><select id="rtr"><option value="serial">${t("r.serial")}</option><option value="tcp">${t("r.tcp")}</option><option value="ble" disabled>${t("r.ble")}</option></select>
      <div id="rser"><label>${t("r.port")}</label><select id="rport">${ports.map(p => `<option ${p === rc.address ? "selected" : ""}>${esc(p)}</option>`).join("")}
        ${rc.transport === "serial" && rc.address && !ports.includes(rc.address) ? `<option selected>${esc(rc.address)}</option>` : ""}</select>
        <div class="hint">${ports.length ? "" : t("r.none_detected")}</div></div>
      <div id="rtcp"><label>${t("r.host")}</label><input type="text" id="rhost" value="${rc.transport === "tcp" ? esc(rc.address) : ""}"></div>
      <div id="rmsg"></div><button class="primary" id="rsave">${t("save")}</button></div>
    <div class="card"><h2>${t("r.state")}</h2>${r ? `<dl class="kv">
      <dt>${t("status")}</dt><dd>${r.connected ? `<span class="badge ok">${t("r.connected")}</span>` : `<span class="badge bad">${t("r.not_connected")}</span> <span class="muted small">${esc(r.error || "")}</span>`}</dd>
      ${r.connected ? `<dt>${t("name")}</dt><dd>${esc(r.name)} <span class="muted">${esc(r.short)} · ${esc(r.node_id)}</span></dd>
      <dt>${t("hardware")}</dt><dd>${esc(r.hw)}</dd><dt>${t("r.firmware")}</dt><dd>${esc(r.firmware)}</dd>
      <dt>${t("role")}</dt><dd>${esc(r.role)}</dd><dt>${t("r.region")}</dt><dd>${esc(r.region)} · ${esc(r.preset)}</dd>
      <dt>${t("r.channels")}</dt><dd>${(r.channels || []).map(ch => `${esc(ch.name)} <span class="badge ${ch.public ? "info" : ""}">${ch.public ? t("r.public") : t("r.private_ch")}</span>`).join("<br>")}</dd>` : ""}
      </dl>${r.connected ? `<h3>${r.ready ? `<span class="badge ok">${t("r.ready")}</span>` : `<span class="badge warn">${t("r.not_ready")}</span>`}</h3>
      ${Object.entries(r.checks || {}).map(([k, v]) => `<div>${v ? "✅" : "❌"} ${t("chk." + k)}</div>`).join("")}
      ${r.ready ? "" : `<p><button class="primary" id="prep">${t("r.prepare")}</button></p>`}<div id="pmsg"></div>
      <p class="muted small">${t("r.fw_note")}</p>` : ""}` : `<p class="muted">${t("err.no_radio")}</p>`}</div></div>`;
  const tr = $("#rtr"); tr.value = rc.transport || "serial";
  const sw = () => { $("#rser").classList.toggle("hidden", tr.value !== "serial"); $("#rtcp").classList.toggle("hidden", tr.value !== "tcp"); };
  tr.onchange = sw; sw();
  $("#rsave").onclick = async () => {
    const addr = tr.value === "tcp" ? $("#rhost").value : $("#rport").value;
    try { await api("POST", "/api/radio", { radio: { transport: tr.value, address: addr } }); $("#rmsg").innerHTML = `<div class="msg ok">${t("saved")}</div>`; setTimeout(pageRadio, 6000); }
    catch (e) { $("#rmsg").innerHTML = `<div class="msg bad">${errText(e)}</div>`; }
  };
  if ($("#prep")) $("#prep").onclick = async () => {
    if (!confirm(t("r.prepare_q"))) return;
    $("#prep").disabled = true;
    try { await api("POST", "/api/radio/prepare", {}); $("#pmsg").innerHTML = `<div class="msg ok">${t("r.prepared")}</div>`; setTimeout(pageRadio, 30000); }
    catch (e) { $("#pmsg").innerHTML = `<div class="msg bad">${errText(e)}</div>`; $("#prep").disabled = false; }
  };
}

/* ───────── settings ───────── */
async function pageSettings() {
  const [s, c] = await Promise.all([api("GET", "/api/status"), api("GET", "/api/config")]);
  const reg = !!c.server.hub_id, h = c.hub;
  const ruleBox = (dir, rule) => `<div><h3>${t(dir === "send" ? "rule.send" : "rule.receive")}</h3>
      ${ruleRow(t("l.link_on"), dir, "on", rule)}${ruleRow(t("rule.public"), dir, "public", rule)}${ruleRow(t("rule.private"), dir, "private", rule)}${ruleRow(t("rule.positions"), dir, "positions", rule)}</div>`;
  const inp = (id, key, type, val, dis) => `<label>${t(key)}</label><input type="${type || "text"}" id="${id}" value="${esc(val == null ? "" : val)}" ${dis ? "disabled" : ""}>`;
  app().innerHTML = `<div class="grid g2">
    <div class="card"><h2>${t("s.hub")}</h2>
      ${inp("hname", "s.name", "text", h.name, reg)}${inp("hemail", "s.email", "email", h.email, reg)}
      <div class="grid g2" style="gap:.5rem">${inp("hcountry", "s.country", "text", h.country, reg)}${inp("hcity", "s.city", "text", h.city, reg)}</div>
      <label>${t("s.desc")}</label><textarea id="hdesc" ${reg ? "disabled" : ""}>${esc(h.description || "")}</textarea>
      ${reg ? `<p class="muted small">${t("s.locked")}</p>` : `<div id="hmsg"></div><button class="primary" id="hsave">${t("save")}</button>`}</div>
    <div class="card"><h2>${t("s.server")}</h2>
      <label>${t("s.address")}</label><div class="row"><input type="text" id="saddr" value="${esc(c.server.address)}" style="flex:1"><button id="scheck">${t("s.check")}</button></div>
      ${c.server.fingerprint ? `<label>${t("s.trusted")}</label><div class="mono small">${esc(c.server.fingerprint)}</div>` : ""}
      <div id="sfp"></div>
      <h3>${t("s.registration")}</h3><p>${regText(c.server.status)} ${reg ? `<span class="muted small mono">${esc(c.server.hub_id)}</span>` : ""}</p>
      <p class="muted small">${t("st.server")}: ${t(srvState(s))} ${esc(s.link_detail || "")}</p>
      <div id="jmsg"></div>
      ${!reg && c.server.fingerprint ? `<button class="primary" id="sjoin">${t("s.join")}</button>` : ""}
      ${reg ? `<button class="danger" id="sforget">${t("s.forget")}</button>` : ""}</div>
    <div class="card"><h2>${t("loc.title")}</h2>
      <p class="muted small">${t("loc.hint")}</p>
      <label class="check"><input type="radio" name="lmode" value="radio" ${h.location_mode !== "manual" ? "checked" : ""}> ${t("loc.radio")}</label>
      <label class="check"><input type="radio" name="lmode" value="manual" ${h.location_mode === "manual" ? "checked" : ""}> ${t("loc.manual")}</label>
      <p class="small">${t("loc.radio_pos")}: ${s.radio_position ? `<b>${fmtPos(s.radio_position.lat, s.radio_position.lon)}</b> <button class="small" id="luse">${t("loc.use")}</button>` : `<span class="muted">${t("loc.no_radio_pos")}</span>`}</p>
      <div class="grid g2" style="gap:.5rem">${inp("hlat", "s.lat", "number", h.lat)}${inp("hlon", "s.lon", "number", h.lon)}</div>
      <div id="locmsg"></div><button class="primary" id="locsave">${t("save")}</button></div>
    <div class="card"><h2>${t("s.limits")}</h2>
      ${inp("ahour", "s.air_hour", "number", c.airtime.pct_hour)}${inp("aday", "s.air_day", "number", c.airtime.pct_day)}
      <p class="hint">${t("s.air_hint")}</p>
      <label class="check"><input type="checkbox" id="spos" ${c.share_positions_on_map ? "checked" : ""}> ${t("s.share_pos")}</label>
      <h3>${t("s.defaults")}</h3><div class="grid g2" id="defs">${ruleBox("send", c.defaults.send)}${ruleBox("receive", c.defaults.receive)}</div>
      <div id="lmsg"></div><button class="primary" id="lsave">${t("save")}</button></div>
    <div class="card"><h2>${t("s.password")}</h2><input type="password" id="npw"><div class="hint">${t("password.short")}</div><div id="pwmsg"></div>
      <button id="pwsave">${t("save")}</button> <button id="logout">${t("logout")}</button></div></div>`;
  const hubBody = () => ({ hub: { name: $("#hname").value, email: $("#hemail").value, country: $("#hcountry").value, city: $("#hcity").value,
                                  description: $("#hdesc").value } });
  const lmode = () => ($$("input[name=lmode]").find(i => i.checked) || {}).value;
  const syncMode = () => { const auto = lmode() === "radio"; $("#hlat").disabled = auto; $("#hlon").disabled = auto; };
  $$("input[name=lmode]").forEach(i => i.onchange = syncMode); syncMode();
  if ($("#luse")) $("#luse").onclick = () => { $("#hlat").value = s.radio_position.lat; $("#hlon").value = s.radio_position.lon; };
  $("#locsave").onclick = async () => {
    try { await api("POST", "/api/hub", { hub: { location_mode: lmode(), lat: $("#hlat").value, lon: $("#hlon").value } });
          $("#locmsg").innerHTML = `<div class="msg ok">${t("saved")}</div>`; setTimeout(pageSettings, 1500); }
    catch (e) { $("#locmsg").innerHTML = `<div class="msg bad">${errText(e)}</div>`; }
  };
  if ($("#hsave")) $("#hsave").onclick = async () => { await api("POST", "/api/hub", hubBody()); $("#hmsg").innerHTML = `<div class="msg ok">${t("saved")}</div>`; };
  $("#scheck").onclick = async () => {
    $("#sfp").innerHTML = `<p class="muted">…</p>`;
    try {
      const r = await api("POST", "/api/server/check", { address: $("#saddr").value });
      $("#sfp").innerHTML = `<label>${t("s.fp")}</label><div class="mono small">${esc(r.fingerprint)}</div><p class="hint">${t("s.fp_hint")}</p>
        <button class="primary" id="strust">${t("s.trust")}</button>`;
      $("#strust").onclick = async () => { await api("POST", "/api/server/trust", { address: r.address, fingerprint: r.fingerprint }); pageSettings(); };
    } catch (e) { $("#sfp").innerHTML = `<div class="msg bad">${errText(e)}</div>`; }
  };
  if ($("#sjoin")) $("#sjoin").onclick = async () => {
    try {
      await api("POST", "/api/hub", hubBody());
      const r = await api("POST", "/api/server/join", {});
      $("#jmsg").innerHTML = `<div class="msg ok">${t("s.joined", { x: esc(r.hub_id) })}</div>`; setTimeout(pageSettings, 2500);
    } catch (e) { $("#jmsg").innerHTML = `<div class="msg bad">${errText(e)}</div>`; }
  };
  if ($("#sforget")) $("#sforget").onclick = async () => { if (confirm(t("s.forget_q"))) { await api("POST", "/api/server/forget", {}); pageSettings(); } };
  $("#lsave").onclick = async () => {
    const defaults = { send: { groups: [] }, receive: { groups: [] } };
    $$("#defs input[data-k]").forEach(i => defaults[i.dataset.dir][i.dataset.k] = i.checked);
    try { await api("POST", "/api/hub", { airtime: { pct_hour: $("#ahour").value, pct_day: $("#aday").value }, share_positions_on_map: $("#spos").checked, defaults });
          $("#lmsg").innerHTML = `<div class="msg ok">${t("saved")}</div>`; } catch (e) { $("#lmsg").innerHTML = `<div class="msg bad">${errText(e)}</div>`; }
  };
  $("#pwsave").onclick = async () => { try { await api("POST", "/api/password", { password: $("#npw").value }); $("#pwmsg").innerHTML = `<div class="msg ok">${t("saved")}</div>`; } catch (e) { $("#pwmsg").innerHTML = `<div class="msg bad">${t("password.short")}</div>`; } };
  $("#logout").onclick = async () => { await api("POST", "/api/logout", {}); route(); };
}

/* ───────── login / router ───────── */
async function pageLogin(setup) {
  app().innerHTML = `<div class="center"><div class="card narrow"><h2>${setup ? t("setup.title") : t("login.title")}</h2>
    <label>${t("password")}</label><input type="password" id="pw"><div class="hint">${t("password.short")}</div><div id="lmsg"></div>
    <button class="primary" id="lbtn">${setup ? t("setup.btn") : t("login")}</button></div></div>`;
  const go = async () => {
    try { await api("POST", setup ? "/api/setup" : "/api/login", { password: $("#pw").value }); route(); }
    catch (e) { $("#lmsg").innerHTML = `<div class="msg bad">${e.message === "wrong_password" ? t("password.wrong") : e.message === "locked" ? t("err.locked") : t("password.short")}</div>`; }
  };
  $("#lbtn").onclick = go; $("#pw").onkeydown = e => { if (e.key === "Enter") go(); };
}

async function route() {
  clearInterval(timer);
  if (mapObj) { mapObj.remove(); mapObj = null; }
  renderHeader(t("site.hub"), MENU);
  $("#foot").textContent = t("foot.hub");
  app().innerHTML = `<p class="muted">${t("loading")}</p>`;
  try {
    const sess = await api("GET", "/api/session");
    if (sess.setup_needed || !sess.logged_in) return pageLogin(sess.setup_needed);
    const page = location.hash.replace(/^#\/?/, "").split("/")[0];
    if (page === "links") return await pageLinks();
    if (page === "radio") return await pageRadio();
    if (page === "settings") return await pageSettings();
    await pageStatus();
    timer = setInterval(() => { if (!document.hidden && !document.querySelector("input:focus,select:focus,textarea:focus")) { if (mapObj) { mapObj.remove(); mapObj = null; } pageStatus().catch(() => {}); } }, 30000);
  } catch (e) {
    if (e.status === 401) return pageLogin(false);
    app().innerHTML = `<div class="card msg bad">${t("error")}: ${esc(e.message)}</div>`;
  }
}
Ura.onLang = route;
window.addEventListener("hashchange", route);
document.documentElement.lang = Ura.lang;
route();
