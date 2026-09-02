from pathlib import Path
import re

P=Path('sua-giao-an/v60.html')
s=P.read_text(encoding='utf-8')
MARK='data-v60-transactional-apply="1"'
if MARK in s:
    print('TRANSACTIONAL_PATCH_ALREADY_PRESENT')
    raise SystemExit(0)

needle='})();</script>'
pos=s.rfind(needle)
if pos<0:
    raise SystemExit('SCRIPT_END_NOT_FOUND')

inject=r'''
/* data-v60-transactional-apply="1" */
/* FINAL TRANSACTIONAL APPLY + REAL EXPORT */
function __txCount(hay,needle){const h=norm(hay||''),n=norm(needle||'');if(!n)return 0;let c=0,p=0;while((p=h.indexOf(n,p))>=0){c++;p+=n.length}return c}
function __txCloneParts(d){const o={};for(const[k,v]of Object.entries(d.parts))o[k]=v;return o}
function __txApplyOne(parts,c){
  const beforeParts={...parts};
  const oldXml=parts[c.part];
  if(typeof oldXml!=='string')return{ok:false,reason:'Thiếu XML '+c.part+'.'};
  const beforePars=pars(oldXml),bp=beforePars[c.paragraphIndex];
  if(!bp)return{ok:false,reason:'Không có paragraph '+(c.paragraphIndex+1)+'.'};
  const beforeText=bp.text;
  const anchor=String(c.anchor||c.old_text||'');
  const beforeCount=anchor?__txCount(beforeText,anchor):0;
  if(c.action==='DELETE' && beforeCount<1)return{ok:false,reason:'Anchor DELETE không còn tồn tại.'};
  if(c.action==='REPLACE' && beforeCount<1)return{ok:false,reason:'Anchor REPLACE không còn tồn tại.'};
  let r;
  if(c.type==='INTEGRATION'||c.action==='INSERT_AFTER')r=appendRun(oldXml,{paragraphIndex:c.paragraphIndex,insertText:c.insertText||c.new||c.new_text||''});
  else if(c.action==='DELETE')r=replaceRun(oldXml,{...c,new:''});
  else r=replaceRun(oldXml,c);
  if(!r.ok)return{ok:false,reason:r.reason||'Không áp dụng được.'};
  const afterPars=pars(r.xml),ap=afterPars[c.paragraphIndex];
  if(!ap)return{ok:false,reason:'Không đọc lại được paragraph sau áp dụng.'};
  const afterText=ap.text;
  const afterCount=anchor?__txCount(afterText,anchor):0;
  if(anchor && afterCount!==Math.max(0,beforeCount-1))return{ok:false,reason:'Xác minh OLD/Anchor sau áp dụng không đạt.'};
  const newText=String(c.new||c.new_text||c.insertText||'');
  if(newText && __txCount(afterText,newText)<1)return{ok:false,reason:'Xác minh NEW sau áp dụng không đạt.'};
  parts[c.part]=r.xml;
  return{ok:true,parts,beforeParts}
}
function __txSetExportState(ok,message){
  S.applied=!!ok;
  window.__V60_EXPORT_READY=!!ok;
  $('word').disabled=!ok;
  $('zip').disabled=!ok;
  $('log').disabled=!ok;
  $('aa').textContent=ok?String(S.changes.filter(c=>c.applied&&!c.rejected).length):'0';
  $('out').textContent=message;
  $('validator').textContent=ok?'✅ POST-VALIDATOR PASS · Tất cả thay đổi đã được xác minh.':'❌ APPLY FAILED · Đã rollback toàn bộ; tài liệu làm việc không bị thay đổi.';
  step(ok?7:6);
}
async function __txBuildDocx(d){
  const z=d.zip;
  for(const[k,v]of Object.entries(d.parts))z.file(k,v);
  return z.generateAsync({type:'blob',mimeType:'application/vnd.openxmlformats-officedocument.wordprocessingml.document'});
}
async function __txExportWord(){
  if(!window.__V60_EXPORT_READY){$('out').textContent='⛔ Chưa có bản DOCX hợp lệ sau Validator.';return}
  if(S.docs.length!==1){$('out').textContent='⚠️ Có nhiều DOCX. Dùng 📦 Xuất ZIP để xuất toàn bộ.';return}
  const blob=await __txBuildDocx(S.docs[0]);
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=S.docs[0].name.replace(/\.docx$/i,'')+'_DA_SUA.docx';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),2000);
  $('out').textContent='✅ Đã tạo và tải DOCX đã sửa.';audit('Xuất Word thành công.');
}
async function __txExportZip(){
  if(!window.__V60_EXPORT_READY){$('out').textContent='⛔ Chưa có bản hợp lệ sau Validator.';return}
  const outZip=new JSZip();
  for(const d of S.docs){
    const blob=await __txBuildDocx(d);
    outZip.file(d.name,blob);
  }
  const blob=await outZip.generateAsync({type:'blob',mimeType:'application/zip'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='GOCHOCTAP_KET_QUA_DA_SUA.zip';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),2000);
  $('out').textContent='✅ Đã tạo và tải ZIP kết quả.';audit('Xuất ZIP thành công.');
}
$('apply').onclick=async()=>{
  if(S.gemBusy)return;
  const approved=S.changes.filter(c=>c.approved&&!c.rejected&&!c.applied);
  if(!approved.length){$('out').textContent='⚠️ Không có Change Set hợp lệ đã duyệt.';return}
  $('apply').disabled=true;$('word').disabled=true;$('zip').disabled=true;$('log').disabled=true;
  $('validator').textContent='⏳ Transaction APPLY: đang thử toàn bộ thay đổi trên bản sao...';
  $('preview').textContent='⏳ Đang tạo bản xem trước sau áp dụng...';
  try{
    const staged=S.docs.map(d=>({d,parts:__txCloneParts(d)}));
    const byDoc=new Map(staged.map(x=>[x.d.name,x]));
    const ordered=[...approved].sort((a,b)=>{
      if(a.document!==b.document)return String(a.document).localeCompare(String(b.document));
      if(a.part!==b.part)return String(a.part).localeCompare(String(b.part));
      return (b.paragraphIndex-a.paragraphIndex)||(b.matchStart-a.matchStart);
    });
    const failures=[];
    for(const c of ordered){
      const box=byDoc.get(c.document);
      if(!box){failures.push(c.id+': không tìm thấy DOCX.');continue}
      const r=__txApplyOne(box.parts,c);
      if(!r.ok){failures.push(c.id+': '+r.reason);continue}
    }
    if(failures.length)throw Error(failures.join(' | '));
    for(const box of staged){box.d.parts=box.parts}
    approved.forEach(c=>c.applied=true);
    $('aa').textContent=String(approved.length);
    $('validator').textContent='✅ POST-VALIDATOR PASS · '+approved.length+' Change Set đã áp dụng và xác minh.';
    $('preview').textContent=S.docs.map(d=>d.name+'\n'+Object.entries(d.parts).map(([p,x])=>p+'\n'+pars(x).map(a=>a.text).join('\n')).join('\n')).join('\n\n');
    __txSetExportState(true,'✅ Bản làm việc đã sửa thành công. Word/ZIP đã được mở.');
    $('bulkStatus').textContent='✅ Áp dụng thành công '+approved.length+' Change Set (transaction commit).';
    audit('Áp dụng transaction thành công: '+approved.length+' Change Set.');
  }catch(e){
    for(const c of approved)c.applied=false;
    $('aa').textContent='0';
    __txSetExportState(false,'❌ '+e.message+' Không có thay đổi nào được ghi vào bản làm việc.');
    $('preview').textContent='⛔ Rollback hoàn tất. Bản làm việc giữ nguyên trước APPLY.';
    $('bulkStatus').textContent='❌ APPLY bị rollback toàn bộ.';
    audit('APPLY rollback: '+e.message);
  }finally{$('apply').disabled=!S.changes.some(c=>c.approved&&!c.rejected&&!c.applied)}
};
$('word').onclick=__txExportWord;
$('zip').onclick=__txExportZip;
$('log').onclick=()=>{
  const lines=S.changes.filter(c=>c.applied).map(c=>({id:c.id,subject:c.subject,document:c.document,part:c.part,paragraph:c.paragraphIndex+1,old:c.anchor,new:c.new,action:c.action}));
  const blob=new Blob([JSON.stringify(lines,null,2)],{type:'application/json;charset=utf-8'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='CHANGE_LOG.json';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),2000);audit('Xuất Change Log.');
};
window.__V60_TRANSACTIONAL_APPLY_READY=true;
'''
s=s[:pos]+inject+s[pos:]
p.write_text(s,encoding='utf-8')
print('TRANSACTIONAL_PATCH_OK',len(s))
