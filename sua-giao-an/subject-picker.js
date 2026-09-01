(()=>{'use strict';
function install(){
 const sel=document.getElementById('subject'); if(!sel||sel.dataset.checkboxReady)return;
 sel.dataset.checkboxReady='1';
 const wrap=document.createElement('div'); wrap.id='subjectCheckboxes'; wrap.style.cssText='display:grid;gap:6px;margin:6px 0 8px';
 [...sel.options].forEach((o)=>{
  const label=document.createElement('label');
  label.style.cssText='display:flex;align-items:center;gap:8px;padding:7px 9px;border:1px solid #d8e1ee;border-radius:8px;background:#fff;cursor:pointer;user-select:none';
  const cb=document.createElement('input'); cb.type='checkbox'; cb.value=o.value; cb.style.cssText='width:16px;height:16px;accent-color:#1f5eea;cursor:pointer';
  cb.checked=o.selected;
  cb.addEventListener('change',()=>{o.selected=cb.checked; sel.dispatchEvent(new Event('change',{bubbles:true}));});
  const text=document.createElement('span'); text.textContent=o.textContent; label.append(cb,text); wrap.appendChild(label);
 });
 sel.style.display='none'; sel.parentNode.insertBefore(wrap,sel);
 const sync=()=>wrap.querySelectorAll('input').forEach(cb=>{const o=[...sel.options].find(x=>x.value===cb.value); if(o)cb.checked=o.selected});
 new MutationObserver(sync).observe(sel,{attributes:true,subtree:true});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install);else install();
})();