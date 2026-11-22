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
/* Menu items: [href, textKey], or {key, items: [[href, textKey], …]} for a menu with a submenu. */
function renderHeader(title, items, extraRight) {
  const hash = location.hash || "#/", cur = hash.split("/")[1] || "";
  const isActive = h => h === hash || ((h.split("/")[1] || "") === cur && (h.split("/").length < 3 || hash.startsWith(h)));
  const item = it => Array.isArray(it)
    ? `<a href="${it[0]}" class="${isActive(it[0]) ? "active" : ""}">${t(it[1])}</a>`
    : `<div class="dd ${it.items.some(x => isActive(x[0])) ? "active" : ""}"><button type="button" class="ddb">${t(it.key)} <span class="caret">▾</span></button>
        <div class="ddm">${it.items.map(x => `<a href="${x[0]}" class="${isActive(x[0]) ? "active" : ""}">${t(x[1])}</a>`).join("")}</div></div>`;
  document.getElementById("top").innerHTML = `
    <div class="in">
      <a class="brand" href="#/">${LOGO}<span>Ura <small>${esc(title)}</small></span></a>
      <nav class="menu">${items.map(item).join("")}</nav>
      ${extraRight || ""}
      <div class="lang"><button data-l="en" class="${Ura.lang === "en" ? "on" : ""}">EN</button><button data-l="sq" class="${Ura.lang === "sq" ? "on" : ""}">SQ</button></div>
    </div>`;
  $$(".lang button").forEach(b => b.onclick = () => Ura.setLang(b.dataset.l));
  $$("nav.menu .ddb").forEach(b => b.onclick = e => {           // open / close a submenu (touch screens; mouse: hover)
    e.stopPropagation(); const d = b.parentElement, was = d.classList.contains("open");
    $$("nav.menu .dd.open").forEach(x => x.classList.remove("open")); if (!was) d.classList.add("open");
  });
  $$("nav.menu .ddm a").forEach(a => a.addEventListener("click", () => $$("nav.menu .dd.open").forEach(x => x.classList.remove("open"))));
}
document.addEventListener("click", () => $$("nav.menu .dd.open").forEach(x => x.classList.remove("open")));

