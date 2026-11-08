// Menu of this point's own pages only. The point works on its own; it has no links into the server.
(() => {
  const nav = document.getElementById("menu");
  if (!nav) return;
  const page = nav.dataset.page;
  const item = (key, href, label) => `<a href="${href}" class="${page === key ? "on" : ""}">${label}</a>`;
  nav.innerHTML = item("status", "./", "📊 Status") + item("admin", "settings", "⚙️ Admin");
})();
