from pathlib import Path
import re

p = Path('sua-giao-an/v60.html')
s = p.read_text(encoding='utf-8')

# Remove excluded subjects and obsolete model names defensively.
for v in ('TIENG_ANH','TIN_HOC','MI_THUAT','AM_NHAC'):
    s = re.sub(r'<label><input class="subjectCheck" type="checkbox" value="' + v + r'">.*?</label>', '', s, flags=re.S)
for a,b in [('gemini-3.6-flash','gemini-3.7-flash'),('Gemini 3.6 Flash','Gemini 3.7 Flash'),('gemini-3.5-flash-lite','gemini-2.5-flash'),('Gemini 3.5 Flash-Lite','Gemini 2.5 Flash')]:
    s = s.replace(a,b)

# Validator + Preview controls.
if 'id="validateNow"' not in s:
    old = '<h2>🔎 Validator + Preview + Audit</h2><div id="validator" class="st">Chưa sửa.</div>'
    new = '<h2>🔎 Validator + Preview + Audit</h2><button id="validateNow" class="btn y">🛡️ CHẠY VALIDATOR</button><button id="previewNow" class="btn i">👁️ CẬP NHẬT PREVIEW</button><div id="validator" class="st">Chưa kiểm tra.</div>'
    if old not in s: raise SystemExit('VALIDATOR_UI_ANCHOR_NOT_FOUND')
    s = s.replace(old,new,1)

# Authoritative downstream helpers and APPLY handler.
if 'function __v60FinalRefresh()' not in s:
    marker = "$('apply').onclick=()=>{"
    idx = s.find(marker)
    if idx < 0: raise SystemExit('APPLY_HANDLER_NOT_FOUND')
    block = r'''function __v60FinalKey(c){return [c.document,c.part,c.paragraphIndex,c.matchStart,c.matchLength,norm(c.anchor||''),norm(c.new||c.replacement||c.insertText||'')].join('|')}
function __v60FinalRefresh(){if(!$('validator')||!$('preview'))return{approved:0,invalid:0,review:0,duplicate:0};let invalid=0,review=0,duplicate=0;const seen=new Set();for(const c of S.changes){if(c.rejected)continue;const d=S.docs.find(x=>x.name===c.document);let para=null;try{para=d?.parts?.[c.part]?pars(d.parts[c.part])[c.paragraphIndex]:null}catch{}const a=norm(c.anchor||'');if(!d||!para||!a||!norm(para.text).includes(a)){invalid++;continue}const k=__v60FinalKey(c);if(seen.has(k)){duplicate++;continue}seen.add(k);if(c.status==='NEED_VERIFY'||c.status==='REVIEW_REQUIRED'){review++}}const approved=S.changes.filter(c=>c.approved&&!c.rejected).length;$('validator').textContent='🛡️ Preflight · Đã duyệt: '+approved+' · Trùng: '+duplicate+' · Cần xác minh: '+review+' · Anchor lỗi: '+invalid;return{approved,invalid,review,duplicate}}
function __v60FinalPreview(){if(!S.docs.length){$('preview').textContent='⚠️ Chưa có DOCX.';return}const out=[];for(const d of S.docs){out.push('📄 '+d.name);for(const[p,x]of Object.entries(d.parts)){out.push('['+p+']');try{out.push(pars(x).map(q=>q.text).join('\\n'))}catch{out.push('⚠️ XML không đọc được')}}}$('preview').textContent=out.join('\\n\\n')}
function __v60FinalDedupeApproved(){const seen=new Set();let removed=0;for(const c of S.changes.filter(x=>x.approved&&!x.rejected)){const k=__v60FinalKey(c);if(seen.has(k)){c.approved=false;c.rejected=true;c.applyNote='Tự động loại vì trùng Change Set đã duyệt.';removed++}else{seen.add(k)}}return removed}
'''
    s = s[:idx] + block + s[idx:]

