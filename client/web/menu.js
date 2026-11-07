// One menu for every page of this point: Status · Admin · Ura server.
(() => {
  const nav = document.getElementById("menu");
  if (!nav) return;
  const page = nav.dataset.page;
  const item = (key, href, label) => `<a href="${href}" class="${page === key ? "on" : ""}">${label}</a>`;
  nav.innerHTML = item("status", "./", "📊 Status") + item("admin", "settings", "⚙️ Admin") +
    `<a id="menu-server" href="#" target="_blank" rel="noopener" hidden>🌍 Ura server ↗</a>`;
  fetch("api/state").then(r => r.ok ? r.json() : null).then(st => {
    const url = st && st.server && st.server.enabled && st.server.url;
    if (url && /^https?:\/\//.test(url)) { const a = document.getElementById("menu-server"); a.href = url.replace(/\/+$/, "") + "/"; a.hidden = false; }
  }).catch(() => {});
})();
