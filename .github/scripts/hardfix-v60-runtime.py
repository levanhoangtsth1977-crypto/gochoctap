from pathlib import Path
import re

p=Path('sua-giao-an/v60.html')
s=p.read_text(encoding='utf-8')

pattern=r"function replaceRun\(xml,c\)\{return false;\}function appendRun\(xml,c\)\{return false;\}function validate\(d,c\)\{.*?\$\('apply'\)\.onclick="
m=re.search(pattern,s,re.S)
if not m:
    raise SystemExit('OLD_APPLY_BLOCK_NOT_FOUND')

new="""function __v60SafeXmlEdit(xml,c,mode){try{const d=parseXml(xml),ps=[...d.getElementsByTagNameNS(W,'p')],p=ps[c.paragraphIndex];if(!p)return{ok:false,reason:'Không tìm thấy paragraph '+(c.paragraphIndex+1)+'.'};const ts=[...p.getElementsByTagNameNS(W,'t')],text=ts.map(t=>t.textContent||'').join('');if(mode==='INSERT_AFTER'){const r=styled(d,null,String(c.insertText||''));p.appendChild(r)}else{const anchor=String(c.anchor||c.old_text||''),replacement=String(c.new||c.new_text||'');const idx=text.indexOf(anchor);if(idx<0)return{ok:false,reason:'Anchor không còn tồn tại.'};const end=idx+anchor.length;let pos=0,si=-1,ei=-1,so=0,eo=0;for(let i=0;i<ts.length;i++){const n=pos+(ts[i].textContent||'').length;if(si<0&&idx>=pos&&idx<n){si=i;so=idx-pos}if(end>pos&&end<=n){ei=i;eo=end-pos;break}pos=n}if(si<0||ei<0)return{ok:false,reason:'Không xác định được vùng Anchor.'};const vals=ts.map(t=>t.textContent||'');const repl=mode==='DELETE'?'':replacement;vals[si]=vals[si].slice(0,so)+repl+vals[si].slice(eo);for(let i=si+1;i<=ei;i++)vals[i]=i===ei?vals[i].slice(eo):'';for(let i=ts.length-1;i>=0;i--){const t=ts[i],v=vals[i];while(t.firstChild)t.removeChild(t.firstChild);t.textContent=v}}return{ok:true,xml:new XMLSerializer().serializeToString(d)}}catch(e){return{ok:false,reason:e&&e.message?e.message:String(e)}}}function replaceRun(xml,c){return __v60SafeXmlEdit(xml,c,'REPLACE')}function appendRun(xml,c){return __v60SafeXmlEdit(xml,c,'INSERT_AFTER')}function validate(d,c){const p=pars(d.parts[c.part])[c.paragraphIndex];if(!p)return false;return c.type==='INTEGRATION'?norm(p.text).includes(norm(c.insertText)):norm(p.text).includes(norm(c.new))&&!norm(p.text).includes(norm(c.anchor))}$('apply').onclick="""
s=s[:m.start()]+new+s[m.end():]

