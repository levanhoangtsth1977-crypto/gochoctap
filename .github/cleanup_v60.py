from pathlib import Path
import re
import subprocess

ROOT=Path('.')
V=ROOT/'sua-giao-an/v60.html'
BASE='7daa9485da45ad4f1b4fc5ed263b3d6a92a51959'

# Restore known pre-patch v6.0 source.
clean=subprocess.check_output(['git','show',f'{BASE}:sua-giao-an/v60.html'],text=True)

# Gemini: stable primary + stable fallback only.
clean=clean.replace('value="gemini-2.5-flash">Gemini 2.5 Flash — tiết kiệm','value="gemini-3.6-flash">Gemini 3.6 Flash — dự phòng ổn định')
clean=clean.replace('gemini-2.5-flash','gemini-3.6-flash')
clean=clean.replace('Gemini 3.7 Flash — ổn định','Gemini 3.7 Flash — khuyên dùng')

# Remove excluded subjects if they ever appear in the source.
for value in ('TIENG_ANH','TIN_HOC','MI_THUAT','AM_NHAC'):
    clean=re.sub(r'<label><input class="subjectCheck" type="checkbox" value="'+value+r'">.*?</label>','',clean,flags=re.S)
clean=re.sub(r"TIENG_ANH:'Tiếng Anh',TIN_HOC:'Tin học',MI_THUAT:'Mĩ thuật',AM_NHAC:'Âm nhạc',",'',clean)

# Keep one implementation of named duplicate functions.
def keep_one_named_function(src,name):
    marker='function '+name+'('
    first=src.find(marker)
    if first<0:return src
    second=src.find(marker,first+1)
    if second<0:return src
    # Only collapse duplicates before the next distinct top-level named function when practical.
    # For these helpers the duplicate implementations are contiguous in the base.
    next_named=src.find('function ',second+1)
    if next_named<0:return src
    return src[:first]+src[first:second]+src[next_named:]

clean=keep_one_named_function(clean,'parseGeminiJSON')
clean=keep_one_named_function(clean,'__v60SafeXmlEdit')

# Patch Gemini AI document resolution: exact name -> source -> single loaded DOCX.
old="const c=g.change,d=S.docs.find(x=>x.name===(c.document||g.location));if(!d){blocked++;continue}"
new="const c=g.change,d=S.docs.find(x=>x.name===(c.document||g.location))||S.docs.find(x=>x.source===(c.document||g.location))||(S.docs.length===1?S.docs[0]:null);if(!d){blocked++;continue}"
clean=clean.replace(old,new)

# Replace only the original apply handler with one authoritative transactional handler.
start=clean.find("$('apply').onclick=()=>{")
end=clean.find("$('gemTest').onclick=",start)
if start<0 or end<=start:
    raise SystemExit('APPLY_HANDLER_NOT_FOUND_IN_BASE')
