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
  "sec.hint": { en: "One line per part. Click a line for details and settings.", sq: "Një rresht për çdo pjesë. Klikoni një rresht për detaje dhe cilësime." },
  "st.overview": { en: "Overview", sq: "Përmbledhje" },
  "st.announce.hint": { en: "Announce sends this radio's name, telemetry and (if it has one) its position to the mesh and across the links. Ask neighbours makes nearby nodes answer with theirs.",
                        sq: "Njoftimi dërgon emrin, telemetrinë dhe (nëse ka) pozicionin e kësaj radioje në rrjet dhe përmes lidhjeve. Kërkesa fqinjëve bën që nyjet afër të përgjigjen me të tyret." },
  "dg.no_data": { en: "The node received the request but sent nothing back (waited {s} s). Some nodes do not answer telemetry or position requests, or have nothing to report.",
                  sq: "Nyja e mori kërkesën por nuk ktheu asgjë (pritëm {s} s). Disa nyje nuk u përgjigjen kërkesave për telemetri ose pozicion, ose nuk kanë çfarë të raportojnë." },
  "wd.log": { en: "What the watchdog found", sq: "Çfarë gjeti mbikëqyrësi" },
  "wd.short": { en: "restarted {n}× (7 days)", sq: "rindezur {n}× (7 ditë)" },
  "rx.deaf_short": { en: "hears nothing", sq: "nuk dëgjon asgjë" },
  "nl.older": { en: "older", sq: "më të vjetra" },
  "dg.short": { en: "message · traceroute · telemetry · position · channel test", sq: "mesazh · gjurmim rruge · telemetri · pozicion · test kanali" },
  "dev.identity": { en: "Name and position", sq: "Emri dhe pozicioni" },
  "dev.updown": { en: "Up / down", sq: "Lart / poshtë" }, "dev.kind": { en: "Kind", sq: "Lloji" }, "dev.fields": { en: "Fields", sq: "Fusha" },
  "loc.mode": { en: "Taken from", sq: "Merret nga" }, "loc.mode.radio": { en: "the radio", sq: "radio" }, "loc.mode.manual": { en: "typed in", sq: "e shkruar me dorë" },
  "tr.max_n": { en: "max {n} hops", sq: "maks. {n} hapa" }, "s.share_pos_short": { en: "Positions on map", sq: "Pozicione në hartë" },
  "s.locked_short": { en: "locked while registered", sq: "e kyçur gjatë regjistrimit" },
  "s.pw_short": { en: "change the password of this page", sq: "ndryshoni fjalëkalimin e kësaj faqeje" },
  "adv.changed_n": { en: "{n} changed from default", sq: "{n} ndryshuar nga parazgjedhja" }, "adv.all_default": { en: "all at default", sq: "të gjitha me parazgjedhje" },
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
  "s.forget_q": { en: "Leave the server? The server removes this hub and ends ALL its links at once (the partner hubs are told). You would need to register again.", sq: "Të largohem nga serveri? Serveri e heq këtë hub dhe mbyll menjëherë TË GJITHA lidhjet e tij (hub-et partnere njoftohen). Do t'ju duhet të regjistroheni përsëri." },
  "s.forget_force_q": { en: "The server could not be reached, so it cannot remove this hub and end its links now. Forget the registration here anyway? (The administrator can remove the hub on the server.)", sq: "Serveri nuk u arrit, ndaj nuk mund ta heqë tani këtë hub dhe të mbyllë lidhjet e tij. Ta harroj gjithsesi regjistrimin këtu? (Administratori mund ta heqë hub-in në server.)" },
  "s.trusted_server": { en: "Trusted server:", sq: "Serveri i besuar:" },
  "s.join_to": { en: "The registration request goes to {x}.", sq: "Kërkesa për regjistrim shkon te {x}." },
  "s.join_check_first": { en: "The address above is not the trusted server. Press “Check server”, compare the fingerprint and trust it first.", sq: "Adresa më sipër nuk është serveri i besuar. Shtypni “Kontrollo serverin”, krahasoni gjurmën dhe besojeni së pari." },
  "err.not_trusted": { en: "Send the request only to the trusted server shown above — check and trust the server first.", sq: "Dërgojeni kërkesën vetëm te serveri i besuar që shfaqet më sipër — kontrolloni dhe besojeni serverin së pari." },
  "pend.title": { en: "Connected — waiting for the administrator's approval", sq: "I lidhur — në pritje të miratimit nga administratori" },
  "pend.text": { en: "Your registration request reached the server {x}. Until the server's administrator approves it, your nodes are not on the map and links with other hubs are not possible yet. Nothing else to do here — this page updates by itself.",
                 sq: "Kërkesa juaj për regjistrim arriti te serveri {x}. Derisa administratori i serverit ta miratojë, nyjet tuaja nuk janë në hartë dhe lidhjet me hub-e të tjerë ende nuk janë të mundshme. Këtu nuk ka asgjë tjetër për të bërë — faqja përditësohet vetë." },
  "pend.links": { en: "Waiting for the administrator's approval — links with other hubs are possible once the server has approved this hub.", sq: "Në pritje të miratimit nga administratori — lidhjet me hub-e të tjerë janë të mundshme pasi serveri ta ketë miratuar këtë hub." },
  "pend.removed": { en: "The server's administrator has removed this hub. Register again under Settings if this was a mistake.", sq: "Administratori i serverit e ka hequr këtë hub. Regjistrohuni përsëri te Cilësimet nëse ishte gabim." },
  "pend.none": { en: "This hub is not registered with a server yet.", sq: "Ky hub ende nuk është regjistruar në një server." },
  "err.leave_not_confirmed": { en: "The server could not be told.", sq: "Serveri nuk mund të njoftohej." },
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
  "adv.node_max_age_days": { en: "A node counts as “heard here” if heard within (days)", sq: "Një nyje llogaritet “dëgjuar këtu” nëse është dëgjuar brenda (ditë)" },
  "adv.nodes_report_min": { en: "Send the full node list to the server at least every (minutes)", sq: "Dërgo listën e plotë të nyjeve te serveri të paktën çdo (minuta)" },
  "adv.nodes_check_s": { en: "Check for node changes every (seconds)", sq: "Kontrollo për ndryshime të nyjeve çdo (sekonda)" },
  "adv.location_follow_m": { en: "Follow the radio's position when it moved more than (metres)", sq: "Ndiq pozicionin e radios kur ka lëvizur më shumë se (metra)" },
  "adv.location_check_s": { en: "Check the radio's position every (seconds)", sq: "Kontrollo pozicionin e radios çdo (sekonda)" },
  "adv.clock_sync": { en: "Set the radio's clock from this computer", sq: "Vendos orën e radios nga ky kompjuter" },
  "adv.clock_sync.hint": { en: "Radios without GPS or internet lose the right time; wrong times break “last heard” and message times.", sq: "Radiot pa GPS ose internet humbasin orën e saktë; orët e gabuara prishin “dëgjuar së fundi” dhe kohët e mesazheve." },
  "adv.clock_sync_min": { en: "Set the radio's clock every (minutes)", sq: "Vendos orën e radios çdo (minuta)" },
  "adv.mqtt_address": { en: "MQTT address written by “Prepare radio”", sq: "Adresa MQTT që shkruan “Përgatit radion”" },
  "adv.mqtt_address.hint": { en: "Must be a private IP. It is never contacted (the radio talks to the hub over USB/IP); a private address makes the firmware pass on every packet.", sq: "Duhet të jetë IP private. Nuk kontaktohet kurrë (radio flet me hub-in përmes USB/IP); një adresë private bën që firmware të kalojë çdo paketë." },
  "adv.replay_window_s": { en: "Reject sealed boxes older than (seconds)", sq: "Refuzo kutitë e mbyllura më të vjetra se (sekonda)" },
  "adv.replay_window_s.hint": { en: "Protection against someone replaying old traffic. Clocks of both hubs must be within this window.", sq: "Mbrojtje kundër dikujt që riprodhon trafik të vjetër. Orët e të dy hub-eve duhet të jenë brenda këtij intervali." },
  "adv.session_hours": { en: "Stay logged in for (hours)", sq: "Qëndro i identifikuar për (orë)" },
  "adv.lockout_attempts": { en: "Lock out an address after wrong passwords", sq: "Blloko një adresë pas fjalëkalimesh të gabuara" },
  "adv.lockout_minutes": { en: "Lockout lasts (minutes)", sq: "Bllokimi zgjat (minuta)" },
  "adv.password_min": { en: "Minimum password length", sq: "Gjatësia minimale e fjalëkalimit" },
  "adv.server_retry_s": { en: "Reconnect to the server after (seconds)", sq: "Rilidhu me serverin pas (sekonda)" },
  "adv.refused_retry_s": { en: "After a refusal, try again after (seconds)", sq: "Pas një refuzimi, provo përsëri pas (sekonda)" },
  "adv.keepalive_s": { en: "Keep-alive to the server every (seconds)", sq: "Mbaj gjallë lidhjen me serverin çdo (sekonda)" },
  "adv.server_timeout_s": { en: "Consider the server gone after silence of (seconds)", sq: "Konsidero serverin të shkëputur pas heshtjes prej (sekonda)" },
  "adv.queue_max": { en: "Packets kept while the server is unreachable", sq: "Paketa të mbajtura kur serveri është i paarritshëm" },
  "adv.tile_source": { en: "Map tiles", sq: "Pllakat e hartës" },
  "adv.tile_source.hint": { en: "“server” = through the Ura server (works without internet here), then OpenStreetMap. Or an https URL with {z}/{x}/{y}.", sq: "“server” = përmes serverit Ura (funksionon edhe pa internet këtu), pastaj OpenStreetMap. Ose një URL https me {z}/{x}/{y}." },
  "adv.tile_cache_days": { en: "Keep map tiles for (days)", sq: "Mbaj pllakat e hartës për (ditë)" },
  "adv.tile_backoff_s": { en: "After a failed tile download, pause for (seconds)", sq: "Pas një shkarkimi të dështuar, prit për (sekonda)" },
  "adv.page_refresh_s": { en: "Refresh the status page every (seconds)", sq: "Rifresko faqen e gjendjes çdo (sekonda)" },
  "adv.g.radio": { en: "Radio", sq: "Radio" },
  "adv.g.nodes": { en: "Nodes and location", sq: "Nyjet dhe vendndodhja" },
  "adv.g.server": { en: "Connection to the server", sq: "Lidhja me serverin" },
  "adv.g.security": { en: "Security and login", sq: "Siguria dhe hyrja" },
  "adv.g.web": { en: "Map and website", sq: "Harta dhe faqja" },
  "map.title": { en: "Nodes heard by this hub's radio", sq: "Nyjet që dëgjon radio e këtij hub-i" },
  "map.own_only": { en: "Nodes of other hubs are listed below the map", sq: "Nyjet e hub-eve të tjera janë në listën poshtë hartës" },
  "map.this_radio": { en: "This hub's radio", sq: "Radio e këtij hub-i" },
  "wd.last": { en: "Last message from the radio", sq: "Mesazhi i fundit nga radio" },
  "wd.events": { en: "The radio stopped talking to the hub and was restarted automatically {n}× in the last 7 days (last: {x}). If this repeats, check that nothing else is connected to this radio (app over Wi-Fi or Bluetooth) — or switch its Wi-Fi/Bluetooth off under Device settings.",
                 sq: "Radio ndaloi së foluri me hub-in dhe u rindez automatikisht {n}× në 7 ditët e fundit (së fundi: {x}). Nëse përsëritet, kontrolloni që asgjë tjetër të mos jetë e lidhur me këtë radio (aplikacion përmes Wi-Fi ose Bluetooth) — ose fikni Wi-Fi/Bluetooth te Cilësimet e pajisjes." },
  "adv.radio_watchdog_min": { en: "Restart the radio if it sends the hub nothing for (minutes, 0 = off)", sq: "Rindize radion nëse nuk i dërgon asgjë hub-it për (minuta, 0 = joaktiv)" },
  "adv.radio_watchdog_min.hint": { en: "A connected radio reports at least every minute. Silence means it is stuck or another program took its connection.", sq: "Një radio e lidhur raporton të paktën çdo minutë. Heshtja do të thotë që ka ngecur ose një program tjetër ia mori lidhjen." },
  "adv.diag_timeout_s": { en: "Diagnostics waits for an answer (seconds)", sq: "Diagnostikimi pret përgjigje (sekonda)" },
  "adv.server_web_port": { en: "Web port of the Ura server (for map tiles)", sq: "Porta web e serverit Ura (për pllakat e hartës)" },
  "err.unreachable": { en: "The server could not be reached. Check the address and port. If the server is in your own network and you use its public name, your router may not support connections from inside to its own public address (“hairpin NAT”) — use the server's internal address instead, or add a hairpin rule on the router.",
                       sq: "Serveri nuk u arrit. Kontrolloni adresën dhe portën. Nëse serveri është në rrjetin tuaj dhe përdorni emrin e tij publik, ruteri juaj mund të mos i lejojë lidhjet nga brenda drejt adresës së vet publike (“hairpin NAT”) — përdorni adresën e brendshme të serverit, ose shtoni një rregull hairpin në ruter." },
  "err.fingerprint_mismatch": { en: "The server's certificate is not the one you trusted. Do not continue unless the server's administrator confirms a change.", sq: "Certifikata e serverit nuk është ajo që keni besuar. Mos vazhdoni nëse administratori i serverit nuk konfirmon një ndryshim." },
  "err.registrations_closed": { en: "The server does not accept new registrations at the moment.", sq: "Serveri nuk pranon regjistrime të reja për momentin." },
  "err.invalid": { en: "Some values are outside their limits (marked red).", sq: "Disa vlera janë jashtë kufijve (të shënuara me të kuqe)." },
  "dg.title": { en: "Diagnostics", sq: "Diagnostikimi" },
  "dg.hint": { en: "Test a node — local or in another country — from this hub's radio. The answer travels back the same way, so a reply proves both directions.",
               sq: "Testoni një nyje — lokale ose në një shtet tjetër — nga radio e këtij hub-i. Përgjigjja kthehet në të njëjtën rrugë, ndaj një përgjigje provon të dyja drejtimet." },
  "dg.node": { en: "Node ID", sq: "ID e nyjes" }, "dg.text": { en: "Text for the private message", sq: "Teksti i mesazhit privat" },
  "dg.dm": { en: "Private message + delivery check", sq: "Mesazh privat + kontroll dorëzimi" }, "dg.trace": { en: "Traceroute", sq: "Gjurmimi i rrugës" },
  "dg.telemetry": { en: "Ask for telemetry", sq: "Kërko telemetrinë" }, "dg.position": { en: "Ask for position", sq: "Kërko pozicionin" },
  "dg.broadcast": { en: "Send the text to this channel", sq: "Dërgo tekstin në këtë kanal" },
  "dg.broadcast.hint": { en: "Everyone on that channel receives it — here and, through Ura, in linked hubs (if your rules allow). Use sparingly.", sq: "Të gjithë në atë kanal e marrin — këtu dhe, përmes Ura, në hub-et e lidhur (nëse rregullat e lejojnë). Përdoreni me masë." },
  "dg.sent": { en: "Sent. Check the counters on the Status page of the linked hub, or a radio there.", sq: "U dërgua. Kontrolloni numëruesit në faqen e Gjendjes së hub-it të lidhur, ose një radio atje." },
  "r.exclusive": { en: "⚠️ While the hub runs, nothing else may be connected to this radio (no Meshtastic app over Bluetooth or Wi-Fi, no other program). The radio hands bridge packets to whichever connected program reads first — anything else connected makes traffic silently go missing.",
                   sq: "⚠️ Ndërsa hub-i punon, asgjë tjetër nuk duhet të jetë e lidhur me këtë radio (asnjë aplikacion Meshtastic përmes Bluetooth ose Wi-Fi, asnjë program tjetër). Radio ua jep paketat e urës cilitdo program të lidhur që lexon i pari — çdo gjë tjetër e lidhur bën që trafiku të humbasë pa u vënë re." },
  "dg.waiting": { en: "Sent — waiting for the answer…", sq: "U dërgua — në pritje të përgjigjes…" },
  "dg.noanswer": { en: "No answer within {s} s. The node may be off, out of range, or a rule blocks this kind of traffic.", sq: "Asnjë përgjigje brenda {s} s. Nyja mund të jetë e fikur, jashtë rrezes, ose një rregull e bllokon këtë lloj trafiku." },
  "dg.delivered": { en: "Delivered — the node confirmed it after {s} s.", sq: "U dorëzua — nyja e konfirmoi pas {s} s." },
  "dg.route": { en: "Route found after {s} s:", sq: "Rruga u gjet pas {s} s:" }, "dg.me": { en: "this radio", sq: "kjo radio" },
  "dg.answer": { en: "Answer after {s} s:", sq: "Përgjigje pas {s} s:" }, "dg.other": { en: "Answer “{x}” after {s} s.", sq: "Përgjigje “{x}” pas {s} s." },
  "err.bad_node": { en: "Enter a node ID like !abcd1234.", sq: "Vendosni një ID nyjeje si !abcd1234." },
  "nav.device": { en: "Device settings", sq: "Cilësimet e pajisjes" },
  "dev.warn": { en: "These settings are written straight into the radio. Wrong values (region, LoRa, channels) can cut this radio off from the local mesh. Settings marked “restarts” make the radio reboot (about 30 s).",
                sq: "Këto cilësime shkruhen drejtpërdrejt në radio. Vlera të gabuara (rajoni, LoRa, kanalet) mund ta shkëpusin këtë radio nga rrjeti lokal. Cilësimet e shënuara “rindizet” e rindezin radion (rreth 30 s)." },
  "dev.owner": { en: "Name of the radio", sq: "Emri i radios" }, "dev.long": { en: "Long name (max. 39)", sq: "Emri i gjatë (maks. 39)" },
  "dev.short": { en: "Short name (max. 4)", sq: "Emri i shkurtër (maks. 4)" }, "dev.owner.bad": { en: "Long name 1–39, short name 1–4 characters.", sq: "Emri i gjatë 1–39, i shkurtri 1–4 karaktere." },
  "dev.fixed": { en: "Fixed position", sq: "Pozicion fiks" }, "dev.fixed.on": { en: "The radio stays at this position (no GPS)", sq: "Radio qëndron në këtë pozicion (pa GPS)" },
  "dev.alt": { en: "Altitude (m)", sq: "Lartësia (m)" }, "dev.restarts": { en: "The radio restarts now.", sq: "Radio po rindizet tani." },
  "dev.channels": { en: "Channels (groups)", sq: "Kanalet (grupet)" },
  "dev.channels.hint": { en: "Channel 0 is the primary channel. A group works between two radios only with the SAME name and the SAME key. To let a group cross Ura, also tick it in Links & rules on both hubs.",
                         sq: "Kanali 0 është kanali kryesor. Një grup funksionon ndërmjet dy radiove vetëm me të NJËJTIN emër dhe të NJËJTIN çelës. Që grupi të kalojë Ura, shënojeni edhe te Lidhjet & rregullat në të dy hub-et." },
  "dev.primary": { en: "primary", sq: "kryesor" }, "dev.secondary": { en: "secondary", sq: "dytësor" }, "dev.nokey": { en: "no encryption", sq: "pa enkriptim" },
  "dev.preset_name": { en: "(preset name, e.g. LongFast)", sq: "(emri i presetit, p.sh. LongFast)" },
  "dev.addch": { en: "Add a channel", sq: "Shto një kanal" }, "dev.delch": { en: "Delete channel", sq: "Fshi kanalin" },
  "dev.del_q": { en: "Delete this channel from the radio?", sq: "Ta fshij këtë kanal nga radio?" },
  "dev.chname": { en: "Name (max. 11)", sq: "Emri (maks. 11)" }, "dev.role": { en: "Role", sq: "Roli" }, "dev.key": { en: "Key", sq: "Çelësi" },
  "dev.key.keep": { en: "keep current key", sq: "mbaj çelësin aktual" }, "dev.key.random": { en: "new secure random key (256-bit)", sq: "çelës i ri i rastësishëm i sigurt (256-bit)" },
  "dev.key.default": { en: "public default key (AQ==)", sq: "çelësi publik i parazgjedhur (AQ==)" }, "dev.key.custom": { en: "own key", sq: "çelës i vetë" },
  "dev.key.none": { en: "no encryption", sq: "pa enkriptim" },
  "dev.pp": { en: "Position precision (bits, 0 = no position)", sq: "Saktësia e pozicionit (bit, 0 = pa pozicion)" },
  "dev.pp.hint": { en: "32 = exact, 13 ≈ 1.5 km, 0 = never share position on this channel.", sq: "32 = e saktë, 13 ≈ 1.5 km, 0 = mos e nda kurrë pozicionin në këtë kanal." },
  "dev.uplink": { en: "Uplink (to Ura)", sq: "Uplink (te Ura)" }, "dev.downlink": { en: "Downlink (from Ura)", sq: "Downlink (nga Ura)" },
  "dev.muted": { en: "Muted (no notifications)", sq: "Pa zë (pa njoftime)" },
  "dev.ch_restart": { en: "The radio applies it within a few seconds.", sq: "Radio e zbaton brenda pak sekondash." },
  "dev.url": { en: "Link to share these channels with other radios (Meshtastic app → scan/open)", sq: "Lidhja për t'i ndarë këto kanale me radio të tjera (aplikacioni Meshtastic → skano/hap)" },
  "dev.all": { en: "All radio settings", sq: "Të gjitha cilësimet e radios" },
  "dev.all.hint": { en: "Every setting of the Meshtastic firmware, read live from the radio. Names are Meshtastic's own. Only changed fields are written.",
                    sq: "Çdo cilësim i firmware-it Meshtastic, i lexuar drejtpërdrejt nga radio. Emrat janë ato të Meshtastic. Shkruhen vetëm fushat e ndryshuara." },
  "dev.module": { en: "module", sq: "modul" }, "dev.config": { en: "radio", sq: "radio" }, "dev.reboot": { en: "restarts", sq: "rindizet" },
  "dev.nochange": { en: "Nothing changed.", sq: "Asgjë nuk ndryshoi." },
  "dev.invalid": { en: "Not accepted: {x}", sq: "Nuk u pranua: {x}" },
  "dev.mqtt_q": { en: "Ura needs MQTT “proxy to client” on, encryption on and a private address. Changing MQTT can stop the bridge. Continue?", sq: "Ura ka nevojë për MQTT “proxy to client” aktiv, enkriptim aktiv dhe adresë private. Ndryshimi i MQTT mund ta ndalë urën. Të vazhdoj?" },
  "sec.device": { en: "Device", sq: "Pajisja" }, "sec.position": { en: "Position", sq: "Pozicioni" }, "sec.power": { en: "Power", sq: "Energjia" },
  "sec.network": { en: "Network (Wi-Fi/Ethernet)", sq: "Rrjeti (Wi-Fi/Ethernet)" }, "sec.display": { en: "Display", sq: "Ekrani" },
  "sec.lora": { en: "LoRa (region, preset, power)", sq: "LoRa (rajoni, preseti, fuqia)" }, "sec.bluetooth": { en: "Bluetooth", sq: "Bluetooth" },
  "sec.security": { en: "Security", sq: "Siguria" }, "sec.mqtt": { en: "MQTT (used by Ura)", sq: "MQTT (përdoret nga Ura)" }, "sec.telemetry": { en: "Telemetry", sq: "Telemetria" },
  "st.transit": { en: "Passed on for other hubs (multi-hop)", sq: "Kaluar për hub-e të tjerë (shumë-hop)" },
  "ls.pub": { en: "public", sq: "publik" }, "ls.priv": { en: "private", sq: "privat" }, "ls.pos": { en: "positions", sq: "pozicione" },
  "ls.grp": { en: "{n} group(s)", sq: "{n} grup(e)" }, "ls.nothing": { en: "nothing", sq: "asgjë" },
  "ls.reach": { en: "How far", sq: "Sa larg" }, "ls.stop": { en: "stops at {x}", sq: "ndalon te {x}" }, "ls.linked": { en: "linked", sq: "e lidhur" }, "ls.cancel": { en: "Cancel request", sq: "Anulo kërkesën" },
  "ls.incoming": { en: "Link requests waiting for you", sq: "Kërkesa për lidhje që ju presin" },
  "ls.outgoing": { en: "Requests you sent", sq: "Kërkesat që keni dërguar" },
  "ls.hint": { en: "One line per link: what you send and receive, how far your packets may go, packets sent ↑ / received ↓ (orange = stopped by a rule). Click a line for its rules.",
               sq: "Një rresht për çdo lidhje: çfarë dërgoni dhe merrni, sa larg mund të shkojnë paketat tuaja, paketa të dërguara ↑ / të marra ↓ (portokalli = ndalur nga një rregull). Klikoni një rresht për rregullat e saj." },
  "reach.title": { en: "How far may my packets go through {x}?", sq: "Sa larg mund të shkojnë paketat e mia përmes {x}?" },
  "pr.sends": { en: "It sends to us", sq: "Na dërgon ne" }, "pr.accepts": { en: "It accepts from us", sq: "Pranon nga ne" },
  "pr.multihop": { en: "Multi-hop", sq: "Shumë-hop" },
  "pr.own_reach": { en: "How far {x}'s own packets may go beyond us", sq: "Sa larg mund të shkojnë paketat e vetë {x} përtej nesh" },
  "pr.hub_transit": { en: "{x} passes traffic between its linked hubs", sq: "{x} kalon trafikun ndërmjet hub-eve të saj të lidhura" },
  "pr.to_us": { en: "{x} passes other hubs' packets on to {me}", sq: "{x} ua kalon paketat e hub-eve të tjerë {me}" },
  "pr.offers": { en: "{x} can pass our packets on to", sq: "{x} mund t'i kalojë paketat tona te" },
  "pr.from_beyond": { en: "{x} accepts packets that {me} passes on from other hubs", sq: "{x} pranon paketa që {me} i kalon nga hub-e të tjerë" },
  "reach.short": { en: "How far its packets may go", sq: "Sa larg mund të shkojnë paketat e tij" },
  "reach.0": { en: "Only to {x} — no further", sq: "Vetëm te {x} — jo më tej" },
  "reach.1": { en: "1 hub further", sq: "1 hub më tej" },
  "reach.n": { en: "{n} hubs further", sq: "{n} hub-e më tej" },
  "reach.any": { en: "Anywhere (as far as the other hubs allow)", sq: "Kudo (aq larg sa lejojnë hub-et e tjera)" },
  "reach.none_ticked": { en: "Nothing ticked: your packets stop at {x}. Tick the links of {x} they may continue on.", sq: "Asgjë e shënuar: paketat tuaja ndalojnë te {x}. Shënoni lidhjet e {x} ku mund të vazhdojnë." },
  "reach.all_links": { en: "Through every link {x} offers.", sq: "Përmes çdo lidhjeje që ofron {x}." },
  "tr.title": { en: "Multi-hop (transit)", sq: "Shumë-hop (tranzit)" },
  "tr.hint": { en: "Let traffic between your linked hubs pass through this hub — e.g. hub A → this hub → hub C. A packet is passed on only if the hub it started at allowed it to go that far (and through that link), your per-link rules allow it, and the receiving hub accepts packets from further away. Packets never go back to a hub they already passed. How far YOUR packets go is chosen per link under Links & rules.",
               sq: "Lejo që trafiku ndërmjet hub-eve të tua të lidhura të kalojë përmes këtij hub-i — p.sh. hub-i A → ky hub → hub-i C. Një paketë kalohet vetëm nëse hub-i ku nisi e ka lejuar të shkojë aq larg (dhe përmes asaj lidhjeje), rregullat e tua për lidhjen e lejojnë dhe hub-i marrës pranon paketa nga më larg. Paketat nuk kthehen kurrë te një hub ku kanë kaluar. Sa larg shkojnë paketat E TUA zgjidhet për çdo lidhje te Lidhjet & rregullat." },
  "tr.on": { en: "Pass traffic between my linked hubs", sq: "Kalo trafikun ndërmjet hub-eve të mia të lidhura" },
  "tr.hops": { en: "Pass on other hubs' packets only in chains of at most (hub-to-hub hops)", sq: "Kalo paketat e hub-eve të tjerë vetëm në zinxhirë deri në (kalime hub-në-hub)" },
  "tr.hops.hint": { en: "2 = origin → this hub → next hub. Higher values reach further but use more airtime everywhere.", sq: "2 = origjina → ky hub → hub-i tjetër. Vlera më të larta arrijnë më larg, por përdorin më shumë kohë në ajër kudo." },
  "rule.onward": { en: "Further hubs my packets may reach", sq: "Hub-e të tjera ku mund të arrijnë paketat e mia" },
  "rule.onward_to": { en: "{x} offers to pass your packets on to these hubs — tick where your packets may go (multi-hop):", sq: "{x} ofron t'i kalojë paketat tuaja te këto hub-e — shënoni ku mund të shkojnë paketat tuaja (shumë-hop):" },
  "rule.onward_to.none": { en: "{x} offers no further hubs (it has no other links, or multi-hop is off there). Your packets stop at {x}.", sq: "{x} nuk ofron hub-e të tjera (nuk ka lidhje të tjera, ose shumë-hop është joaktiv atje). Paketat tuaja ndalojnë te {x}." },
  "rule.transit": { en: "Pass other hubs' packets to this hub", sq: "Kalo paketat e hub-eve të tjerë te ky hub" },
  "rule.transit.hint": { en: "only if multi-hop is on in Settings", sq: "vetëm nëse shumë-hop është aktiv te Cilësimet" },
  "rule.from_beyond": { en: "Accept packets from hubs beyond this one", sq: "Prano paketa nga hub-et përtej këtij" },
  "rule.from_beyond.hint": { en: "traffic that started at a hub further away and was passed on by this hub", sq: "trafik që nisi te një hub më larg dhe u kalua nga ky hub" },
  "why.transit_off": { en: "transit not allowed on this link", sq: "tranziti i palejuar në këtë lidhje" },
  "why.from_beyond": { en: "from a hub further away", sq: "nga një hub më larg" },
  "why.loop": { en: "went round in a circle", sq: "bëri një rreth" },
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

