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
  "ls.pub": { en: "public", sq: "publik" }, "ls.priv": { en: "private", sq: "privat" }, "ls.pos": { en: "positions", sq: "pozicione" },
  "ls.grp": { en: "{n} group(s)", sq: "{n} grup(e)" }, "ls.nothing": { en: "nothing", sq: "asgjë" }, "ls.reach": { en: "How far", sq: "Sa larg" },
  "ls.stop": { en: "stops at {x}", sq: "ndalon te {x}" }, "ls.30d": { en: "30 days", sq: "30 ditë" },
  "ls.open_all": { en: "Open all", sq: "Hapi të gjitha" }, "ls.close_all": { en: "Close all", sq: "Mbylli të gjitha" },
  "ls.rules_of": { en: "Rules {x} applies on its link with {y}", sq: "Rregullat që zbaton {x} në lidhjen me {y}" },
  "ls.hint_srv": { en: "One line per link, as published by this hub: what it sends and accepts, how far its packets may go, packets sent ↑ / received ↓ in the last 30 days. Click a line for the full rules.",
                   sq: "Një rresht për çdo lidhje, siç e publikon ky hub: çfarë dërgon dhe pranon, sa larg mund të shkojnë paketat e tij, paketa të dërguara ↑ / të marra ↓ në 30 ditët e fundit. Klikoni një rresht për rregullat e plota." },
  "rule.transit": { en: "Passes other hubs' packets on", sq: "Kalon paketat e hub-eve të tjerë" },
  "rule.from_beyond": { en: "Accepts packets from hubs further away", sq: "Pranon paketa nga hub-e më larg" },
  "live.on": { en: "Live traffic", sq: "Trafiku drejtpërdrejt" },
  "live.count": { en: "{n} packets since you opened the map", sq: "{n} paketa që kur hapët hartën" },
  "hubs.codes": { en: "Code = country (2–3 letters) + city / region (2–3 letters chosen by the operator), written XX-YY. A code always names exactly one hub. Networks: which radios a hub has (greyed = not connected) and how many nodes each network has. Remote nodes appear in your Meshtastic/MeshCore app like any other node — to message one, open it and choose “Send message”.",
                  sq: "Kodi = shteti (2–3 shkronja) + qyteti / rajoni (2–3 shkronja të zgjedhura nga operatori), shkruar XX-YY. Një kod emërton gjithmonë vetëm një hub. Rrjetet: cilat radio ka një hub (gri = e palidhur) dhe sa nyje ka çdo rrjet. Nyjet e largëta shfaqen në aplikacionin tuaj Meshtastic/MeshCore si çdo nyje tjetër — për t'i shkruar, hapeni dhe zgjidhni “Dërgo mesazh”." },
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
  "map.hubs": { en: "Hubs", sq: "Hub-et" }, "map.links_n": { en: "links: {n}", sq: "lidhje: {n}" },
  "map.show_nodes": { en: "Show nodes", sq: "Shfaq nyjet" }, "map.zoom_for_nodes": { en: "Zoom in to see the nodes", sq: "Zmadhoni për të parë nyjet" },
  "map.linked_with": { en: "Linked with", sq: "E lidhur me" }, "map.link7d": { en: "Packets in the last 7 days", sq: "Paketa në 7 ditët e fundit" },
  "stats.share": { en: "Share", sq: "Pjesa" }, "stats.no_traffic": { en: "no traffic", sq: "pa trafik" },
  "stats.lines_hint": { en: "One line per link, busiest first: packets in each direction, their share, and a small chart. Click a line for the full chart (hover a bar for the numbers).",
                        sq: "Një rresht për çdo lidhje, më e ngarkuara e para: paketat në secilin drejtim, pjesa e tyre dhe një grafik i vogël. Klikoni një rresht për grafikun e plotë (kaloni mbi një shtyllë për numrat)." },
  "stats.links_active": { en: "Active links", sq: "Lidhje aktive" }, "stats.hubs_online": { en: "Hubs online", sq: "Hub-e në linjë" },
  "stats.nodes": { en: "Nodes seen", sq: "Nyje të para" }, "stats.packets": { en: "Packets", sq: "Paketa" },
  "join.title": { en: "Register a hub", sq: "Regjistro një hub" },
  "join.intro": { en: "A hub is a small Linux computer (Raspberry Pi, mini PC, virtual machine or Proxmox container) next to a Meshtastic or MeshCore radio. It connects out to this server — no port forwarding needed at your site.",
                  sq: "Hub-i është një kompjuter i vogël Linux (Raspberry Pi, mini PC, makinë virtuale ose kontejner Proxmox) pranë një radioje Meshtastic ose MeshCore. Ai lidhet me këtë server nga brenda — nuk nevojitet hapje portash në vendin tuaj." },
  "join.s1": { en: "Install ura-hub on the computer and connect your radio (USB, or Wi-Fi/IP for Meshtastic).", sq: "Instaloni ura-hub në kompjuter dhe lidhni radion (USB, ose Wi-Fi/IP për Meshtastic)." },
  "join.s2": { en: "Open the hub's own page, enter this server's address and check the fingerprint above.", sq: "Hapni faqen e hub-it, vendosni adresën e këtij serveri dhe kontrolloni gjurmën më lart." },
  "join.s3": { en: "Fill in the hub name, your e-mail address, the country and city / region code and the hub's approximate location, then send the request.",
               sq: "Plotësoni emrin e hub-it, adresën tuaj të e-mail-it, kodin e shtetit dhe të qytetit / rajonit dhe vendndodhjen e përafërt të hub-it, pastaj dërgoni kërkesën." },
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
  "join.copy": { en: "Copy", sq: "Kopjo" }, "join.copied": { en: "copied", sq: "u kopjua" },
  "join.open": { en: "open", sq: "të hapura" }, "join.closed_short": { en: "closed", sq: "të mbyllura" },
  "join.registrations": { en: "New registrations", sq: "Regjistrime të reja" }, "join.hubs_here": { en: "Hubs on this server", sq: "Hub-e në këtë server" },
  "join.server_hint": { en: "Enter the address in your hub (setup wizard step 4, or Links & rules → Link settings → Ura server), press Check server and compare the fingerprint it shows with the one here. Only if they are identical, trust it.",
                        sq: "Vendosni adresën në hub-in tuaj (hapi 4 i udhëzuesit, ose Lidhjet & rregullat → Cilësimet e lidhjeve → Serveri Ura), shtypni Kontrollo serverin dhe krahasoni gjurmën që shfaq me këtë këtu. Vetëm nëse janë identike, besojeni." },
  "join.steps": { en: "Steps", sq: "Hapat" },
  "join.steps_hint": { en: "One line per step. Click a line for what to do and where in the hub.", sq: "Një rresht për çdo hap. Klikoni një rresht për çfarë të bëni dhe ku në hub." },
  "join.t1": { en: "Install the hub", sq: "Instaloni hub-in" }, "join.w1": { en: "on the computer next to your radio", sq: "në kompjuterin pranë radios" },
  "join.d1": { en: "Follow the install guide (button above). The hub's page then runs on https://&lt;computer&gt;:8091: choose the login password, and the setup wizard guides you — name, radio, Prepare radio for Ura, this server.",
               sq: "Ndiqni udhëzuesin e instalimit (butoni lart). Faqja e hub-it pastaj punon në https://&lt;kompjuteri&gt;:8091: zgjidhni fjalëkalimin e hyrjes dhe udhëzuesi ju çon hap pas hapi — emri, radio, Përgatit radion për Ura, ky server." },
  "join.t2": { en: "Connect to this server", sq: "Lidhuni me këtë server" }, "join.w2": { en: "hub → setup wizard, step 4", sq: "hub → udhëzuesi, hapi 4" },
  "join.d2": { en: "Use the address and fingerprint from the box above. A different fingerprint means you are not talking to this server — do not trust it.",
               sq: "Përdorni adresën dhe gjurmën nga kutia lart. Një gjurmë tjetër do të thotë që nuk po flisni me këtë server — mos e besoni." },
  "join.t3": { en: "Describe your hub and send the request", sq: "Përshkruani hub-in dhe dërgoni kërkesën" }, "join.w3": { en: "hub → setup wizard, step 1", sq: "hub → udhëzuesi, hapi 1" },
  "join.d3": { en: "The code is your country (2–3 letters) plus a city / region code (2–3 letters), e.g. XX-ABC — one hub per code. The approximate location is typed in or clicked on the map.",
               sq: "Kodi është shteti juaj (2–3 shkronja) plus një kod qyteti / rajoni (2–3 shkronja), p.sh. XX-ABC — një hub për kod. Vendndodhja e përafërt shkruhet ose klikohet në hartë." },
  "join.t4": { en: "Wait for approval", sq: "Prisni miratimin" }, "join.w4": { en: "the hub shows “waiting for approval”", sq: "hub-i tregon “në pritje të miratimit”" },
  "join.t5": { en: "Ask another hub for a link", sq: "Kërkoni lidhje me një hub tjetër" }, "join.w5": { en: "hub → Links & rules", sq: "hub → Lidhjet & rregullat" },
  "join.d5": { en: "Compare the safety code with the other operator once. Then set, per link, what you send and receive and how far your packets may go.",
               sq: "Krahasoni kodin e sigurisë me operatorin tjetër një herë. Pastaj caktoni, për çdo lidhje, çfarë dërgoni dhe merrni dhe sa larg mund të shkojnë paketat tuaja." },
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
  "c.all": { en: "All", sq: "Të gjitha" }, "c.answered": { en: "answered", sq: "me përgjigje" },
  "c.no_answer": { en: "No answer yet.", sq: "Ende pa përgjigje." }, "c.updated": { en: "Last change", sq: "Ndryshimi i fundit" },
  "c.none_filter": { en: "No cases match.", sq: "Asnjë rast nuk përputhet." }, "c.more": { en: "Show more ({n})", sq: "Shfaq më shumë ({n})" },
  "c.lines_hint": { en: "One line per case, newest first. Click a line for the whole text and the answer.", sq: "Një rresht për çdo rast, më i riu i pari. Klikoni një rresht për tekstin e plotë dhe përgjigjen." },
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
  "a.hubs_online": { en: "Hubs online", sq: "Hub-e në linjë" }, "a.open_compl": { en: "Open complaints", sq: "Ankesa të hapura" },
  "a.days": { en: "{n} days left", sq: "edhe {n} ditë" }, "a.n_open": { en: "{n} open", sq: "{n} të hapura" },
  "a.email_unconf": { en: "not confirmed", sq: "pa konfirmuar" },
  "a.reject": { en: "Reject", sq: "Refuzo" }, "a.public_page": { en: "Public page", sq: "Faqja publike" },
  "a.description": { en: "Description", sq: "Përshkrimi" },
  "a.complaints": { en: "Complaints", sq: "Ankesat" }, "a.set_status": { en: "Update case", sq: "Përditëso rastin" },
  "a.nopending": { en: "No requests waiting.", sq: "Nuk ka kërkesa në pritje." },
  "a.change_pw": { en: "Change admin password", sq: "Ndrysho fjalëkalimin e administratorit" },
  "a.requested": { en: "Requested", sq: "Kërkuar" },
  "notfound": { en: "Not found.", sq: "Nuk u gjet." },
  "map.hub_offline": { en: "its hub has been offline since {x}", sq: "hub-i i saj është offline që nga {x}" },
  "adv.offline_grey_h": { en: "Map: show nodes of a hub offline for longer than (hours) in grey", sq: "Harta: shfaq gri nyjet e një hub-i offline më shumë se (orë)" },
  "adv.offline_hide_days": { en: "Map: hide nodes of a hub offline for longer than (days)", sq: "Harta: fshih nyjet e një hub-i offline më shumë se (ditë)" },
    "map.nodes_short": { en: "nodes", sq: "nyje" },
  "hub.no_link_net": { en: "no tunnel", sq: "pa tunel" },
  "hub.mt_link": { en: "Meshtastic tunnel", sq: "Tuneli Meshtastic" }, "hub.mc_link": { en: "MeshCore tunnel", sq: "Tuneli MeshCore" },
  "hub.radio_none": { en: "not used by this hub", sq: "nuk përdoret nga ky hub" },
  "hub.radio_on": { en: "connected", sq: "e lidhur" }, "hub.radio_off": { en: "not connected", sq: "e palidhur" },
  "hub.mt_on": { en: "Meshtastic on this link", sq: "Meshtastic në këtë lidhje" },
  "hub.mc_rules.none": { en: "This hub has not published MeshCore rules (older version).", sq: "Ky hub nuk ka publikuar rregulla MeshCore (version më i vjetër)." },
  "hubs.networks": { en: "Networks", sq: "Rrjetet" },
  "mcr.on": { en: "MeshCore on this link", sq: "MeshCore në këtë lidhje" }, "mcr.adverts": { en: "Adverts", sq: "Reklamat" },
  "mcr.public": { en: "Public channel", sq: "Kanali Public" }, "mcr.private": { en: "Private messages", sq: "Mesazhe private" },
  "mcr.other_groups": { en: "Other people's channels", sq: "Kanalet e të tjerëve" },
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

