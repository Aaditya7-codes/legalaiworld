(() => {
  const path = window.location.pathname;
  const navItems = [
    ['/category/ai-tools/', 'AI Tools'],
    ['/category/legal-research/', 'Legal Research'],
    ['/category/compliance/', 'Compliance'],
    ['/about-us/', 'About']
  ];

  document.querySelectorAll('.masthead .main-nav').forEach((nav) => {
    nav.innerHTML = navItems.map(([href, label]) => {
      const active = path.startsWith(href) || (href === '/about-us/' && path === '/about-us/');
      return `<a${active ? ' class="active"' : ''} href="${href}">${label}</a>`;
    }).join('');
  });

  document.querySelectorAll('[data-current-year]').forEach((node) => {
    node.textContent = new Date().getFullYear();
  });
})();
