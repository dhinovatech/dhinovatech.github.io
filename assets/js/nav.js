/* Dhinovatech Navbar & Submenu Touch Handler */
document.addEventListener('DOMContentLoaded', function () {
  const submenuContainers = document.querySelectorAll('.dropdown-submenu');

  submenuContainers.forEach(function (container) {
    const link = container.querySelector('a[href]');
    const menu = container.querySelector('.dropdown-menu');
    const toggleBtn = container.querySelector('.submenu-toggle-btn');

    if (toggleBtn && menu) {
      toggleBtn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();

        const isShown = menu.classList.contains('show');

        // Close other open submenus in the same list
        const parentList = container.parentElement;
        if (parentList) {
          const openMenus = parentList.querySelectorAll('.dropdown-menu.show');
          openMenus.forEach(m => {
            if (m !== menu) m.classList.remove('show');
          });
          const openSubmenus = parentList.querySelectorAll('.dropdown-submenu.show');
          openSubmenus.forEach(s => {
            if (s !== container) s.classList.remove('show');
          });
        }

        if (!isShown) {
          container.classList.add('show');
          menu.classList.add('show');
        } else {
          container.classList.remove('show');
          menu.classList.remove('show');
        }
      });
    }

    if (link) {
      link.addEventListener('click', function (e) {
        // If click target is the submenu toggle button, let toggle handler process it
        if (e.target.closest('.submenu-toggle-btn')) {
          return;
        }
        // Otherwise navigate directly to href
        const href = this.getAttribute('href');
        if (href && href !== '#' && href !== 'javascript:void(0)') {
          window.location.href = href;
        }
      });
    }
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
