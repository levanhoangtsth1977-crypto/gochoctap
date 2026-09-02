from pathlib import Path
import re

p = Path('sua-giao-an/v60.html')
s = p.read_text(encoding='utf-8')

pat = re.compile(r"function syncSubjects\(\)\{.*?\}document\.querySelectorAll\('\.subjectCheck'\)\.forEach\(x=>x\.addEventListener\('change',syncSubjects\)\);", re.S)
new = """function syncSubjects(){S.subjects=[...document.querySelectorAll('.subjectCheck:checked')].map(x=>x.value);const admins=S.subjects.filter(x=>ADMIN.has(x));$('subjectPicked').textContent=S.subjects.length?'✅ Đã chọn: '+S.subjects.map(x=>LABEL[x]).join(' · '):'⚠️ Chưa chọn môn';$('route').innerHTML=S.subjects.length?'🗺️ Địa giới: '+(admins.length?admins.map(x=>LABEL[x]).join(' · '):'không chạy')+'<br>🧩 Rà soát ngữ nghĩa: '+S.subjects.map(x=>LABEL[x]).join(' · '):'⚠️ Chưa chọn môn';const scanReady=Boolean(S.docs.length&&S.subjects.length&&DATA.master&&!S.gemBusy);$('scan').disabled=!scanReady;$('gemReview').disabled=!S.docs.length||!S.subjects.length||S.gemBusy;step(S.subjects.length?2:1)}document.querySelectorAll('.subjectCheck').forEach(x=>x.addEventListener('change',syncSubjects));"""
if not pat.search(s):
    raise SystemExit('SYNC_SUBJECTS_ANCHOR_NOT_FOUND')
s = pat.sub(new, s, count=1)

marker = "})();</script>"
if marker not in s:
    raise SystemExit('RUNTIME_END_NOT_FOUND')

inject = r"""
(function installStableDocxInput(){
  const old=$('files');
  if(!old) throw Error('FILES_INPUT_MISSING');
  const fresh=old.cloneNode(true);
  old.replaceWith(fresh);
  fresh.addEventListener('change',async()=>{
    try{
      if(!fresh.files || !fresh.files.length){
        $('picked').textContent='Chưa nạp.';
        syncSubjects();
        return;
      }
      S.docs=[];S.changes=[];S.integration=[];S.applied=false;S.exportReady=false;
      $('picked').textContent='📥 Đang đọc '+fresh.files.length+' tài liệu…';
      for(const f of fresh.files){
        await addDoc(await f.arrayBuffer(),f.name,'DOCX');
      }
      const chars=S.docs.reduce((n,d)=>n+(d.text||'').length,0);
      $('picked').textContent='✅ Đã nạp '+S.docs.length+' tài liệu · '+chars.toLocaleString('vi-VN')+' ký tự';
      $('msg').textContent='✅ DOCX đã vào Document Engine. Hãy chọn môn rồi quét.';
      audit('Nạp '+S.docs.length+' DOCX vào Document Engine.');
      syncSubjects();
    }catch(e){
      $('picked').textContent='❌ Nạp DOCX lỗi: '+(e?.message||e);
      $('msg').textContent='❌ Không thể nạp DOCX: '+(e?.message||e);
      audit('Nạp DOCX lỗi: '+(e?.message||e));
      syncSubjects();
    }
  });
  syncSubjects();
})();
"""
s = s.replace(marker, inject + marker, 1)
p.write_text(s,encoding='utf-8')

# Safety checks for this focused fix.
if "value=\"TIENG_ANH\"" in s or "value=\"TIN_HOC\"" in s or "value=\"MI_THUAT\"" in s or "value=\"AM_NHAC\"" in s:
    raise SystemExit('EXCLUDED_SUBJECT_PRESENT')
if "$('scan').disabled=!scanReady" not in s:
    raise SystemExit('SCAN_ENABLE_RULE_MISSING')
if 'installStableDocxInput' not in s:
    raise SystemExit('DOCX_INPUT_FIX_MISSING')
print('SCAN_CLEAN_FIX_OK', len(s))
