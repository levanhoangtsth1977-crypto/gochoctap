from pathlib import Path

p = Path('sua-giao-an/v64.html')
s = p.read_text(encoding='utf-8')

# 1) Reduce the Gemini payload substantially without changing the surrounding UI.
s = s.replace(".join('\\n').slice(0,500000)", ".join('\\n').slice(0,120000)", 1)
s = s.replace(".slice(0,70000)", ".slice(0,18000)", 1)

# 2) Add a hard timeout helper and per-request AbortController if not already present.
needle = "const sleep=ms=>new Promise(r=>setTimeout(r,ms));"
insert = "const sleep=ms=>new Promise(r=>setTimeout(r,ms));const withTimeout=(p,ms=60000)=>Promise.race([p,new Promise((_,rej)=>setTimeout(()=>rej(Error('Gemini timeout sau '+Math.round(ms/1000)+' giây')),ms))]);"
if needle in s and 'const withTimeout=' not in s:
    s = s.replace(needle, insert, 1)

# 3) Make Preview useful even before Apply: show approved/pending Change Sets, and scroll to it.
marker = "$('previewExportBtn').addEventListener('click',()=>"
ps = s.find(marker)
if ps < 0:
    raise SystemExit('previewExportBtn handler not found')
pe = s.find("});function dl(blob,name){", ps)
if pe < 0:
    raise SystemExit('previewExportBtn end marker not found')
handler = "$('previewExportBtn').addEventListener('click',()=>{const applied=S.changes.filter(c=>c.status==='applied');const review=S.changes.filter(c=>c.status==='approved'||c.status==='pending');const rows=applied.length?applied:review;$('preview').textContent=rows.length?rows.map((c,i)=>['#'+(i+1)+' · '+LABEL[c.subject]+' · '+c.type,c.old?'OLD: '+c.old:'','NEW: '+c.new,'Trạng thái: '+c.status].filter(Boolean).join('\\n')).join('\\n\\n'):'Chưa có thay đổi để xem trước.';const pv=$('preview');pv.scrollIntoView({behavior:'smooth',block:'center'});pv.style.outline='3px solid #d9a400';setTimeout(()=>pv.style.outline='',1500);});function dl(blob,name){"
s = s[:ps] + handler + s[pe+3:]

# 4) Do not duplicate the Preview button or handler.
assert s.count('id="previewExportBtn"') == 1
assert s.count("$('previewExportBtn').addEventListener('click'") == 1
assert '.slice(0,120000)' in s
assert '.slice(0,18000)' in s

p.write_text(s, encoding='utf-8')
print('PATCH PASS', len(s))