const MENU = [["#/", "nav.status"], ["#/links", "nav.links"], ["#/radio", "nav.radio"], ["#/device", "nav.device"], ["#/settings", "nav.settings"]];
const app = () => document.getElementById("app");
let mapObj = null, timer = null;

function errText(e) { const k = "err." + e.message; return (t(k) !== k ? t(k) : esc(e.message)) + (e.data && e.data.detail ? ` <span class="small mono">(${esc(e.data.detail)})</span>` : ""); }
function srvState(s) { return `srv.${s.link_state}`; }
function regText(st) { return st ? t("reg." + st) : t("reg.none"); }
function ruleRow(lbl, dir, key, rule) { return `<label class="check"><input type="checkbox" data-dir="${dir}" data-k="${key}" ${rule[key] ? "checked" : ""}> ${lbl}</label>`; }

/* One line per section with a short summary; a click opens the details. Which sections are open is kept
   per page, so the automatic refresh does not close what the operator is looking at. */
const openSecs = {};
function secs(page, defaults) { if (!openSecs[page]) openSecs[page] = new Set(defaults.filter(Boolean)); return openSecs[page]; }
const B = (cls, txt) => `<span class="badge ${cls}">${txt}</span>`;
function secBox(page, key, title, cells, body, opts) {
  opts = opts || {};
  const cell = ([k, v]) => `<div class="lr-cell">${k ? `<span class="lr-k">${k}</span>` : ""}${v}</div>`;
  return `<details class="linkbox secline ${opts.cls || ""}" data-page="${page}" data-sec="${esc(key)}" ${opts.attrs || ""} ${openSecs[page] && openSecs[page].has(key) ? "open" : ""}>
    <summary><div class="linkrow lsec"><div class="lr-peer">${title}</div><div class="lr-cells">${cells.map(cell).join("")}</div></div></summary>
    <div class="linkbody">${body}</div></details>`;
}
const secTools = () => `<div class="row"><button class="small" data-secall="1">${t("adv.open_all")}</button><button class="small" data-secall="0">${t("adv.close_all")}</button></div>`;
const secCard = (title, inner) => `<div class="card"><div class="spread"><h2>${title}</h2>${secTools()}</div>${inner}</div>`;
function bindSecs() {
  $$("details.secline").forEach(d => d.addEventListener("toggle", () => {
    const set = openSecs[d.dataset.page] = openSecs[d.dataset.page] || new Set();
    if (d.open) set.add(d.dataset.sec); else set.delete(d.dataset.sec);
  }));
  $$("button[data-secall]").forEach(b => b.onclick = () => $$("details.secline", b.closest(".card")).forEach(d => d.open = b.dataset.secall === "1"));
  $$("details.secline > summary button, details.secline > summary a").forEach(x => x.addEventListener("click", e => e.stopPropagation()));
}

