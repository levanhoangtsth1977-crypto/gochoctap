from pathlib import Path
import re
p=Path('sua-giao-an/v60.html')
s=p.read_text(encoding='utf-8')
for v in ('TIENG_ANH','TIN_HOC','MI_THUAT','AM_NHAC'):
    s=re.sub(r'<label><input class="subjectCheck" type="checkbox" value="'+v+r'">.*?</label>','',s,flags=re.S)
s=re.sub(r"TIENG_ANH:'Tiếng Anh',TIN_HOC:'Tin học',MI_THUAT:'Mĩ thuật',AM_NHAC:'Âm nhạc',",'',s)
for a,b in [('gemini-3.6-flash','gemini-3.7-flash'),('Gemini 3.6 Flash','Gemini 3.7 Flash'),('gemini-3.5-flash-lite','gemini-2.5-flash'),('Gemini 3.5 Flash-Lite','Gemini 2.5 Flash')]: s=s.replace(a,b)
s=s.replace('S.subjects.filter(x=>!ADMIN.has(x))','S.subjects')
s=s.replace("$('gemReview').disabled=!(S.changes.length||S.integration.length);", "$('gemReview').disabled=!S.docs.length||!S.subjects.length;")
if 'id="validateNow"' not in s:
    old='<h2>🔎 Validator + Preview + Audit</h2><div id="validator" class="st">Chưa sửa.</div>'
    new='<h2>🔎 Validator + Preview + Audit</h2><button id="validateNow" class="btn y">🛡️ CHẠY VALIDATOR</button><button id="previewNow" class="btn i">👁️ CẬP NHẬT PREVIEW</button><div id="validator" class="st">Chưa kiểm tra.</div>'
    if old not in s: raise SystemExit('VALIDATOR_UI_ANCHOR_NOT_FOUND')
    s=s.replace(old,new,1)
if 'function __v60Preflight()' not in s:
    marker="$('apply').onclick=()=>{"
    idx=s.find(marker)
    if idx<0: raise SystemExit('APPLY_HANDLER_NOT_FOUND')
    block=r'''function __v60Preflight(){if(!S.docs.length){$('validator').textContent='⚠️ Chưa có DOCX để kiểm tra.';return{valid:0,invalid:0,review:0,approved:0}}let valid=0,invalid=0,review=0;for(const c of S.changes){if(c.rejected)continue;const d=S.docs.find(x=>x.name===c.document);let para=null;try{para=d?.parts?.[c.part]?pars(d.parts[c.part])[c.paragraphIndex]:null}catch{}const a=norm(c.anchor||'');if(!d||!para||!a||!norm(para.text).includes(a)){invalid++;continue}if(c.status==='NEED_VERIFY'||c.status==='REVIEW_REQUIRED'){review++;continue}valid++}const approved=S.changes.filter(c=>c.approved&&!c.rejected).length;$('validator').textContent='🛡️ Preflight · Hợp lệ: '+valid+' · Cần xác minh: '+review+' · Không hợp lệ: '+invalid+' · Đã duyệt: '+approved;return{valid,invalid,review,approved}}function __v60Preview(){if(!S.docs.length){$('preview').textContent='⚠️ Chưa có DOCX.';return}const chunks=[];for(const d of S.docs){chunks.push('📄 '+d.name);for(const[p,x]of Object.entries(d.parts)){chunks.push('['+p+']');try{chunks.push(pars(x).map(a=>a.text).join('\n'))}catch{chunks.push('⚠️ XML không đọc được')}}}$('preview').textContent=chunks.join('\n\n')}function __v60Refresh(){const r=__v60Preflight();__v60Preview();$('log').disabled=!S.changes.length;return r}'''
    s=s[:idx]+block+s[idx:]
