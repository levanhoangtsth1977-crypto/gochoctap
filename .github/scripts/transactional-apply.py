from pathlib import Path
import re

p = Path('sua-giao-an/v60.html')
s = p.read_text(encoding='utf-8')

pattern = re.compile(r"\$\('apply'\)\.onclick=\(\)=>\{.*?\}\;\$\('word'\)\.onclick", re.S)

new_apply = r'''$('apply').onclick=()=>{if(S.gemBusy)return;const approved=S.changes.filter(c=>c.approved&&!c.rejected);if(!approved.length){$('validator').textContent='❌ Không có Change Set đã duyệt.';$('out').textContent='⚠️ Chưa có thay đổi được duyệt.';return}const seen=new Set(),selected=[];for(const c of approved){const k=[c.document,c.part,c.paragraphIndex,c.matchStart,c.matchLength,norm(c.anchor||''),norm(c.new||c.insertText||'')].join('|');if(seen.has(k)){c.rejected=true;c.approved=false;c.applyNote='Tự động loại vì trùng Change Set.'}else{seen.add(k);selected.push(c)}}const clones=new Map(S.docs.map(d=>[d.name,{parts:{...d.parts}}]));const applied=[],fail=[];function validateXml(parts,c){const x=parts[c.part];if(!x)return{ok:false,reason:'Thiếu XML: '+c.part};const ps=pars(x),p=ps[c.paragraphIndex];if(!p)return{ok:false,reason:'Không có paragraph '+c.paragraphIndex};const text=norm(p.text),nw=norm(c.new||c.insertText||'');if(c.type==='INTEGRATION')return text.includes(nw)?{ok:true}:{ok:false,reason:'Nội dung bổ sung chưa tồn tại sau áp dụng.'};return text.includes(nw)&&!text.includes(norm(c.anchor))?{ok:true}:{ok:false,reason:'Sau áp dụng chưa đạt OLD→NEW tại đúng đoạn.'} }for(const c of selected.sort((a,b)=>(b.matchStart||0)-(a.matchStart||0))){const holder=clones.get(c.document);if(!holder){fail.push(c.id+': không tìm thấy tài liệu.');continue}const r=c.type==='INTEGRATION'?appendRun(holder.parts[c.part],c):replaceRun(holder.parts[c.part],c);if(!r.ok){fail.push(c.id+': '+r.reason);continue}holder.parts[c.part]=r.xml;const vr=validateXml(holder.parts,c);if(!vr.ok){fail.push(c.id+': '+vr.reason);continue}applied.push(c)}if(fail.length){S.applied=false;$('aa').textContent='0';$('validator').textContent='❌ APPLY bị HỦY TOÀN BỘ · '+fail.join(' | ');$('preview').textContent='Không ghi thay đổi vì transaction không đạt.';$('out').textContent='❌ Không xuất Word/ZIP: áp dụng chưa đạt Validator.';document.body.dataset.exportReady='0';$('word').disabled=true;$('zip').disabled=true;$('log').disabled=false;audit('APPLY rollback: '+fail.join(' | '));return}for(const d of S.docs){const holder=clones.get(d.name);if(holder)d.parts=holder.parts}for(const c of applied)c.applied=true;S.applied=applied.length>0;$('aa').textContent=String(applied.length);$('validator').textContent='✅ Transaction APPLY + Validator đạt · '+applied.length+' thay đổi · 0 lỗi.';$('preview').textContent=S.docs.map(d=>d.name+'\n'+Object.entries(d.parts).map(([pn,xx])=>pn+'\n'+pars(xx).map(a=>a.text).join('\n')).join('\n')).join('\n');$('word').disabled=!S.applied;$('zip').disabled=!S.applied;$('log').disabled=!S.changes.length;document.body.dataset.exportReady=S.applied?'1':'0';$('out').textContent=S.applied?'✅ Đã sửa thật và Validator sau áp dụng đạt. Word/ZIP đã sẵn sàng.':'❌ Chưa có bản sửa hợp lệ để xuất.';step(7);audit('APPLY transaction thành công: '+applied.length+' Change Set.');}​$('word').onclick'''.replace('}​$('word','}$('word')

if not pattern.search(s):
    raise SystemExit('APPLY_HANDLER_PATTERN_NOT_FOUND')
s2 = pattern.sub(new_apply, s, count=1)
if s2 == s:
    raise SystemExit('NO_CHANGE')
# safety checks
for bad in ('value="TIENG_ANH"','value="TIN_HOC"','value="MI_THUAT"','value="AM_NHAC"'):
    if bad in s2: raise SystemExit('EXCLUDED_SUBJECT_PRESENT: '+bad)
if s2.count("$('apply').onclick=()=>{") != 1:
    raise SystemExit('APPLY_HANDLER_COUNT_FAIL')
if 'exportReady' not in s2:
    raise SystemExit('EXPORT_READY_MARKER_MISSING')
p.write_text(s2, encoding='utf-8')
print('TRANSACTIONAL_APPLY_PATCH_OK', len(s2))