/* ───────── status ───────── */
const LOCAL_COLOR = "#0f7b6c";
const REMOTE_COLORS = ["#2a56c6", "#c2410c", "#7c3aed", "#b91c1c", "#0e7490", "#a16207", "#be185d"];
let SESS = { password_min: 8, page_refresh_s: 30 };
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
  const now = Date.now() / 1000, WEEK = (s.node_max_age_days || 7) * 86400;
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
  const pendingNote = s.server.status === "pending" ? `<div class="msg warn"><b>${t("pend.title")}</b><br>${t("pend.text", { x: esc(s.server.address) })}</div>`
                    : s.server.status === "removed" ? `<div class="msg bad">${t("pend.removed")}</div>`
                    : !s.server.hub_id ? `<div class="msg info">${t("pend.none")} <a href="#/settings">${t("nav.settings")} →</a></div>` : "";
  const remote = nodes.filter(n => n.remote);
  secs("status", [!r || !r.connected || !r.ready ? "radio" : null, s.link_state !== "connected" ? "server" : null, "local"]);
  const lim = (used, win, l) => `<b>${pct(used, win)}</b> <span class="muted small">${l ? "/ " + l + " %" : ""}</span>`;
  const active = s.links.filter(l => l.state === "active");
  const radioBody = r ? `<dl class="kv">
        <dt>${t("status")}</dt><dd>${r.connected ? B("ok", t("r.connected")) : `${B("bad", t("r.not_connected"))} <span class="muted small">${esc(r.error || "")}</span>`}</dd>
        <dt>${t("name")}</dt><dd>${esc(r.name || "–")} <span class="muted">${esc(r.short || "")}</span></dd>
        <dt>${t("r.firmware")}</dt><dd>${esc(r.firmware || "–")}</dd>
        <dt>${t("r.ready")}</dt><dd>${r.connected ? (r.ready ? B("ok", t("yes")) : `<a href="#/radio" class="badge warn">${t("r.not_ready")}</a>`) : "–"}</dd>
        <dt>${t("wd.last")}</dt><dd>${r.connected ? ago(now - r.silent_s) : "–"}</dd></dl>
        ${(r.watchdog || []).length ? `<div class="msg warn small">${t("wd.events", { n: r.watchdog.length, x: ago(r.watchdog[r.watchdog.length - 1]) })}</div>` : ""}
        ${(r.watchdog_events || []).length ? `<h3>${t("wd.log")}</h3><div class="small">${r.watchdog_events.slice().reverse().map(e => `<div>${ago(e.time)} — ${esc(e.finding)}</div>`).join("")}</div>` : ""}`
      : `<p class="muted">${t("err.no_radio")} <a href="#/radio">${t("nav.radio")} →</a></p>`;
  const lines = [
    secBox("status", "hub", `<b>${t("st.hub")}</b>`,
      [[t("name"), `<b>${esc(s.hub.name || "–")}</b>`], [t("code"), s.hub.country && s.hub.city ? esc(s.hub.country + "-" + s.hub.city) : "–"], [t("s.registration"), regText(s.server.status)]],
      `<dl class="kv"><dt>${t("name")}</dt><dd><b>${esc(s.hub.name || "–")}</b></dd>
        <dt>${t("code")}</dt><dd>${s.hub.country && s.hub.city ? esc(s.hub.country + "-" + s.hub.city) : "–"}</dd>
        <dt>${t("s.registration")}</dt><dd>${regText(s.server.status)}</dd></dl><p class="small"><a href="#/settings">${t("nav.settings")} →</a></p>`),
    secBox("status", "server", `<b>${t("st.server")}</b>`,
      [[t("status"), B(srvBadge, t(srvState(s)))], [t("s.address"), `<span class="mono small">${esc(s.server.address || "–")}</span>`],
       [t("links"), active.map(l => esc(l.peer_code) + (l.e2e && l.e2e.state === "ok" ? " 🔒" : " ⚠️")).join(", ") || t("none")]],
      `<dl class="kv"><dt>${t("status")}</dt><dd>${B(srvBadge, t(srvState(s)))} <span class="muted small">${esc(s.link_detail || "")}</span></dd>
        <dt>${t("s.address")}</dt><dd class="mono">${esc(s.server.address || "–")}</dd>
        <dt>${t("links")}</dt><dd>${active.map(l => esc(l.peer_code) + (l.e2e && l.e2e.state === "ok" ? " 🔒" : " ⚠️")).join(", ") || t("none")} · <a href="#/links">${t("nav.links")} →</a></dd></dl>`),
    secBox("status", "radio", `<b>${t("st.radio")}</b>`, r ? [
        [t("status"), r.connected ? B("ok", t("r.connected")) : B("bad", t("r.not_connected"))], [t("name"), esc(r.name || "–")],
        [t("r.ready"), r.connected ? (r.ready ? B("ok", t("yes")) : B("warn", t("r.not_ready"))) : "–"],
        [t("wd.last"), r.connected ? ago(now - r.silent_s) : "–"],
        ...((r.watchdog || []).length ? [["", B("warn", t("wd.short", { n: r.watchdog.length }))]] : [])] : [["", B("bad", t("err.no_radio"))]], radioBody),
    secBox("status", "airtime", `<b>${t("st.airtime")}</b>`,
      [[t("st.hour"), lim(a.used_hour, 3600, a.limits.pct_hour)], [t("st.day"), lim(a.used_day, 86400, a.limits.pct_day)],
       ["", `<button class="small" id="ann">${t("st.announce")}</button> <button class="small" id="ask">${t("st.ask")}</button> <span id="annmsg" class="muted small"></span>`]],
      `<p>${t("st.hour")}: <b>${pct(a.used_hour, 3600)}</b> (${a.limits.pct_hour ? t("st.limit", { x: a.limits.pct_hour + " %" }) : t("st.nolimit")})<br>
         ${t("st.day")}: <b>${pct(a.used_day, 86400)}</b> (${a.limits.pct_day ? t("st.limit", { x: a.limits.pct_day + " %" }) : t("st.nolimit")})</p>
       <p class="muted small">${t("st.announce.hint")}</p>`),
    secBox("status", "rx", `<b>${t("rx.title")}</b>`, s.radio_stats && s.radio_stats.time ? [
        [t("rx.rx"), s.radio_stats.numPacketsRx != null ? `<b>${s.radio_stats.numPacketsRx}</b>` : "–"],
        [t("rx.chutil"), s.radio_stats.channelUtilization != null ? s.radio_stats.channelUtilization.toFixed(1) + " %" : "–"],
        [t("rx.updated"), ago(s.radio_stats.time)],
        ...(s.radio_stats.numPacketsRx === 0 ? [["", B("warn", t("rx.deaf_short"))]] : [])] : [["", `<span class="muted small">${t("rx.none")}</span>`]],
      receptionHtml(s.radio_stats)),
    secBox("status", "local", `<span class="dot" style="background:${LOCAL_COLOR}"></span> <b>${t("nl.local")}</b>`,
      [[t("nc.map"), `<b>${localRecent.length + (own ? 1 : 0)}</b>`], [t("nc.memory"), `${nodes.length}`],
       ...(hidden ? [[t("nl.older"), `${hidden}`]] : []), ...(own ? [[t("st.radio"), `${esc(own.name || own.id)} ${own.lat != null ? "📍" : ""}`]] : [])],
      `<p class="muted small">${t("nl.local.hint")}</p>
        ${hidden ? `<label class="check small"><input type="checkbox" id="showold" ${showOld ? "checked" : ""}> ${t("nl.show_old", { n: hidden })}</label>` : ""}
        ${own ? `<p class="small">${t("st.radio")}: <b>${esc(own.name || own.id)}</b> ${own.lat != null ? "📍" : `<span class="muted">(${t("nl.nopos")})</span>`}</p>` : ""}
        <div id="localtable"></div>`),
    secBox("status", "remote", `<span class="dot" style="background:${REMOTE_COLORS[0]}"></span> <b>${t("nl.remote")}</b>`,
      [[t("nc.remote"), `<b>${remote.length}</b>`],
       ...gkeys.map(k => [k === "?" ? t("nl.unknown") : esc((codeOf(k) || "").split(" · ")[0]), `<span class="dot" style="background:${color[k]}"></span>${groups[k].length}`])],
      `<p class="muted small">${t("nl.remote.hint")}</p>
        ${gkeys.length ? gkeys.map((k, i) => `<details class="grp" data-g="${esc(k)}" ${i === 0 && k !== "?" ? "open" : ""}><summary><span class="dot" style="background:${color[k]}"></span><b>${esc(k === "?" ? t("nl.unknown") : codeOf(k))}</b> (${groups[k].length})</summary><div class="grptable"></div></details>`).join("")
          : `<p class="muted">${t("none")}</p>`}`)];
  app().innerHTML = `${pendingNote}
    <div class="grid g4">
      <div class="stat"><div class="v">${g.heard}</div><div class="l">${t("st.heard")}</div></div>
      <div class="stat"><div class="v">${g.sent}</div><div class="l">${t("st.sent")}</div></div>
      <div class="stat"><div class="v">${g.received}</div><div class="l">${t("st.received")}</div></div>
      <div class="stat"><div class="v">${g.to_radio}</div><div class="l">${t("st.to_radio")}</div></div>
      ${g.transit ? `<div class="stat"><div class="v">${g.transit}</div><div class="l">${t("st.transit")}</div></div>` : ""}
    </div>
    <div class="card" style="margin-top:1rem"><div class="spread"><h2>${t("map.title")}</h2><span class="muted small">${t("map.own_only")}</span></div>
      <div id="map" class="minimap" style="height:440px"></div>
      <div class="legend"><span><span class="dot big" style="background:${LOCAL_COLOR}"></span>${t("map.this_radio")}</span>
        <span><span class="dot" style="background:${LOCAL_COLOR}"></span>${t("nl.local")}</span></div></div>
    ${secCard(t("st.overview"), `<p class="muted small">${t("sec.hint")}</p>` + lines.join(""))}`;
  bindSecs();
  const cols = [
    { key: "name", label: t("name"), render: n => `${esc(n.name || "–")} <span class="muted">${esc(n.short || "")}</span>`, sort: n => (n.name || "").toLowerCase() },
    { key: "id", label: t("id"), render: n => `<span class="mono small">${esc(n.id)}</span>` },
    { key: "last_heard", label: t("last_heard"), render: n => ago(n.last_heard) },
    { key: "hops", label: t("hops") }, { key: "snr", label: "SNR", render: n => n.snr != null ? n.snr + " dB" : "–" },
    { key: "lat", label: "📍", render: n => n.lat != null ? "📍" : "", sort: n => n.lat != null ? 1 : 0 }];
  const dtOpts = { searchKeys: ["name", "short", "id"], initialSort: "last_heard", pageSize: 50 };
  dataTable($("#localtable"), local, cols, Object.assign({ empty: t("nl.none_local") }, dtOpts));
  $$("details.grp").forEach(d => {
    const fill = () => { if (!d.dataset.done) { d.dataset.done = 1; dataTable($(".grptable", d), groups[d.dataset.g], cols, dtOpts); } };
    if (d.open) fill();
    d.addEventListener("toggle", fill);
  });
  const b = [];
  mapObj = makeMap("map", null, null, { guard: true });
  const dot = (n, c, rad) => { if (n.lat == null) return; L.circleMarker([n.lat, n.lon], { radius: rad, color: "#fff", weight: 1.5, fillColor: c, fillOpacity: .95 })
      .bindPopup(`<b>${esc(n.name || n.id)}</b> ${esc(n.short || "")}<br>${t("last_heard")}: ${ago(n.last_heard)}`).addTo(mapObj); b.push([n.lat, n.lon]); };
  local.forEach(n => dot(n, LOCAL_COLOR, 6));        // only nodes this hub's radio hears; remote nodes are in the list below
  if (own) dot(own, LOCAL_COLOR, 10);
  if (b.length) mapObj.fitBounds(b, { padding: [30, 30], maxZoom: 12 });
  if ($("#showold")) $("#showold").onchange = e => { showOld = e.target.checked; if (mapObj) { mapObj.remove(); mapObj = null; } pageStatus(); };
  const ann = async ask => { try { await api("POST", "/api/radio/announce", { ask }); $("#annmsg").textContent = t("st.announced"); } catch (e) { $("#annmsg").textContent = errText(e); } };
  $("#ann").onclick = () => ann(false); $("#ask").onclick = () => ann(true);
}

