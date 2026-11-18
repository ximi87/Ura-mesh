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
  "adv.diag_timeout_s": { en: "Diagnostics waits for an answer (seconds)", sq: "Diagnostikimi pret përgjigje (sekonda)" },
  "adv.server_web_port": { en: "Web port of the Ura server (for map tiles)", sq: "Porta web e serverit Ura (për pllakat e hartës)" },
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

function errText(e) { const k = "err." + e.message; return t(k) !== k ? t(k) : esc(e.message); }
function srvState(s) { return `srv.${s.link_state}`; }
function regText(st) { return st ? t("reg." + st) : t("reg.none"); }
function ruleRow(lbl, dir, key, rule) { return `<label class="check"><input type="checkbox" data-dir="${dir}" data-k="${key}" ${rule[key] ? "checked" : ""}> ${lbl}</label>`; }

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
      <p class="muted small">${t("r.fw_note")}</p><div class="msg warn small">${t("r.exclusive")}</div>` : ""}` : `<p class="muted">${t("err.no_radio")}</p>`}</div></div>`;
  if (r && r.connected) {
    const nodes = await api("GET", "/api/nodes");
    const card = document.createElement("div"); card.className = "card";
    card.innerHTML = `<h2>${t("dg.title")}</h2><p class="muted small">${t("dg.hint")}</p>
      <label>${t("dg.node")}</label><input type="text" id="dgnode" list="dglist" placeholder="!abcd1234">
      <datalist id="dglist">${nodes.filter(n => !n.own).sort((a, b) => (b.last_heard || 0) - (a.last_heard || 0)).map(n => `<option value="${esc(n.id)}">${esc(n.name || "")}${n.remote ? " · " + t("remote") : ""}</option>`).join("")}</datalist>
      <label>${t("dg.text")}</label><input type="text" id="dgtext" maxlength="200" value="Ura test">
      <div class="row" style="margin-top:.6rem">
        <button data-dg="dm">${t("dg.dm")}</button><button data-dg="trace">${t("dg.trace")}</button>
        <button data-dg="telemetry">${t("dg.telemetry")}</button><button data-dg="position">${t("dg.position")}</button></div>
      <div class="row" style="margin-top:.8rem"><select id="dgch" style="max-width:260px">${(r.channels || []).map(ch => `<option value="${ch.index}">${esc(ch.name)}${ch.public ? " (" + t("r.public") + ")" : ""}</option>`).join("")}</select>
        <button data-dg="broadcast">${t("dg.broadcast")}</button></div><div class="hint">${t("dg.broadcast.hint")}</div>
      <div id="dgout"></div>`;
    app().appendChild(card);
    $$("button[data-dg]").forEach(b => b.onclick = async () => {
      const node = $("#dgnode").value.trim();
      $$("button[data-dg]").forEach(x => x.disabled = true);
      $("#dgout").innerHTML = `<div class="msg info">${t("dg.waiting")}</div>`;
      try {
        const r2 = await api("POST", "/api/diag", { node, kind: b.dataset.dg, text: $("#dgtext").value, channel: $("#dgch") ? $("#dgch").value : 0 });
        let body = "";
        if (!r2.answered) body = `<div class="msg bad">${t("dg.noanswer", { s: r2.seconds })}</div>`;
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
  app().innerHTML = `
    <div class="msg warn">${t("dev.warn")}</div>
    <div class="grid g2">
      <div class="card"><h2>${t("dev.owner")}</h2>
        <label>${t("dev.long")}</label><input type="text" id="olong" maxlength="39" value="${esc(d.owner.long_name)}">
        <label>${t("dev.short")}</label><input type="text" id="oshort" maxlength="4" value="${esc(d.owner.short_name)}">
        <div id="omsg"></div><button class="primary" id="osave">${t("save")}</button></div>
      <div class="card"><h2>${t("dev.fixed")}</h2>
        <label class="check"><input type="checkbox" id="fxon" ${d.fixed.enabled ? "checked" : ""}> ${t("dev.fixed.on")}</label>
        <div class="grid g3" style="gap:.5rem"><div><label>${t("s.lat")}</label><input type="number" step="any" id="fxlat" value="${esc(d.fixed.lat ?? "")}"></div>
          <div><label>${t("s.lon")}</label><input type="number" step="any" id="fxlon" value="${esc(d.fixed.lon ?? "")}"></div>
          <div><label>${t("dev.alt")}</label><input type="number" id="fxalt" value="${esc(d.fixed.alt ?? 0)}"></div></div>
        <div id="fxmsg"></div><button class="primary" id="fxsave">${t("save")}</button></div>
    </div>
    <div class="card"><h2>${t("dev.channels")}</h2><p class="muted small">${t("dev.channels.hint")}</p>
      ${ch.map(c => `<details class="chbox" data-ch="${c.index}"><summary><b>#${c.index}</b> ${esc(c.name || t("dev.preset_name"))} <span class="badge ${c.role === "PRIMARY" ? "info" : ""}">${c.role === "PRIMARY" ? t("dev.primary") : t("dev.secondary")}</span> <span class="badge ${c.psk === "default" ? "warn" : "ok"}">${c.psk === "default" ? t("r.public") : c.psk === "none" ? t("dev.nokey") : t("r.private_ch")}</span></summary>
          ${chForm(c)}</details>`).join("")}
      ${free ? `<details class="chbox" data-ch="${free.index}" data-new="1"><summary>➕ ${t("dev.addch")}</summary>${chForm({ index: free.index, role: "SECONDARY", name: "", psk: "random", uplink: true, downlink: true, position_precision: 0, muted: false })}</details>` : ""}
      ${d.url ? `<p class="small">${t("dev.url")}: <a href="${esc(d.url)}" target="_blank" rel="noopener" class="mono">${esc(d.url)}</a></p>` : ""}
      <div id="chmsg"></div></div>
    <div class="card"><h2>${t("dev.all")}</h2><p class="muted small">${t("dev.all.hint")}</p>
      ${d.sections.map(s => `<details class="secbox" data-sec="${s.name}" data-kind="${s.kind}"><summary><b>${SEC_NAMES[s.name] ? t(SEC_NAMES[s.name]) : esc(human(s.name))}</b> <span class="muted small">${s.kind === "module" ? t("dev.module") : t("dev.config")}${s.reboot ? " · " + t("dev.reboot") : ""}</span></summary>
        <div class="grid g3" style="gap:.4rem 1rem;margin-top:.6rem">${s.fields.map(f => field(s.name, f, s.values[f.name])).join("")}</div>
        <div class="row" style="margin-top:.6rem"><button class="primary" data-save-sec="${s.name}">${t("save")}</button><span class="muted small" data-secmsg="${s.name}"></span></div></details>`).join("")}</div>`;
  const orig = {}; d.sections.forEach(s => orig[s.name] = s.values);
  $("#osave").onclick = async () => { try { await api("POST", "/api/radio/owner", { long_name: $("#olong").value, short_name: $("#oshort").value }); $("#omsg").innerHTML = `<div class="msg ok">${t("saved")}</div>`; } catch (e) { $("#omsg").innerHTML = `<div class="msg bad">${t("dev.owner.bad")}</div>`; } };
  $("#fxsave").onclick = async () => { try { await api("POST", "/api/radio/fixed", { fixed: { enabled: $("#fxon").checked, lat: $("#fxlat").value, lon: $("#fxlon").value, alt: $("#fxalt").value } }); $("#fxmsg").innerHTML = `<div class="msg ok">${t("saved")} ${t("dev.restarts")}</div>`; } catch (e) { $("#fxmsg").innerHTML = `<div class="msg bad">${errText(e)}</div>`; } };
  $$("button[data-save-sec]").forEach(b => b.onclick = async () => {
    const box = b.closest("[data-sec]"), sec = box.dataset.sec, values = {};
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
    <div class="card"><h2>${t("s.password")}</h2><input type="password" id="npw"><div class="hint">${t("password.min", { n: SESS.password_min })}</div><div id="pwmsg"></div>
      <button id="pwsave">${t("save")}</button> <button id="logout">${t("logout")}</button></div></div>
    <div class="card"><h2>${t("adv.title")}</h2><p class="muted small">${t("adv.intro")}</p><div id="advform"></div>
      <div><label>${t("adv.server_web_port")}</label><input type="number" id="swebport" min="1" max="65535" value="${esc(c.server.web_port || 8443)}"></div>
      <div id="advmsg"></div><button class="primary" id="advsave">${t("save")}</button></div>`;
  const spec = await api("GET", "/api/advanced_spec");
  const af = advancedForm($("#advform"), spec, c.advanced || {});
  $("#advsave").onclick = async () => {
    try { await api("POST", "/api/advanced", { advanced: af.read(), server_web_port: $("#swebport").value }); af.mark([]); $("#advmsg").innerHTML = `<div class="msg ok">${t("saved")}</div>`; }
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
