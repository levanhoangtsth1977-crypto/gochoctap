(()=>{'use strict';
const q=(d,s)=>d.querySelector(s),qa=(d,s)=>[...d.querySelectorAll(s)];
function boot(frame){
  const d=frame.contentDocument||frame.contentWindow.document;if(!d)return;
  const $=s=>q(d,s), $$=s=>qa(d,s), auditBox=$('#audit'), validator=$('#validator'), preview=$('#preview'), apply=$('#apply'), word=$('#word'), zip=$('#zip'), log=$('#log'), changes=$('#changes'), parts=$('#parts');
  if(!validator||!preview||!changes)return;
  const title=validator.parentElement?.querySelector('h2');
  if(title&&!$('#validateNow')){
    const v=d.createElement('button');v.id='validateNow';v.className='btn y';v.textContent='🛡️ CHẠY VALIDATOR';
    const p=d.createElement('button');p.id='previewNow';p.className='btn i';p.textContent='👁️ CẬP NHẬT PREVIEW';
    title.insertAdjacentElement('afterend',p);title.insertAdjacentElement('afterend',v);
  }
  const audit=t=>{if(!auditBox)return;const now=new Date().toLocaleString('vi-VN');const old=(auditBox.textContent&&auditBox.textContent!=='Audit log.')?auditBox.textContent+'\n':'';auditBox.textContent=old+now+' · '+t};
  const approved=()=>$$('.change.approved').length,total=()=>$$('.change').length;
  const refresh=()=>{const a=approved(),t=total();validator.textContent=t?`🛡️ Preflight sau duyệt · Tổng ${t} Change Set · Đã duyệt ${a} · ${a?'✅ Sẵn sàng áp dụng.':'⚠️ Chưa có mục được duyệt.'}`:'🛡️ Preflight · Chưa có Change Set để kiểm tra.';if(a&&apply&&!apply.dataset.applied)apply.disabled=false;if(log)log.disabled=!t;if(parts&&parts.textContent&&parts.textContent!=='Chưa quét.')preview.textContent=parts.textContent;};
  const bind=(el,fn)=>{if(el&&!el.dataset.bridgeBound){el.dataset.bridgeBound='1';el.addEventListener('click',fn,true)}};
  const approveWire=()=>{$$('.change button[data-a]').forEach(b=>bind(b,()=>setTimeout(()=>{refresh();audit('Duyệt Change Set #'+(+b.dataset.a+1)+'.')},0)));$$('.change button[data-r]').forEach(b=>bind(b,()=>setTimeout(()=>{refresh();audit('Từ chối Change Set #'+(+b.dataset.r+1)+'.')},0)))};
  const bulkWire=()=>$$('#high,#all,#none').forEach(b=>bind(b,()=>setTimeout(()=>{refresh();audit(b.textContent.trim())},50)));
  bind(apply,()=>setTimeout(()=>{apply.dataset.applied='1';validator.textContent='🔎 Đã thực hiện ÁP DỤNG; đang kiểm tra lại nội dung DOCX…';if(word)word.disabled=false;if(zip)zip.disabled=false;if(log)log.disabled=false;audit('Áp dụng Change Set và chuyển sang kiểm tra sau sửa.')},120));
  bind($('#previewNow'),()=>{refresh();audit('Cập nhật Preview.')});
  bind($('#validateNow'),()=>{const a=approved(),t=total();validator.textContent=t?`🛡️ Validator · Tổng ${t} · Đã duyệt ${a} · ${a?'✅ Có thể áp dụng.':'⚠️ Chưa có mục duyệt.'}`:'🛡️ Validator · Chưa có Change Set.';audit('Chạy Validator.')});
  const poll=()=>{approveWire();bulkWire();refresh()};poll();setInterval(poll,500);
}
window.V60Bridge={boot};
})();
