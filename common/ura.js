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
  "password.min": { en: "At least {n} characters.", sq: "Të paktën {n} karaktere." },
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
  // canvas renderer: hundreds of node markers stay fast
  const m = L.map(el, { worldCopyJump: true, zoomAnimation: false, markerZoomAnimation: false, fadeAnimation: false, preferCanvas: true }).setView(center || [45, 15], zoom || 4);
  // tiles come through Ura's own cache (OpenStreetMap blocks anonymous browser requests)
  L.tileLayer("/tiles/{z}/{x}/{y}.png", { maxZoom: 18, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>' }).addTo(m);
  return m;
}
const HUB_COLORS = ["#0f7b6c", "#2a56c6", "#c2410c", "#7c3aed", "#b91c1c", "#0e7490", "#a16207", "#be185d"];
function colorFor(i) { return HUB_COLORS[i % HUB_COLORS.length]; }

/* Simple bar chart (SVG). series: [{label, values:[...]}], labels: x labels */
/* One bar per time bucket, split into the two directions of a link (each part = its share).
   a, b: arrays of counts; names: [label A->B, label B->A] */
function splitBarChart(el, labels, a, b, names) {
  const W = 800, H = 230, P = 34, n = labels.length || 1;
  const max = Math.max(1, ...a.map((v, i) => v + b[i]));
  const bw = (W - P - 10) / n;
  let s = `<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none"><line class="axis" x1="${P}" y1="${H - 20}" x2="${W}" y2="${H - 20}"/>`;
  s += `<text x="0" y="12">${max}</text><text x="0" y="${H - 22}">0</text>`;
  a.forEach((va, i) => {
    const vb = b[i], tot = va + vb;
    if (!tot) return;
    const ha = (H - 40) * va / max, hb = (H - 40) * vb / max, x = P + i * bw, w = Math.max(1, bw - 2);
    const pa = Math.round(100 * va / tot), pb = 100 - pa;
    const tip = `${esc(labels[i])} — ${esc(names[0])}: ${va} (${pa}%) · ${esc(names[1])}: ${vb} (${pb}%)`;
    s += `<g><title>${tip}</title><rect class="bar" x="${x}" y="${H - 20 - ha}" width="${w}" height="${ha}"/>`;
    s += `<rect class="bar2" x="${x}" y="${H - 20 - ha - hb}" width="${w}" height="${hb}"/></g>`;
  });
  const step = Math.ceil(n / 8);
  labels.forEach((l, i) => { if (i % step === 0) s += `<text x="${P + i * bw}" y="${H - 4}">${esc(l)}</text>`; });
  el.innerHTML = s + "</svg>";
}

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

/* Advanced settings form. spec: {key: {default, min, max}}, values: {key: v}. Labels come from
   translations "adv.<key>" and "adv.<key>.hint". Returns a function that reads the form. */
function advancedForm(el, spec, values) {
  const rows = Object.entries(spec).map(([k, sp]) => {
    const v = values[k] == null ? sp.default : values[k];
    const hint = t("adv." + k + ".hint") !== "adv." + k + ".hint" ? t("adv." + k + ".hint") : "";
    const lim = sp.min != null ? ` <span class="muted small">(${sp.min}–${sp.max}; ${t("adv.default")} ${sp.default})</span>` : ` <span class="muted small">(${t("adv.default")} ${esc(String(sp.default))})</span>`;
    if (typeof sp.default === "boolean")
      return `<label class="check" data-adv-row="${k}"><input type="checkbox" data-adv="${k}" ${v ? "checked" : ""}> ${t("adv." + k)}${lim}</label>${hint ? `<div class="hint">${hint}</div>` : ""}`;
    const type = typeof sp.default === "number" ? "number" : "text";
    return `<div data-adv-row="${k}"><label>${t("adv." + k)}${lim}</label><input type="${type}" data-adv="${k}" value="${esc(v)}" ${sp.min != null ? `min="${sp.min}" max="${sp.max}"` : ""}>${hint ? `<div class="hint">${hint}</div>` : ""}</div>`;
  });
  el.innerHTML = rows.join("");
  return {
    read() { const o = {}; $$("[data-adv]", el).forEach(i => o[i.dataset.adv] = i.type === "checkbox" ? i.checked : (i.type === "number" ? Number(i.value) : i.value)); return o; },
    mark(fields) { $$("[data-adv-row]", el).forEach(r => r.style.outline = (fields || []).includes(r.dataset.advRow) ? "2px solid var(--bad)" : ""); },
  };
}
Ura.add({ "adv.title": { en: "Advanced settings", sq: "Cilësime të avancuara" }, "adv.default": { en: "default", sq: "parazgjedhur" },
          "adv.invalid": { en: "Some values are outside their limits (marked red).", sq: "Disa vlera janë jashtë kufijve (të shënuara me të kuqe)." },
          "adv.intro": { en: "Every operational value of this program. The defaults are sensible; change them only if you know why.", sq: "Çdo vlerë operative e këtij programi. Parazgjedhjet janë të arsyeshme; ndryshojini vetëm nëse e dini pse." } });

/* Table for long lists (hundreds of nodes): search box, sortable columns, pages.
   columns: [{key, label, render?(row), sort?(row)}]; opts: {pageSize, searchKeys, initialSort, empty} */
function dataTable(el, rows, columns, opts) {
  opts = Object.assign({ pageSize: 50, searchKeys: [], initialSort: null, desc: true, empty: t("none") }, opts || {});
  const st = { q: "", sort: opts.initialSort, desc: opts.desc, page: 0 };
  el.innerHTML = `<div class="row dt-tools"><input type="text" class="dt-q" placeholder="${t("dt.search")}" style="max-width:280px">
    <span class="muted small dt-info"></span></div><div class="tablewrap"><table class="dt"></table></div><div class="row dt-pager"></div>`;
  const val = (r, c) => c.sort ? c.sort(r) : r[c.key];
  const draw = () => {
    const q = st.q.toLowerCase();
    let list = q ? rows.filter(r => opts.searchKeys.some(k => String(r[k] == null ? "" : r[k]).toLowerCase().includes(q))) : rows.slice();
    if (st.sort) {
      const c = columns.find(x => x.key === st.sort);
      // empty values (e.g. "never heard") always go last, whatever the direction
      list.sort((a, b) => { const x = val(a, c), y = val(b, c); if ((x == null) !== (y == null)) return x == null ? 1 : -1;
                            const r = (x > y) - (x < y); return st.desc ? -r : r; });
    }
    const pages = Math.max(1, Math.ceil(list.length / opts.pageSize));
    st.page = Math.min(st.page, pages - 1);
    const view = list.slice(st.page * opts.pageSize, (st.page + 1) * opts.pageSize);
    $(".dt", el).innerHTML = `<tr>${columns.map(c => `<th data-k="${c.key}" style="cursor:pointer">${c.label}${st.sort === c.key ? (st.desc ? " ▼" : " ▲") : ""}</th>`).join("")}</tr>` +
      (view.map(r => `<tr>${columns.map(c => `<td>${c.render ? c.render(r) : esc(r[c.key] == null ? "–" : r[c.key])}</td>`).join("")}</tr>`).join("")
       || `<tr><td colspan="${columns.length}" class="muted">${opts.empty}</td></tr>`);
    $(".dt-info", el).textContent = t("dt.count", { n: list.length, m: rows.length });
    $(".dt-pager", el).innerHTML = pages > 1 ? `<button class="small" data-p="-1" ${st.page ? "" : "disabled"}>‹</button>
      <span class="small">${t("dt.page", { p: st.page + 1, n: pages })}</span><button class="small" data-p="1" ${st.page < pages - 1 ? "" : "disabled"}>›</button>` : "";
    $$("th[data-k]", el).forEach(th => th.onclick = () => { st.desc = st.sort === th.dataset.k ? !st.desc : true; st.sort = th.dataset.k; draw(); });
    $$("[data-p]", el).forEach(b => b.onclick = () => { st.page += +b.dataset.p; draw(); });
  };
  $(".dt-q", el).oninput = e => { st.q = e.target.value; st.page = 0; draw(); };
  draw();
}
Ura.add({ "dt.search": { en: "Search name or ID…", sq: "Kërko emër ose ID…" },
          "dt.count": { en: "{n} of {m}", sq: "{n} nga {m}" }, "dt.page": { en: "page {p} of {n}", sq: "faqja {p} nga {n}" } });
