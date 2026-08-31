document.addEventListener('DOMContentLoaded', () => {
  const menu = document.querySelector('.menu');
  if (menu && !menu.querySelector('[data-target="Giáo án Master Editor"]')) {
    const row = menu.querySelector('.menu-row');
    const btn = document.createElement('a');
    btn.className = 'nav-btn nav-master-editor';
    btn.href = 'sua-giao-an/v08.html';
    btn.target = '_blank';
    btn.rel = 'noopener noreferrer';
    btn.style.textDecoration = 'none';
    btn.innerHTML = '<span>🛠️</span>Master Editor';
    if (row) row.appendChild(btn);
  }

  const buttons = [...document.querySelectorAll('.nav-btn')];
  const sections = [...document.querySelectorAll('.content-section')];
  const NAV_KEY = 'gochoctap_navigation_stack_v2';
  let navigationStack = [];
  try {
    const saved = JSON.parse(sessionStorage.getItem(NAV_KEY) || '[]');
    if (Array.isArray(saved)) navigationStack = saved.filter(Boolean);
  } catch (_) {}
  const isValidTarget = target => buttons.some(b => b.dataset.target === target);
  const normalizeTarget = target => isValidTarget(target) ? target : 'home';
  const currentTarget = () => navigationStack[navigationStack.length - 1] || 'home';
  function persistNavigation(){ try { sessionStorage.setItem(NAV_KEY, JSON.stringify(navigationStack)); } catch (_) {} }
  function targetFromHash(){ try { return decodeURIComponent(location.hash.slice(1)); } catch (_) { return ''; } }
  function updateUrl(target, replace=false){
    const url = target === 'home' ? location.pathname + location.search : location.pathname + location.search + '#' + encodeURIComponent(target);
    if (replace) history.replaceState({section: target}, '', url); else history.pushState({section: target}, '', url);
  }
  function render(target){
    const safe = normalizeTarget(target);
    buttons.forEach(btn => btn.classList.toggle('active', btn.dataset.target === safe));
    sections.forEach(section => section.classList.toggle('active', section.dataset.section === safe));
    if (typeof window.closeMobileMenu === 'function') window.closeMobileMenu();
    window.scrollTo({top: 0, behavior: 'smooth'});
    return safe;
  }
  function openMenu(target){
    const safe = render(target);
    if (currentTarget() !== safe) navigationStack.push(safe);
    persistNavigation(); updateUrl(safe); updateGlobalControls();
  }
  function goBack(){
    if (navigationStack.length > 1) { navigationStack.pop(); const previous = currentTarget(); render(previous); persistNavigation(); updateUrl(previous); updateGlobalControls(); }
    else goHome();
  }
  function goHome(){ navigationStack = ['home']; render('home'); persistNavigation(); updateUrl('home'); updateGlobalControls(); }
  function updateGlobalControls(){
    const controls = document.getElementById('globalNavigationControls'); if (!controls) return;
    const isHome = currentTarget() === 'home'; controls.classList.toggle('visible', !isHome); controls.setAttribute('aria-hidden', isHome ? 'true' : 'false');
  }
  function createGlobalControls(){
    if (document.getElementById('globalNavigationControls')) return;
    const controls = document.createElement('div'); controls.id = 'globalNavigationControls'; controls.className = 'global-navigation-controls';
    controls.innerHTML = '<button type="button" class="page-back-btn" id="globalBackBtn" aria-label="Quay lại menu liền trước"><span aria-hidden="true">←</span> Quay lại</button><button type="button" class="page-home-btn" id="globalHomeBtn" aria-label="Về trang chủ"><span aria-hidden="true">🏠</span> Trang chủ</button>';
    const topbar = document.querySelector('.topbar'); if (topbar) topbar.insertAdjacentElement('afterend', controls); else document.body.prepend(controls);
    controls.querySelector('#globalBackBtn').addEventListener('click', goBack); controls.querySelector('#globalHomeBtn').addEventListener('click', goHome);
  }
  function createSectionControls(){
    sections.forEach(section => {
      if (section.dataset.section === 'home' || section.querySelector('.section-navigation')) return;
      const nav = document.createElement('div'); nav.className = 'section-navigation'; nav.setAttribute('aria-label', 'Điều hướng trang');
      nav.innerHTML = '<button type="button" class="page-back-btn" aria-label="Quay lại menu liền trước"><span aria-hidden="true">←</span> Quay lại</button><button type="button" class="page-home-btn" aria-label="Về trang chủ"><span aria-hidden="true">🏠</span> Trang chủ</button>';
      section.insertBefore(nav, section.firstElementChild); nav.querySelector('.page-back-btn').addEventListener('click', goBack); nav.querySelector('.page-home-btn').addEventListener('click', goHome);
    });
  }
  buttons.forEach(btn => { if (btn.tagName === 'BUTTON') btn.addEventListener('click', () => openMenu(btn.dataset.target)); });
  window.addEventListener('popstate', () => { const safe = render(targetFromHash() || 'home'); if (currentTarget() !== safe) navigationStack.push(safe); persistNavigation(); updateGlobalControls(); });
  const initial = normalizeTarget(targetFromHash() || 'home'); navigationStack = [initial]; render(initial); updateUrl(initial, true); createGlobalControls(); createSectionControls(); updateGlobalControls();
  (function initMobileMenu(){
    const topbar = document.querySelector('.topbar'); const menu = document.querySelector('.menu'); if (!topbar || !menu || document.getElementById('mobileMenuToggle')) return;
    const toggle = document.createElement('button'); toggle.id='mobileMenuToggle'; toggle.type='button'; toggle.className='mobile-menu-toggle'; toggle.setAttribute('aria-label','Mở menu'); toggle.setAttribute('aria-expanded','false'); toggle.innerHTML='<span class="hamburger-icon" aria-hidden="true"><i></i><i></i><i></i></span><span class="hamburger-label">MENU</span>';
    const overlay=document.createElement('div'); overlay.id='mobileMenuOverlay'; overlay.className='mobile-menu-overlay'; overlay.setAttribute('aria-hidden','true');
    const close=document.createElement('button'); close.type='button'; close.className='mobile-menu-close'; close.setAttribute('aria-label','Đóng menu'); close.innerHTML='×';
    topbar.appendChild(toggle); topbar.appendChild(overlay); menu.appendChild(close);
    function openMobileMenu(){ menu.classList.add('mobile-open'); overlay.classList.add('active'); toggle.classList.add('active'); toggle.setAttribute('aria-expanded','true'); toggle.setAttribute('aria-label','Đóng menu'); document.body.classList.add('mobile-menu-lock'); }
    window.closeMobileMenu=function(){ menu.classList.remove('mobile-open'); overlay.classList.remove('active'); toggle.classList.remove('active'); toggle.setAttribute('aria-expanded','false'); toggle.setAttribute('aria-label','Mở menu'); document.body.classList.remove('mobile-menu-lock'); };
    toggle.addEventListener('click',()=>menu.classList.contains('mobile-open')?window.closeMobileMenu():openMobileMenu()); close.addEventListener('click',window.closeMobileMenu); overlay.addEventListener('click',window.closeMobileMenu); document.addEventListener('keydown',e=>{if(e.key==='Escape')window.closeMobileMenu();}); window.addEventListener('resize',()=>{if(window.innerWidth>620)window.closeMobileMenu();});
  })();
});