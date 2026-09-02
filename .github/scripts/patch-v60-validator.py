from pathlib import Path
import re

p = Path('sua-giao-an/v60.html')
s = p.read_text(encoding='utf-8')

# Remove excluded subjects completely.
for v in ('TIENG_ANH','TIN_HOC','MI_THUAT','AM_NHAC'):
    s=re.sub(r'<label><input class="subjectCheck" type="checkbox" value="'+v+r'">.*?</label>','',s,flags=re.S)
s=re.sub(r"TIENG_ANH:'Tiếng Anh',TIN_HOC:'Tin học',MI_THUAT:'Mĩ thuật',AM_NHAC:'Âm nhạc',",'',s)

# Current Gemini model names.
for a,b in [('gemini-3.6-flash','gemini-3.7-flash'),('Gemini 3.6 Flash','Gemini 3.7 Flash'),('gemini-3.5-flash-lite','gemini-2.5-flash'),('Gemini 3.5 Flash-Lite','Gemini 2.5 Flash')]:
    s=s.replace(a,b)

# Scan every selected subject.
s=s.replace('S.subjects.filter(x=>!ADMIN.has(x))','S.subjects')

# Gemini is available after a successful scan even when Rule Engine has zero hits.
s=s.replace("$('gemReview').disabled=!(S.changes.length||S.integration.length);", "$('gemReview').disabled=!S.docs.length||!S.subjects.length;")

# Add Validator/Preview UI once.
if 'id="validateNow"' not in s:
    old='<h2>🔎 Validator + Preview + Audit</h2><div id="validator" class="st">Chưa sửa.</div>'
    new='<h2>🔎 Validator + Preview + Audit</h2><button id="validateNow" class="btn y">🛡️ CHẠY VALIDATOR</button><button id="previewNow" class="btn i">👁️ CẬP NHẬT PREVIEW</button><div id="validator" class="st">Chưa kiểm tra.</div>'
    if old not in s:
        raise SystemExit('VALIDATOR_UI_ANCHOR_NOT_FOUND')
    s=s.replace(old,new,1)

# Downstream refresh helpers.
if 'function __v60Preflight()' not in s:
    marker="$('apply').onclick=()=>{"
    idx=s.find(marker)
    if idx<0:
        raise SystemExit('APPLY_HANDLER_NOT_FOUND')
    block=r'''function __v60Preflight(){if(!S.docs.length){$('validator').textContent='⚠️ Chưa có DOCX để kiểm tra.';return{valid:0,invalid:0,review:0,approved:0,duplicate:0}}let valid=0,invalid=0,review=0,duplicate=0;const seen=new Set();for(const c of S.changes){if(c.rejected)continue;const d=S.docs.find(x=>x.name===c.document);let para=null;try{para=d?.parts?.[c.part]?pars(d.parts[c.part])[c.paragraphIndex]:null}catch{}const a=norm(c.anchor||'');if(!d||!para||!a||!norm(para.text).includes(a)){invalid++;continue}const key=[c.document,c.part,c.paragraphIndex,c.matchStart,c.matchLength,norm(c.anchor||''),norm(c.new||c.replacement||'')].join('|');if(seen.has(key)){duplicate++;continue}seen.add(key);if(c.status==='NEED_VERIFY'||c.status==='REVIEW_REQUIRED'){review++;continue}valid++}const approved=S.changes.filter(c=>c.approved&&!c.rejected).length;$('validator').textContent='🛡️ Preflight · Hợp lệ: '+valid+' · Trùng: '+duplicate+' · Cần xác minh: '+review+' · Không hợp lệ: '+invalid+' · Đã duyệt: '+approved;return{valid,invalid,review,approved,duplicate}}function __v60Preview(){if(!S.docs.length){$('preview').textContent='⚠️ Chưa có DOCX.';return}const chunks=[];for(const d of S.docs){chunks.push('📄 '+d.name);for(const[p,x]of Object.entries(d.parts)){chunks.push('['+p+']');try{chunks.push(pars(x).map(a=>a.text).join('\\n'))}catch{chunks.push('⚠️ XML không đọc được')}}}$('preview').textContent=chunks.join('\\n\\n')}function __v60Refresh(){const r=__v60Preflight();__v60Preview();$('log').disabled=!S.changes.length;return r}'''
    s=s[:idx]+block+s[idx:]