const ynBadge = v => v ? `<span class="badge ok">${t("rule.on")}</span>` : `<span class="badge bad">${t("rule.off")}</span>`;
function mcRuleTable(m) {
  if (!m) return `<p class="muted small">${t("hub.mc_rules.none")}</p>`;
  const yn = ynBadge, s = m.send || {}, r = m.receive || {}, on = (x, k) => x.on !== false && x[k] !== false;
  return `<table class="small"><tr><th></th><th>${t("rule.send")}</th><th>${t("rule.receive")}</th></tr>
      <tr><td>${t("mcr.on")}</td><td>${yn(s.on !== false)}</td><td>${yn(r.on !== false)}</td></tr>
      <tr><td>${t("mcr.adverts")}</td><td>${yn(on(s, "adverts"))}</td><td>${yn(on(r, "adverts"))}</td></tr>
      <tr><td>${t("mcr.public")}</td><td>${yn(on(s, "public"))}</td><td>${yn(on(r, "public"))}</td></tr>
      <tr><td>${t("mcr.private")}</td><td>${yn(on(s, "private"))}</td><td>${yn(on(r, "private"))}</td></tr>
      <tr><td>${t("rule.groups")}</td><td>${esc((s.groups || []).join(", ") || t("none"))}</td><td>${esc((r.groups || []).join(", ") || t("none"))}</td></tr>
      <tr><td>${t("mcr.other_groups")}</td><td>${yn(s.on !== false && !!s.other_groups)}</td><td>${yn(r.on !== false && !!r.other_groups)}</td></tr>
      <tr><td>${t("rule.transit")}</td><td>${yn(s.transit !== false)}</td><td></td></tr>
      <tr><td>${t("rule.from_beyond")}</td><td></td><td>${yn(r.from_beyond !== false)}</td></tr></table>`;
}
function ruleTable(x) {
  if (!x) return `<p class="muted small">${t("hub.rules.none")}</p>`;
  const yn = ynBadge;
  return `<table class="small"><tr><th></th><th>${t("rule.send")}</th><th>${t("rule.receive")}</th></tr>
      <tr><td>${t("hub.mt_on")}</td><td>${yn(x.send && x.send.on)}</td><td>${yn(x.receive && x.receive.on)}</td></tr>
      <tr><td>${t("rule.public")}</td><td>${yn(x.send && x.send.public)}</td><td>${yn(x.receive && x.receive.public)}</td></tr>
      <tr><td>${t("rule.groups")}</td><td>${esc(((x.send && x.send.groups) || []).join(", ") || t("none"))}</td><td>${esc(((x.receive && x.receive.groups) || []).join(", ") || t("none"))}</td></tr>
      <tr><td>${t("rule.private")}</td><td>${yn(x.send && x.send.private)}</td><td>${yn(x.receive && x.receive.private)}</td></tr>
      <tr><td>${t("rule.positions")}</td><td>${yn(x.send && x.send.positions)}</td><td>${yn(x.receive && x.receive.positions)}</td></tr>
      <tr><td>${t("rule.onward")}</td><td>${reachTxt(x.send || {})}</td><td></td></tr>
      <tr><td>${t("rule.transit")}</td><td>${yn(x.send && x.send.transit !== false)}</td><td></td></tr>
      <tr><td>${t("rule.from_beyond")}</td><td></td><td>${yn(!x.receive || x.receive.from_beyond !== false)}</td></tr></table>`;
}
/* A hub's radios: one row per network — name, hardware, firmware, connected or not; "not used" if it has none. */
function radiosHtml(h) {
  return ["mt", "mc"].map(net => {
    const r = (h.radios || []).find(x => x.net === net);
    const state = !r ? `<span class="muted">${t("hub.radio_none")}</span>`
      : `${r.connected ? `<span class="badge ok"><span class="dot ok"></span>${t("hub.radio_on")}</span>` : `<span class="badge bad">${t("hub.radio_off")}</span>`}
         ${r.name ? `<b>${esc(r.name)}</b>` : ""} <span class="muted small">${esc([r.hw, r.firmware].filter(Boolean).join(" · "))}</span>`;
    return `<div class="radiorow ${net}"><span class="rr-net">${net === "mc" ? "MeshCore" : "Meshtastic"}</span> ${state}</div>`;
  }).join("");
}
function netsCell(h) {
  return ["mt", "mc"].map(net => { const r = (h.radios || []).find(x => x.net === net), n = (h.nodes_net || {})[net] || 0;
    return r ? `<span class="netpill ${net} ${r.connected ? "" : "off"}" title="${esc(r.connected ? t("hub.radio_on") : t("hub.radio_off"))}">${net === "mc" ? "MeshCore" : "Meshtastic"} <b>${n}</b></span>` : ""; }).join(" ") || "–";
}
function generalRules(r) {
  if (!r) return `<p class="muted">${t("hub.rules.none")}</p>`;
  let s = "";
  const tr = (x, extra) => x ? `<b>${x.enabled ? t("hub.transit.on", { n: x.max_hops }) : t("rule.off")}</b>${extra || ""}` : "–";
  const air = a => a ? `<b>${a.pct_hour}${t("pct_hour")}</b>${a.pct_day ? `, <b>${a.pct_day}${t("pct_day")}</b>` : ""}` : "–";
  return `<div class="tablewrap"><table class="small gtable"><tr><th></th><th>Meshtastic</th><th>MeshCore</th></tr>
    <tr><td>${t("hub.transit")}</td><td>${tr(r.transit, (r.transit_to || []).length ? ` — ${t("hub.transit_to", { n: r.transit_to.length })}` : "")}</td><td>${tr(r.transit_mc)}</td></tr>
    <tr><td>${t("rule.airtime")}</td><td>${air(r.airtime)}</td><td>${air(r.airtime_mc)}</td></tr></table></div>`;
}
const chipsOf = r => !r ? `<span class="muted small">–</span>` : !r.on ? `<span class="badge bad">${t("rule.off")}</span>`
  : [r.public && t("ls.pub"), r.private && t("ls.priv"), r.positions && t("ls.pos"), (r.groups || []).length && t("ls.grp", { n: r.groups.length })]
      .filter(Boolean).map(x => `<span class="chip">${x}</span>`).join("") || `<span class="muted small">${t("ls.nothing")}</span>`;