s=s.replace("audit('Quét hoàn tất: '+S.subjects.map(x=>LABEL[x]).join(', '))", "__v60Refresh();audit('Quét hoàn tất: '+S.subjects.map(x=>LABEL[x]).join(', '))")
s=s.replace("render();$('gemStatus').textContent='✅ Gemini đã rà soát toàn bộ môn đã chọn · thêm '+added+' Change Set hợp lệ.'", "render();__v60Refresh();$('gemStatus').textContent='✅ Gemini đã rà soát toàn bộ môn đã chọn · thêm '+added+' Change Set hợp lệ.'")
s=s.replace("$('bulkStatus').textContent='✅ Đã duyệt Change Set #'+(+b.dataset.a+1);step(5);render()", "$('bulkStatus').textContent='✅ Đã duyệt Change Set #'+(+b.dataset.a+1);step(5);render();__v60Refresh()")
s=s.replace("$('bulkStatus').textContent='❌ Đã từ chối Change Set #'+(+b.dataset.r+1);step(5);render()", "$('bulkStatus').textContent='❌ Đã từ chối Change Set #'+(+b.dataset.r+1);step(5);render();__v60Refresh()")
s=s.replace("$('bulkStatus').textContent='✅ Duyệt chắc chắn: '+n+' Change Set.';step(5);render()", "$('bulkStatus').textContent='✅ Duyệt chắc chắn: '+n+' Change Set.';step(5);render();__v60Refresh()")
s=s.replace("$('bulkStatus').textContent='☑️ Duyệt tất cả có bằng chứng: '+n+' Change Set.';step(5);render()", "$('bulkStatus').textContent='☑️ Duyệt tất cả có bằng chứng: '+n+' Change Set.';step(5);render();__v60Refresh()")
s=s.replace("$('bulkStatus').textContent='❌ Đã từ chối: '+n+' Change Set.';step(5);render()", "$('bulkStatus').textContent='❌ Đã từ chối: '+n+' Change Set.';step(5);render();__v60Refresh()")
s=s.replace("$('apply').onclick=()=>{let ok=0,fail=[];", "$('apply').onclick=()=>{const pf=__v60Refresh();if(!pf.approved||pf.invalid||pf.review){$('bulkStatus').textContent='🔒 Chưa thể áp dụng: '+pf.approved+' đã duyệt · '+pf.invalid+' lỗi · '+pf.review+' cần xác minh.';return}let ok=0,fail=[];")
s=s.replace("$('word').disabled=!!(fail.length||bad.length)||!ok;$('zip').disabled=!!(fail.length||bad.length)||!ok;$('log').disabled=!S.changes.length;$('preview').textContent=S.docs.map(d=>d.name+'\\n'+Object.entries(d.parts).map(([p,x])=>p+'\\n'+pars(x).map(a=>a.text).join('\\n')).join('\\n')).join('\\n\\n');$('bulkStatus').textContent='✏️ Đã áp dụng '+ok+' Change Set.';step(6);audit('Áp dụng '+ok+' thay đổi.')", "__v60Preview();const post=__v60Preflight();S.applied=ok>0&&fail.length===0&&post.invalid===0;$('aa').textContent=ok;$('validator').textContent=post.invalid||post.review?'❌ Sau áp dụng: '+post.invalid+' lỗi · '+post.review+' cần xác minh.':'✅ Sau áp dụng: '+ok+' thay đổi đã được kiểm tra.';$('word').disabled=!S.applied;$('zip').disabled=!S.applied;$('log').disabled=!S.changes.length;$('bulkStatus').textContent='✏️ Đã áp dụng '+ok+' Change Set.';step(6);audit('Áp dụng '+ok+' thay đổi.')")
if "$('validateNow').onclick" not in s:
    anchor="$('gemTest').onclick=async()=>{"
    wire="$('validateNow').onclick=()=>{const r=__v60Refresh();$('bulkStatus').textContent='🛡️ Validator: '+r.valid+' hợp lệ · '+r.review+' xác minh · '+r.invalid+' lỗi · '+r.approved+' đã duyệt.';audit('Chạy Validator preflight.')};$('previewNow').onclick=()=>{__v60Preview();audit('Cập nhật Preview.')}"
    if anchor not in s: raise SystemExit('WIRE_ANCHOR_NOT_FOUND')
    s=s.replace(anchor,wire+anchor,1)
for bad in ('value="TIENG_ANH"','value="TIN_HOC"','value="MI_THUAT"','value="AM_NHAC"','gemini-3.6-flash','gemini-3.5-flash-lite','S.subjects.filter(x=>!ADMIN.has(x))'):
    if bad in s: raise SystemExit('LEGACY_TOKEN '+bad)
for req in ('id="validateNow"','id="previewNow"','function __v60Preflight()','function __v60Preview()','function __v60Refresh()'):
    if req not in s: raise SystemExit('MISSING '+req)
js=re.findall(r'<script>(.*?)</script>',s,re.S)[0]
Path('/tmp/v60.js').write_text(js,encoding='utf-8')
p.write_text(s,encoding='utf-8')
print('PATCH_OK',len(s))
