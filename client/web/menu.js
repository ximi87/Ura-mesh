// The same full menu as on the server: Map · Dashboard · Manage points · Points ▾, plus this point's Status · Admin.
(() => {
  const nav = document.getElementById("menu");
  if (!nav) return;
  const page = nav.dataset.page;
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const flag = cc => cc && /^[A-Z]{2}$/.test(cc) ? String.fromCodePoint(...[...cc].map(c => 0x1F1A5 + c.charCodeAt(0))) : "🏳️";
  const item = (key, href, label) => `<a href="${href}" class="${page === key ? "on" : ""}">${label}</a>`;
  const ext = (href, label) => href ? `<a href="${esc(href)}" target="_blank" rel="noopener">${label}</a>` : "";
  const draw = m => {
    const srv = m.server_url && /^https?:\/\//.test(m.server_url) ? m.server_url.replace(/\/+$/, "") : "";
    const pts = (m.points || []).map(p => {
      const dot = `<i class="dot ${p.online ? "on" : ""}"></i>`, name = `${flag(p.country)} ${esc(p.name)}`;
      if (p.id === m.me) return `<a href="./">${dot}${name} <span class="muted">this point</span></a>`;
      return /^https?:\/\//.test(p.page_url) ? `<a href="${esc(p.page_url)}" target="_blank" rel="noopener">${dot}${name} <span class="muted">↗</span></a>`
        : `<span>${dot}${name} <span class="muted">no page address</span></span>`;
    }).join("") || `<span class="muted">${srv ? "Not approved by the server yet." : "Not connected to a server."}</span>`;
    nav.innerHTML = item("status", "./", "📊 Status") + item("admin", "settings", "⚙️ Admin") +
      (srv ? `<span class="sep"></span>` + ext(srv + "/", "🗺️ Map") + ext(srv + "/admin/dashboard", "📊 Dashboard") +
        ext(srv + "/admin", "⚙️ Manage points") : "") +
      `<details class="dd"><summary>📡 Points</summary><div class="dd-list">${pts}</div></details>`;
  };
  draw({});
  document.addEventListener("click", e => { const d = nav.querySelector("details.dd"); if (d && !d.contains(e.target)) d.open = false; });
  fetch("api/state").then(r => r.ok ? r.json() : null).then(st => st && st.menu && draw(st.menu)).catch(() => {});
})();