/* ───────── links ───────── */
const openLinks = new Set();      // links whose rules are open on the Links page (kept across refreshes)
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
      ${dir === "send" ? onwardBox(peer, rule) + ruleRow(t("rule.transit") + ` <span class="muted small">${t("rule.transit.hint")}</span>`, dir, "transit", rule)
                       : ruleRow(t("rule.from_beyond") + ` <span class="muted small">${t("rule.from_beyond.hint")}</span>`, dir, "from_beyond", rule)}
      <div class="small muted" style="margin-top:.4rem">${t("rule.groups")}</div>
      ${groups.length ? groups.map(gname => `<label class="check"><input type="checkbox" data-dir="${dir}" data-g="${esc(gname)}" ${(rule.groups || []).includes(gname) ? "checked" : ""}> ${esc(gname)}</label>`).join("") : `<div class="muted small">${t("l.nogroups")}</div>`}</div>`;
  // the hubs this peer offers to pass my packets on to (its published transit list), each with a tick box
  const REACH_ANY = 7;
  const reachOf = rule => rule.reach != null ? +rule.reach : ((rule.onward_to || []).length ? Math.min(REACH_ANY, ((c.transit && c.transit.max_hops) || 2) - 1) : 0);
  const reachText = (n, pc) => n === 0 ? t("reach.0", { x: pc }) : n >= REACH_ANY ? t("reach.any") : t(n === 1 ? "reach.1" : "reach.n", { n });
  const onwardBox = (peer, rule) => {
    const h = s.directory.find(x => x.id === peer), offered = ((h && h.rules && h.rules.transit_to) || []).filter(x => x !== s.server.hub_id);
    const pc = esc((h && h.code) || peer), r = reachOf(rule);
    const opts = Array.from({ length: REACH_ANY + 1 }, (_, n) => `<option value="${n}" ${n === r ? "selected" : ""}>${reachText(n, pc)}</option>`).join("");
    const ticks = offered.length
      ? offered.map(id => { const o = s.directory.find(x => x.id === id); return `<label class="check"><input type="checkbox" data-onward="${esc(id)}" ${(rule.onward_to || []).includes(id) ? "checked" : ""}> ${esc(o ? o.code + " · " + o.name : id)}</label>`; }).join("")
      : `<div class="muted small">${t("rule.onward_to.none", { x: pc })}</div>`;
    return `<div class="reachbox" data-reachbox><div class="small" style="margin-top:.5rem"><b>${t("reach.title", { x: pc })}</b></div>
      <select data-reach>${opts}</select>
      <div data-reach-ticks>${offered.length ? `<div class="small muted" style="margin-top:.4rem">${t("rule.onward_to", { x: pc })}</div>` : ""}${ticks}
        <div class="msg warn small" data-reach-none hidden>${t("reach.none_ticked", { x: pc })}</div></div>
      <div class="small muted" data-reach-all hidden>${t("reach.all_links", { x: pc })}</div></div>`;
  };
  const syncReach = box => {
    const r = +$("[data-reach]", box).value, any = r >= REACH_ANY;
    $("[data-reach-ticks]", box).style.display = r === 0 || any ? "none" : "";
    $("[data-reach-all]", box).hidden = !any;
    const ticked = $$("input[data-onward]", box).some(i => i.checked);
    $("[data-reach-none]", box).hidden = !(r > 0 && !any && !ticked && $$("input[data-onward]", box).length);
  };
  // the partner's published rules: for this link, plus its hub-wide multi-hop setting and what it offers onward
  const peerRules = l => { const h = s.directory.find(x => x.id === l.peer); const hr = h && h.rules;
    const pr = hr && hr.links && hr.links[s.hub.country + "-" + s.hub.city]; return pr ? { link: pr, hub: hr } : null; };
  const countsHtml = peer => { const p = peerCounts[peer]; if (!p) return `<p class="muted small">–</p>`;
    const bl = o => Object.entries(o).map(([k, v]) => `${t("why." + k)}: ${v}`).join(", ");
    return `<p class="small">${p.transit ? `${t("st.transit")}: <b>${p.transit}</b><br>` : ""}${t("rule.send")}: <b>${p.sent}</b>${Object.keys(p.blocked_send).length ? ` · ${t("l.blocked")}: ${bl(p.blocked_send)}` : ""}<br>
      ${t("rule.receive")}: <b>${p.received}</b>${Object.keys(p.blocked_recv).length ? ` · ${t("l.blocked")}: ${bl(p.blocked_recv)}` : ""}</p>`; };
  const yn = v => v ? `<span class="badge ok">${t("rule.on")}</span>` : `<span class="badge bad">${t("rule.off")}</span>`;
  const prHtml = (both, pc) => {
    if (!both) return `<p class="muted small">${t("l.peer_rules.none")}</p>`;
    const pr = both.link, hr = both.hub, me = esc(s.hub.country + "-" + s.hub.city);
    const tr = hr.transit || {}, hubOn = !!tr.enabled;
    const offered = (hr.transit_to || []).filter(id => id !== s.server.hub_id).map(id => { const o = s.directory.find(x => x.id === id); return esc(o ? o.code : id); });
    return `<table class="small"><tr><th></th><th>${t("pr.sends")}</th><th>${t("pr.accepts")}</th></tr>
     ${["on", "public", "private", "positions"].map(k => `<tr><td>${t(k === "on" ? "link" : "rule." + k)}</td><td>${yn(pr.send[k])}</td><td>${yn(pr.receive[k])}</td></tr>`).join("")}
     <tr><td>${t("rule.groups")}</td><td>${esc((pr.send.groups || []).join(", ") || "–")}</td><td>${esc((pr.receive.groups || []).join(", ") || "–")}</td></tr></table>
     <h4 style="margin:.7rem 0 .3rem">${t("pr.multihop")}</h4>
     <table class="small">
     <tr><td>${t("pr.own_reach", { x: pc })}</td><td>${reachText(reachOf(pr.send), me)}</td></tr>
     <tr><td>${t("pr.hub_transit", { x: pc })}</td><td>${hubOn ? `${yn(true)} <span class="muted">${t("tr.max_n", { n: tr.max_hops || 2 })}</span>` : yn(false)}</td></tr>
     <tr><td>${t("pr.to_us", { x: pc, me })}</td><td>${yn(hubOn && pr.send.on && pr.send.transit !== false)}</td></tr>
     <tr><td>${t("pr.offers", { x: pc })}</td><td>${hubOn && offered.length ? offered.join(", ") : `<span class="muted">${t("none")}</span>`}</td></tr>
     <tr><td>${t("pr.from_beyond", { x: pc, me })}</td><td>${yn(pr.receive.on && pr.receive.from_beyond !== false)}</td></tr></table>`;
  };
  const why = s.server.status === "pending" ? t("pend.links") : !s.server.hub_id ? t("pend.none") : t("l.not_connected");
  // several links: one compact line per link, its rules open on click (state kept across refreshes)
  const active = s.links.filter(l => l.state === "active");
  const incoming = s.links.filter(l => l.state !== "active" && !l.i_accepted);
  const outgoing = s.links.filter(l => l.state !== "active" && l.i_accepted);
  if (active.length === 1 && !openLinks.size) openLinks.add(active[0].peer);
  const chips = r => !r.on ? `<span class="badge bad">${t("rule.off")}</span>`
    : [r.public && t("ls.pub"), r.private && t("ls.priv"), r.positions && t("ls.pos"), (r.groups || []).length && t("ls.grp", { n: r.groups.length })]
        .filter(Boolean).map(x => `<span class="chip">${x}</span>`).join("") || `<span class="muted small">${t("ls.nothing")}</span>`;
  const blockedN = p => p ? Object.values(p.blocked_send).reduce((x, y) => x + y, 0) + Object.values(p.blocked_recv).reduce((x, y) => x + y, 0) : 0;
  const lock = l => l.e2e.state === "ok" ? `<span title="${esc(t("e2e.title"))}">🔒</span>` : `<span class="badge bad" title="${esc(t("e2e.title"))}">⚠</span>`;
  const linkLine = l => {
    const r = rulesOf(l.peer), p = peerCounts[l.peer] || { sent: 0, received: 0, blocked_send: {}, blocked_recv: {} }, nb = blockedN(p);
    return `<div class="linkrow">
      <div class="lr-peer"><b>${esc(l.peer_code)}</b> · ${esc(l.peer_name)} ${onlineBadge(l.peer_online)}</div>
      <div class="lr-e2e">${lock(l)}</div>
      <div class="lr-dir"><span class="lr-k">${t("rule.send")}</span>${chips(r.send)}</div>
      <div class="lr-dir"><span class="lr-k">${t("rule.receive")}</span>${chips(r.receive)}</div>
      <div class="lr-reach"><span class="lr-k">${t("ls.reach")}</span>${r.send.on ? (reachOf(r.send) === 0 ? t("ls.stop", { x: esc(l.peer_code) }) : reachText(reachOf(r.send), "")) : "–"}</div>
      <div class="lr-tr"><span title="${esc(t("rule.send"))}">↑ ${p.sent}</span> <span title="${esc(t("rule.receive"))}">↓ ${p.received}</span>
        ${nb ? `<span class="badge warn" title="${esc(t("l.blocked"))}">${nb}</span>` : ""}</div></div>`;
  };
  const linkBody = l => `
        <div class="msg ${l.e2e.state === "ok" ? "ok" : "bad"}" style="margin-top:.5rem"><b>${t("e2e.title")}</b><br>
          ${l.e2e.state === "ok" ? t("e2e.ok") : l.e2e.state === "changed" ? t("e2e.changed", { x: esc(l.peer_code) }) : t("e2e.missing", { x: esc(l.peer_code) })}
          ${l.e2e.code ? `<div style="margin-top:.4rem">${t("e2e.code")}: <b class="mono" style="font-size:1.1rem">${esc(l.e2e.code)}</b></div><div class="small">${t("e2e.code.hint", { x: esc(l.peer_code) })}</div>` : ""}
          ${l.e2e.state === "changed" ? `<button class="danger small" data-trust="${l.peer}" style="margin-top:.4rem">${t("e2e.trust")}</button>` : ""}</div>
        <h3>${t("l.rules")}</h3><p class="muted small">${t("l.rules.hint", { x: esc(l.peer_code) })}</p>
        <div class="grid g2">${dirCol(l.peer, "send", rulesOf(l.peer).send)}${dirCol(l.peer, "receive", rulesOf(l.peer).receive)}</div>
        <div class="row"><button class="primary" data-save="${l.peer}">${t("save")}</button><span class="muted" data-saved="${l.peer}"></span>
          <span style="flex:1"></span><button class="danger small" data-rm="${l.id}" data-code="${esc(l.peer_code)}">${t("l.remove")}</button></div>
        <div class="grid g2"><div><h3>${t("l.peer_rules", { x: esc(l.peer_code) })}</h3>${prHtml(peerRules(l), esc(l.peer_code))}</div>
        <div><h3>${t("l.counts")}</h3>${countsHtml(l.peer)}</div></div>`;
  const reqRow = (l, mine) => `<div class="spread reqrow"><div><b>${esc(l.peer_code)}</b> · ${esc(l.peer_name)} ${onlineBadge(l.peer_online)}
      <div class="muted small">${mine ? t("l.wait_peer", { x: esc(l.peer_code) }) : t("l.wait_me", { x: esc(l.peer_code) })}</div></div>
      <div class="row">${mine ? "" : `<button class="primary small" data-acc="${l.id}">${t("l.accept")}</button>`}
      <button class="danger small" data-rm="${l.id}" data-code="${esc(l.peer_code)}">${mine ? t("ls.cancel") : t("l.decline")}</button></div></div>`;
  app().innerHTML = `${ok ? "" : `<div class="msg warn">${why}</div>`}
    ${incoming.length ? `<div class="card attention"><h2>${t("ls.incoming")} (${incoming.length})</h2>${incoming.map(l => reqRow(l, false)).join("")}</div>` : ""}
    <div class="card"><div class="spread"><h2>${t("l.mylinks")} (${active.length})</h2>
      ${active.length > 1 ? `<div class="row"><button class="small" data-lall="1">${t("adv.open_all")}</button><button class="small" data-lall="0">${t("adv.close_all")}</button></div>` : ""}</div>
      ${active.length > 5 ? `<input type="text" id="lfilter" placeholder="${t("dt.search")}" style="max-width:280px;margin-bottom:.5rem">` : ""}
      ${active.length ? `<p class="muted small">${t("ls.hint")}</p>` + active.map(l => `
      <details class="linkbox" data-link="${l.id}" data-peer="${l.peer}" data-q="${esc((l.peer_code + " " + l.peer_name).toLowerCase())}" ${openLinks.has(l.peer) ? "open" : ""}>
        <summary>${linkLine(l)}</summary><div class="linkbody">${linkBody(l)}</div></details>`).join("") : `<p class="muted">${t("l.none")}</p>`}
      ${outgoing.length ? `<h3>${t("ls.outgoing")} (${outgoing.length})</h3>${outgoing.map(l => reqRow(l, true)).join("")}` : ""}</div>
    <div class="card"><h2>${t("l.dir")} (${others.length})</h2><div id="hubdir"></div></div>`;
  dataTable($("#hubdir"), others, [
    { key: "code", label: t("code"), render: h => `<b>${esc(h.code)}</b>` },
    { key: "name", label: t("name"), render: h => esc(h.name) },
    { key: "online", label: t("status"), render: h => onlineBadge(h.online), sort: h => h.online ? 1 : 0 },
    { key: "lat", label: t("position"), render: h => fmtPos(h.lat, h.lon), sort: h => h.lat },
    { key: "id", label: "", render: h => linked.has(h.id) ? `<span class="muted small">${t(s.links.find(l => l.peer === h.id).state === "active" ? "ls.linked" : "l.state.pending")}</span>`
        : `<button class="small" data-ask="${h.id}" ${ok ? "" : `disabled title="${esc(why)}"`}>${t("l.ask")}</button>`, sort: h => linked.has(h.id) ? 1 : 0 }],
    { searchKeys: ["code", "name"], initialSort: "online", pageSize: 25, empty: t("l.dir.none") });
  $$("details.linkbox").forEach(d => d.addEventListener("toggle", () => { if (d.open) openLinks.add(d.dataset.peer); else openLinks.delete(d.dataset.peer); }));
  $$("button[data-lall]").forEach(b => b.onclick = () => $$("details.linkbox").forEach(d => d.open = b.dataset.lall === "1"));
  if ($("#lfilter")) $("#lfilter").oninput = e => { const q = e.target.value.toLowerCase(); $$("details.linkbox").forEach(d => d.style.display = d.dataset.q.includes(q) ? "" : "none"); };
  const act = async (path, body, btn) => { btn.disabled = true; btn.textContent = "…"; try { await api("POST", path, body); } catch (e) { const k = "err." + e.message; alert(t(k) !== k ? t(k) : e.message); } setTimeout(pageLinks, 800); };
  $("#hubdir").addEventListener("click", e => { const b = e.target.closest("button[data-ask]"); if (b) act("/api/links/request", { to: b.dataset.ask }, b); });
  $$("button[data-acc]").forEach(b => b.onclick = () => act("/api/links/accept", { link: +b.dataset.acc }, b));
  $$("button[data-rm]").forEach(b => b.onclick = () => { if (confirm(t("l.remove_q", { x: b.dataset.code }))) act("/api/links/remove", { link: +b.dataset.rm }, b); });
  $$("button[data-trust]").forEach(b => b.onclick = () => act("/api/links/trust_key", { peer: b.dataset.trust }, b));
  $$("[data-reachbox]").forEach(box => { syncReach(box); box.addEventListener("change", () => syncReach(box)); });
  $$("button[data-save]").forEach(b => b.onclick = async () => {
    const peer = b.dataset.save, box = b.closest("[data-peer]"), rules = { send: { groups: [] }, receive: { groups: [] } };
    $$("input[data-k]", box).forEach(i => rules[i.dataset.dir][i.dataset.k] = i.checked);
    $$("input[data-g]", box).forEach(i => { if (i.checked) rules[i.dataset.dir].groups.push(i.dataset.g); });
    rules.send.onward_to = $$("input[data-onward]", box).filter(i => i.checked).map(i => i.dataset.onward);
    rules.send.reach = +$("[data-reach]", box).value;
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
  const nodes = r && r.connected ? await api("GET", "/api/nodes").catch(() => []) : [];
  secs("radio", [!r || !r.connected ? "conn" : null, r && r.connected && !r.ready ? "state" : null, r && r.connected && r.ready ? "diag" : null]);
  const connBody = `
      <label>${t("r.type")}</label><select id="rtype"><option value="mt">Meshtastic</option><option value="mc" disabled>MeshCore – ${t("r.mc_soon")}</option></select>
      <label>${t("r.transport")}</label><select id="rtr"><option value="serial">${t("r.serial")}</option><option value="tcp">${t("r.tcp")}</option><option value="ble" disabled>${t("r.ble")}</option></select>
      <div id="rser"><label>${t("r.port")}</label><select id="rport">${ports.map(p => `<option ${p === rc.address ? "selected" : ""}>${esc(p)}</option>`).join("")}
        ${rc.transport === "serial" && rc.address && !ports.includes(rc.address) ? `<option selected>${esc(rc.address)}</option>` : ""}</select>
        <div class="hint">${ports.length ? "" : t("r.none_detected")}</div></div>
      <div id="rtcp"><label>${t("r.host")}</label><input type="text" id="rhost" value="${rc.transport === "tcp" ? esc(rc.address) : ""}"></div>
      <div id="rmsg"></div><button class="primary" id="rsave">${t("save")}</button>`;
  const stateBody = r ? `<dl class="kv">
      <dt>${t("status")}</dt><dd>${r.connected ? B("ok", t("r.connected")) : `${B("bad", t("r.not_connected"))} <span class="muted small">${esc(r.error || "")}</span>`}</dd>
      ${r.connected ? `<dt>${t("name")}</dt><dd>${esc(r.name)} <span class="muted">${esc(r.short)} · ${esc(r.node_id)}</span></dd>
      <dt>${t("hardware")}</dt><dd>${esc(r.hw)}</dd><dt>${t("r.firmware")}</dt><dd>${esc(r.firmware)}</dd>
      <dt>${t("role")}</dt><dd>${esc(r.role)}</dd><dt>${t("r.region")}</dt><dd>${esc(r.region)} · ${esc(r.preset)}</dd>
      <dt>${t("r.channels")}</dt><dd>${(r.channels || []).map(ch => `${esc(ch.name)} ${B(ch.public ? "info" : "", ch.public ? t("r.public") : t("r.private_ch"))}`).join("<br>")}</dd>` : ""}
      </dl>${r.connected ? `<h3>${r.ready ? B("ok", t("r.ready")) : B("warn", t("r.not_ready"))}</h3>
      ${Object.entries(r.checks || {}).map(([k, v]) => `<div>${v ? "✅" : "❌"} ${t("chk." + k)}</div>`).join("")}
      ${r.ready ? "" : `<p><button class="primary" id="prep">${t("r.prepare")}</button></p>`}<div id="pmsg"></div>
      <p class="muted small">${t("r.fw_note")}</p><div class="msg warn small">${t("r.exclusive")}</div>` : ""}` : `<p class="muted">${t("err.no_radio")}</p>`;
  const diagBody = `<p class="muted small">${t("dg.hint")}</p>
      <label>${t("dg.node")}</label><input type="text" id="dgnode" list="dglist" placeholder="!abcd1234">
      <datalist id="dglist">${nodes.filter(n => !n.own).sort((a, b) => (b.last_heard || 0) - (a.last_heard || 0)).map(n => `<option value="${esc(n.id)}">${esc(n.name || "")}${n.remote ? " · " + t("remote") : ""}</option>`).join("")}</datalist>
      <label>${t("dg.text")}</label><input type="text" id="dgtext" maxlength="200" value="Ura test">
      <div class="row" style="margin-top:.6rem">
        <button data-dg="dm">${t("dg.dm")}</button><button data-dg="trace">${t("dg.trace")}</button>
        <button data-dg="telemetry">${t("dg.telemetry")}</button><button data-dg="position">${t("dg.position")}</button></div>
      <div class="row" style="margin-top:.8rem"><select id="dgch" style="max-width:260px">${((r && r.channels) || []).map(ch => `<option value="${ch.index}">${esc(ch.name)}${ch.public ? " (" + t("r.public") + ")" : ""}</option>`).join("")}</select>
        <button data-dg="broadcast">${t("dg.broadcast")}</button></div><div class="hint">${t("dg.broadcast.hint")}</div>
      <div id="dgout"></div>`;
  const lines = [
    secBox("radio", "conn", `<b>${t("r.title")}</b>`,
      [[t("r.type"), "Meshtastic"], [t("r.transport"), rc.transport === "tcp" ? t("r.tcp") : t("r.serial")],
       [t("r.port"), `<span class="mono small">${esc((rc.address || "–").replace(/^.*\/(usb-)?/, ""))}</span>`]], connBody),
    secBox("radio", "state", `<b>${t("r.state")}</b>`, r ? [
        [t("status"), r.connected ? B("ok", t("r.connected")) : B("bad", t("r.not_connected"))],
        ...(r.connected ? [[t("name"), `${esc(r.name)} <span class="muted small">${esc(r.node_id)}</span>`], [t("r.firmware"), esc(r.firmware)],
                           [t("r.ready"), r.ready ? B("ok", t("yes")) : B("warn", t("r.not_ready"))]] : [["", `<span class="muted small">${esc(r.error || "")}</span>`]])]
      : [["", B("bad", t("err.no_radio"))]], stateBody),
    ...(r && r.connected ? [secBox("radio", "diag", `<b>${t("dg.title")}</b>`, [["", `<span class="muted small">${t("dg.short")}</span>`]], diagBody)] : [])];
  app().innerHTML = secCard(t("nav.radio"), `<p class="muted small">${t("sec.hint")}</p>` + lines.join(""));
  bindSecs();
  if (r && r.connected) {
    $$("button[data-dg]").forEach(b => b.onclick = async () => {
      const node = $("#dgnode").value.trim();
      $$("button[data-dg]").forEach(x => x.disabled = true);
      $("#dgout").innerHTML = `<div class="msg info">${t("dg.waiting")}</div>`;
      try {
        const r2 = await api("POST", "/api/diag", { node, kind: b.dataset.dg, text: $("#dgtext").value, channel: $("#dgch") ? $("#dgch").value : 0 });
        let body = "";
        if (r2.result === "no_data") body = `<div class="msg warn">${t("dg.no_data", { s: r2.seconds })}</div>`;
        else if (!r2.answered) body = `<div class="msg bad">${t("dg.noanswer", { s: r2.seconds })}</div>`;
        else if (r2.result === "sent") body = `<div class="msg ok">${t("dg.sent")}</div>`;
        else if (r2.result === "delivered") body = `<div class="msg ok">✅ ${t("dg.delivered", { s: r2.seconds })}</div>`;
        else if (r2.result === "route") body = `<div class="msg ok">${t("dg.route", { s: r2.seconds })}<br><b>→</b> ${esc([t("dg.me"), ...r2.route_to, node].join(" → "))}<br><b>←</b> ${esc([node, ...r2.route_back, t("dg.me")].join(" → "))}</div>`;
        else if (r2.result === "telemetry") body = `<div class="msg ok">${t("dg.answer", { s: r2.seconds })}<pre class="small">${esc(JSON.stringify(r2.telemetry, null, 1))}</pre></div>`;
        else if (r2.result === "position") body = `<div class="msg ok">${t("dg.answer", { s: r2.seconds })} ${fmtPos(r2.position.lat, r2.position.lon)}</div>`;
        else body = `<div class="msg warn">${t("dg.other", { x: esc(r2.result), s: r2.seconds })}</div>`;
        $("#dgout").innerHTML = body;
      } catch (e) { $("#dgout").innerHTML = `<div class="msg bad">${errText(e)}</div>`; }
      $$("button[data-dg]").forEach(x => x.disabled = false);
    });
  }
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

/* ───────── device settings (program the radio) ───────── */
const human = s => String(s).replace(/_/g, " ").replace(/\./g, " › ").replace(/^\w/, c => c.toUpperCase());
const SEC_NAMES = { device: "sec.device", position: "sec.position", power: "sec.power", network: "sec.network", display: "sec.display",
  lora: "sec.lora", bluetooth: "sec.bluetooth", security: "sec.security", mqtt: "sec.mqtt", telemetry: "sec.telemetry" };

async function pageDevice() {
  let d;
  try { d = await api("GET", "/api/radio/settings"); }
  catch (e) { app().innerHTML = `<div class="card msg warn">${errText(e)} <a href="#/radio">${t("nav.radio")} →</a></div>`; return; }
  const field = (sec, f, v) => {
    const id = `f_${sec}_${f.name.replace(/\./g, "__")}`, lbl = `<label for="${id}">${esc(human(f.name))}</label>`;
    if (f.readonly) return `<div>${lbl}<input type="text" disabled value="${esc(Array.isArray(v) ? v.join(", ") : v)}"></div>`;
    if (f.type === "bool") return `<label class="check"><input type="checkbox" id="${id}" data-f="${esc(f.name)}" ${v ? "checked" : ""}> ${esc(human(f.name))}</label>`;
    if (f.type === "enum") return `<div>${lbl}<select id="${id}" data-f="${esc(f.name)}">${f.options.map(o => `<option value="${esc(o)}" ${o === v ? "selected" : ""}>${esc(human(o.toLowerCase()))}</option>`).join("")}</select></div>`;
    return `<div>${lbl}<input type="${f.type === "string" ? "text" : "number"}" ${f.type === "float" ? 'step="any"' : ""} id="${id}" data-f="${esc(f.name)}" data-t="${f.type}" value="${esc(v)}"></div>`;
  };
  const ch = d.channels.filter(c => c.role !== "DISABLED"), free = d.channels.find(c => c.role === "DISABLED");
  secs("device", []);
  const keyBadge = c => B(c.psk === "default" ? "warn" : "ok", c.psk === "default" ? t("r.public") : c.psk === "none" ? t("dev.nokey") : t("r.private_ch"));
  const secTitle = sc => SEC_NAMES[sc.name] ? t(SEC_NAMES[sc.name]) : esc(human(sc.name));
  app().innerHTML = `
    <div class="msg warn">${t("dev.warn")}</div>
    ${secCard(t("dev.identity"), `<p class="muted small">${t("sec.hint")}</p>` +
      secBox("device", "owner", `<b>${t("dev.owner")}</b>`, [[t("dev.long"), `<b>${esc(d.owner.long_name)}</b>`], [t("dev.short"), esc(d.owner.short_name)]],
        `<label>${t("dev.long")}</label><input type="text" id="olong" maxlength="39" value="${esc(d.owner.long_name)}">
        <label>${t("dev.short")}</label><input type="text" id="oshort" maxlength="4" value="${esc(d.owner.short_name)}">
        <div id="omsg"></div><button class="primary" id="osave">${t("save")}</button>`) +
      secBox("device", "fixed", `<b>${t("dev.fixed")}</b>`,
        [[t("status"), d.fixed.enabled ? B("ok", t("on")) : B("", t("off"))], [t("position"), d.fixed.lat != null && d.fixed.lat !== "" ? fmtPos(d.fixed.lat, d.fixed.lon) : "–"]],
        `<label class="check"><input type="checkbox" id="fxon" ${d.fixed.enabled ? "checked" : ""}> ${t("dev.fixed.on")}</label>
        <div class="grid g3" style="gap:.5rem"><div><label>${t("s.lat")}</label><input type="number" step="any" id="fxlat" value="${esc(d.fixed.lat ?? "")}"></div>
          <div><label>${t("s.lon")}</label><input type="number" step="any" id="fxlon" value="${esc(d.fixed.lon ?? "")}"></div>
          <div><label>${t("dev.alt")}</label><input type="number" id="fxalt" value="${esc(d.fixed.alt ?? 0)}"></div></div>
        <div id="fxmsg"></div><button class="primary" id="fxsave">${t("save")}</button>`))}
    ${secCard(`${t("dev.channels")} (${ch.length})`, `<p class="muted small">${t("dev.channels.hint")}</p>
      ${ch.map(c => secBox("device", "ch" + c.index, `<b>#${c.index}</b> ${esc(c.name || t("dev.preset_name"))}`,
          [[t("dev.role"), B(c.role === "PRIMARY" ? "info" : "", c.role === "PRIMARY" ? t("dev.primary") : t("dev.secondary"))], [t("dev.key"), keyBadge(c)],
           [t("dev.updown"), `${c.uplink ? "↑" : "–"} ${c.downlink ? "↓" : "–"}`], ...(c.muted ? [["", B("", t("dev.muted"))]] : [])],
          chForm(c), { cls: "chbox", attrs: `data-ch="${c.index}"` })).join("")}
      ${free ? secBox("device", "chnew", `➕ ${t("dev.addch")}`, [], chForm({ index: free.index, role: "SECONDARY", name: "", psk: "random", uplink: true, downlink: true, position_precision: 0, muted: false }),
          { cls: "chbox", attrs: `data-ch="${free.index}" data-new="1"` }) : ""}
      ${d.url ? `<p class="small">${t("dev.url")}: <a href="${esc(d.url)}" target="_blank" rel="noopener" class="mono">${esc(d.url)}</a></p>` : ""}
      <div id="chmsg"></div>`)}
    ${secCard(`${t("dev.all")} (${d.sections.length})`, `<p class="muted small">${t("dev.all.hint")}</p>
      ${d.sections.map(sc => secBox("device", sc.name, `<b>${secTitle(sc)}</b>`,
          [[t("dev.kind"), sc.kind === "module" ? t("dev.module") : t("dev.config")], [t("dev.fields"), sc.fields.length],
           ...(sc.reboot ? [["", B("warn", t("dev.reboot"))]] : []), ["", `<span class="muted small" data-secmsg="${sc.name}"></span>`]],
          `<div class="grid g3" style="gap:.4rem 1rem;margin-top:.6rem">${sc.fields.map(f => field(sc.name, f, sc.values[f.name])).join("")}</div>
          <div class="row" style="margin-top:.6rem"><button class="primary" data-save-sec="${sc.name}">${t("save")}</button></div>`,
          { attrs: `data-kind="${sc.kind}"` })).join("")}`)}`;
  bindSecs();
  const orig = {}; d.sections.forEach(s => orig[s.name] = s.values);
  $("#osave").onclick = async () => { try { await api("POST", "/api/radio/owner", { long_name: $("#olong").value, short_name: $("#oshort").value }); $("#omsg").innerHTML = `<div class="msg ok">${t("saved")}</div>`; } catch (e) { $("#omsg").innerHTML = `<div class="msg bad">${t("dev.owner.bad")}</div>`; } };
  $("#fxsave").onclick = async () => { try { await api("POST", "/api/radio/fixed", { fixed: { enabled: $("#fxon").checked, lat: $("#fxlat").value, lon: $("#fxlon").value, alt: $("#fxalt").value } }); $("#fxmsg").innerHTML = `<div class="msg ok">${t("saved")} ${t("dev.restarts")}</div>`; } catch (e) { $("#fxmsg").innerHTML = `<div class="msg bad">${errText(e)}</div>`; } };
  $$("button[data-save-sec]").forEach(b => b.onclick = async () => {
    const box = b.closest("details[data-sec]"), sec = box.dataset.sec, values = {};
    $$("[data-f]", box).forEach(i => { const v = i.type === "checkbox" ? i.checked : i.value; if (String(v) !== String(orig[sec][i.dataset.f])) values[i.dataset.f] = v; });
    const msg = $(`[data-secmsg="${sec}"]`);
    if (!Object.keys(values).length) { msg.textContent = t("dev.nochange"); return; }
    if (box.dataset.sec === "mqtt" && !confirm(t("dev.mqtt_q"))) return;
    b.disabled = true;
    try { const r = await api("POST", "/api/radio/section", { kind: box.dataset.kind, section: sec, values }); Object.assign(orig[sec], values);
          msg.textContent = "✓ " + t("saved") + (r.reboot ? " — " + t("dev.restarts") : ""); }
    catch (e) { msg.textContent = t("dev.invalid", { x: ((e.data && e.data.fields) || []).join(", ") }); }
    b.disabled = false;
  });
  $$(".chbox").forEach(box => {
    const save = $("[data-chsave]", box), del = $("[data-chdel]", box);
    save.onclick = async () => {
      const g = n => $(`[data-c="${n}"]`, box);
      const c = { index: +box.dataset.ch, role: g("role").value, name: g("name").value, psk: g("pskmode").value === "keep" ? g("pskcur").value : g("pskmode").value === "custom" ? g("psk").value : g("pskmode").value,
                  uplink: g("uplink").checked, downlink: g("downlink").checked, position_precision: g("pp").value, muted: g("muted").checked };
      save.disabled = true;
      try { await api("POST", "/api/radio/channel", { channel: c }); $("#chmsg").innerHTML = `<div class="msg ok">${t("saved")} ${t("dev.ch_restart")}</div>`; setTimeout(pageDevice, 4000); }
      catch (e) { $("#chmsg").innerHTML = `<div class="msg bad">${t("dev.invalid", { x: ((e.data && e.data.fields) || []).join(", ") })}</div>`; save.disabled = false; }
    };
    if (del) del.onclick = async () => { if (!confirm(t("dev.del_q"))) return; await api("POST", "/api/radio/channel", { channel: { index: +box.dataset.ch, role: "DISABLED" } }); $("#chmsg").innerHTML = `<div class="msg ok">${t("saved")}</div>`; setTimeout(pageDevice, 4000); };
  });
}

