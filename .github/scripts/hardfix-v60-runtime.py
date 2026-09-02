from pathlib import Path
import re

P=Path('sua-giao-an/v60.html')
s=P.read_text(encoding='utf-8')

# Remove previous authoritative override so this patch is idempotent.
s=re.sub(r"\n/\* FINAL AUTHORITATIVE APPLY:.*?window\.__V60_TRANSACTIONAL_APPLY_READY=true;\n", "\n", s, flags=re.S)

# Replace the Safe XML editor, preserving Word runs and never using insertBefore.
start=s.find('function __v60SafeXmlEdit')
if start<0:
    raise SystemExit('SAFE_XML_EDITOR_NOT_FOUND')
end=s.find("function replaceRun",start)
if end<0:
    raise SystemExit('REPLACE_RUN_ANCHOR_NOT_FOUND')

safe=r'''function __v60BuildNormMap(raw){const src=String(raw||'').normalize('NFC');let text='',map=[],space=false;for(let i=0;i<src.length;i++){let ch=src[i];if(ch==='\u00a0')ch=' ';if(ch==='–'||ch==='—')ch='-';if(/\s/.test(ch)){if(!text||space)continue;ch=' ';space=true}else{space=false;ch=ch.toLowerCase()}text+=ch;map.push(i)}while(text.endsWith(' ')){text=text.slice(0,-1);map.pop()}return{text,map}}
function __v60SafeXmlEdit(xml,c,mode){try{const d=parseXml(xml),ps=[...d.getElementsByTagNameNS(W,'p')],p=ps[c.paragraphIndex];if(!p)return{ok:false,reason:'Không tìm thấy paragraph '+(c.paragraphIndex+1)+'.'};const ts=[...p.getElementsByTagNameNS(W,'t')],text=ts.map(t=>t.textContent||'').join('');if(mode==='INSERT_AFTER'){const r=styled(d,null,String(c.insertText||''));p.appendChild(r)}else{const anchor=String(c.anchor||c.old_text||''),replacement=String(c.new||c.new_text||'');let idx=text.indexOf(anchor),end;if(idx>=0){end=idx+anchor.length}else{const hm=__v60BuildNormMap(text),nn=norm(anchor),nidx=hm.text.indexOf(nn);if(nidx<0)return{ok:false,reason:'Anchor không còn tồn tại.'};idx=hm.map[nidx];const last=hm.map[nidx+nn.length-1];end=last+1}const startRaw=idx;const endRaw=end;let pos=0,si=-1,ei=-1,so=0,eo=0;for(let i=0;i<ts.length;i++){const len=(ts[i].textContent||'').length,n=pos+len;if(si<0&&startRaw>=pos&&startRaw<=n){si=i;so=startRaw-pos;if(startRaw===n&&len>0)continue}if(endRaw>pos&&endRaw<=n){ei=i;eo=endRaw-pos;break}pos=n}if(si<0||ei<0)return{ok:false,reason:'Không xác định được vùng Anchor.'};const vals=ts.map(t=>t.textContent||'');const repl=mode==='DELETE'?'':replacement;vals[si]=vals[si].slice(0,so)+repl+vals[si].slice(eo);for(let i=si+1;i<=ei;i++)vals[i]=i===ei?vals[i].slice(eo):'';for(let i=0;i<ts.length;i++){const t=ts[i],v=vals[i];while(t.firstChild)t.removeChild(t.firstChild);if(v)t.appendChild(d.createTextNode(v))}}return{ok:true,xml:new XMLSerializer().serializeToString(d)}}catch(e){return{ok:false,reason:e&&e.message?e.message:String(e)}}}
function replaceRun(xml,c){return __v60SafeXmlEdit(xml,c,'REPLACE')}function appendRun(xml,c){return __v60SafeXmlEdit(xml,c,'INSERT_AFTER')}function validate(d,c){const p=pars(d.parts[c.part])[c.paragraphIndex];if(!p)return false;return c.type==='INTEGRATION'?norm(p.text).includes(norm(c.insertText)):norm(p.text).includes(norm(c.new))&&!norm(p.text).includes(norm(c.anchor))}
'''
s=s[:start]+safe+s[end+len('function replaceRun(xml,c){return false;}function appendRun(xml,c){return false;}function validate(d,c){return false}'):]

