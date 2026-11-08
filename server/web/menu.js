// Menu of the server's own pages only. The server does not reach into the points.
(() => {
  const nav = document.getElementById("menu");
  if (!nav) return;
  const page = nav.dataset.page, admin = nav.dataset.admin === "1";
  const item = (key, href, label) => `<a href="${href}" class="${page === key ? "on" : ""}">${label}</a>`;
  nav.innerHTML = item("map", "/", "🗺️ Map") +
    (admin ? item("dashboard", "/admin/dashboard", "📊 Dashboard") + item("admin", "/admin", "⚙️ Points &amp; rules")
      : item("login", "/admin/dashboard", "🔐 Admin"));
})();
