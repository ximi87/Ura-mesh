/* Ura — shared helpers for ura-server and ura-hub pages: language, API calls, formatting, layout. */
"use strict";

const LOGO = `<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M3 22c4-9 22-9 26 0" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/><path d="M8 22v-4M16 22v-7M24 22v-4" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/><path d="M2 25h28" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></svg>`;

const Ura = {
  lang: (() => { try { return localStorage.getItem("ura_lang") || "en"; } catch (e) { return "en"; } })(),
  dict: {},
  add(d) { for (const k in d) this.dict[k] = d[k]; },
  t(key, vars) {
    const e = this.dict[key];
    let s = e ? (e[this.lang] || e.en) : key;
    if (vars) for (const k in vars) s = s.split("{" + k + "}").join(vars[k]);
    return s;
  },
  setLang(l) { this.lang = l; try { localStorage.setItem("ura_lang", l); } catch (e) {} document.documentElement.lang = l; if (this.onLang) this.onLang(); },
};
const t = (k, v) => Ura.t(k, v);

/* Common words used on both sites. Each site adds its own with Ura.add({...}). */
Ura.add({
  "lang.en": { en: "EN", sq: "EN" }, "lang.sq": { en: "SQ", sq: "SQ" },
  "online": { en: "online", sq: "në linjë" }, "offline": { en: "offline", sq: "jashtë linje" },
  "yes": { en: "yes", sq: "po" }, "no": { en: "no", sq: "jo" },
  "save": { en: "Save", sq: "Ruaj" }, "saved": { en: "Saved", sq: "U ruajt" }, "cancel": { en: "Cancel", sq: "Anulo" },
  "login": { en: "Log in", sq: "Hyr" }, "logout": { en: "Log out", sq: "Dil" }, "password": { en: "Password", sq: "Fjalëkalimi" },
  "password.new": { en: "New password", sq: "Fjalëkalim i ri" },
  "password.short": { en: "At least 8 characters.", sq: "Të paktën 8 karaktere." },
  "password.wrong": { en: "Wrong password.", sq: "Fjalëkalim i gabuar." },
  "setup.title": { en: "First start: choose the admin password", sq: "Nisja e parë: zgjidhni fjalëkalimin e administratorit" },
  "setup.btn": { en: "Set password", sq: "Vendos fjalëkalimin" },
  "name": { en: "Name", sq: "Emri" }, "id": { en: "ID", sq: "ID" }, "code": { en: "Code", sq: "Kodi" },
  "hardware": { en: "Hardware", sq: "Pajisja" }, "role": { en: "Role", sq: "Roli" },
  "position": { en: "Position", sq: "Pozicioni" }, "last_heard": { en: "Last heard", sq: "Dëgjuar së fundi" },
  "hops": { en: "Hops away", sq: "Hope larg" }, "status": { en: "Status", sq: "Statusi" },
  "nodes": { en: "Nodes", sq: "Nyjet" }, "hub": { en: "Hub", sq: "Hub" }, "hubs": { en: "Hubs", sq: "Hub-et" },
  "links": { en: "Links", sq: "Lidhjet" }, "link": { en: "Link", sq: "Lidhja" },
  "never": { en: "never", sq: "asnjëherë" }, "unknown": { en: "unknown", sq: "e panjohur" },
  "none": { en: "none", sq: "asnjë" }, "loading": { en: "Loading…", sq: "Duke u ngarkuar…" },
  "error": { en: "Error", sq: "Gabim" }, "network": { en: "Network", sq: "Rrjeti" },
  "meshtastic": { en: "Meshtastic", sq: "Meshtastic" }, "meshcore": { en: "MeshCore", sq: "MeshCore" },
  "ago.s": { en: "{n} s ago", sq: "{n} s më parë" }, "ago.m": { en: "{n} min ago", sq: "{n} min më parë" },
  "ago.h": { en: "{n} h ago", sq: "{n} orë më parë" }, "ago.d": { en: "{n} days ago", sq: "{n} ditë më parë" },
  "both_ways": { en: "both ways", sq: "në të dyja drejtimet" },
  "rule.send": { en: "Send", sq: "Dërgo" }, "rule.receive": { en: "Receive", sq: "Merr" },
  "rule.public": { en: "Public group", sq: "Grupi publik" }, "rule.groups": { en: "Groups", sq: "Grupet" },
  "rule.private": { en: "Private messages", sq: "Mesazhe private" }, "rule.positions": { en: "Positions (coordinates)", sq: "Pozicionet (koordinatat)" },
  "rule.airtime": { en: "Airtime limit", sq: "Kufiri i kohës në ajër" },
  "rule.on": { en: "on", sq: "aktiv" }, "rule.off": { en: "off", sq: "joaktiv" },
  "pct_hour": { en: "% per hour", sq: "% në orë" }, "pct_day": { en: "% per day", sq: "% në ditë" },
  "frames": { en: "packets", sq: "paketa" },
  "map": { en: "Map", sq: "Harta" }, "statistics": { en: "Statistics", sq: "Statistika" },
  "open_page": { en: "Open page", sq: "Hap faqen" }, "details": { en: "Details", sq: "Detaje" },
  "remote": { en: "remote", sq: "në distancë" }, "local": { en: "local", sq: "lokal" },
  "albanian_note": { en: "", sq: "" },
});

