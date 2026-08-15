// Dark mode toggle — system preference default, manual override (no localStorage; sandboxed)
(function () {
  var root = document.documentElement;
  var toggle = document.querySelector('[data-theme-toggle]');
  var dark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  root.setAttribute('data-theme', dark ? 'dark' : 'light');
  if (toggle) {
    renderIcon(toggle, dark);
    toggle.addEventListener('click', function () {
      dark = !dark;
      root.setAttribute('data-theme', dark ? 'dark' : 'light');
      renderIcon(toggle, dark);
    });
  }
  function renderIcon(el, isDark) {
    el.setAttribute('aria-label', 'Switch to ' + (isDark ? 'light' : 'dark') + ' mode');
    el.innerHTML = isDark
      ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>'
      : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
  }
})();