# Final authoritative APPLY override. It runs after all earlier patches because this script is executed late in the pipeline.
final_js=r'''
/* FINAL AUTHORITATIVE APPLY: resolve current XML anchors + document references at click time. */
function __v60ResolveDoc(c){
  if(Number.isInteger(c.docIndex)&&S.docs[c.docIndex]) return S.docs[c.docIndex];
  const ref=String(c.document||c.location||'').trim();
  if(ref){const exact=S.docs.find(d=>d.name===ref);if(exact)return exact;const byBase=S.docs.find(d=>norm(d.name)===norm(ref));if(byBase)return byBase}
  if(S.docs.length===1)return S.docs[0];
  return null;
}
function __v60ResolveAnchor(parts,c){
  const anchor=String(c.anchor||c.old_text||'');
  if(!anchor)return null;
  const targetPart=c.part&&parts[c.part]?c.part:null;
  const partNames=targetPart?[targetPart]:Object.keys(parts);
  const hits=[];
  for(const part of partNames){
    const ps=pars(parts[part]);
    for(const pp of ps){
      const at=pp.text.indexOf(anchor);
      if(at>=0)hits.push({part,paragraphIndex:pp.i,matchStart:at,matchLength:anchor.length});
      const na=norm(pp.text),nn=norm(anchor),nat=na.indexOf(nn);
      if(at<0&&nat>=0)hits.push({part,paragraphIndex:pp.i,matchStart:nat,matchLength:anchor.length,normalized:true});
    }
  }
  if(hits.length===1)return hits[0];
  if(hits.length>1){
    if(Number.isInteger(c.paragraphIndex)){const h=hits.find(x=>x.paragraphIndex===c.paragraphIndex);if(h)return h;}
    return null;
  }
  return null;
}
function __v60ApplyOneCurrent(parts,c){
  const loc=__v60ResolveAnchor(parts,c);
  if(!loc)return{ok:false,reason:'Anchor không còn tồn tại hoặc không đủ duy nhất để xác định.'};
  const cc={...c,...loc};
  const xml=parts[loc.part];
  const before=norm(pars(xml)[loc.paragraphIndex]?.text||'');
  const old=norm(c.anchor||c.old_text||'');
  if(c.action==='DELETE'||c.action==='REPLACE'){
    if(!old||before.indexOf(old)<0)return{ok:false,reason:'Anchor không còn tồn tại ở vị trí hiện tại.'};
  }
  let r;
  if(c.type==='INTEGRATION'||c.action==='INSERT_AFTER')r=appendRun(xml,{...cc,insertText:c.insertText||c.new||c.new_text||''});
  else if(c.action==='DELETE')r=__v60SafeXmlEdit(xml,{...cc,new:''},'DELETE');
  else r=__v60SafeXmlEdit(xml,cc,'REPLACE');
  if(!r.ok)return r;
  const after=pars(r.xml)[loc.paragraphIndex]?.text||'';
  const newText=String(c.new||c.new_text||c.insertText||'');
  if(newText&&!norm(after).includes(norm(newText)))return{ok:false,reason:'Không xác minh được NEW sau khi áp dụng.'};
  parts[loc.part]=r.xml;
  return{ok:true,loc};
}
$('apply').onclick=async()=>{
  if(S.gemBusy)return;
  const approved=S.changes.filter(c=>c.approved&&!c.rejected&&!c.applied);
  if(!approved.length){$('bulkStatus').textContent='⚠️ Không có Change Set hợp lệ đã duyệt.';return;}
  $('apply').disabled=true;$('word').disabled=true;$('zip').disabled=true;$('log').disabled=true;
  $('validator').textContent='⏳ APPLY: đang kiểm tra tài liệu và định vị lại Anchor trên bản hiện tại...';
  const staged=S.docs.map(d=>({d,parts:{...d.parts},docIndex:S.docs.indexOf(d)}));
  const byDoc=new Map(staged.map(x=>[x.d,x]));
  const seen=new Set(),selected=[],fail=[];
  for(const c of approved){
    const doc=__v60ResolveDoc(c);
    if(!doc){fail.push((c.id||'Change')+': không xác định được tài liệu.');continue}
    const key=[doc.name,c.part,norm(c.anchor||c.old_text||''),norm(c.new||c.new_text||c.insertText||''),String(c.action||'REPLACE')].join('|');
    if(seen.has(key)){c.rejected=true;c.approved=false;c.applyNote='Tự động loại vì trùng mục tiêu sau chuẩn hóa.';continue;}
    seen.add(key);
    const box=byDoc.get(doc);selected.push({c,box});
  }
  try{
    for(const item of selected.sort((a,b)=>String(a.c.document||'').localeCompare(String(b.c.document||''))||((b.c.paragraphIndex||0)-(a.c.paragraphIndex||0)))){
      const r=__v60ApplyOneCurrent(item.box.parts,item.c);
      if(!r.ok)fail.push((item.c.id||'Change')+': '+r.reason);
      else {item.c._resolvedPart=r.loc.part;item.c._resolvedParagraph=r.loc.paragraphIndex;}
    }
    if(fail.length)throw Error(fail.join(' | '));
    for(const item of selected)item.box.d.parts=item.box.parts;
    selected.forEach(item=>item.c.applied=true);
    $('aa').textContent=String(selected.length);
    S.applied=selected.length>0;
    window.__V60_EXPORT_READY=!!S.applied;
    $('validator').textContent='✅ APPLY + POST-VALIDATOR PASS · '+selected.length+' Change Set đã áp dụng.';
    $('preview').textContent=S.docs.map(d=>d.name+'\n'+Object.entries(d.parts).map(([p,x])=>p+'\n'+pars(x).map(a=>a.text).join('\n')).join('\n')).join('\n\n');
    $('bulkStatus').textContent='✅ Áp dụng thành công: '+selected.length+' Change Set.';
    $('word').disabled=!S.applied;$('zip').disabled=!S.applied;$('log').disabled=!S.applied;
    $('out').textContent=S.applied?'✅ Bản làm việc đã sửa và kiểm tra. Có thể xuất Word/ZIP.':'⚠️ Chưa có thay đổi hợp lệ.';
    audit('Áp dụng thành công: '+selected.length+' Change Set.');step(7);
  }catch(e){
    __v60SetExportState(false,'❌ '+(e.message||String(e)));
    $('preview').textContent='⛔ Rollback hoàn tất. Bản làm việc giữ nguyên trước APPLY.';
    $('bulkStatus').textContent='❌ APPLY rollback toàn bộ.';
    audit('APPLY rollback: '+(e.message||String(e)));
  }finally{
    $('apply').disabled=!S.changes.some(c=>c.approved&&!c.rejected&&!c.applied);
  }
};
window.__V60_TRANSACTIONAL_APPLY_READY=true;
'''

start=s.find("$('gemTest')")
if start<0:
    raise SystemExit('GEM_TEST_ANCHOR_NOT_FOUND')
s=s[:start]+final_js+'\n'+s[start:]

# Hard fail if the final APPLY region contains unsafe DOM insertion.
start=s.find('function __v60ResolveDoc')
end=s.find("$('gemTest')",start)
rt=s[start:end] if start>=0 and end>start else ''
if 'insertBefore(' in rt:
    raise SystemExit('UNSAFE_INSERTBEFORE_IN_FINAL_APPLY')
if "$('apply').onclick=async()=>" not in rt:
    raise SystemExit('FINAL_APPLY_HANDLER_MISSING')

p.write_text(s,encoding='utf-8')
print('FINAL_APPLY_RUNTIME_PATCH_OK',len(s))