function chForm(c) {
  const isNew = c.psk === "random" && !c.name;
  return `<div class="grid g3" style="gap:.4rem 1rem;margin-top:.6rem">
    <div><label>${t("dev.chname")}</label><input type="text" data-c="name" maxlength="11" value="${esc(c.name)}" placeholder="${c.index === 0 ? esc(t("dev.preset_name")) : ""}"></div>
    <div><label>${t("dev.role")}</label><select data-c="role" ${c.index === 0 ? "disabled" : ""}>${c.index === 0 ? `<option value="PRIMARY">${t("dev.primary")}</option>` : `<option value="SECONDARY">${t("dev.secondary")}</option>`}</select></div>
    <div><label>${t("dev.key")}</label><select data-c="pskmode">
      ${isNew ? "" : `<option value="keep">${t("dev.key.keep")}</option>`}
      <option value="random" ${isNew ? "selected" : ""}>${t("dev.key.random")}</option><option value="default">${t("dev.key.default")}</option>
      <option value="custom">${t("dev.key.custom")}</option><option value="none">${t("dev.key.none")}</option></select>
      <input type="hidden" data-c="pskcur" value="${esc(c.psk)}"></div>
    <div><label>${t("dev.key.custom")} (base64)</label><input type="text" data-c="psk" value="${c.psk !== "default" && c.psk !== "none" && c.psk !== "random" ? esc(c.psk) : ""}"></div>
    <div><label>${t("dev.pp")}</label><input type="number" min="0" max="32" data-c="pp" value="${esc(c.position_precision)}"><div class="hint">${t("dev.pp.hint")}</div></div>
    <div><label class="check"><input type="checkbox" data-c="uplink" ${c.uplink ? "checked" : ""}> ${t("dev.uplink")}</label>
      <label class="check"><input type="checkbox" data-c="downlink" ${c.downlink ? "checked" : ""}> ${t("dev.downlink")}</label>
      <label class="check"><input type="checkbox" data-c="muted" ${c.muted ? "checked" : ""}> ${t("dev.muted")}</label></div></div>
    <div class="row" style="margin-top:.5rem"><button class="primary" data-chsave="1">${t("save")}</button>${c.index > 0 && c.name !== "" || (c.index > 0 && !isNew) ? `<button class="danger" data-chdel="1">${t("dev.delch")}</button>` : ""}</div>`;
}