function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }
function $(sel, root) { return (root || document).querySelector(sel); }
function $$(sel, root) { return Array.from((root || document).querySelectorAll(sel)); }

async function api(method, path, body) {
  const opt = { method, headers: {}, credentials: "same-origin" };
  if (body !== undefined) { opt.headers["Content-Type"] = "application/json"; opt.body = JSON.stringify(body); }
  const r = await fetch(path, opt);
  let data = null;
  try { data = await r.json(); } catch (e) { data = {}; }
  if (!r.ok) { const err = new Error((data && data.error) || ("HTTP " + r.status)); err.status = r.status; err.data = data; throw err; }
  return data;
}

function ago(ts) {
  if (!ts) return t("never");
  const s = Math.max(0, Math.round(Date.now() / 1000 - ts));
  if (s < 90) return t("ago.s", { n: s });
  if (s < 5400) return t("ago.m", { n: Math.round(s / 60) });
  if (s < 172800) return t("ago.h", { n: Math.round(s / 3600) });
  return t("ago.d", { n: Math.round(s / 86400) });
}
function dt(ts) { return ts ? new Date(ts * 1000).toLocaleString(Ura.lang === "sq" ? "sq-AL" : "en-GB") : "–"; }
function fmtPos(lat, lon) { return (lat == null || lon == null) ? "–" : `${(+lat).toFixed(5)}, ${(+lon).toFixed(5)}`; }
function onlineBadge(on) { return on ? `<span class="badge ok"><span class="dot ok"></span>${t("online")}</span>` : `<span class="badge"><span class="dot"></span>${t("offline")}</span>`; }

/* Header with brand, menu and language switch. items: [[hash, labelKey], ...] */
function renderHeader(title, items, extraRight) {
  const cur = location.hash.split("/")[1] || "";
  document.getElementById("top").innerHTML = `
    <div class="in">
      <a class="brand" href="#/">${LOGO}<span>Ura <small>${esc(title)}</small></span></a>
      <nav class="menu">${items.map(([h, k]) => `<a href="${h}" class="${(h.split("/")[1] || "") === cur ? "active" : ""}">${t(k)}</a>`).join("")}</nav>
      ${extraRight || ""}
      <div class="lang"><button data-l="en" class="${Ura.lang === "en" ? "on" : ""}">EN</button><button data-l="sq" class="${Ura.lang === "sq" ? "on" : ""}">SQ</button></div>
    </div>`;
  $$(".lang button").forEach(b => b.onclick = () => Ura.setLang(b.dataset.l));
}

/* Leaflet map with OpenStreetMap tiles. */
function makeMap(el, center, zoom) {
  // no zoom animation: removing a map mid-animation (page change) throws inside Leaflet
  const m = L.map(el, { worldCopyJump: true, zoomAnimation: false, markerZoomAnimation: false, fadeAnimation: false }).setView(center || [45, 15], zoom || 4);
  // tiles come through Ura's own cache (OpenStreetMap blocks anonymous browser requests)
  L.tileLayer("/tiles/{z}/{x}/{y}.png", { maxZoom: 18, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>' }).addTo(m);
  return m;
}
const HUB_COLORS = ["#0f7b6c", "#2a56c6", "#c2410c", "#7c3aed", "#b91c1c", "#0e7490", "#a16207", "#be185d"];
function colorFor(i) { return HUB_COLORS[i % HUB_COLORS.length]; }

/* Simple bar chart (SVG). series: [{label, values:[...]}], labels: x labels */
function barChart(el, labels, series) {
  const W = 800, H = 220, P = 30, n = labels.length || 1;
  const max = Math.max(1, ...series.flatMap(s => s.values));
  const bw = (W - P - 10) / n;
  let s = `<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none"><line class="axis" x1="${P}" y1="${H - 20}" x2="${W}" y2="${H - 20}"/>`;
  s += `<text x="0" y="12">${max}</text><text x="0" y="${H - 22}">0</text>`;
  series.forEach((ser, si) => ser.values.forEach((v, i) => {
    const h = (H - 40) * v / max, w = bw / series.length;
    s += `<rect class="${si ? "bar2" : "bar"}" x="${P + i * bw + si * w}" y="${H - 20 - h}" width="${Math.max(1, w - 1)}" height="${h}"><title>${esc(labels[i])}: ${v}</title></rect>`;
  }));
  const step = Math.ceil(n / 8);
  labels.forEach((l, i) => { if (i % step === 0) s += `<text x="${P + i * bw}" y="${H - 4}">${esc(l)}</text>`; });
  el.innerHTML = s + "</svg>";
}
