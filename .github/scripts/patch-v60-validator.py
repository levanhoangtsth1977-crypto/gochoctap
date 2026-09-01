from pathlib import Path
p=Path('sua-giao-an/v60.html')
s=p.read_text(encoding='utf-8')
# UI actions
s=s.replace('<h2>🔎 Validator + Preview + Audit</h2><div id="validator" class="st">Chưa sửa.</div>', '<h2>🔎 Validator + Preview + Audit</h2><button id="validateNow" class="btn y">🛡️ CHẠY VALIDATOR</button><button id="previewNow" class="btn i">👁️ CẬP NHẬT PREVIEW</button><div id="validator" class="st">Chưa kiểm tra.</div>')
# Preflight/preview functions before apply gate.
needle="function updateApply(){$('apply').disabled=!S.changes.some(c=>c.approved&&!c.rejected)||S.applied}"
insert="""function preflight(){if(!S.docs.length){$('validator').textContent='⚠️ Chưa có DOCX để kiểm tra.';return{valid:0,invalid:0,review:0}}let valid=0,invalid=0,review=0;for(const c of S.changes){if(c.rejected)continue;const d=S.docs.find(x=>x.name===c.document),p=d?.parts?.[c.part],para=p?pars(p)[c.paragraphIndex]:null,a=norm(c.anchor||'');if(!d||!para||!a||!norm(para.text).includes(a)){invalid++;continue}if(c.status==='NEED_VERIFY'||c.status==='REVIEW_REQUIRED')review++;else valid++}const msg='🛡️ Preflight · Hợp lệ: '+valid+' · Cần xác minh: '+review+' · Không hợp lệ: '+invalid+'.'+(invalid?' Không cho phép áp dụng mục không hợp lệ.':'');$('validator').textContent=msg;return{valid,invalid,review}}function preview(){if(!S.docs.length){$('preview').textContent='⚠️ Chưa có DOCX.';return}const text=S.docs.map(d=>d.name+'\\n'+Object.entries(d.parts).map(([p,x])=>p+'\\n'+pars(x).map(a=>a.text).join('\\n')).join('\\n')).join('\\n\\n');$('preview').textContent=text}function runPreflight(){const r=preflight();preview();$('log').disabled=!S.changes.length;return r}updateApply();$('validateNow').onclick=()=>{const r=preflight();$('bulkStatus').textContent='🛡️ Validator: '+r.valid+' hợp lệ · '+r.review+' xác minh · '+r.invalid+' lỗi.';audit('Chạy Validator preflight.')};$('previewNow').onclick=()=>{preview();audit('Cập nhật Preview.')}"""
if needle in s:s=s.replace(needle,insert)
# Run validator/preview after scan and after Gemini.
s=s.replace("audit('Quét hoàn tất: '+S.subjects.map(x=>LABEL[x]).join(', '))", "runPreflight();audit('Quét hoàn tất: '+S.subjects.map(x=>LABEL[x]).join(', '))")
s=s.replace("render();$('gemStatus').textContent='✅ Gemini đã rà soát toàn bộ môn đã chọn · thêm '+added+' Change Set hợp lệ.'", "render();runPreflight();$('gemStatus').textContent='✅ Gemini đã rà soát toàn bộ môn đã chọn · thêm '+added+' Change Set hợp lệ.'")
# Apply must pass preflight first.
s=s.replace("$('apply').onclick=()=>{let ok=0,fail=[];", "$('apply').onclick=()=>{const pf=preflight();if(pf.invalid||pf.review){$('bulkStatus').textContent='🔒 Chưa thể áp dụng: Validator còn mục lỗi/xác minh.';return}let ok=0,fail=[];")
# After successful apply, refresh preview.
s=s.replace("$('preview').textContent=S.docs.map(d=>d.name", "preview();$('preview').textContent=S.docs.map(d=>d.name") if "$('preview').textContent=S.docs.map(d=>d.name" in s else s
# Make change log available after scan.
s=s.replace("$('gemReview').disabled=!S.docs.length||!S.subjects.length;", "$('gemReview').disabled=!S.docs.length||!S.subjects.length;")
for bad in ('value="TIENG_ANH"','value="TIN_HOC"','value="MI_THUAT"','value="AM_NHAC"','gemini-3.6-flash','gemini-3.5-flash-lite'):
    if bad in s: raise SystemExit('SANITY_FAIL '+bad)
if 'id="validateNow"' not in s or 'function preflight()' not in s: raise SystemExit('SANITY_FAIL validator injection')
p.write_text(s,encoding='utf-8')
print('PATCH_OK',len(s))