/* ───────── settings ───────── */
async function pageSettings() {
  const [s, c] = await Promise.all([api("GET", "/api/status"), api("GET", "/api/config")]);
  const reg = !!c.server.hub_id, h = c.hub;
  const ruleBox = (dir, rule) => `<div><h3>${t(dir === "send" ? "rule.send" : "rule.receive")}</h3>
      ${ruleRow(t("l.link_on"), dir, "on", rule)}${ruleRow(t("rule.public"), dir, "public", rule)}${ruleRow(t("rule.private"), dir, "private", rule)}${ruleRow(t("rule.positions"), dir, "positions", rule)}
      ${dir === "send" ? ruleRow(t("rule.transit"), dir, "transit", rule) : ruleRow(t("rule.from_beyond"), dir, "from_beyond", rule)}</div>`;
  const inp = (id, key, type, val, dis) => `<label>${t(key)}</label><input type="${type || "text"}" id="${id}" value="${esc(val == null ? "" : val)}" ${dis ? "disabled" : ""}>`;
  const spec = await api("GET", "/api/advanced_spec");
  spec.server_web_port = { default: 8443, min: 1, max: 65535 };   // stored with the server address, edited here
  const advChanged = Object.entries(c.advanced || {}).filter(([k, v]) => spec[k] && String(v) !== String(spec[k].default)).length
                   + ((c.server.web_port || 8443) !== 8443 ? 1 : 0);
  const sb = s.link_state === "connected" ? "ok" : (s.link_state === "connecting" ? "warn" : "bad");
  secs("settings", [!reg ? "hub" : null, !reg || s.link_state !== "connected" ? "server" : null]);
  const onoff = v => v ? B("ok", t("on")) : B("", t("off"));
  const lines = [
    secBox("settings", "hub", `<b>${t("s.hub")}</b>`,
      [[t("s.name"), `<b>${esc(h.name || "–")}</b>`], [t("code"), h.country && h.city ? esc(h.country + "-" + h.city) : "–"], [t("s.email"), esc(h.email || "–")],
       ...(reg ? [["", B("", "🔒 " + t("s.locked_short"))]] : [])],
      `${inp("hname", "s.name", "text", h.name, reg)}${inp("hemail", "s.email", "email", h.email, reg)}
      <div class="grid g2" style="gap:.5rem">${inp("hcountry", "s.country", "text", h.country, reg)}${inp("hcity", "s.city", "text", h.city, reg)}</div>
      <label>${t("s.desc")}</label><textarea id="hdesc" ${reg ? "disabled" : ""}>${esc(h.description || "")}</textarea>
      ${reg ? `<p class="muted small">${t("s.locked")}</p>` : `<div id="hmsg"></div><button class="primary" id="hsave">${t("save")}</button>`}`),
    secBox("settings", "server", `<b>${t("s.server")}</b>`,
      [[t("s.address"), `<span class="mono small">${esc(c.server.address || "–")}</span>`], [t("status"), B(sb, t(srvState(s)))], [t("s.registration"), regText(c.server.status)]],
      `<label>${t("s.address")}</label><div class="row"><input type="text" id="saddr" value="${esc(c.server.address)}" style="flex:1"><button id="scheck">${t("s.check")}</button></div>
      ${c.server.fingerprint ? `<div class="msg info small" style="margin-top:.6rem">${t("s.trusted_server")} <b class="mono">${esc(c.server.address)}</b><br>${t("s.trusted")}: <span class="mono">${esc(c.server.fingerprint)}</span></div>` : ""}
      <div id="sfp"></div>
      <h3>${t("s.registration")}</h3><p>${regText(c.server.status)} ${reg ? `<span class="muted small mono">${esc(c.server.hub_id)}</span>` : ""}</p>
      <p class="muted small">${t("st.server")}: ${t(srvState(s))} ${esc(s.link_detail || "")}</p>
      <div id="jmsg"></div>
      ${!reg && c.server.fingerprint ? `<div id="sjoinbox"><p class="small">${t("s.join_to", { x: `<b class="mono">${esc(c.server.address)}</b>` })}</p><button class="primary" id="sjoin">${t("s.join")}</button></div>
        <p class="msg warn small hidden" id="sjoinwarn">${t("s.join_check_first")}</p>` : ""}
      ${reg ? `<button class="danger" id="sforget">${t("s.forget")}</button>` : ""}`),
    secBox("settings", "loc", `<b>${t("loc.title")}</b>`,
      [[t("loc.mode"), h.location_mode === "manual" ? t("loc.mode.manual") : t("loc.mode.radio")], [t("position"), h.lat != null && h.lat !== "" ? fmtPos(h.lat, h.lon) : "–"]],
      `<p class="muted small">${t("loc.hint")}</p>
      <label class="check"><input type="radio" name="lmode" value="radio" ${h.location_mode !== "manual" ? "checked" : ""}> ${t("loc.radio")}</label>
      <label class="check"><input type="radio" name="lmode" value="manual" ${h.location_mode === "manual" ? "checked" : ""}> ${t("loc.manual")}</label>
      <p class="small">${t("loc.radio_pos")}: ${s.radio_position ? `<b>${fmtPos(s.radio_position.lat, s.radio_position.lon)}</b> <button class="small" id="luse">${t("loc.use")}</button>` : `<span class="muted">${t("loc.no_radio_pos")}</span>`}</p>
      <div class="grid g2" style="gap:.5rem">${inp("hlat", "s.lat", "number", h.lat)}${inp("hlon", "s.lon", "number", h.lon)}</div>
      <div id="locmsg"></div><button class="primary" id="locsave">${t("save")}</button>`),
    secBox("settings", "limits", `<b>${t("s.limits")}</b>`,
      [[t("st.hour"), c.airtime.pct_hour ? c.airtime.pct_hour + " %" : t("st.nolimit")], [t("st.day"), c.airtime.pct_day ? c.airtime.pct_day + " %" : t("st.nolimit")],
       [t("tr.title"), onoff(c.transit && c.transit.enabled) + (c.transit && c.transit.enabled ? ` <span class="small">${t("tr.max_n", { n: c.transit.max_hops || 2 })}</span>` : "")],
       [t("s.share_pos_short"), onoff(c.share_positions_on_map)]],
      `${inp("ahour", "s.air_hour", "number", c.airtime.pct_hour)}${inp("aday", "s.air_day", "number", c.airtime.pct_day)}
      <p class="hint">${t("s.air_hint")}</p>
      <label class="check"><input type="checkbox" id="spos" ${c.share_positions_on_map ? "checked" : ""}> ${t("s.share_pos")}</label>
      <h3>${t("tr.title")}</h3><p class="hint">${t("tr.hint")}</p>
      <label class="check"><input type="checkbox" id="tron" ${c.transit && c.transit.enabled ? "checked" : ""}> ${t("tr.on")}</label>
      <label>${t("tr.hops")}</label><input type="number" id="trhops" min="2" max="8" value="${esc((c.transit && c.transit.max_hops) || 2)}"><div class="hint">${t("tr.hops.hint")}</div>
      <h3>${t("s.defaults")}</h3><div class="grid g2" id="defs">${ruleBox("send", c.defaults.send)}${ruleBox("receive", c.defaults.receive)}</div>
      <div id="lmsg"></div><button class="primary" id="lsave">${t("save")}</button>`),
    secBox("settings", "pw", `<b>${t("s.password")}</b>`, [["", `<span class="muted small">${t("s.pw_short")}</span>`], ["", `<button class="small" id="logout">${t("logout")}</button>`]],
      `<input type="password" id="npw"><div class="hint">${t("password.min", { n: SESS.password_min })}</div><div id="pwmsg"></div>
      <button id="pwsave">${t("save")}</button>`),
    secBox("settings", "adv", `<b>${t("adv.title")}</b>`, [["", advChanged ? B("warn", t("adv.changed_n", { n: advChanged })) : `<span class="muted small">${t("adv.all_default")}</span>`]],
      `<p class="muted small">${t("adv.intro")}</p><div id="advform"></div>
      <div id="advmsg"></div><button class="primary" id="advsave">${t("save")}</button>`)];
  app().innerHTML = secCard(t("nav.settings"), `<p class="muted small">${t("sec.hint")}</p>` + lines.join(""));
  bindSecs();
  const af = advancedForm($("#advform"), spec, Object.assign({}, c.advanced || {}, { server_web_port: c.server.web_port || 8443 }), {
    groups: [["adv.g.radio", ["clock_sync", "clock_sync_min", "radio_watchdog_min", "diag_timeout_s", "mqtt_address"]],
             ["adv.g.nodes", ["node_max_age_days", "nodes_check_s", "nodes_report_min", "location_follow_m", "location_check_s"]],
             ["adv.g.server", ["server_retry_s", "refused_retry_s", "keepalive_s", "server_timeout_s", "queue_max", "server_web_port"]],
             ["adv.g.security", ["replay_window_s", "session_hours", "lockout_attempts", "lockout_minutes", "password_min"]],
             ["adv.g.web", ["tile_source", "tile_cache_days", "tile_backoff_s", "page_refresh_s"]]],
    depends: { clock_sync_min: "clock_sync" } });
  $("#advsave").onclick = async () => {
    const all = af.read(), port = all.server_web_port; delete all.server_web_port;
    try { await api("POST", "/api/advanced", { advanced: all, server_web_port: port }); af.mark([]); $("#advmsg").innerHTML = `<div class="msg ok">${t("saved")}</div>`; }
    catch (e) { af.mark((e.data && e.data.fields) || []); $("#advmsg").innerHTML = `<div class="msg bad">${errText(e)}</div>`; }
  };
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
  // the registration button only appears while the address field shows exactly the trusted server
  const norm = a => { a = (a || "").trim().replace(/^[a-z]+:\/\//i, "").replace(/\/+$/, ""); return a && !a.includes(":") ? a + ":8100" : a; };
  const syncJoin = () => { if (!$("#sjoinbox")) return; const ok = norm($("#saddr").value) === c.server.address;
                           $("#sjoinbox").classList.toggle("hidden", !ok); $("#sjoinwarn").classList.toggle("hidden", ok); };
  $("#saddr").addEventListener("input", syncJoin); syncJoin();
  if ($("#sjoin")) $("#sjoin").onclick = async () => {
    try {
      await api("POST", "/api/hub", hubBody());
      const r = await api("POST", "/api/server/join", { address: $("#saddr").value });
      $("#jmsg").innerHTML = `<div class="msg ok">${t("s.joined", { x: esc(r.hub_id) })}</div>`; setTimeout(pageSettings, 2500);
    } catch (e) { $("#jmsg").innerHTML = `<div class="msg bad">${errText(e)}</div>`; }
  };
  if ($("#sforget")) $("#sforget").onclick = async () => {
    if (!confirm(t("s.forget_q"))) return;
    try { await api("POST", "/api/server/forget", {}); }
    catch (e) {
      if (e.message !== "leave_not_confirmed" || !confirm(t("s.forget_force_q"))) { $("#jmsg").innerHTML = `<div class="msg bad">${errText(e)}</div>`; return; }
      await api("POST", "/api/server/forget", { force: true });
    }
    pageSettings();
  };
  $("#lsave").onclick = async () => {
    const defaults = { send: { groups: [] }, receive: { groups: [] } };
    $$("#defs input[data-k]").forEach(i => defaults[i.dataset.dir][i.dataset.k] = i.checked);
    try { await api("POST", "/api/hub", { airtime: { pct_hour: $("#ahour").value, pct_day: $("#aday").value }, share_positions_on_map: $("#spos").checked, defaults,
                                           transit: { enabled: $("#tron").checked, max_hops: $("#trhops").value } });
          $("#lmsg").innerHTML = `<div class="msg ok">${t("saved")}</div>`; } catch (e) { $("#lmsg").innerHTML = `<div class="msg bad">${errText(e)}</div>`; }
  };
  $("#pwsave").onclick = async () => { try { await api("POST", "/api/password", { password: $("#npw").value }); $("#pwmsg").innerHTML = `<div class="msg ok">${t("saved")}</div>`; } catch (e) { $("#pwmsg").innerHTML = `<div class="msg bad">${t("password.min", { n: SESS.password_min })}</div>`; } };
  $("#logout").onclick = async () => { await api("POST", "/api/logout", {}); route(); };
}

/* ───────── login / router ───────── */
async function pageLogin(setup) {
  app().innerHTML = `<div class="center"><div class="card narrow"><h2>${setup ? t("setup.title") : t("login.title")}</h2>
    <label>${t("password")}</label><input type="password" id="pw"><div class="hint">${t("password.min", { n: SESS.password_min })}</div><div id="lmsg"></div>
    <button class="primary" id="lbtn">${setup ? t("setup.btn") : t("login")}</button></div></div>`;
  const go = async () => {
    try { await api("POST", setup ? "/api/setup" : "/api/login", { password: $("#pw").value }); route(); }
    catch (e) { $("#lmsg").innerHTML = `<div class="msg bad">${e.message === "wrong_password" ? t("password.wrong") : e.message === "locked" ? t("err.locked") : t("password.min", { n: SESS.password_min })}</div>`; }
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
    SESS = sess;
    if (sess.setup_needed || !sess.logged_in) return pageLogin(sess.setup_needed);
    const page = location.hash.replace(/^#\/?/, "").split("/")[0];
    if (page === "links") return await pageLinks();
    if (page === "radio") return await pageRadio();
    if (page === "device") return await pageDevice();
    if (page === "settings") return await pageSettings();
    await pageStatus();
    timer = setInterval(() => { if (!document.hidden && !document.querySelector("input:focus,select:focus,textarea:focus")) { if (mapObj) { mapObj.remove(); mapObj = null; } pageStatus().catch(() => {}); } }, (SESS.page_refresh_s || 30) * 1000);
  } catch (e) {
    if (e.status === 401) return pageLogin(false);
    app().innerHTML = `<div class="card msg bad">${t("error")}: ${esc(e.message)}</div>`;
  }
}
Ura.onLang = route;
window.addEventListener("hashchange", route);
document.documentElement.lang = Ura.lang;
route();