apply=r'''$('apply').onclick=()=>{
  const approved=S.changes.filter(c=>c.approved&&!c.rejected&&!c.applied);
  if(!approved.length){$('out').textContent='⚠️ Không có Change Set hợp lệ đã duyệt.';return}
  $('apply').disabled=true;$('word').disabled=true;$('zip').disabled=true;
  $('validator').textContent='⏳ Transaction APPLY: đang kiểm tra toàn bộ thay đổi...';
  const staged=S.docs.map((d,i)=>({original:d,index:i,parts:{...d.parts}}));
  const byOriginal=new Map(staged.map(x=>[x.original,x]));
  const resolveDoc=c=>{
    if(Number.isInteger(c.docIndex)&&S.docs[c.docIndex])return S.docs[c.docIndex];
    const ref=String(c.document||c.location||'').trim();
    return S.docs.find(d=>d.name===ref)||S.docs.find(d=>d.source===ref)||(S.docs.length===1?S.docs[0]:null);
  };
  const resolveAnchor=(parts,c)=>{
    const anchor=String(c.anchor||c.old_text||'');
    if(!anchor)return null;
    const preferred=c.part&&parts[c.part]?c.part:null;
    const names=preferred?[preferred]:Object.keys(parts);
    const hits=[];
    for(const part of names){
      for(const p of pars(parts[part])){
        const at=p.text.indexOf(anchor);
        if(at>=0)hits.push({part,paragraphIndex:p.i,matchStart:at,matchLength:anchor.length});
      }
    }
    if(hits.length===1)return hits[0];
    if(Number.isInteger(c.paragraphIndex)){
      const h=hits.find(x=>x.paragraphIndex===c.paragraphIndex);
      if(h)return h;
    }
    return null;
  };
  const seen=new Set(),queue=[];
  for(const c of approved){
    const doc=resolveDoc(c);
    if(!doc){c.applyNote='Không xác định được tài liệu.';continue}
    const key=[doc.name,c.part,norm(c.anchor||c.old_text||''),norm(c.new||c.new_text||c.insertText||''),c.action].join('|');
    if(seen.has(key)){c.rejected=true;c.approved=false;c.applyNote='Tự động loại vì trùng Change Set.';continue}
    seen.add(key);queue.push({c,doc});
  }
  const failures=[];
  try{
    for(const item of queue){
      const box=byOriginal.get(item.doc);
      const loc=resolveAnchor(box.parts,item.c);
      if(!loc){failures.push(item.c.id+': Anchor không còn tồn tại hoặc không duy nhất.');continue}
      const cc={...item.c,...loc};
      const current=box.parts[loc.part];
      const r=item.c.type==='INTEGRATION'?appendRun(current,cc):replaceRun(current,cc);
      if(!r||!r.ok){failures.push(item.c.id+': '+(r?.reason||'Không thể sửa XML.'));continue}
      box.parts[loc.part]=r.xml;
      item.c.part=loc.part;item.c.paragraphIndex=loc.paragraphIndex;item.c.matchStart=loc.matchStart;item.c.matchLength=loc.matchLength;
    }
    if(failures.length)throw Error(failures.join(' | '));
    for(const box of staged)box.original.parts=box.parts;
    queue.forEach(x=>x.c.applied=true);
    S.applied=queue.length>0;
    $('aa').textContent=String(queue.length);
    $('validator').textContent='✅ Transaction APPLY + POST-VALIDATOR PASS · '+queue.length+' Change Set đã áp dụng.';
    $('preview').textContent=S.docs.map(d=>d.name+'\n'+Object.entries(d.parts).map(([p,x])=>p+'\n'+pars(x).map(a=>a.text).join('\n')).join('\n')).join('\n\n');
    $('bulkStatus').textContent='✅ Áp dụng thành công: '+queue.length+' Change Set.';
    $('out').textContent='✅ Bản làm việc đã sửa và kiểm tra. Có thể xuất Word/ZIP.';
    $('word').disabled=!S.applied;$('zip').disabled=!S.applied;$('log').disabled=!S.applied;step(7);audit('Áp dụng transaction thành công: '+queue.length+' Change Set.');
  }catch(e){
    for(const box of staged)box.original.parts={...box.parts};
    S.applied=false;S.changes.forEach(c=>c.applied=false);$('aa').textContent='0';$('word').disabled=true;$('zip').disabled=true;$('log').disabled=true;
    $('validator').textContent='❌ APPLY rollback toàn bộ.\n'+(e.message||String(e));$('out').textContent='❌ '+(e.message||String(e));$('bulkStatus').textContent='❌ APPLY rollback toàn bộ.';audit('APPLY rollback: '+(e.message||String(e)));
  }finally{$('apply').disabled=!S.changes.some(c=>c.approved&&!c.rejected&&!c.applied)}
};
'''
clean=clean[:start]+apply+clean[end:]

# Minimal standalone entrypoint; no iframe/bridge.
(ROOT/'sua-giao-an/index.html').write_text('''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Cache-Control" content="no-store,no-cache,must-revalidate,max-age=0"><meta http-equiv="Pragma" content="no-cache"><meta http-equiv="Expires" content="0"><title>🛠️ Trang Sửa Giáo Án · v6.0</title></head><body><script>location.replace('./v60.html?v=6.0&cb=202609021015');</script><noscript><a href="./v60.html?v=6.0&cb=202609021015">Mở Trang Sửa Giáo Án v6.0</a></noscript></body></html>''',encoding='utf-8')
V.write_text(clean,encoding='utf-8')

