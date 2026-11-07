// One menu for every server page: Map · Dashboard · Manage points · Points ▾ (each point's own page).
(() => {
  const nav = document.getElementById("menu");
  if (!nav) return;
  const page = nav.dataset.page, admin = nav.dataset.admin === "1";
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const flag = cc => cc && /^[A-Z]{2}$/.test(cc) ? String.fromCodePoint(...[...cc].map(c => 0x1F1A5 + c.charCodeAt(0))) : "🏳️";
  const item = (key, href, label) => `<a href="${href}" class="${page === key ? "on" : ""}">${label}</a>`;
  nav.innerHTML = item("map", "/", "🗺️ Map") +
    (admin ? item("dashboard", "/admin/dashboard", "📊 Dashboard") + item("admin", "/admin", "⚙️ Manage points") +
      `<details class="dd"><summary>📡 Points</summary><div class="dd-list" id="menu-points"><span class="muted">loading…</span></div></details>`
      : item("login", "/admin/dashboard", "🔐 Admin"));
  if (!admin) return;
  document.addEventListener("click", e => { const d = nav.querySelector("details.dd"); if (d && !d.contains(e.target)) d.open = false; });
  fetch("/api/admin/state").then(r => r.ok ? r.json() : null).then(st => {
    const box = document.getElementById("menu-points");
    if (!st) { box.innerHTML = `<a href="/admin/login">🔐 Log in to see the points</a>`; return; }
    const list = ((st && st.bridges) || []).filter(b => b.status === "approved");
    box.innerHTML = list.length ? list.map(b => {
      const dot = `<i class="dot ${b.online ? "on" : ""}"></i>`;
      const name = `${flag(b.country)} ${esc(b.name)}`;
      return b.page_url ? `<a href="${esc(b.page_url)}" target="_blank" rel="noopener">${dot}${name} <span class="muted">↗</span></a>`
        : `<span title="This point has not set its page address (Admin → This point)">${dot}${name} <span class="muted">no page address</span></span>`;
    }).join("") : `<span class="muted">No approved points yet.</span>`;
  }).catch(() => {});
})();