/* Leaflet map with OpenStreetMap tiles. */
function makeMap(el, center, zoom, opts) {
  // no zoom animation: removing a map mid-animation (page change) throws inside Leaflet
  // canvas renderer: hundreds of node markers stay fast
  // opts.guard: a map inside a scrolling page — the mouse wheel scrolls the PAGE; Ctrl/⌘ + wheel zooms the map;
  // on touch screens one finger scrolls the page, two fingers move/zoom the map
  const guard = !!(opts && opts.guard), touch = L.Browser.touch && L.Browser.mobile;
  const m = L.map(el, { worldCopyJump: true, zoomAnimation: false, markerZoomAnimation: false, fadeAnimation: false, preferCanvas: true,
                        scrollWheelZoom: !guard, dragging: !(guard && touch), tap: !(guard && touch) }).setView(center || [45, 15], zoom || 4);
  if (guard) mapGuard(m);
  // tiles come through Ura's own cache (OpenStreetMap blocks anonymous browser requests)
  L.tileLayer("/tiles/{z}/{x}/{y}.png", { maxZoom: 18, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>' }).addTo(m);
  return m;
}
function mapGuard(m) {
  const box = m.getContainer(), mac = /Mac|iPhone|iPad/.test(navigator.platform);
  const hint = L.DomUtil.create("div", "map-hint", box);
  let timer = 0, acc = 0, last = 0;
  const show = text => { hint.textContent = text; hint.classList.add("on"); clearTimeout(timer); timer = setTimeout(() => hint.classList.remove("on"), 1200); };
  box.addEventListener("wheel", e => {
    if (!(e.ctrlKey || e.metaKey)) { show(t(mac ? "map.cmd" : "map.ctrl")); return; }   // let the page scroll
    e.preventDefault();                                                                  // no browser page zoom
    hint.classList.remove("on");
    acc += e.deltaY;
    const now = Date.now();
    if (Math.abs(acc) < 40 && now - last < 250) return;
    last = now;
    const step = acc < 0 ? 1 : -1; acc = 0;
    m.setZoomAround(m.mouseEventToContainerPoint(e), Math.max(m.getMinZoom(), Math.min(m.getMaxZoom(), m.getZoom() + step)));
  }, { passive: false });
  if (L.Browser.touch && L.Browser.mobile) {
    box.addEventListener("touchstart", e => {
      if (e.touches.length >= 2) { m.dragging.enable(); hint.classList.remove("on"); } else { m.dragging.disable(); }
    }, { passive: true });
    box.addEventListener("touchmove", e => { if (e.touches.length === 1) show(t("map.two")); }, { passive: true });
    box.addEventListener("touchend", e => { if (e.touches.length < 2) m.dragging.disable(); }, { passive: true });
  }
}
Ura.add({ "map.ctrl": { en: "Hold Ctrl and scroll to zoom the map", sq: "Mbani Ctrl dhe rrotulloni për të zmadhuar hartën" },
          "map.cmd": { en: "Hold ⌘ and scroll to zoom the map", sq: "Mbani ⌘ dhe rrotulloni për të zmadhuar hartën" },
          "map.two": { en: "Use two fingers to move the map", sq: "Përdorni dy gishta për të lëvizur hartën" } });

const HUB_COLORS = ["#0f7b6c", "#2a56c6", "#c2410c", "#7c3aed", "#b91c1c", "#0e7490", "#a16207", "#be185d"];
function colorFor(i) { return HUB_COLORS[i % HUB_COLORS.length]; }

/* Simple bar chart (SVG). series: [{label, values:[...]}], labels: x labels */
/* One bar per time bucket, split into the two directions of a link (each part = its share).
   a, b: arrays of counts; names: [label A->B, label B->A] */
function splitBarChart(el, labels, a, b, names, opts) {
  const mini = !!(opts && opts.mini);                       // small sparkline: no axis labels
  const W = mini ? 300 : 800, H = mini ? 60 : 230, P = mini ? 0 : 34, n = labels.length || 1;
  const max = Math.max(1, ...a.map((v, i) => v + b[i]));
  const bw = (W - P - 10) / n;
  let s = `<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none"><line class="axis" x1="${P}" y1="${H - 20}" x2="${W}" y2="${H - 20}"/>`;
  if (!mini) s += `<text x="0" y="12">${max}</text><text x="0" y="${H - 22}">0</text>`;
  a.forEach((va, i) => {
    const vb = b[i], tot = va + vb;
    if (!tot) return;
    const top = mini ? 4 : 40, ha = (H - top) * va / max, hb = (H - top) * vb / max, x = P + i * bw, w = Math.max(1, bw - (mini ? 1 : 2));
    const pa = Math.round(100 * va / tot), pb = 100 - pa;
    const tip = `${esc(labels[i])} — ${esc(names[0])}: ${va} (${pa}%) · ${esc(names[1])}: ${vb} (${pb}%)`;
    s += `<g><title>${tip}</title><rect class="bar" x="${x}" y="${H - 20 - ha}" width="${w}" height="${ha}"/>`;
    s += `<rect class="bar2" x="${x}" y="${H - 20 - ha - hb}" width="${w}" height="${hb}"/></g>`;
  });
  const step = Math.ceil(n / 8);
  if (!mini) labels.forEach((l, i) => { if (i % step === 0) s += `<text x="${P + i * bw}" y="${H - 4}">${esc(l)}</text>`; });
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

/* Advanced settings form, in sections.
   spec: {key: {default, min, max}}, values: {key: v}
   opts.groups:  [[titleKey, [keys...]], ...]  — keys not listed land in "Other", so nothing is ever hidden
   opts.depends: {key: booleanKey}             — key is greyed out while booleanKey is off
   Labels come from translations "adv.<key>" (a trailing "(unit)" is shown next to the input) and "adv.<key>.hint". */
function advancedForm(el, spec, values, opts) {
  opts = opts || {};
  const groups = (opts.groups || []).map(([k, keys]) => [k, keys.filter(x => x in spec)]);
  const listed = new Set(groups.flatMap(g => g[1]));
  const rest = Object.keys(spec).filter(k => !listed.has(k));
  if (rest.length) groups.push(["adv.g.other", rest]);
  const val = k => values[k] == null ? spec[k].default : values[k];
  const row = k => {
    const sp = spec[k], v = val(k), full = t("adv." + k), hk = "adv." + k + ".hint";
    const m = full.match(/^(.*?)\s*\(([^()]*)\)\s*$/), label = m ? m[1] : full, unit = m ? m[2] : "";
    const hint = t(hk) !== hk ? `<div class="hint">${t(hk)}</div>` : "";
    const range = sp.min != null ? `${sp.min}–${sp.max} · ` : "";
    const meta = `<div class="adv-meta">${range}${t("adv.default")} ${esc(typeof sp.default === "boolean" ? t(sp.default ? "adv.on" : "adv.off") : String(sp.default))}
      <button type="button" class="linkbtn adv-reset" data-reset="${k}">↺ ${t("adv.reset")}</button></div>`;
    let ctl;
    if (typeof sp.default === "boolean")
      ctl = `<label class="switch"><input type="checkbox" data-adv="${k}" ${v ? "checked" : ""}><span></span></label>`;
    else if (typeof sp.default === "number")
      ctl = `<div class="adv-num"><input type="number" data-adv="${k}" value="${esc(v)}" ${sp.min != null ? `min="${sp.min}" max="${sp.max}"` : ""}>${unit ? `<span class="muted small">${esc(unit)}</span>` : ""}</div>`;
    else
      ctl = `<input type="text" data-adv="${k}" value="${esc(v)}">`;
    const wide = typeof sp.default === "string" ? " wide" : "";
    return `<div class="adv-row${wide}" data-adv-row="${k}"><div class="adv-text"><div class="adv-label">${esc(label)}${typeof sp.default === "number" || !unit ? "" : ` <span class="muted small">(${esc(unit)})</span>`}</div>${hint}</div>
      <div class="adv-ctl">${ctl}${meta}</div></div>`;
  };
  el.innerHTML = `<div class="row adv-tools"><button type="button" class="small" data-all="1">${t("adv.open_all")}</button>
      <button type="button" class="small" data-all="0">${t("adv.close_all")}</button></div>` +
    groups.map(([title, keys]) => `<details class="adv-group" data-group="${title}"><summary><b>${t(title)}</b>
      <span class="muted small">${keys.length}</span> <span class="badge warn adv-changed" hidden></span></summary>
      <div class="adv-body">${keys.map(row).join("")}</div></details>`).join("");
  const input = k => $(`[data-adv="${k}"]`, el);
  const cur = i => i.type === "checkbox" ? i.checked : (i.type === "number" ? Number(i.value) : i.value);
  const refresh = () => {
    $$("[data-adv]", el).forEach(i => {
      const k = i.dataset.adv, changed = String(cur(i)) !== String(spec[k].default);
      i.closest(".adv-row").classList.toggle("changed", changed);
      const dep = opts.depends && opts.depends[k];
      if (dep && input(dep)) { i.disabled = !input(dep).checked; i.closest(".adv-row").classList.toggle("off", i.disabled); }
    });
    $$(".adv-group", el).forEach(g => {
      const n = $$(".adv-row.changed", g).length, b = $(".adv-changed", g);
      b.style.display = n ? "" : "none"; b.textContent = t("adv.n_changed", { n });
    });
  };
  el.addEventListener("input", refresh); el.addEventListener("change", refresh);
  el.addEventListener("click", e => {
    const r = e.target.closest("[data-reset]"), a = e.target.closest("[data-all]");
    if (r) { const i = input(r.dataset.reset), d = spec[r.dataset.reset].default; if (i.type === "checkbox") i.checked = d; else i.value = d; refresh(); }
    if (a) $$(".adv-group", el).forEach(g => g.open = a.dataset.all === "1");
  });
  refresh();
  return {
    read() { const o = {}; $$("[data-adv]", el).forEach(i => o[i.dataset.adv] = cur(i)); return o; },
    mark(fields) {
      $$("[data-adv-row]", el).forEach(r => r.classList.toggle("invalid", (fields || []).includes(r.dataset.advRow)));
      $$(".adv-row.invalid", el).forEach(r => r.closest(".adv-group").open = true);
    },
  };
}
Ura.add({ "adv.title": { en: "Advanced settings", sq: "Cilësime të avancuara" }, "adv.default": { en: "default", sq: "parazgjedhur" },
          "adv.invalid": { en: "Some values are outside their limits (marked red).", sq: "Disa vlera janë jashtë kufijve (të shënuara me të kuqe)." },
          "adv.reset": { en: "default", sq: "parazgjedhja" }, "adv.on": { en: "on", sq: "aktiv" }, "adv.off": { en: "off", sq: "joaktiv" },
          "adv.open_all": { en: "Open all", sq: "Hapi të gjitha" }, "adv.close_all": { en: "Close all", sq: "Mbylli të gjitha" },
          "adv.n_changed": { en: "{n} changed", sq: "{n} ndryshuar" }, "adv.g.other": { en: "Other", sq: "Të tjera" },
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


/* Log viewer (hub: /api/logs, server: /api/admin/logs): newest lines, filter, search, auto-refresh, download. */
let logTimer = null;
function logViewer(el, base, extra) {
  clearInterval(logTimer);
  el.innerHTML = `<div class="row logbar">
      <label class="small">${t("lg.lines")} <select id="lglines"><option>200</option><option selected>500</option><option>2000</option><option>10000</option></select></label>
      <select id="lglevel" style="max-width:200px"><option value="">${t("lg.all")}</option><option value="warning">${t("lg.warn")}</option><option value="error">${t("lg.err")}</option></select>
      <input type="text" id="lgq" placeholder="${t("lg.search")}" style="max-width:240px">
      <label class="check small"><input type="checkbox" id="lgauto" checked> ${t("lg.auto")}</label>
      <button class="small" id="lgnow">${t("lg.refresh")}</button></div>
    <div id="lgfiles" class="small" style="margin:.4rem 0"></div>
    <pre class="logbox" id="lgbox"></pre>`;
  const load = async () => {
    if (!document.body.contains(el)) { clearInterval(logTimer); return; }
    const q = new URLSearchParams(Object.assign({ lines: $("#lglines").value, level: $("#lglevel").value, q: $("#lgq").value }, extra || {}));
    const d = await api("GET", base + "?" + q);
    if (!document.body.contains(el) || !$("#lgbox")) return;        // the page was left meanwhile
    const box = $("#lgbox"), atEnd = box.scrollTop + box.clientHeight >= box.scrollHeight - 40;
    box.innerHTML = d.lines.map(l => `<span class="${/ (ERROR|CRITICAL) /.test(l) ? "lg-e" : / WARNING /.test(l) ? "lg-w" : ""}">${esc(l)}</span>`).join("\n")
      || `<span class="muted">${t("lg.none")}</span>`;
    if (atEnd || !box.dataset.seen) { box.scrollTop = box.scrollHeight; box.dataset.seen = 1; }
    $("#lgfiles").innerHTML = `<span class="muted">${t("lg.download")}:</span> ` + d.files.map(f =>
      `<a href="${base}/file?name=${encodeURIComponent(f.name)}" download data-logfile="${esc(f.name)}">${esc(f.name)}</a> <span class="muted">(${Math.max(1, Math.round(f.size / 1024))} KB)</span>`).join(" · ");
  };
  ["lglines", "lglevel"].forEach(id => $("#" + id).onchange = load);
  $("#lgq").oninput = () => { clearTimeout(el._qt); el._qt = setTimeout(load, 400); };
  $("#lgnow").onclick = load;
  load().catch(e => { if ($("#lgbox")) $("#lgbox").textContent = e.message; });
  logTimer = setInterval(() => { if ($("#lgauto") && $("#lgauto").checked && !document.hidden) load().catch(() => {}); }, 5000);
}

/* Restart / stop of the program itself (not the computer). path: /api/program or /api/admin/program. */
function programControl(el, path, started, version, name) {
  el.innerHTML = `<dl class="kv"><dt>${t("pg.version")}</dt><dd>${esc(version || "–")}</dd><dt>${t("pg.since")}</dt><dd>${started ? new Date(started * 1000).toLocaleString() : "–"} (${ago(started)})</dd></dl>
    <p class="muted small">${t("pg.hint", { x: esc(name) })}</p>
    <div class="row"><button class="primary" id="pgrestart">${t("pg.restart")}</button><button class="danger" id="pgstop">${t("pg.stop")}</button></div>
    <div id="pgmsg"></div>`;
  const wait = async () => {           // poll until the program answers again, then reload the page
    for (let i = 0; i < 60; i++) {
      await new Promise(r => setTimeout(r, 2000));
      try { await fetch("/api/session", { cache: "no-store" }).then(r => { if (!r.ok && r.status !== 401) throw 0; }); location.reload(); return; } catch (e) {}
    }
    $("#pgmsg").innerHTML = `<div class="msg bad">${t("pg.noreturn")}</div>`;
  };
  $("#pgrestart").onclick = async () => {
    if (!confirm(t("pg.restart_q", { x: name }))) return;
    await api("POST", path, { action: "restart" });
    $("#pgmsg").innerHTML = `<div class="msg info">${t("pg.restarting")}</div>`; wait();
  };
  $("#pgstop").onclick = async () => {
    if (!confirm(t("pg.stop_q", { x: name }))) return;
    await api("POST", path, { action: "stop" });
    $("#pgmsg").innerHTML = `<div class="msg warn">${t("pg.stopped", { x: name })}</div>`;
  };
}

Ura.add({
  "nav.logs": { en: "Logs", sq: "Regjistrat" },
  "lg.title": { en: "Log", sq: "Regjistri" }, "lg.lines": { en: "Lines", sq: "Rreshta" },
  "lg.all": { en: "Everything", sq: "Gjithçka" }, "lg.warn": { en: "Warnings and errors", sq: "Paralajmërime dhe gabime" }, "lg.err": { en: "Errors only", sq: "Vetëm gabime" },
  "lg.search": { en: "Search text…", sq: "Kërko tekst…" }, "lg.auto": { en: "update every 5 s", sq: "përditëso çdo 5 s" },
  "lg.refresh": { en: "Refresh", sq: "Rifresko" }, "lg.download": { en: "Download", sq: "Shkarko" }, "lg.none": { en: "No lines.", sq: "Asnjë rresht." },
  "lg.hint": { en: "The program's own log: newest at the bottom. The files keep the last ~5 MB; download one to send it to someone.",
               sq: "Regjistri i vetë programit: më të rejat poshtë. Skedarët mbajnë ~5 MB e fundit; shkarkoni një për ta dërguar." },
  "pg.title": { en: "Program", sq: "Programi" }, "pg.version": { en: "Version", sq: "Versioni" }, "pg.since": { en: "Running since", sq: "Punon që nga" },
  "pg.hint": { en: "Restart or stop the {x} program only — the computer keeps running. After “Stop”, the program (and this page) stay off until it is started again on the computer (sudo systemctl start {x}) or the computer restarts.",
               sq: "Rindiz ose ndalo vetëm programin {x} — kompjuteri vazhdon të punojë. Pas “Ndalo”, programi (dhe kjo faqe) mbeten jashtë deri sa të nisen përsëri në kompjuter (sudo systemctl start {x}) ose kompjuteri të rindizet." },
  "pg.restart": { en: "Restart program", sq: "Rindiz programin" }, "pg.stop": { en: "Stop program", sq: "Ndalo programin" },
  "pg.restart_q": { en: "Restart {x} now? Links pause for a few seconds.", sq: "Të rindizet {x} tani? Lidhjet ndalen për disa sekonda." },
  "pg.stop_q": { en: "Stop {x}? Nothing passes until it is started again on the computer. This page will stop working too.",
                 sq: "Të ndalet {x}? Asgjë nuk kalon deri sa të niset përsëri në kompjuter. Edhe kjo faqe do të ndalojë." },
  "pg.restarting": { en: "Restarting… this page reloads by itself.", sq: "Po rindizet… kjo faqe ringarkohet vetë." },
  "pg.stopped": { en: "{x} is stopped. Start it on the computer: sudo systemctl start {x}", sq: "{x} u ndal. Niseni në kompjuter: sudo systemctl start {x}" },
  "pg.noreturn": { en: "The program did not come back within 2 minutes — look on the computer (journalctl -u …).", sq: "Programi nuk u kthye brenda 2 minutave — shikoni në kompjuter (journalctl -u …)." },
});