# Remove duplicate/older final override blocks inserted by earlier patches.
s=re.sub(r"\n/\* FINAL AUTHORITATIVE APPLY:.*?window\.__V60_TRANSACTIONAL_APPLY_READY=true;\n", "\n", s, flags=re.S)
s=re.sub(r"\n/\* DIRECT WORKING-DOC EXPORT FIX \*/\n\(function\(\)\{.*?\n\}\)\(\);\n", "\n", s, flags=re.S)

final_js=r'''
/* FINAL AUTHORITATIVE APPLY: current-anchor resolution + transactional commit. */
function __v60ResolveDoc(c){
  if(Number.isInteger(c.docIndex)&&S.docs[c.docIndex])return S.docs[c.docIndex];
  const ref=String(c.document||c.location||'').trim();
  if(ref){const exact=S.docs.find(d=>d.name===ref);if(exact)return exact;const same=S.docs.find(d=>norm(d.name)===norm(ref));if(same)return same}
  return S.docs.length===1?S.docs[0]:null;
}
function __v60ResolveAnchor(parts,c){
  const anchor=String(c.anchor||c.old_text||'');if(!anchor)return null;
  const requested=c.part&&parts[c.part]?c.part:null;
  const names=requested?[requested]:Object.keys(parts),hits=[];
  for(const part of names){
    const ps=pars(parts[part]);
    for(const pp of ps){
      const at=pp.text.indexOf(anchor);
      if(at>=0){hits.push({part,paragraphIndex:pp.i,matchStart:at,matchLength:anchor.length});continue}
      const hm=__v60BuildNormMap(pp.text),nn=norm(anchor),ni=hm.text.indexOf(nn);
      if(ni>=0){const rawStart=hm.map[ni],rawEnd=hm.map[ni+nn.length-1]+1;hits.push({part,paragraphIndex:pp.i,matchStart:rawStart,matchLength:Math.max(1,rawEnd-rawStart),normalized:true})}
    }
  }
  if(hits.length===1)return hits[0];
  if(hits.length>1&&Number.isInteger(c.paragraphIndex)){const same=hits.filter(h=>h.paragraphIndex===c.paragraphIndex);if(same.length===1)return same[0]}
  return null;
}
function __v60ApplyOneCurrent(parts,c){
  if(c.type==='INTEGRATION'||c.action==='INSERT_AFTER'){
    const loc=__v60ResolveAnchor(parts,c)||{part:c.part,paragraphIndex:Number(c.paragraphIndex)};
    if(!loc||!parts[loc.part])return{ok:false,reason:'Không xác định được vị trí chèn.'};
    const r=appendRun(parts[loc.part],{...c,...loc,insertText:c.insertText||c.new||c.new_text||''});
    if(!r.ok)return r;parts[loc.part]=r.xml;return{ok:true,loc};
  }
  const loc=__v60ResolveAnchor(parts,c);
  if(!loc)return{ok:false,reason:'Anchor không còn tồn tại hoặc không đủ duy nhất để xác định.'};
  const r=__v60SafeXmlEdit(parts[loc.part],{...c,...loc},c.action==='DELETE'?'DELETE':'REPLACE');
  if(!r.ok)return r;
  const after=pars(r.xml)[loc.paragraphIndex]?.text||'';
  const old=String(c.anchor||c.old_text||''),newText=String(c.new||c.new_text||'');
  if((c.action||'REPLACE')==='REPLACE'&&newText&&!norm(after).includes(norm(newText)))return{ok:false,reason:'Không xác minh được NEW sau áp dụng.'};
  if(old&&c.action==='DELETE'&&norm(after).includes(norm(old)))return{ok:false,reason:'Không xác minh được DELETE sau áp dụng.'};
  parts[loc.part]=r.xml;return{ok:true,loc};
}
$('apply').onclick=async()=>{
  const approved=S.changes.filter(c=>c.approved&&!c.rejected&&!c.applied);
  if(!approved.length){$('bulkStatus').textContent='⚠️ Không có Change Set hợp lệ đã duyệt.';return;}
  $('apply').disabled=true;$('word').disabled=true;$('zip').disabled=true;$('log').disabled=true;
  $('validator').textContent='⏳ Transaction APPLY: định vị lại Anchor và kiểm tra tài liệu...';
  const staged=S.docs.map((d,i)=>({d,parts:{...d.parts},docIndex:i}));
  const byDoc=new Map(staged.map(x=>[x.d,x])),seen=new Set(),selected=[],fail=[];
  for(const c of approved){
    const doc=__v60ResolveDoc(c);
    if(!doc){fail.push((c.id||'Change')+': không xác định được tài liệu.');continue}
    const key=[doc.name,c.part,norm(c.anchor||c.old_text||''),norm(c.new||c.new_text||c.insertText||''),c.action||'REPLACE'].join('|');
    if(seen.has(key)){c.rejected=true;c.approved=false;c.applyNote='Tự động loại vì trùng mục tiêu sau chuẩn hóa.';continue}
    seen.add(key);selected.push({c,box:byDoc.get(doc)});
  }
  try{
    for(const item of selected){const r=__v60ApplyOneCurrent(item.box.parts,item.c);if(!r.ok)fail.push((item.c.id||'Change')+': '+r.reason);else{item.c._resolvedPart=r.loc?.part||item.c.part;item.c._resolvedParagraph=r.loc?.paragraphIndex??item.c.paragraphIndex}}
    if(fail.length)throw Error(fail.join(' | '));
    for(const item of selected)item.box.d.parts=item.box.parts;
    selected.forEach(item=>item.c.applied=true);
    S.applied=selected.length>0;window.__V60_EXPORT_READY=!!S.applied;$('aa').textContent=String(selected.length);
    $('validator').textContent='✅ APPLY + POST-VALIDATOR PASS · '+selected.length+' Change Set đã áp dụng.';
    $('preview').textContent=S.docs.map(d=>d.name+'\n'+Object.entries(d.parts).map(([p,x])=>p+'\n'+pars(x).map(a=>a.text).join('\n')).join('\n')).join('\n\n');
    $('bulkStatus').textContent='✅ Áp dụng thành công: '+selected.length+' Change Set.';$('out').textContent='✅ Bản làm việc đã sửa thật. Có thể xuất Word/ZIP.';
    $('word').disabled=!S.applied;$('zip').disabled=!S.applied;$('log').disabled=!S.applied;audit('Áp dụng thành công: '+selected.length+' Change Set.');step(7);
  }catch(e){
    selected.forEach(item=>item.c.applied=false);S.applied=false;window.__V60_EXPORT_READY=false;$('aa').textContent='0';$('word').disabled=true;$('zip').disabled=true;$('log').disabled=true;
    $('validator').textContent='❌ APPLY FAILED · Đã rollback toàn bộ; tài liệu làm việc không bị thay đổi.';$('preview').textContent='⛔ Rollback hoàn tất. Bản làm việc giữ nguyên trước APPLY.';$('bulkStatus').textContent='❌ APPLY rollback toàn bộ.';$('out').textContent='❌ '+(e.message||String(e));audit('APPLY rollback: '+(e.message||String(e)));step(6);
  }finally{$('apply').disabled=!S.changes.some(c=>c.approved&&!c.rejected&&!c.applied)}
};
window.__V60_TRANSACTIONAL_APPLY_READY=true;
'''

anchor=s.find("$('gemTest')")
if anchor<0:raise SystemExit('GEM_TEST_ANCHOR_NOT_FOUND')
s=s[:anchor]+final_js+'\n'+s[anchor:]

# Required source checks.
if 'function __v60SafeXmlEdit' not in s:raise SystemExit('SAFE_EDITOR_MISSING')
if 'function __v60ResolveDoc' not in s:raise SystemExit('DOC_RESOLVER_MISSING')
if "$('apply').onclick=async()=>" not in s:raise SystemExit('APPLY_HANDLER_MISSING')
rt=s[s.find('function __v60ResolveDoc'):s.find("$('gemTest')",s.find('function __v60ResolveDoc'))]
if 'insertBefore(' in rt:raise SystemExit('UNSAFE_INSERTBEFORE_IN_APPLY')
if s.count("$('apply').onclick=async()=>")<1:raise SystemExit('APPLY_HANDLER_MISSING')
P.write_text(s,encoding='utf-8')
print('FINAL_RUNTIME_APPLY_PATCH_OK',len(s))