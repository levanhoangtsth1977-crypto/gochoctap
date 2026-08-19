const buttons = [...document.querySelectorAll('.nav-btn')];
const sections = [...document.querySelectorAll('.content-section')];

function sectionTargetFromHash(){
  return decodeURIComponent(location.hash.replace(/^#/, ''));
}

function showSection(target, updateHistory=false){
  const safeTarget = buttons.some(b => b.dataset.target === target) ? target : 'home';
  buttons.forEach(b => b.classList.toggle('active', b.dataset.target === safeTarget));
  sections.forEach(s => s.classList.toggle('active', s.dataset.section === safeTarget));

  if(updateHistory){
    const newUrl = safeTarget === 'home'
      ? location.pathname + location.search
      : location.pathname + location.search + '#' + encodeURIComponent(safeTarget);
    history.pushState({section: safeTarget}, '', newUrl);
  }

  const topbar = document.querySelector('.topbar');
  window.scrollTo({top: topbar ? topbar.offsetHeight : 0, behavior:'smooth'});
  closeMobileMenu();
}

function createNavigationControls(){
  sections.forEach(section => {
    if(section.dataset.section === 'home' || section.querySelector('.section-navigation')) return;

    const nav = document.createElement('div');
    nav.className = 'section-navigation';
    nav.setAttribute('aria-label', 'Điều hướng trang');
    nav.innerHTML = `
      <button type="button" class="page-back-btn" aria-label="Quay lại trang trước">
        <span aria-hidden="true">←</span> Quay lại
      </button>
      <button type="button" class="page-home-btn" aria-label="Về trang chủ">
        <span aria-hidden="true">🏠</span> Trang chủ
      </button>
    `;

    section.insertBefore(nav, section.firstElementChild);

    nav.querySelector('.page-back-btn').addEventListener('click', () => {
      if(location.hash){
        history.back();
      }else{
        showSection('home', true);
      }
    });

    nav.querySelector('.page-home-btn').addEventListener('click', () => {
      if(section.dataset.section === 'home') return;
      showSection('home', true);
    });
  });
}

buttons.forEach(btn => btn.addEventListener('click', () => {
  showSection(btn.dataset.target, true);
}));

window.addEventListener('popstate', () => {
  const hash = sectionTargetFromHash();
  showSection(hash || 'home', false);
});

const initialHash = sectionTargetFromHash();
history.replaceState({section: initialHash || 'home'}, '', location.href);
showSection(initialHash || 'home', false);
createNavigationControls();

/* ============================================================
   MOBILE MENU — RESPONSIVE HAMBURGER
   ============================================================ */
(function initMobileMenu(){
  const topbar = document.querySelector('.topbar');
  const menu = document.querySelector('.menu');
  if (!topbar || !menu) return;

  if (document.getElementById('mobileMenuToggle')) return;

  const toggle = document.createElement('button');
  toggle.id = 'mobileMenuToggle';
  toggle.type = 'button';
  toggle.className = 'mobile-menu-toggle';
  toggle.setAttribute('aria-label', 'Mở menu');
  toggle.setAttribute('aria-expanded', 'false');
  toggle.innerHTML = '<span class="hamburger-icon" aria-hidden="true"><i></i><i></i><i></i></span><span class="hamburger-label">MENU</span>';

  const overlay = document.createElement('div');
  overlay.id = 'mobileMenuOverlay';
  overlay.className = 'mobile-menu-overlay';
  overlay.setAttribute('aria-hidden', 'true');

  const close = document.createElement('button');
  close.type = 'button';
  close.className = 'mobile-menu-close';
  close.setAttribute('aria-label', 'Đóng menu');
  close.innerHTML = '×';

  topbar.appendChild(toggle);
  topbar.appendChild(overlay);
  menu.appendChild(close);

  function openMobileMenu(){
    menu.classList.add('mobile-open');
    overlay.classList.add('active');
    toggle.classList.add('active');
    toggle.setAttribute('aria-expanded', 'true');
    toggle.setAttribute('aria-label', 'Đóng menu');
    document.body.classList.add('mobile-menu-lock');
  }

  window.closeMobileMenu = function(){
    menu.classList.remove('mobile-open');
    overlay.classList.remove('active');
    toggle.classList.remove('active');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Mở menu');
    document.body.classList.remove('mobile-menu-lock');
  };

  toggle.addEventListener('click', () => {
    if (menu.classList.contains('mobile-open')) window.closeMobileMenu();
    else openMobileMenu();
  });

  close.addEventListener('click', window.closeMobileMenu);
  overlay.addEventListener('click', window.closeMobileMenu);

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') window.closeMobileMenu();
  });

  window.addEventListener('resize', () => {
    if (window.innerWidth > 620) window.closeMobileMenu();
  });
})();
