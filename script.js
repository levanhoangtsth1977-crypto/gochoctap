const buttons = [...document.querySelectorAll('.nav-btn')];
const sections = [...document.querySelectorAll('.content-section')];

function showSection(target, updateHash=true){
  buttons.forEach(b => b.classList.toggle('active', b.dataset.target === target));
  sections.forEach(s => s.classList.toggle('active', s.dataset.section === target));
  if(updateHash){
    history.replaceState(null, '', target === 'home' ? location.pathname : '#' + encodeURIComponent(target));
  }
  const topbar = document.querySelector('.topbar');
  window.scrollTo({top: topbar ? topbar.offsetHeight : 0, behavior:'smooth'});
}

buttons.forEach(btn => btn.addEventListener('click', () => {
  showSection(btn.dataset.target);
  closeMobileMenu();
}));

const hash = decodeURIComponent(location.hash.replace(/^#/, ''));
const valid = buttons.some(b => b.dataset.target === hash);
showSection(valid ? hash : 'home', false);

/* ============================================================
   MOBILE MENU — RESPONSIVE HAMBURGER
   Không thay đổi hệ thống điều hướng hiện tại; chỉ bổ sung
   lớp giao diện mobile cho menu đang có trong index.html.
   ============================================================ */
(function initMobileMenu(){
  const topbar = document.querySelector('.topbar');
  const menu = document.querySelector('.menu');
  if (!topbar || !menu) return;

  // Tránh tạo trùng nếu script được tải lại.
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

  // Đặt nút trong topbar và overlay trước menu để menu vẫn giữ nguyên DOM.
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

  // ESC đóng menu trên thiết bị có bàn phím.
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') window.closeMobileMenu();
  });

  // Khi quay về màn hình desktop, đảm bảo trạng thái mobile được reset.
  window.addEventListener('resize', () => {
    if (window.innerWidth > 620) window.closeMobileMenu();
  });
})();