const openHubLinks = new Set();   // links opened on a hub page (kept while browsing)

/* ───────── pages ───────── */

const NODES_FROM_ZOOM = 5;          // below this zoom only hubs and links are drawn (a world of nodes is unreadable)
async function pageMap() {
  const [hubs, nodes, st] = await Promise.all([api("GET", "/api/public/hubs"), api("GET", "/api/public/nodes"),
                                               api("GET", "/api/public/stats?hours=168").catch(() => ({ rows: [] }))]);
  app().innerHTML = `<div id="map" class="fullmap"></div>`;
  mapObj = makeMap("map");
  const m = mapObj, color = {}, bounds = [];
  hubs.forEach((h, i) => color[h.id] = colorFor(i));
  const byId = Object.fromEntries(hubs.map(h => [h.id, h]));
  const pk = {}; (st.rows || []).forEach(r => pk[r.src + ">" + r.dst] = (pk[r.src + ">" + r.dst] || 0) + r.frames);
  // links: one line per pair, clickable
  const lines = {}, linesOf = {};
  hubs.forEach(h => (h.links || []).forEach(l => {
    const p = byId[l.peer], key = [h.id, l.peer].sort().join();
    if (!p || lines[key] || h.lat == null || p.lat == null) return;
    const [x, y] = [h, p].sort((u, v) => u.code.localeCompare(v.code));
    const ln = L.polyline([[x.lat, x.lon], [y.lat, y.lon]], { color: "#0f7b6c", weight: 3, dashArray: "6 6", opacity: .7 })
      .bindPopup(`<b><a href="#/hub/${x.id}">${esc(x.code)}</a> ⇄ <a href="#/hub/${y.id}">${esc(y.code)}</a></b><br>
        <span class="small">${t("map.link7d")}</span><br>${esc(x.code)} → ${esc(y.code)}: <b>${pk[x.id + ">" + y.id] || 0}</b><br>${esc(y.code)} → ${esc(x.code)}: <b>${pk[y.id + ">" + x.id] || 0}</b>
        <br><a href="#/stats">${t("nav.stats")} →</a>`).addTo(m);
    lines[key] = ln; (linesOf[h.id] = linesOf[h.id] || []).push(ln); (linesOf[p.id] = linesOf[p.id] || []).push(ln);
  }));
  // nodes: own layer, shown when zoomed in (and the switch is on)
  const nodeLayer = L.layerGroup(), netLayer = { mt: L.layerGroup().addTo(nodeLayer), mc: L.layerGroup().addTo(nodeLayer) };
  const netCount = { mt: 0, mc: 0 };
  const nowS = Date.now() / 1000, offFor = h => (h && !h.online && h.last_seen) ? nowS - h.last_seen : 0;
  nodes.forEach(n => {
    if (n.lat == null || n.lon == null) return;
    const h = byId[n.hub], mc = n.net === "mc", off = offFor(h);
    if (off > (INFO.offline_hide_days || 3) * 86400) return;          // hub offline for days: its nodes are hidden
    const grey = off > (INFO.offline_grey_h || 24) * 3600;              // hub offline for long: its nodes grey
    netCount[mc ? "mc" : "mt"]++;
    // Meshtastic: round dot with a white rim; MeshCore: same hub colour with a thick dark-orange rim
    L.circleMarker([n.lat, n.lon], mc ? { radius: 6, color: grey ? "#9ca3af" : "#b45309", weight: 3, fillColor: grey ? "#d1d5db" : (color[n.hub] || "#666"), fillOpacity: grey ? .6 : .95 }
                                      : { radius: 6, color: "#fff", weight: 1.5, fillColor: grey ? "#d1d5db" : (color[n.hub] || "#666"), fillOpacity: grey ? .6 : .95 })
      .bindPopup(`<b><a href="${nodeHref(n)}">${esc(n.name || n.id)}</a></b> ${esc(n.short || "")}<br>${netBadge(n.net)}<br>${t("node.on_hub")}: ${h ? `<a href="#/hub/${h.id}">${esc(h.code)}</a>` : ""}${grey ? `<br><span class="muted">${t("map.hub_offline", { x: ago(h.last_seen) })}</span>` : ""}<br>${t("last_heard")}: ${ago(n.last_heard)}`)
      .addTo(netLayer[mc ? "mc" : "mt"]);
    bounds.push([n.lat, n.lon]);
  });
  const hubMarker = {};
  hubs.forEach(h => {
    if (h.lat == null) return;
    hubMarker[h.id] = L.circleMarker([h.lat, h.lon], { radius: 11, color: color[h.id], weight: 3, fillColor: "#fff", fillOpacity: 1 })
      .bindPopup(`<b><a href="#/hub/${h.id}">${esc(h.code)} · ${esc(h.name)}</a></b><br>${onlineBadge(h.online)}<br>${t("map.nodes_on", { n: h.nodes, d: INFO.node_max_age_days })}
        ${(h.links || []).length ? `<br>${t("map.linked_with")}: ${(h.links || []).map(l => `<a href="#/hub/${l.peer}">${esc(l.peer_code)}</a>`).join(", ")}` : ""}`)
      .addTo(m);
    bounds.push([h.lat, h.lon]);
  });
  let showNodes = true;
  const syncNodes = () => {
    const want = showNodes && m.getZoom() >= NODES_FROM_ZOOM;
    if (want && !m.hasLayer(nodeLayer)) { nodeLayer.addTo(m); Object.values(hubMarker).forEach(x => x.bringToFront()); }
    if (!want && m.hasLayer(nodeLayer)) m.removeLayer(nodeLayer);
    const z = $("#zoomhint"); if (z) z.hidden = !(showNodes && m.getZoom() < NODES_FROM_ZOOM && nodes.length);
  };
  m.on("zoomend", syncNodes);
  // panel: one line per hub, search, click = fly there and highlight its links
  const panel = L.control({ position: "topright" });
  panel.onAdd = () => {
    const d = L.DomUtil.create("div", "livebox mappanel");
    const phone = window.matchMedia("(max-width: 760px)").matches;     // on phones: folded into one line
    d.innerHTML = `<details class="mp-fold" ${phone ? "" : "open"}><summary><b>${t("map.hubs")} ${hubs.length}</b> · ${t("map.links_n", { n: Object.keys(lines).length })} · ${netCount.mt + netCount.mc} ${t("map.nodes_short")}</summary>
      <label class="check small"><input type="checkbox" id="liveon" checked> ${t("live.on")}</label><div class="small muted" id="livecount"></div>
      <label class="check small"><input type="checkbox" id="nodeson" checked> ${t("map.show_nodes")}</label>
      <div class="small" style="margin:.1rem 0 .2rem 1.4rem">
        <label class="check small"><input type="checkbox" id="net_mt" checked> <span class="mkr mt"></span> Meshtastic (${netCount.mt})</label>
        <label class="check small"><input type="checkbox" id="net_mc" checked> <span class="mkr mc"></span> MeshCore (${netCount.mc})</label></div>
      <div class="small muted" id="zoomhint" hidden>${t("map.zoom_for_nodes")}</div>
      <details id="hubpanel"><summary class="small"><b>${t("map.hubs")} (${hubs.length})</b> · ${t("map.links_n", { n: Object.keys(lines).length })}</summary>
        ${hubs.length > 6 ? `<input type="text" id="hubq" placeholder="${t("dt.search")}" class="small">` : ""}
        <div class="hublist">${hubs.slice().sort((x, y) => (y.online - x.online) || x.code.localeCompare(y.code)).map(h => `
          <a class="hubline" data-hub="${h.id}" data-q="${esc((h.code + " " + h.name).toLowerCase())}">
            <span class="dot" style="background:${color[h.id]}"></span><b>${esc(h.code)}</b> <span class="muted">${esc(h.name)}</span>
            <span class="hl-meta"><span class="dot ${h.online ? "ok" : "bad"}"></span>${h.nodes} · ${(h.links || []).length}⇄</span></a>`).join("")}</div></details></details>`;
    L.DomEvent.disableClickPropagation(d); L.DomEvent.disableScrollPropagation(d);
    return d;
  };
  panel.addTo(m);
  $("#nodeson").onchange = e => { showNodes = e.target.checked; syncNodes(); };
  ["mt", "mc"].forEach(k => $("#net_" + k).onchange = e => { if (e.target.checked) netLayer[k].addTo(nodeLayer); else nodeLayer.removeLayer(netLayer[k]); });
  if ($("#hubq")) $("#hubq").oninput = e => { const q = e.target.value.toLowerCase(); $$(".hubline").forEach(x => x.style.display = x.dataset.q.includes(q) ? "" : "none"); };
  let hl = [];
  $$(".hubline").forEach(a => a.onclick = () => {
    const h = byId[a.dataset.hub];
    hl.forEach(x => x.setStyle({ weight: 3, opacity: .7, color: "#0f7b6c" })); hl = linesOf[h.id] || [];
    hl.forEach(x => x.setStyle({ weight: 6, opacity: 1, color: color[h.id] }));
    $$(".hubline").forEach(x => x.classList.toggle("sel", x === a));
    if (h.lat != null) { m.setView([h.lat, h.lon], Math.max(m.getZoom(), 8)); hubMarker[h.id].openPopup(); }
  });
  const hubPts = hubs.filter(h => h.lat != null).map(h => L.latLng(h.lat, h.lon));
  const near = hubPts.length ? bounds.filter(b => hubPts.some(h => h.distanceTo(b) < 600000)) : bounds;
  if (near.length) m.fitBounds(near, { padding: [40, 40], maxZoom: 12 });
  // the map fills the screen below the menu (the menu is taller on phones)
  const fitH = () => { const el = $("#map"); if (!el) { window.removeEventListener("resize", fitH); return; }
    el.style.height = Math.max(320, window.innerHeight - el.getBoundingClientRect().top - window.scrollY - 12) + "px"; m.invalidateSize(); };
  fitH(); window.addEventListener("resize", fitH);
  syncNodes();
  liveTraffic(m, byId, color, true);
}

