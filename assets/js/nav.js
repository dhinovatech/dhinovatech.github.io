/* Dhinovatech Navbar & Submenu Touch Handler */
document.addEventListener('DOMContentLoaded', function () {
  const submenuToggles = document.querySelectorAll('.dropdown-submenu > .dropdown-toggle');

  submenuToggles.forEach(function (toggle) {
    toggle.addEventListener('click', function (e) {
      const parent = this.parentElement;
      const menu = parent.querySelector('.dropdown-menu');
      if (!menu) return;

      const isTouchOrMobile = window.innerWidth < 992 || ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);

      if (isTouchOrMobile) {
        if (!menu.classList.contains('show')) {
          e.preventDefault();
          e.stopPropagation();

          // Close other open submenus in the same dropdown
          const openSiblings = parent.parentElement.querySelectorAll('.dropdown-submenu.show, .dropdown-submenu .dropdown-menu.show');
          openSiblings.forEach(function (el) {
            el.classList.remove('show');
          });

          parent.classList.add('show');
          menu.classList.add('show');
        }
      }
    });
  });

  // Ensure nested submenus close when main dropdown closes
  const mainDropdowns = document.querySelectorAll('.nav-item.dropdown');
  mainDropdowns.forEach(function (dropdown) {
    dropdown.addEventListener('hidden.bs.dropdown', function () {
      const activeSubmenus = this.querySelectorAll('.dropdown-submenu, .dropdown-menu');
      activeSubmenus.forEach(function (el) {
        el.classList.remove('show');
      });
    });
  });
});
