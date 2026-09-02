from pathlib import Path
import re

p=Path('sua-giao-an/v60.html')
s=p.read_text(encoding='utf-8')

start=s.find("$('apply').onclick=()=>{")
end=s.find("$('gemTest')", start)
if start<0 or end<0 or end<=start:
    raise SystemExit('APPLY_HANDLER_ANCHOR_NOT_FOUND')

handler=r'''$('apply').onclick=async()=>{
  const approved=[];
  const seen=new Set();
  for(const c of S.changes){
    if(!c.approved||c.rejected)continue;
    const key=[c.id,c.document,c.part,c.paragraphIndex,c.matchStart,c.matchLength,norm(c.anchor||''),norm(c.new||c.new_text||c.insertText||'')].join('|');
    if(seen.has(key)){c.rejected=true;c.approved=false;c.applyNote='Tự động loại vì trùng Change Set.';continue}
    seen.add(key);approved.push(c);
  }
  if(!S.docs.length){$('bulkStatus').textContent='❌ Chưa có tài liệu để áp dụng.';return}
  if(!approved.length){$('bulkStatus').textContent='⚠️ Không có Change Set đã duyệt hợp lệ.';updateApply();return}
  const original={};
  for(const d of S.docs){original[d.name]={...d.parts}}
  const failures=[];
  const applied=[];
  const resolveDoc=(c)=>{
    if(Number.isInteger(c.docIndex)&&S.docs[c.docIndex])return S.docs[c.docIndex];
    const exact=S.docs.find(d=>d.name===c.document||d.source===c.document);
    if(exact)return exact;
    if(S.docs.length===1)return S.docs[0];
    return null;
  };
  try{
    // Apply onto the working copy only; commit to S.docs only after every approved item succeeds.
    for(const c of approved){
      const d=resolveDoc(c);
      if(!d){failures.push(c.id+': không tìm thấy tài liệu tương ứng.');continue}
      const current=d.parts[c.part];
      if(typeof current!=='string'){failures.push(c.id+': không tìm thấy '+c.part+' trong tài liệu '+d.name+'.');continue}
      const r=c.type==='INTEGRATION'?appendRun(current,c):replaceRun(current,c);
      if(!r||!r.ok){failures.push(c.id+': '+(r?.reason||'Không thể sửa XML.'));continue}
      d.parts[c.part]=r.xml;
      applied.push({c,d});
    }
    // All-or-nothing: any failure restores every part modified in this APPLY.
    if(failures.length){
      for(const d of S.docs){const snap=original[d.name];if(snap)d.parts={...snap}}
      for(const c of approved)c.applied=false;
      S.applied=false;
      $('aa').textContent='0';
      $('validator').textContent='❌ APPLY thất bại · đã rollback toàn bộ.\n'+failures.join('\n');
      $('preview').textContent='';
      $('out').textContent='❌ '+failures.join(' | ');
      $('word').disabled=true;$('zip').disabled=true;
      $('bulkStatus').textContent='❌ APPLY rollback toàn bộ.';
      audit('APPLY rollback: '+failures.join(' | '));
      render();
      step(5);
      return;
    }
    // Commit the successful working copy and validate every applied item.
    const bad=[];
    for(const item of applied){
      item.c.applied=true;
      const d=item.d;
      if(!validate(d,item.c))bad.push(item.c.id+': post-validator không đạt.');
    }
    if(bad.length){
      for(const d of S.docs){const snap=original[d.name];if(snap)d.parts={...snap}}
      for(const c of approved)c.applied=false;
      S.applied=false;
      $('aa').textContent='0';
      $('validator').textContent='❌ POST-VALIDATOR thất bại · đã rollback toàn bộ.\n'+bad.join('\n');
      $('preview').textContent='';
      $('out').textContent='❌ '+bad.join(' | ');
      $('word').disabled=true;$('zip').disabled=true;
      $('bulkStatus').textContent='❌ Rollback vì Validator sau áp dụng không đạt.';
      audit('POST-VALIDATOR rollback: '+bad.join(' | '));
      render();
      step(5);
      return;
    }
    S.applied=true;
    $('aa').textContent=String(applied.length);
    $('validator').textContent='✅ APPLY thành công · '+applied.length+' thay đổi · POST-VALIDATOR đạt.';
    $('preview').textContent=S.docs.map(d=>d.name+'\n'+Object.entries(d.parts).map(([p,x])=>p+'\n'+pars(x).map(a=>a.text).join('\n')).join('\n')).join('\n\n');
    $('out').textContent='✅ Bản làm việc đã được sửa và kiểm tra. Có thể xuất Word/ZIP.';
    $('word').disabled=false;$('zip').disabled=false;$('log').disabled=false;
    $('bulkStatus').textContent='✅ Đã áp dụng '+applied.length+' Change Set.';
    audit('APPLY thành công: '+applied.length+' thay đổi.');
    step(6);
    render();
  }catch(e){
    for(const d of S.docs){const snap=original[d.name];if(snap)d.parts={...snap}}
    for(const c of approved)c.applied=false;
    S.applied=false;$('aa').textContent='0';
    const msg=e?.message||String(e);
    $('validator').textContent='❌ APPLY exception · đã rollback toàn bộ.\n'+msg;
    $('preview').textContent='';$('out').textContent='❌ '+msg;
    $('word').disabled=true;$('zip').disabled=true;
    $('bulkStatus').textContent='❌ APPLY rollback toàn bộ.';
    audit('APPLY exception: '+msg);
    render();step(5);
  }
};
'''

s=s[:start]+handler+s[end:]
if s.count("$('apply').onclick=()=>{")!=0:
    raise SystemExit('OLD_APPLY_HANDLER_REMAINS')
if "$('apply').onclick=async()=>{" not in s:
    raise SystemExit('NEW_APPLY_HANDLER_MISSING')
# Required guard: the final apply handler must not use the old document-only nested loop.
idx=s.find("$('apply').onclick=async()=>{")
seg=s[idx:s.find("$('gemTest')",idx)]
for bad in ('for(const d of S.docs)for(const c of S.changes.filter', 'c.document===d.name'):
    if bad in seg:
        raise SystemExit('LEGACY_APPLY_PATTERN_REMAINS: '+bad)
p.write_text(s,encoding='utf-8')
print('FORCE_APPLY_RUNTIME_OK',len(s))
