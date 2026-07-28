const menu = document.querySelector(".menu-button");
const sidebar = document.querySelector(".sidebar");

if (menu && sidebar) {
  menu.addEventListener("click", () => sidebar.classList.toggle("open"));
  document.addEventListener("click", (event) => {
    if (window.innerWidth <= 900 && !sidebar.contains(event.target) && !menu.contains(event.target)) {
      sidebar.classList.remove("open");
    }
  });
}