# Refresh after scan, Gemini, and approve/reject actions.
s=s.replace("audit('Quét hoàn tất: '+S.subjects.map(x=>LABEL[x]).join(', '))", "__v60Refresh();audit('Quét hoàn tất: '+S.subjects.map(x=>LABEL[x]).join(', '))")
s=s.replace("render();$('gemStatus').textContent='✅ Gemini đã rà soát toàn bộ môn đã chọn · thêm '+added+' Change Set hợp lệ.'", "render();__v60Refresh();$('gemStatus').textContent='✅ Gemini đã rà soát toàn bộ môn đã chọn · thêm '+added+' Change Set hợp lệ.'")

# Replace approval handlers with refresh.
for old,new in {
    "$('bulkStatus').textContent='✅ Đã duyệt Change Set #'+(+b.dataset.a+1);step(5);render()":"$('bulkStatus').textContent='✅ Đã duyệt Change Set #'+(+b.dataset.a+1);step(5);render();__v60Refresh()",
    "$('bulkStatus').textContent='❌ Đã từ chối Change Set #'+(+b.dataset.r+1);step(5);render()":"$('bulkStatus').textContent='❌ Đã từ chối Change Set #'+(+b.dataset.r+1);step(5);render();__v60Refresh()",
    "$('bulkStatus').textContent='✅ Duyệt chắc chắn: '+n+' Change Set.';step(5);render()":"$('bulkStatus').textContent='✅ Duyệt chắc chắn: '+n+' Change Set.';step(5);render();__v60Refresh()",
    "$('bulkStatus').textContent='☑️ Duyệt tất cả có bằng chứng: '+n+' Change Set.';step(5);render()":"$('bulkStatus').textContent='☑️ Duyệt tất cả có bằng chứng: '+n+' Change Set.';step(5);render();__v60Refresh()",
    "$('bulkStatus').textContent='❌ Đã từ chối: '+n+' Change Set.';step(5);render()":"$('bulkStatus').textContent='❌ Đã từ chối: '+n+' Change Set.';step(5);render();__v60Refresh()",
}.items():
    s=s.replace(old,new)

