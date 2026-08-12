
const buttons = [...document.querySelectorAll('.nav-btn')];
const sections = [...document.querySelectorAll('.content-section')];

function showSection(target, updateHash=true){
  buttons.forEach(b => b.classList.toggle('active', b.dataset.target === target));
  sections.forEach(s => s.classList.toggle('active', s.dataset.section === target));
  if(updateHash){
    history.replaceState(null, '', target === 'home' ? location.pathname : '#' + encodeURIComponent(target));
  }
  window.scrollTo({top: document.querySelector('.topbar').offsetHeight, behavior:'smooth'});
}

buttons.forEach(btn => btn.addEventListener('click', () => showSection(btn.dataset.target)));

const hash = decodeURIComponent(location.hash.replace(/^#/, ''));
const valid = buttons.some(b => b.dataset.target === hash);
showSection(valid ? hash : 'home', false);
