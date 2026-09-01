(()=>{'use strict';
const q=(d,s)=>d.querySelector(s),qa=(d,s)=>[...d.querySelectorAll(s)];
function boot(frame){
  const d=frame.contentDocument||frame.contentWindow.document;if(!d)return;
  const $=s=>q(d,s), $$=s=>qa(d,s), auditBox=$('#audit'), validator=$('#validator'), preview=$('#preview'), apply=$('#apply'), word=$('#word'), zip=$('#zip'), log=$('#log'), bulk=$('#bulkStatus'), changes=$('#changes'), parts=$('#parts');
  if(!validator||!preview||!changes)return;
  const audit=t=>{if(!auditBox)return;const now=new Date().toLocaleString('vi-VN');auditBox.textContent=((auditBox.textContent&&auditBox.textContent!=='Audit log.')?auditBox.textContent+'\n':'')+now+' · '+t};
  const approved=()=>$$('.change.approved').length;
  const total=()=>$$('.change').length;
  const refresh=()=>{const a=approved(),t=total();validator.textContent=t?`🛡️ Preflight sau duyệt · Tổng ${t} Change Set · Đã duyệt ${a} · ${a?'✅ Sẵn sàng áp dụng.':'⚠️ Chưa có mục được duyệt.'}`:'🛡️ Preflight · Chưa có Change Set để kiểm tra.';if(a&&apply)apply.disabled=false;if(log)log.disabled=!t;if(parts&&parts.textContent&&parts.textContent!=='Chưa quét.')preview.textContent=parts.textContent;};
  const approveWire=()=>{$$('.change button[data-a]').forEach(b=>{if(b.dataset.bridgeBound)return;b.dataset.bridgeBound='1';b.addEventListener('click',()=>setTimeout(()=>{refresh();audit('Duyệt Change Set #'+(+b.dataset.a+1)+'.');},0),true)});$$('[data-a]').forEach(b=>{if(b.dataset.bridgeBound)return;b.dataset.bridgeBound='1';b.addEventListener('click',()=>setTimeout(refresh,0),true)});};
  const bulkWire=()=>$$('#high,#all,#none').forEach(b=>{if(b.dataset.bridgeBound)return;b.dataset.bridgeBound='1';b.addEventListener('click',()=>setTimeout(()=>{refresh();audit(b.textContent.trim());},50),true)});
  const applyWire=()=>{if(!apply||apply.dataset.bridgeBound)return;if(apply)apply.dataset.bridgeBound='1';apply?.addEventListener('click',()=>setTimeout(()=>{const text=validator.textContent||'';validator.textContent=text.startsWith('❌')?text:'🔎 Đã chạy bước ÁP DỤNG; đang kiểm tra lại nội dung DOCX…';if(word)word.disabled=false;if(zip)zip.disabled=false;if(log)log.disabled=false;const flow=$$('#flow .step');if(flow[5]){flow.forEach((x,i)=>{x.classList.toggle('done',i<6);x.classList.toggle('on',i===5)})}audit('Áp dụng Change Set và kiểm tra sau sửa.');},120),true)};
  const previewWire=()=>{const p=$('#previewNow');if(p&& !p.dataset.bridgeBound){p.dataset.bridgeBound='1';p.addEventListener('click',()=>setTimeout(()=>{refresh();audit('Cập nhật Preview.');},0),true)}};
  const validateWire=()=>{const v=$('#validateNow');if(v&&!v.dataset.bridgeBound){v.dataset.bridgeBound='1';v.addEventListener('click',()=>setTimeout(()=>{refresh();audit('Chạy Validator.');},0),true)}};
  const poll=()=>{approveWire();bulkWire();applyWire();previewWire();validateWire();refresh()};poll();setInterval(poll,500);
}
window.V60Bridge={boot};
})();
