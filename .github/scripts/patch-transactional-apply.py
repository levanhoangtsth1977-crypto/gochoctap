from pathlib import Path

P=Path('sua-giao-an/v60.html')
s=P.read_text(encoding='utf-8')
MARK='data-v60-transactional-apply="1"'
if MARK in s:
    print('TRANSACTIONAL_PATCH_ALREADY_PRESENT')
    raise SystemExit(0)

# v6.0 is a minified IIFE. Insert immediately before the final IIFE close,
# independent of whether the closing script tag is inline/whitespace formatted.
pos=s.rfind('})();')
if pos<0:
    raise SystemExit('IIFE_END_NOT_FOUND')

inject=r'''
/* data-v60-transactional-apply="1" */
/* FINAL TRANSACTIONAL APPLY + REAL EXPORT */
function __txCount(hay,needle){const h=norm(hay||''),n=norm(needle||'');if(!n)return 0;let c=0,p=0;while((p=h.indexOf(n,p))>=0){c++;p+=n.length}return c}
function __txCloneParts(d){const o={};for(const[k,v]of Object.entries(d.parts))o[k]=v;return o}
function __txApplyOne(parts,c){
  const oldXml=parts[c.part];
  if(typeof oldXml!=='string')return{ok:false,reason:'Thiếu XML '+c.part+'.'};
  const bp=pars(oldXml)[c.paragraphIndex];
  if(!bp)return{ok:false,reason:'Không có paragraph '+(c.paragraphIndex+1)+'.'};
  const anchor=String(c.anchor||c.old_text||'');
  const beforeCount=anchor?__txCount(bp.text,anchor):0;
  if((c.action==='DELETE'||c.action==='REPLACE')&&beforeCount<1)return{ok:false,reason:'Anchor không còn tồn tại.'};
  let r;
  if(c.type==='INTEGRATION'||c.action==='INSERT_AFTER')r=appendRun(oldXml,{paragraphIndex:c.paragraphIndex,insertText:c.insertText||c.new||c.new_text||''});
  else if(c.action==='DELETE')r=replaceRun(oldXml,{...c,new:''});
  else r=replaceRun(oldXml,c);
  if(!r.ok)return{ok:false,reason:r.reason||'Không áp dụng được.'};
  const ap=pars(r.xml)[c.paragraphIndex];
  if(!ap)return{ok:false,reason:'Không đọc lại paragraph sau áp dụng.'};
  const afterText=ap.text,afterCount=anchor?__txCount(afterText,anchor):0;
  if(anchor&&afterCount!==Math.max(0,beforeCount-1))return{ok:false,reason:'Xác minh OLD/Anchor sau áp dụng không đạt.'};
  const newText=String(c.new||c.new_text||c.insertText||'');
  if(newText&&__txCount(afterText,newText)<1)return{ok:false,reason:'Xác minh NEW sau áp dụng không đạt.'};
  parts[c.part]=r.xml;return{ok:true}
}
function __txSetExportState(ok,message){
  S.applied=!!ok;window.__V60_EXPORT_READY=!!ok;document.body.dataset.exportReady=ok?'1':'0';
  $('word').disabled=!ok;$('zip').disabled=!ok;$('log').disabled=!ok;$('aa').textContent=ok?String(S.changes.filter(c=>c.applied&&!c.rejected).length):'0';
  $('validator').textContent=ok?'✅ POST-VALIDATOR PASS · Tất cả Change Set đã áp dụng và xác minh.':'❌ APPLY FAILED · Đã rollback toàn bộ.';$('out').textContent=message;step(ok?7:6)
}
async function __txBuildDocx(d){for(const[k,v]of Object.entries(d.parts))d.zip.file(k,v);return d.zip.generateAsync({type:'blob',mimeType:'application/vnd.openxmlformats-officedocument.wordprocessingml.document'})}
async function __txExportWord(){
  if(!window.__V60_EXPORT_READY){$('out').textContent='⛔ Chưa có bản DOCX hợp lệ sau Validator.';return}
  if(S.docs.length!==1){$('out').textContent='⚠️ Có nhiều DOCX. Dùng 📦 Xuất ZIP.';return}
  const blob=await __txBuildDocx(S.docs[0]),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=S.docs[0].name.replace(/\.docx$/i,'')+'_DA_SUA.docx';a.click();setTimeout(()=>URL.revokeObjectURL(url),2000);$('out').textContent='✅ Đã tạo và tải DOCX đã sửa.';audit('Xuất Word thành công.')
}
async function __txExportZip(){
  if(!window.__V60_EXPORT_READY){$('out').textContent='⛔ Chưa có bản hợp lệ sau Validator.';return}
  const z=new JSZip();for(const d of S.docs)z.file(d.name,await __txBuildDocx(d));const blob=await z.generateAsync({type:'blob',mimeType:'application/zip'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='GOCHOCTAP_KET_QUA_DA_SUA.zip';a.click();setTimeout(()=>URL.revokeObjectURL(url),2000);$('out').textContent='✅ Đã tạo và tải ZIP kết quả.';audit('Xuất ZIP thành công.')
}
$('apply').onclick=async()=>{
  const approved=S.changes.filter(c=>c.approved&&!c.rejected&&!c.applied);
  if(!approved.length){$('out').textContent='⚠️ Không có Change Set hợp lệ đã duyệt.';return}
  $('apply').disabled=true;$('word').disabled=true;$('zip').disabled=true;
  $('validator').textContent='⏳ Transaction APPLY: thử toàn bộ trên bản sao…';$('preview').textContent='⏳ Đang kiểm tra thay đổi…';
  try{
    const staged=S.docs.map(d=>({d,parts:__txCloneParts(d)})),byDoc=new Map(staged.map(x=>[x.d.name,x]));
    const seen=new Set(),selected=[];
    for(const c of approved){const k=[c.document,c.part,c.paragraphIndex,c.matchStart,c.matchLength,norm(c.anchor||''),norm(c.new||c.insertText||'')].join('|');if(seen.has(k)){c.approved=false;c.rejected=true;c.applyNote='Tự động loại vì trùng Change Set đã duyệt.'}else{seen.add(k);selected.push(c)}}
    selected.sort((a,b)=>String(a.document).localeCompare(String(b.document))||String(a.part).localeCompare(String(b.part))||(b.paragraphIndex-a.paragraphIndex)||(b.matchStart-a.matchStart));
    const failures=[];
    for(const c of selected){const box=byDoc.get(c.document);if(!box){failures.push(c.id+': không tìm thấy DOCX.');continue}const r=__txApplyOne(box.parts,c);if(!r.ok)failures.push(c.id+': '+r.reason)}
    if(failures.length)throw Error(failures.join(' | '));
    for(const x of staged)x.d.parts=x.parts;for(const c of selected)c.applied=true;
    S.applied=selected.length>0;__txSetExportState(true,'✅ Đã sửa thật và Validator sau áp dụng đạt. Word/ZIP đã sẵn sàng.');
    $('bulkStatus').textContent='✅ Transaction APPLY thành công: '+selected.length+' Change Set.';audit('APPLY transaction thành công: '+selected.length)
  }catch(e){for(const c of approved)c.applied=false;__txSetExportState(false,'❌ '+e.message+' Không ghi thay đổi nào.');$('preview').textContent='⛔ Rollback hoàn tất. Bản làm việc giữ nguyên.';$('bulkStatus').textContent='❌ APPLY rollback toàn bộ.';audit('APPLY rollback: '+e.message)}
  finally{$('apply').disabled=!S.changes.some(c=>c.approved&&!c.rejected&&!c.applied)}
};
$('word').onclick=__txExportWord;$('zip').onclick=__txExportZip;
$('log').onclick=()=>{const lines=S.changes.filter(c=>c.applied).map(c=>({id:c.id,subject:c.subject,document:c.document,part:c.part,paragraph:c.paragraphIndex+1,old:c.anchor,new:c.new,action:c.action}));const blob=new Blob([JSON.stringify(lines,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='CHANGE_LOG.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),2000);audit('Xuất Change Log.')};
window.__V60_TRANSACTIONAL_APPLY_READY=true;
'''
s=s[:pos]+inject+s[pos:]
if s.count(MARK)!=1:raise SystemExit('TRANSACTIONAL_MARKER_COUNT_FAIL')
p.write_text(s,encoding='utf-8');print('TRANSACTIONAL_PATCH_OK',len(s))