pattern = r"\$\('apply'\)\.onclick=\(\)=>\{.*?\};\$\('gemTest'\)\.onclick=async\(\)=>\{"
replacement = r'''$('apply').onclick=()=>{let removed=__v60FinalDedupeApproved();const pre=__v60FinalRefresh();if(!pre.approved||pre.invalid||pre.review){$('bulkStatus').textContent='🔒 Chưa thể áp dụng · đã duyệt '+pre.approved+' · trùng '+pre.duplicate+' · xác minh '+pre.review+' · Anchor lỗi '+pre.invalid;return}let ok=0,fail=[],verify=[];const approved=S.changes.filter(c=>c.approved&&!c.rejected).sort((a,b)=>{if(a.document!==b.document)return String(a.document).localeCompare(String(b.document));if(a.part!==b.part)return String(a.part).localeCompare(String(b.part));return (b.matchStart||0)-(a.matchStart||0)});for(const c of approved){const d=S.docs.find(x=>x.name===c.document);if(!d||!d.parts[c.part]){fail.push(c.id+': thiếu tài liệu/XML');continue}const r=c.type==='INTEGRATION'||c.action==='INSERT_AFTER'?appendRun(d.parts[c.part],c):replaceRun(d.parts[c.part],c);if(!r.ok){fail.push(c.id+': '+r.reason);continue}d.parts[c.part]=r.xml;c.applied=true;ok++}for(const c of S.changes.filter(x=>x.applied&&!x.rejected)){const d=S.docs.find(x=>x.name===c.document);try{const pp=pars(d.parts[c.part])[c.paragraphIndex];if(c.action==='DELETE'){if(norm(pp.text).includes(norm(c.anchor)))verify.push(c.id+': OLD vẫn còn')}else if(!norm(pp.text).includes(norm(c.new||c.replacement||c.insertText||''))){verify.push(c.id+': NEW không tồn tại')}}catch{verify.push(c.id+': không đọc được XML sau sửa')}}const success=ok>0&&fail.length===0&&verify.length===0;S.applied=success;$('aa').textContent=ok;$('validator').textContent=success?'✅ Validator sau áp dụng đạt · '+ok+' thay đổi đã kiểm tra.':'❌ Validator thất bại · '+fail.concat(verify).join(' | ');__v60FinalPreview();$('word').disabled=!success;$('zip').disabled=!success;$('log').disabled=!S.changes.length;$('out').textContent=success?'✅ Bản làm việc đã được sửa và kiểm tra. Hai nút Xuất Word/ZIP đã sẵn sàng.':'🔒 Chưa thể xuất: áp dụng thất bại hoặc Validator chưa đạt.';$('bulkStatus').textContent='✏️ Đã áp dụng '+ok+' · loại trùng '+removed+'.';step(success?7:5);audit('Áp dụng '+ok+' thay đổi; Validator sau sửa: '+(success?'ĐẠT':'CHƯA ĐẠT'))};$('gemTest').onclick=async()=>{'''
s,n = re.subn(pattern,replacement,s,count=1,flags=re.S)
if n != 1: raise SystemExit('APPLY_REPLACE_FAILED')

# Wire validator/preview buttons once.
if "$('validateNow').onclick" not in s:
    anchor = "$('gemTest').onclick=async()=>{"
    wire = "$('validateNow').onclick=()=>{const r=__v60FinalRefresh();$('bulkStatus').textContent='🛡️ Validator: '+r.approved+' duyệt · '+r.duplicate+' trùng · '+r.review+' xác minh · '+r.invalid+' lỗi.';audit('Chạy Validator preflight.')};$('previewNow').onclick=()=>{__v60FinalPreview();audit('Cập nhật Preview.')}"
    if anchor not in s: raise SystemExit('WIRE_ANCHOR_NOT_FOUND')
    s = s.replace(anchor,wire+anchor,1)

# Remove duplicate parser definitions if present.
needle = "function parseGeminiJSON(raw){const t=String(raw||'').trim().replace(/^```(?:json)?\\s*/i,'').replace(/\\s*```$/,'').trim();try{return JSON.parse(t)}catch{}const a=t.indexOf('{'),b=t.lastIndexOf('}');if(a>=0&&b>a)return JSON.parse(t.slice(a,b+1));throw Error('Gemini trả về JSON không hợp lệ.')}"
s = s.replace(needle+'\n'+needle, needle, 1)

# Syntax/semantic invariants in source.
required = ['id="validateNow"','id="previewNow"','function __v60FinalRefresh()','function __v60FinalPreview()','function __v60FinalDedupeApproved()','S.applied=success',"$('word').disabled=!success","$('zip').disabled=!success"]
missing=[x for x in required if x not in s]
if missing: raise SystemExit('MISSING: '+', '.join(missing))
for bad in ['value="TIENG_ANH"','value="TIN_HOC"','value="MI_THUAT"','value="AM_NHAC"','gemini-3.6-flash','gemini-3.5-flash-lite']:
    if bad in s: raise SystemExit('LEGACY: '+bad)
js = re.findall(r'<script>(.*?)</script>',s,re.S)[0]
Path('/tmp/v60-final.js').write_text(js,encoding='utf-8')
p.write_text(s,encoding='utf-8')
print('FINAL_V60_PATCH_OK')