# Replace the entire APPLY handler with dedupe + apply + post-validation.
pattern=r"\$\('apply'\)\.onclick=\(\)=>\{.*?\};\$\('gemTest'\)\.onclick=async\(\)=>\{" 
replacement=r'''$('apply').onclick=()=>{const pre=__v60Refresh();if(!pre.approved||pre.invalid||pre.review){$('bulkStatus').textContent='🔒 Chưa thể áp dụng: '+pre.approved+' đã duyệt · '+pre.duplicate+' trùng · '+pre.invalid+' lỗi · '+pre.review+' cần xác minh.';return}let ok=0,fail=[],used=new Set();const approved=S.changes.filter(c=>c.approved&&!c.rejected).map((c,idx)=>({c,idx})).sort((a,b)=>{if(a.c.document!==b.c.document)return String(a.c.document).localeCompare(String(b.c.document));if(a.c.part!==b.c.part)return String(a.c.part).localeCompare(String(b.c.part));if(a.c.paragraphIndex!==b.c.paragraphIndex)return b.c.paragraphIndex-a.c.paragraphIndex;return (b.c.matchStart||0)-(a.c.matchStart||0)});for(const item of approved){const c=item.c;const key=[c.document,c.part,c.paragraphIndex,c.matchStart,c.matchLength,norm(c.anchor||''),norm(c.new||c.replacement||'')].join('|');if(used.has(key)){c.rejected=true;c.approved=false;c.applyNote='Bị loại vì trùng Change Set đã duyệt.';continue}used.add(key);const d=S.docs.find(x=>x.name===c.document);if(!d||!d.parts[c.part]){fail.push(c.id+': Không tìm thấy tài liệu/phần XML.');continue}const r=c.action==='INSERT_AFTER'?appendRun(d.parts[c.part],c):c.action==='DELETE'?replaceRun(d.parts[c.part],{...c,new:''}):replaceRun(d.parts[c.part],c);if(!r.ok){fail.push(c.id+': '+r.reason);continue}d.parts[c.part]=r.xml;c.applied=true;ok++}const verifyFails=[];for(const c of S.changes.filter(x=>x.applied&&!x.rejected)){const d=S.docs.find(x=>x.name===c.document);try{const pp=pars(d.parts[c.part])[c.paragraphIndex];if(c.action==='DELETE'){if(norm(pp.text).includes(norm(c.anchor)))verifyFails.push(c.id+': OLD vẫn còn sau DELETE')}else if(!norm(pp.text).includes(norm(c.new||c.replacement||''))){verifyFails.push(c.id+': NEW không tồn tại sau áp dụng')}}catch{verifyFails.push(c.id+': Không đọc lại được XML sau áp dụng')}}const SApplied=ok>0&&fail.length===0&&verifyFails.length===0;S.applied=SApplied;$('aa').textContent=ok;__v60Preview();$('validator').textContent=SApplied?'✅ Validator sau áp dụng đạt · '+ok+' thay đổi đã được kiểm tra.':('❌ Validator sau áp dụng thất bại · '+fail.concat(verifyFails).join(' | '));$('word').disabled=!SApplied;$('zip').disabled=!SApplied;$('log').disabled=!S.changes.length;$('out').textContent=SApplied?'✅ Bản làm việc đã được áp dụng và kiểm tra. Có thể xuất Word/ZIP.':'🔒 Chưa thể xuất: áp dụng thất bại hoặc Validator chưa đạt.';$('bulkStatus').textContent='✏️ Đã áp dụng '+ok+' Change Set · loại trùng '+(approved.length-ok-fail.length)+'.';step(SApplied?7:5);audit('Áp dụng '+ok+' thay đổi; Validator sau sửa: '+(SApplied?'ĐẠT':'CHƯA ĐẠT'))};$('gemTest').onclick=async()=>{'''
ns,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
if n!=1:
    raise SystemExit('APPLY_HANDLER_REPLACE_FAILED')
s=ns

# Explicit validator/preview buttons.
if "$('validateNow').onclick" not in s:
    anchor="$('gemTest').onclick=async()=>{"
    wire="$('validateNow').onclick=()=>{const r=__v60Refresh();$('bulkStatus').textContent='🛡️ Validator: '+r.valid+' hợp lệ · '+r.duplicate+' trùng · '+r.review+' xác minh · '+r.invalid+' lỗi · '+r.approved+' đã duyệt.';audit('Chạy Validator preflight.')};$('previewNow').onclick=()=>{__v60Preview();audit('Cập nhật Preview.')}"
    if anchor not in s:
        raise SystemExit('WIRE_ANCHOR_NOT_FOUND')
    s=s.replace(anchor,wire+anchor,1)

# Remove accidental duplicate JSON parser function definitions.
needle="function parseGeminiJSON(raw){const t=String(raw||'').trim().replace(/^```(?:json)?\\s*/i,'').replace(/\\s*```$/,'').trim();try{return JSON.parse(t)}catch{}const a=t.indexOf('{'),b=t.lastIndexOf('}');if(a>=0&&b>a)return JSON.parse(t.slice(a,b+1));throw Error('Gemini trả về JSON không hợp lệ.')}"
s=s.replace(needle+"\n"+needle,needle,1)

# Hard exclusions and required functions.
for bad in ('value="TIENG_ANH"','value="TIN_HOC"','value="MI_THUAT"','value="AM_NHAC"','gemini-3.6-flash','gemini-3.5-flash-lite'):
    if bad in s: raise SystemExit('LEGACY_TOKEN '+bad)
for req in ('id="validateNow"','id="previewNow"','function __v60Preflight()','function __v60Preview()','function __v60Refresh()','S.applied=SApplied','if(used.has(key))'):
    if req not in s: raise SystemExit('MISSING '+req)

js=re.findall(r'<script>(.*?)</script>',s,re.S)[0]
Path('/tmp/v60.js').write_text(js,encoding='utf-8')
p.write_text(s,encoding='utf-8')
print('PATCH_OK',len(s))