/* Live traffic: every packet passed between two hubs runs as a dot along their link (no content). */
let liveTimer = null;
function liveTraffic(m, byId, color, hasPanel) {
  clearInterval(liveTimer);
  let seq = null, running = 0;
  if (!hasPanel) {
    const box = L.control({ position: "topright" });
    box.onAdd = () => { const d = L.DomUtil.create("div", "livebox"); d.innerHTML = `<label class="check small"><input type="checkbox" id="liveon" checked> ${t("live.on")}</label><div class="small muted" id="livecount"></div>`; L.DomEvent.disableClickPropagation(d); return d; };
    box.addTo(m);
  }
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
  app().innerHTML = `<div class="card"><h2>${t("hubs.title")} (${hubs.length})</h2><p class="muted small">${t("hubs.codes")}</p><div id="hubtable"></div></div>`;
  dataTable($("#hubtable"), hubs.map(h => Object.assign({ nlinks: (h.links || []).length, linkcodes: (h.links || []).map(l => l.peer_code).join(" ") }, h)), [
    { key: "code", label: t("code"), render: h => `<a href="#/hub/${encodeURIComponent(h.id)}"><b>${esc(h.code)}</b></a>` },
    { key: "name", label: t("name"), render: h => esc(h.name), sort: h => (h.name || "").toLowerCase() },
    { key: "online", label: t("status"), render: h => onlineBadge(h.online), sort: h => h.online ? 1 : 0 },
    { key: "nodes", label: `${t("hubs.networks")} · ${t("nodes")} <span class="muted small">(${INFO.node_max_age_days} d)</span>`, render: h => netsCell(h), sort: h => h.nodes },
    { key: "nlinks", label: t("hubs.links"), render: h => h.nlinks ? `<b>${h.nlinks}</b> <span class="muted small">${(h.links || []).slice(0, 4).map(l => `<a href="#/hub/${encodeURIComponent(l.peer)}">${esc(l.peer_code)}</a>`).join(", ")}${h.nlinks > 4 ? " …" : ""}</span>` : "–" },
    { key: "last_seen", label: t("hub.last_seen"), render: h => h.online ? t("online") : ago(h.last_seen), sort: h => h.online ? 9e12 : (h.last_seen || 0) }],
    { searchKeys: ["code", "name", "linkcodes"], initialSort: "online", pageSize: 50, empty: t("map.nohubs") });
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
  const tr = {}, trn = {}; d.stats30d.forEach(r => { const peer = r.src === h.id ? r.dst : r.src, k = r.src === h.id ? "sent" : "recv", net = r.net === "mc" ? "mc" : "mt";
    (tr[peer] = tr[peer] || { sent: 0, recv: 0 })[k] += r.frames;
    ((trn[peer] = trn[peer] || {})[net] = trn[peer][net] || { sent: 0, recv: 0 })[k] += r.frames; });
  const rulesBy = (h.rules && h.rules.links) || {};
  const links = d.links.slice().sort((x, y) => ((tr[y.peer] || {}).sent || 0) + ((tr[y.peer] || {}).recv || 0) - ((tr[x.peer] || {}).sent || 0) - ((tr[x.peer] || {}).recv || 0));
  if (links.length === 1) openHubLinks.add(h.id + ">" + links[0].peer);
  const reachLine = (x, code) => { if (!x || !x.send || !x.send.on) return "–"; const n = x.send.reach != null ? +x.send.reach : ((x.send.onward_to || []).length ? 1 : 0);
    return n === 0 ? t("ls.stop", { x: esc(code) }) : reachTxt(x.send); };
  const linkLine = l => { const x = rulesBy[l.peer_code], c = tr[l.peer] || { sent: 0, recv: 0 };
    return `<div class="linkrow srv">
      <div class="lr-peer"><a href="#/hub/${encodeURIComponent(l.peer)}"><b>${esc(l.peer_code)}</b> · ${esc(l.peer_name)}</a> ${onlineBadge(l.peer_online)}</div>
      <div class="lr-nets">${["mt", "mc"].map(net => { const on = (l.nets || []).includes(net);
          const cc = (trn[l.peer] || {})[net] || { sent: 0, recv: 0 };
          return `<span class="netpill ${net} ${on ? "" : "off"}">${net === "mc" ? "MeshCore" : "Meshtastic"} ${on ? `✓ <span class="muted">↑ ${cc.sent} ↓ ${cc.recv}</span>` : `<span class="muted">${t("hub.no_link_net")}</span>`}</span>`; }).join(" ")}</div>
      <div class="lr-tr"><span class="lr-k">${t("ls.30d")}</span><span title="${esc(t("hub.sent_to", { x: l.peer_code }))}">↑ ${c.sent}</span> <span title="${esc(t("hub.recv_from", { x: l.peer_code }))}">↓ ${c.recv}</span></div></div>`; };
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
        <dt>${t("hub.radios")}</dt><dd>${radiosHtml(h)}</dd>
        <dt>${t("links")}</dt><dd>${d.links.length || t("none")}</dd>
      </dl>${h.description ? `<p>${esc(h.description)}</p>` : ""}</div>
      <div class="card"><div id="hubmap" class="minimap"></div></div>
    </div>
    <div class="card"><div class="spread"><h2>${t("links")} (${links.length})</h2>
        ${links.length > 1 ? `<div class="row"><button class="small" data-lall="1">${t("ls.open_all")}</button><button class="small" data-lall="0">${t("ls.close_all")}</button></div>` : ""}</div>
      ${generalRules(h.rules)}
      ${links.length > 5 ? `<input type="text" id="lfilter" placeholder="${t("dt.search")}" style="max-width:280px;margin-bottom:.5rem">` : ""}
      ${links.length ? `<p class="muted small">${t("ls.hint_srv")}</p>` + links.map(l => `
        <details class="linkbox" data-k="${esc(h.id + ">" + l.peer)}" data-q="${esc((l.peer_code + " " + l.peer_name).toLowerCase())}" ${openHubLinks.has(h.id + ">" + l.peer) ? "open" : ""}>
          <summary>${linkLine(l)}</summary><div class="linkbody"><h3>${t("ls.rules_of", { x: esc(h.code), y: esc(l.peer_code) })}</h3>
            <div class="grid g2">${(l.nets || []).includes("mt") ? `<div class="netbox mt"><div class="nb-head">${t("hub.mt_link")}</div><div class="nb-body">${ruleTable(rulesBy[l.peer_code])}</div></div>` : ""}
              ${(l.nets || []).includes("mc") ? `<div class="netbox mc"><div class="nb-head">${t("hub.mc_link")}</div><div class="nb-body">${mcRuleTable(rulesBy[l.peer_code] && rulesBy[l.peer_code].mc)}</div></div>` : ""}</div></div></details>`).join("")
        : `<p class="muted">${t("none")}</p>`}</div>
    <div class="card"><h2>${t("nodes")} (${d.nodes.length})</h2><div id="hubnodes"></div></div>
    <div class="card"><h2>${t("hub.complaints")}</h2>${d.complaints.length ? d.complaints.map(c => `<div>#${c.id} · ${dt(c.created)} · ${cStatus(c.status)}</div>`).join("") : `<p class="muted">${t("c.none")}</p>`}
      <p><a href="#/complaints?hub=${encodeURIComponent(h.id)}">${t("hub.complain")} →</a></p></div>`;
  $$("details.linkbox").forEach(x => x.addEventListener("toggle", () => { if (x.open) openHubLinks.add(x.dataset.k); else openHubLinks.delete(x.dataset.k); }));
  $$("button[data-lall]").forEach(b => b.onclick = () => $$("details.linkbox").forEach(x => x.open = b.dataset.lall === "1"));
  if ($("#lfilter")) $("#lfilter").oninput = e => { const q = e.target.value.toLowerCase(); $$("details.linkbox").forEach(x => x.style.display = x.dataset.q.includes(q) ? "" : "none"); };
  $$("details.linkbox summary a").forEach(a => a.addEventListener("click", e => e.stopPropagation()));
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
  const near = h.lat != null ? b.filter(x => L.latLng(h.lat, h.lon).distanceTo(x) < 600000) : b;   // far-away nodes don't zoom it out
  if (near.length > 1) m.fitBounds(near, { padding: [30, 30], maxZoom: 13 });
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

const openStats = new Set();      // links whose chart is open on the Statistics page
async function pageStats() {
  const hours = +(new URLSearchParams(location.hash.split("?")[1] || "").get("h") || 168);
  const [d, hubs, nodes] = await Promise.all([api("GET", "/api/public/stats?hours=" + hours), api("GET", "/api/public/hubs"), api("GET", "/api/public/nodes")]);
  const name = id => (d.hubs[id] && d.hubs[id].code) || id;
  const pairs = {};
  // grouped by hub CODE, not internal id: a hub that registered again keeps one chart with its whole history
  const netOf = {};                     // per link (both directions): packets per network
  d.rows.forEach(r => { const src = name(r.src), dst = name(r.dst), k = src + ">" + dst; (pairs[k] = pairs[k] || { src, dst, total: 0, hours: {} }); pairs[k].total += r.frames; pairs[k].hours[r.hour] = (pairs[k].hours[r.hour] || 0) + r.frames;
    const lk_ = [src, dst].sort().join("|"); netOf[lk_] = netOf[lk_] || {}; netOf[lk_][r.net || "mt"] = (netOf[lk_][r.net || "mt"] || 0) + r.frames; });
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
  // one line per link (busiest first); a click opens its chart. Active links without traffic are listed too.
  const linksSeen = {};
  const addLink = (a, b) => { [a, b] = [a, b].sort(); return linksSeen[a + "|" + b] = linksSeen[a + "|" + b] || { a, b, total: 0 }; };
  Object.values(pairs).forEach(p => addLink(p.src, p.dst).total += p.total);
  const byId = {}; hubs.forEach(h => byId[h.id] = h);
  const byCode = {}; hubs.forEach(h => byCode[h.code] = h);
  links.forEach(k => { const [x, y] = k.split(","); if (byId[x] && byId[y]) addLink(byId[x].code, byId[y].code); });
  const lk = Object.values(linksSeen).sort((x, y) => y.total - x.total || (x.a + x.b).localeCompare(y.a + y.b));
  const ser = (src, dst) => pairs[src + ">" + dst] ? series(src + ">" + dst) : Array(n).fill(0);
  const tot = (src, dst) => pairs[src + ">" + dst] ? pairs[src + ">" + dst].total : 0;
  if (lk.length && !openStats.size && lk[0].total) openStats.add(lk[0].a + "|" + lk[0].b);
  const hubA = c => { const h = byCode[c]; return h ? `<a href="#/hub/${encodeURIComponent(h.id)}"><b>${esc(c)}</b></a><span class="dot ${h.online ? "ok" : "bad"}" style="margin-left:.3rem" title="${esc(t(h.online ? "online" : "offline"))}"></span>` : `<b>${esc(c)}</b>`; };
  const line = (x, i) => { const ab = tot(x.a, x.b), ba = tot(x.b, x.a), all = ab + ba, pa = all ? Math.round(100 * ab / all) : 0;
    return `<details class="linkbox" data-k="${esc(x.a + "|" + x.b)}" data-i="${i}" data-q="${esc((x.a + " " + x.b).toLowerCase())}" ${openStats.has(x.a + "|" + x.b) ? "open" : ""}>
      <summary><div class="linkrow lstat">
        <div class="lr-peer">${hubA(x.a)} ⇄ ${hubA(x.b)}</div>
        <div class="chart mini" id="sp${i}"></div>
        <div><span class="lr-k">${esc(x.a)} → ${esc(x.b)}</span><span class="dot" style="background:var(--accent)"></span><b>${ab}</b></div>
        <div><span class="lr-k">${esc(x.b)} → ${esc(x.a)}</span><span class="dot" style="background:var(--info)"></span><b>${ba}</b></div>
        <div><span class="lr-k">${t("stats.share")}</span>${all ? `<div class="sharebar" title="${pa}% / ${100 - pa}%"><span style="width:${pa}%"></span></div>` : `<span class="muted small">${t("stats.no_traffic")}</span>`}</div>
        <div><span class="lr-k">${t("network")}</span>${Object.entries(netOf[x.a + "|" + x.b] || {}).map(([k, v]) => `${netBadge(k)} <b>${v}</b>`).join(" ") || "–"}</div>
        <div class="lr-tr"><span class="lr-k">${t("stats.total")}</span><b>${all}</b></div></div></summary>
      <div class="linkbody"><div class="chart" id="ch${i}"></div></div></details>`; };
  $("#charts").innerHTML = `<div class="card"><div class="spread"><h2>${t("links")} (${lk.length})</h2>
      ${lk.length > 1 ? `<div class="row"><button class="small" data-lall="1">${t("ls.open_all")}</button><button class="small" data-lall="0">${t("ls.close_all")}</button></div>` : ""}</div>
      ${lk.length > 5 ? `<input type="text" id="lfilter" placeholder="${t("dt.search")}" style="max-width:280px;margin-bottom:.5rem">` : ""}
      ${lk.length ? `<p class="muted small">${t("stats.lines_hint")}</p>` + lk.map(line).join("") : `<p class="muted">${t("stats.none")}</p>`}</div>`;
  const names2 = x => [x.a + " → " + x.b, x.b + " → " + x.a];
  lk.forEach((x, i) => splitBarChart($("#sp" + i), labels, ser(x.a, x.b), ser(x.b, x.a), names2(x), { mini: true }));
  const draw = d => { const x = lk[+d.dataset.i]; if (d.open && !d.dataset.drawn) { d.dataset.drawn = 1; splitBarChart($("#ch" + d.dataset.i), labels, ser(x.a, x.b), ser(x.b, x.a), names2(x)); } };
  $$("#charts details.linkbox").forEach(d => { draw(d); d.addEventListener("toggle", () => { draw(d); if (d.open) openStats.add(d.dataset.k); else openStats.delete(d.dataset.k); }); });
  $$("#charts button[data-lall]").forEach(b => b.onclick = () => $$("#charts details.linkbox").forEach(d => d.open = b.dataset.lall === "1"));
  if ($("#lfilter")) $("#lfilter").oninput = e => { const q = e.target.value.toLowerCase(); $$("#charts details.linkbox").forEach(d => d.style.display = d.dataset.q.includes(q) ? "" : "none"); };
  $$("#charts summary a").forEach(a => a.addEventListener("click", e => e.stopPropagation()));
}

const openSteps = new Set([1]);
async function pageJoin() {
  const host = location.hostname, addr = `${host}:${INFO.hub_port}`;
  const hubs = await api("GET", "/api/public/hubs").catch(() => []);
  const copyRow = (label, value, id) => `<div class="copyrow"><div class="lr-k">${label}</div>
      <div class="copybox"><code id="${id}">${esc(value)}</code><button class="small" data-copy="${id}">${t("join.copy")}</button></div></div>`;
  const steps = [1, 2, 3, 4, 5].map(i => `<details class="linkbox" data-step="${i}" ${openSteps.has(i) ? "open" : ""}>
      <summary><div class="linkrow lstep"><div class="stepno">${i}</div><div><b>${t("join.t" + i)}</b>
        <div class="muted small">${t("join.w" + i)}</div></div></div></summary>
      <div class="linkbody"><p>${t("join.s" + i)}</p>${t("join.d" + i) !== "join.d" + i ? `<p class="muted small">${t("join.d" + i)}</p>` : ""}</div></details>`).join("");
  app().innerHTML = `<div class="card"><div class="spread"><h1>${t("join.title")}</h1>
        <div class="row"><a class="btn primary" href="${esc(INFO.install_guide_url)}" target="_blank" rel="noopener">${t("join.guide")}</a>
        <a class="btn" href="${esc(INFO.project_url)}" target="_blank" rel="noopener">${t("join.project")}</a></div></div>
      <p>${t("join.intro")}</p>
      ${INFO.registrations_open ? "" : `<div class="msg warn">${t("join.closed")}</div>`}</div>
    <div class="grid g4" style="margin-bottom:1rem">
      <div class="stat"><div class="v">${INFO.registrations_open ? `<span style="color:var(--ok)">${t("join.open")}</span>` : `<span style="color:var(--warn)">${t("join.closed_short")}</span>`}</div><div class="l">${t("join.registrations")}</div></div>
      <div class="stat"><div class="v">${hubs.length}</div><div class="l">${t("join.hubs_here")}</div></div>
      <div class="stat"><div class="v">${hubs.filter(h => h.online).length}</div><div class="l">${t("stats.hubs_online")}</div></div>
      <div class="stat"><div class="v">${esc(INFO.version || "–")}</div><div class="l">${t("hub.version")}</div></div>
    </div>
    <div class="card"><h2>${t("join.server")}</h2><p class="muted small">${t("join.server_hint")}</p>
      ${copyRow(t("join.address"), addr, "jaddr")}${copyRow(t("join.fp"), INFO.fingerprint || "", "jfp")}</div>
    <div class="card"><div class="spread"><h2>${t("join.steps")} (5)</h2>
        <div class="row"><button class="small" data-sall="1">${t("ls.open_all")}</button><button class="small" data-sall="0">${t("ls.close_all")}</button></div></div>
      <p class="muted small">${t("join.steps_hint")}</p>${steps}
      <p class="muted small" style="margin-top:.8rem">${t("join.email_note")}</p></div>`;
  $$("details[data-step]").forEach(d => d.addEventListener("toggle", () => { const i = +d.dataset.step; if (d.open) openSteps.add(i); else openSteps.delete(i); }));
  $$("button[data-sall]").forEach(b => b.onclick = () => $$("details[data-step]").forEach(d => d.open = b.dataset.sall === "1"));
  $$("button[data-copy]").forEach(b => b.onclick = async () => {
    const txt = $("#" + b.dataset.copy).textContent;
    try { await navigator.clipboard.writeText(txt); }
    catch (e) { const r = document.createRange(); r.selectNodeContents($("#" + b.dataset.copy)); const sel = getSelection(); sel.removeAllRanges(); sel.addRange(r); document.execCommand("copy"); }
    b.textContent = "✓ " + t("join.copied"); setTimeout(() => b.textContent = t("join.copy"), 2000);
  });
}

function cStatus(s) { const c = { open: "warn", review: "info", resolved: "ok", rejected: "bad" }[s] || ""; return `<span class="badge ${c}">${t("c.st." + s)}</span>`; }

/* Complaints as one line per case (status, subject, start of the text); a click opens the whole case.
   Filters by status + search; long lists show 30 at a time. opts.admin: the opened case has the editor. */
const openCases = new Set();
const dshort = ts => { const d = new Date(ts * 1000), p = x => String(x).padStart(2, "0");
  return `${p(d.getDate())}.${p(d.getMonth() + 1)}.${d.getFullYear()} ${p(d.getHours())}:${p(d.getMinutes())}`; };
function complaintList(el, list, hubs, opts) {
  opts = opts || {};
  const byId = {}; (hubs || []).forEach(h => byId[h.id] = h);
  const st = { status: opts.status || "all", q: "", limit: 30 };
  const subj = c => {
    if (c.subject_type === "hub" && byId[c.subject_id]) return `<a href="#/hub/${encodeURIComponent(c.subject_id)}"><b>${esc(byId[c.subject_id].code)}</b></a>`;
    if (c.subject_type === "node" && c.subject_id) return `${t("c.node")} <span class="mono">${esc(c.subject_id)}</span>`;
    if (c.subject_type === "hub") return `${t("hub")} <span class="mono">${esc(c.subject_id || "")}</span>`;
    return `<span class="muted">${t("c.general")}</span>`;
  };
  const subjText = c => (c.subject_type === "hub" && byId[c.subject_id] ? byId[c.subject_id].code + " " + byId[c.subject_id].name : (c.subject_id || "")) + " " + c.subject_type;
  const counts = { all: list.length }; list.forEach(c => counts[c.status] = (counts[c.status] || 0) + 1);
  const short = x => { x = String(x || ""); return x.length > 110 ? x.slice(0, 110) + "…" : x; };
  const body = c => `<p class="ctext">${esc(c.text)}</p>
      ${opts.admin ? `<div class="muted small">${t("c.email")}: ${esc(c.email || "–")}</div>
        <div class="row" style="margin-top:.4rem"><select data-cs="${c.id}">${["open", "review", "resolved", "rejected"].map(x => `<option value="${x}" ${x === c.status ? "selected" : ""}>${t("c.st." + x)}</option>`).join("")}</select></div>
        <label>${t("c.resolution")}</label><textarea data-cr="${c.id}" style="min-height:60px">${esc(c.resolution || "")}</textarea>
        <button class="small" data-csave="${c.id}">${t("a.set_status")}</button>`
      : c.resolution ? `<div class="msg info"><b>${t("c.resolution")}:</b> ${esc(c.resolution)}</div>` : `<p class="muted small">${t("c.no_answer")}</p>`}
      ${c.updated && c.updated !== c.created ? `<div class="muted small">${t("c.updated")}: ${dt(c.updated)}</div>` : ""}`;
  const line = c => `<details class="linkbox" data-case="${c.id}" ${openCases.has(c.id) ? "open" : ""}><summary><div class="linkrow lcase">
      <div><b>#${c.id}</b></div><div>${cStatus(c.status)}</div><div class="muted small nowrap" title="${esc(dt(c.created))}">${dshort(c.created)}</div>
      <div>${subj(c)}</div><div class="ctext-short">${esc(short(c.text))}</div>
      <div class="lr-tr">${c.resolution ? `<span class="badge ok" title="${esc(t("c.resolution"))}">✓ ${t("c.answered")}</span>` : ""}</div></div></summary>
      <div class="linkbody">${body(c)}</div></details>`;
  const draw = () => {
    const q = st.q.toLowerCase();
    const shown = list.filter(c => (st.status === "all" || c.status === st.status) && (!q || (c.text + " " + (c.resolution || "") + " #" + c.id + " " + subjText(c)).toLowerCase().includes(q)));
    $(".clist", el).innerHTML = shown.slice(0, st.limit).map(line).join("") || `<p class="muted">${list.length ? t("c.none_filter") : t("c.none")}</p>`;
    $(".cmore", el).innerHTML = shown.length > st.limit ? `<button class="small" data-more>${t("c.more", { n: shown.length - st.limit })}</button>` : "";
    $$(".cfilter button", el).forEach(b => b.classList.toggle("primary", b.dataset.st === st.status));
  };
  el.innerHTML = `<div class="row cfilter">${["all", "open", "review", "resolved", "rejected"].map(x => `<button class="small" data-st="${x}">${x === "all" ? t("c.all") : t("c.st." + x)} <span class="muted">${counts[x] || 0}</span></button>`).join("")}
      ${list.length > 5 ? `<input type="text" class="cq" placeholder="${t("dt.search")}" style="max-width:240px;margin:0">` : ""}</div>
    <div class="clist"></div><div class="cmore"></div>`;
  el.addEventListener("click", e => {
    const f = e.target.closest(".cfilter button"); if (f) { st.status = f.dataset.st; st.limit = 30; draw(); }
    if (e.target.closest("[data-more]")) { st.limit += 30; draw(); }
  });
  el.addEventListener("toggle", e => { const d = e.target; if (d.dataset && d.dataset.case) { if (d.open) openCases.add(+d.dataset.case); else openCases.delete(+d.dataset.case); } }, true);
  if ($(".cq", el)) $(".cq", el).oninput = e => { st.q = e.target.value; st.limit = 30; draw(); };
  draw();
}

async function pageComplaints() {
  const qs = new URLSearchParams(location.hash.split("?")[1] || "");
  const pre = qs.get("hub") ? ["hub", qs.get("hub")] : qs.get("node") ? ["node", qs.get("node")] : ["general", ""];
  const [list, hubs] = await Promise.all([api("GET", "/api/public/complaints"), api("GET", "/api/public/hubs")]);
  const preHub = pre[0] === "hub" && hubs.find(h => h.id === pre[1]);
  app().innerHTML = `<div class="card"><div class="spread"><h1>${t("c.title")}</h1><button class="primary" id="cnew">${t("c.new")}</button></div><p>${t("c.intro")}</p>
      <div id="cform" ${pre[1] ? "" : "hidden"}><h2>${t("c.new")}${preHub ? ` — ${esc(preHub.code)} · ${esc(preHub.name)}` : ""}</h2>
        <div class="grid g2" style="gap:.5rem 1rem"><div><label>${t("c.about")}</label><select id="cst"><option value="general">${t("c.general")}</option><option value="hub">${t("hub")}</option><option value="node">${t("c.node")}</option></select></div>
        <div><label>${t("c.subject")}</label><input type="text" id="csi" value="${esc(pre[1])}"></div></div>
        <label>${t("c.email")}</label><input type="email" id="cem">
        <label>${t("c.text")}</label><textarea id="ctx"></textarea>
        <div id="cmsg"></div><button class="primary" id="csend">${t("c.send")}</button></div></div>
    <div class="card"><h2>${t("c.list")} (${list.length})</h2><p class="muted small">${t("c.lines_hint")}</p><div id="cases"></div></div>`;
  $("#cst").value = pre[0];
  $("#cnew").onclick = () => { $("#cform").hidden = !$("#cform").hidden; if (!$("#cform").hidden) $("#ctx").focus(); };
  complaintList($("#cases"), list, hubs, { status: pre[1] ? "all" : "all" });
  $("#csend").onclick = async () => {
    try {
      const r = await api("POST", "/api/public/complaints", { subject_type: $("#cst").value, subject_id: $("#csi").value, email: $("#cem").value, text: $("#ctx").value });
      $("#cmsg").innerHTML = `<div class="msg ok">${t("c.sent", { id: r.id })}</div>`; openCases.add(r.id); setTimeout(pageComplaints, 2500);
    } catch (e) { $("#cmsg").innerHTML = `<div class="msg bad">${t("err." + e.message, { n: INFO.complaint_min_chars }) !== "err." + e.message ? t("err." + e.message, { n: INFO.complaint_min_chars }) : esc(e.message)}</div>`; }
  };
}

const adminOpen = new Set();       // admin sections opened/closed by hand ("!id" = closed by hand)
const openAdminHubs = new Set();
/* Hubs on the admin page: one line per hub (Approve right on the line for waiting hubs), details on click,
   search and 30 at a time. */
function adminHubList(el, hubs, nLinks, pendingList) {
  if (!hubs.length) { el.innerHTML = `<p class="muted">${pendingList ? t("a.nopending") : t("none")}</p>`; return; }
  const st = { q: "", limit: 30 };
  const mail = h => h.email_verified ? `<span class="badge ok">${t("a.email_ok")}</span>` : `<span class="badge warn">${t("a.email_no")}</span>`;
  const btns = h => `${pendingList ? `<button class="primary small" data-a="approve" data-id="${h.id}">${t("a.approve")}</button>` : ""}
      ${h.email_verified ? "" : `<button class="small" data-a="verify_email" data-id="${h.id}">${t("a.verify")}</button>`}
      <button class="danger small" data-a="remove" data-id="${h.id}" data-code="${esc(h.code)}">${pendingList ? t("a.reject") : t("a.remove")}</button>`;
  const line = h => `<details class="linkbox" data-hub="${h.id}" ${openAdminHubs.has(h.id) ? "open" : ""}><summary><div class="linkrow lhub">
      <div class="lr-peer"><b>${esc(h.code)}</b> · ${esc(h.name)}</div><div>${onlineBadge(h.online)}</div>
      <div class="small"><span class="lr-k">${t("a.email")}</span>${h.email_verified ? `<span class="badge ok">✓</span>` : `<span class="badge warn" title="${esc(t("a.email_no"))}">${t("a.email_unconf")}</span>`}</div>
      <div class="muted small"><span class="lr-k">${pendingList ? t("a.requested") : t("hub.last_seen")}</span>${pendingList ? dshort(h.created) : h.online ? t("online") : ago(h.last_seen)}</div>
      <div class="small"><span class="lr-k">${t("nodes")} · ${t("links")}</span>${h.nodes || 0} · ${nLinks[h.id] || 0}</div>
      <div class="lr-tr">${pendingList ? `<button class="primary small" data-a="approve" data-id="${h.id}">${t("a.approve")}</button>` : ""}</div></div></summary>
      <div class="linkbody"><dl class="kv" style="margin-top:.6rem">
        <dt>${t("id")}</dt><dd class="mono">${esc(h.id)}</dd>
        <dt>${t("a.email")}</dt><dd>${esc(h.email || "–")} ${mail(h)}</dd>
        <dt>${t("position")}</dt><dd>${fmtPos(h.lat, h.lon)}</dd>
        <dt>${t("a.requested")}</dt><dd>${dt(h.created)}</dd>
        ${h.version ? `<dt>${t("hub.version")}</dt><dd>${esc(h.version)}</dd>` : ""}
        ${h.description ? `<dt>${t("a.description")}</dt><dd>${esc(h.description)}</dd>` : ""}</dl>
        <div class="row">${btns(h)}${pendingList ? "" : `<a class="small" href="#/hub/${encodeURIComponent(h.id)}">${t("a.public_page")} →</a>`}</div></div></details>`;
  const draw = () => {
    const q = st.q.toLowerCase();
    const shown = hubs.filter(h => !q || (h.code + " " + h.name + " " + (h.email || "") + " " + h.id).toLowerCase().includes(q));
    $(".hlist", el).innerHTML = shown.slice(0, st.limit).map(line).join("") || `<p class="muted">${t("c.none_filter")}</p>`;
    $(".hmore", el).innerHTML = shown.length > st.limit ? `<button class="small" data-hmore>${t("c.more", { n: shown.length - st.limit })}</button>` : "";
  };
  el.innerHTML = `${hubs.length > 5 ? `<input type="text" class="hq" placeholder="${t("dt.search")}" style="max-width:280px">` : ""}<div class="hlist"></div><div class="hmore"></div>`;
  el.addEventListener("click", e => { if (e.target.closest("[data-hmore]")) { st.limit += 30; draw(); } });
  el.addEventListener("toggle", e => { const d = e.target; if (d.dataset && d.dataset.hub) { if (d.open) openAdminHubs.add(d.dataset.hub); else openAdminHubs.delete(d.dataset.hub); } }, true);
  if ($(".hq", el)) $(".hq", el).oninput = e => { st.q = e.target.value; st.limit = 30; draw(); };
  draw();
}

async function pageAdmin() {
  INFO = await api("GET", "/api/public/info");
  adminBadge();
  if (INFO.setup_needed || !INFO.admin) {
    app().innerHTML = `<div class="center"><div class="card narrow"><h2>${INFO.setup_needed ? t("setup.title") : t("a.title")}</h2>
      <label>${t("password")}</label><input type="password" id="pw" autocomplete="current-password"><div class="hint">${t("password.min", { n: INFO.password_min })}</div>
      <div id="lmsg"></div><button class="primary" id="lbtn">${INFO.setup_needed ? t("setup.btn") : t("login")}</button></div></div>`;
    const go = async () => {
      try { await api("POST", INFO.setup_needed ? "/api/setup" : "/api/login", { password: $("#pw").value }); route(); }      // route(): menu with Logs for the admin
      catch (e) { $("#lmsg").innerHTML = `<div class="msg bad">${e.message === "wrong_password" ? t("password.wrong") : e.message === "locked" ? t("a.locked") : e.message === "password_short" ? t("password.short") : esc(e.message)}</div>`; }
    };
    $("#lbtn").onclick = go; $("#pw").onkeydown = e => { if (e.key === "Enter") go(); };
    return;
  }
  const s = await api("GET", "/api/admin/state");
  const pending = s.hubs.filter(h => h.status === "pending"), approved = s.hubs.filter(h => h.status === "approved");
  const nLinks = {}; (s.links || []).filter(l => l.state === "active").forEach(l => { nLinks[l.a] = (nLinks[l.a] || 0) + 1; nLinks[l.b] = (nLinks[l.b] || 0) + 1; });
  const openC = s.complaints.filter(c => c.status === "open").length;
  const cert = s.acme.cert, certWarn = s.acme.state !== "off" && (!cert || cert.days_left < 20);
  const sec = (id, title, body, open, attention) => `<details class="acard card ${attention ? "attention" : ""}" id="${id}" ${adminOpen.has(id) || (open && !adminOpen.has("!" + id)) ? "open" : ""}>
      <summary><h2>${title}</h2></summary><div class="acard-body">${body}</div></details>`;
  const tile = (id, v, l, cls) => `<a class="stat tile ${cls || ""}" href="#/admin" data-go="${id}"><div class="v">${v}</div><div class="l">${l}</div></a>`;
  app().innerHTML = `<div id="adminroot"><div class="spread"><h1>${t("a.title")}</h1><button id="lo">${t("logout")}</button></div>
    <div class="grid g4" style="margin-bottom:1rem">
      ${tile("sec-pending", pending.length, t("a.pending"), pending.length ? "warn" : "")}
      ${tile("sec-hubs", `${approved.filter(h => h.online).length} / ${approved.length}`, t("a.hubs_online"))}
      ${tile("sec-compl", openC, t("a.open_compl"), openC ? "warn" : "")}
      ${tile("sec-cert", s.acme.state === "off" ? t("le.st.off") : cert ? t("a.days", { n: cert.days_left }) : "–", t("le.title"), certWarn ? "warn" : "")}
    </div>
    ${sec("sec-pending", `${t("a.pending")} (${pending.length})`, `<div id="hpending"></div>`, pending.length > 0, pending.length > 0)}
    ${sec("sec-hubs", `${t("a.approved")} (${approved.length})`, `<div id="happroved"></div>`, false)}
    ${sec("sec-compl", `${t("a.complaints")} (${s.complaints.length})${openC ? ` <span class="badge warn">${t("a.n_open", { n: openC })}</span>` : ""}`, `<div id="acases"></div>`, openC > 0)}
    ${sec("sec-cert", t("le.title"), `<p class="muted small">${t("le.hint")}</p>
      <p>${t("status")}: <b>${t("le.st." + (s.acme.state || "off"))}</b> ${s.acme.detail ? `<span class="muted small">— ${esc(s.acme.detail)}</span>` : ""}</p>
      ${cert ? `<p class="small">${t("le.cert", { i: esc(cert.issuer), d: cert.days_left })}</p>` : ""}
      <button id="lerun">${t("le.run")}</button> <span class="muted small" id="lemsg"></span>`, certWarn)}
    ${sec("sec-pw", t("a.change_pw"), `<div style="max-width:420px"><input type="password" id="npw"><div class="hint">${t("password.min", { n: INFO.password_min })}</div><div id="pmsg"></div><button id="pbtn">${t("save")}</button></div>`, false)}
    ${sec("sec-adv", t("adv.title"), `<p class="muted small">${t("adv.intro")}</p><div id="advform"></div><div id="advmsg"></div><button class="primary" id="advsave">${t("save")}</button>`, false)}
    ${sec("sec-prog", t("pg.title"), `<div id="pgctl"></div>`, false)}
</div>`;
  $$("details.acard").forEach(d => d.addEventListener("toggle", () => { adminOpen.delete(d.open ? "!" + d.id : d.id); adminOpen.add(d.open ? d.id : "!" + d.id); }));
  $$("[data-go]").forEach(a => a.onclick = e => { e.preventDefault(); const d = $("#" + a.dataset.go); d.open = true; d.scrollIntoView({ behavior: "smooth", block: "start" }); });
  programControl($("#pgctl"), "/api/admin/program", s.started, s.version, "ura-server");
  adminHubList($("#hpending"), pending, nLinks, true);
  adminHubList($("#happroved"), approved, nLinks, false);
  $("#lerun").onclick = async () => { await api("POST", "/api/admin/acme/run", {}); $("#lemsg").textContent = t("le.started"); setTimeout(pageAdmin, 20000); };
  const af = advancedForm($("#advform"), s.advanced_spec, s.advanced, {
    groups: [["adv.g.reg", ["registrations_open", "project_url", "install_guide_url"]],
             ["adv.g.cert", ["acme_enabled", "acme_domain", "acme_email", "acme_staging"]],
             ["adv.g.traffic", ["node_max_age_days", "offline_grey_h", "offline_hide_days", "max_nodes_per_report", "relay_rate_per_s", "relay_burst", "max_box_bytes", "stats_retention_days"]],
             ["adv.g.complaints", ["complaints_per_hour", "complaint_min_chars", "complaint_max_chars"]],
             ["adv.g.security", ["session_hours", "lockout_attempts", "lockout_minutes", "password_min"]],
             ["adv.g.tiles", ["tile_upstream", "tile_contact", "tile_cache_days", "tile_backoff_s"]]],
    depends: { acme_domain: "acme_enabled", acme_email: "acme_enabled", acme_staging: "acme_enabled" } });
  $("#advsave").onclick = async () => {
    try { await api("POST", "/api/admin/advanced", { advanced: af.read() }); af.mark([]); INFO = {}; $("#advmsg").innerHTML = `<div class="msg ok">${t("saved")}</div>`; }
    catch (e) { af.mark((e.data && e.data.fields) || []); $("#advmsg").innerHTML = `<div class="msg bad">${t("adv.invalid")}</div>`; }
  };
  $("#lo").onclick = async () => { await api("POST", "/api/logout", {}); route(); };
  $("#adminroot").addEventListener("click", async e => {
    const b = e.target.closest("button[data-a]"); if (!b) return;
    e.preventDefault(); e.stopPropagation();
    if (b.dataset.a === "remove" && !confirm(t("a.remove_q", { x: b.dataset.code }))) return;
    b.disabled = true; b.textContent = "…";
    await api("POST", `/api/admin/hub/${b.dataset.id}/${b.dataset.a}`, {}); pageAdmin();
  });
  complaintList($("#acases"), s.complaints, s.hubs || [], { admin: true, status: s.complaints.some(c => c.status === "open") ? "open" : "all" });
  $("#acases").addEventListener("click", async e => {
    const b = e.target.closest("button[data-csave]"); if (!b) return;
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

function pageServerLogs() {
  if (!INFO.admin) { location.hash = "#/admin"; return; }
  app().innerHTML = `<div class="card"><h2>${t("lg.title")} — ura-server</h2><p class="muted small">${t("lg.hint")}</p><div id="logs"></div></div>`;
  logViewer($("#logs"), "/api/admin/logs");
}

async function route() {
  renderHeader(t("site.title"), MENU);
  if (mapObj) { mapObj.remove(); mapObj = null; }
  const parts = location.hash.replace(/^#\/?/, "").split("?")[0].split("/").map(decodeURIComponent);
  app().innerHTML = `<p class="muted">${t("loading")}</p>`;
  try {
    INFO = await api("GET", "/api/public/info");          // fresh on every page: admin state + waiting hubs
    renderHeader(t("site.title"), INFO.admin ? [...MENU, ["#/logs", "nav.logs"]] : MENU);   // Logs: admin only
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
      case "logs": return pageServerLogs();
      default: app().innerHTML = `<div class="card">${t("notfound")}</div>`;
    }
  } catch (e) { app().innerHTML = `<div class="card msg bad">${t("error")}: ${esc(e.message)}</div>`; }
}
Ura.onLang = route;
window.addEventListener("hashchange", route);
document.documentElement.lang = Ura.lang;
route();