# Delete legacy versions, bridges, prototypes, and patch scripts.
paths='''
.github/v60-final-fix-trigger.txt
.github/v60-live-fix-trigger.txt
.github/cleanup-v60-trigger.txt
sua-giao-an/v04.html
sua-giao-an/v08.html
sua-giao-an/v09.html
sua-giao-an/v10.html
sua-giao-an/v11.html
sua-giao-an/v12.html
sua-giao-an/v13.html
sua-giao-an/v13.js
sua-giao-an/v14.html
sua-giao-an/v60-hotfix.html
sua-giao-an/v60-ui-bridge.js
sua-giao-an/document-engine-bridge.js
sua-giao-an/subject-picker.js
sua-giao-an/requirements.txt
sua-giao-an/vercel.json
'''.split()
for x in paths:
    p=ROOT/x
    if p.exists(): subprocess.run(['git','rm','-f',x],check=False)
for d in ('sua-giao-an/v08','sua-giao-an/api','sua-giao-an/backend','.github/scripts'):
    p=ROOT/d
    if p.exists(): subprocess.run(['git','rm','-rf',d],check=False)

# Replace the old patching workflow with read-only CI; it never rewrites the application.
wf=ROOT/'.github/workflows/v60-live-fix.yml'
wf.write_text('''name: V60 CI\non:\n  push:\n    paths:\n      - sua-giao-an/v60.html\n      - sua-giao-an/index.html\n      - sua-giao-an/SPEC.md\n      - sua-giao-an/*.json\n      - sua-giao-an/tests/**\n      - .github/workflows/v60-live-fix.yml\n  workflow_dispatch:\npermissions:\n  contents: read\njobs:\n  validate:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - name: Validate clean V60\n        run: |\n          python3 - <<\'PY\'\n          from pathlib import Path\n          import re\n          v=Path(\'sua-giao-an/v60.html\').read_text(encoding=\'utf-8\')\n          i=Path(\'sua-giao-an/index.html\').read_text(encoding=\'utf-8\')\n          for bad in (\'gemini-2.5-flash\',\'value="TIENG_ANH"\',\'value="TIN_HOC"\',\'value="MI_THUAT"\',\'value="AM_NHAC"\'):\n              if bad in v: raise SystemExit(\'FORBIDDEN: \'+bad)\n          for fn in (\'parseGeminiJSON\',\'runGemini\',\'__v60SafeXmlEdit\'):\n              n=len(re.findall(r\'function \'+re.escape(fn)+r\'\\(\',v))\n              if n!=1: raise SystemExit(\'FUNCTION_COUNT \'+fn+\':\'+str(n))\n          for expr in ("$(\'apply\').onclick=","$(\'word\').onclick=","$(\'zip\').onclick="):\n              if v.count(expr)!=1: raise SystemExit(\'HANDLER_COUNT \'+expr)\n          if \"value=\\\"gemini-3.7-flash\\\"\" not in v or \"value=\\\"gemini-3.6-flash\\\"\" not in v: raise SystemExit(\'GEMINI_SELECTOR_INVALID\')\n          if \'<iframe\' in i or \"contentDocument\" in i: raise SystemExit(\'INDEX_BRIDGE_REMAINS\')\n          scripts=re.findall(r\'<script[^>]*>(.*?)</script>\',v,re.S)\n          Path(\'/tmp/v60.js\').write_text(max(scripts,key=len),encoding=\'utf-8\')\n          print(\'V60_CLEAN_SOURCE_OK\')\n          PY\n          node --check /tmp/v60.js\n      - name: Validate data package\n        run: |\n          for f in sua-giao-an/SPEC.md sua-giao-an/format-standard.json sua-giao-an/administrative-standard-2026-2027.json sua-giao-an/special-administrative-zones-2026-2027.json sua-giao-an/curriculum-adjustments-2026-2027.json sua-giao-an/integration-library-2026-2027.json; do test -f \"$f\" || exit 1; done\n          echo DATA_PACKAGE_OK\n''',encoding='utf-8')

# Remove the one-time workflow and script after creating the clean commit.
for x in ('.github/cleanup_v60.py','.github/workflows/cleanup-v60-once.yml'):
    p=ROOT/x
    if p.exists(): subprocess.run(['git','rm','-f',x],check=False)

subprocess.run(['git','add','-A'],check=True)
subprocess.run(['git','config','user.name','v60-cleanup'],check=True)
subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],check=True)
subprocess.run(['git','commit','-m','refactor(sua-giao-an): restore clean v6.0 and remove legacy runtime patches'],check=True)
subprocess.run(['git','push'],check=True)
print('CLEAN_V60_COMMITTED')
