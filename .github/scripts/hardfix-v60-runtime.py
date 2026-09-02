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

# Remove any duplicate const bad introduced by earlier variants before the validator assignment.
s=re.sub(r"S\.applied=ok>0;const bad=S\.changes\.filter\(c=>c\.applied&&!validate\(S\.docs\.find\(d=>d\.name===c\.document\),c\)\);S\.applied=ok>0;const bad=", "S.applied=ok>0;const bad=", s)

start=s.find('function __v60SafeXmlEdit')
end=s.find("$('gemTest')",start)
runtime=s[start:end] if start>=0 and end>start else ''
if 'insertBefore(' in runtime:
    raise SystemExit('UNSAFE_INSERTBEFORE_FOUND_IN_RUNTIME_PATCH')
if "function replaceRun(xml,c){return __v60SafeXmlEdit(xml,c,'REPLACE')}" not in s:
    raise SystemExit('REPLACER_NOT_LOCKED')
if "function appendRun(xml,c){return __v60SafeXmlEdit(xml,c,'INSERT_AFTER')}" not in s:
    raise SystemExit('APPENDER_NOT_LOCKED')

p.write_text(s,encoding='utf-8')
print('HARD_RUNTIME_PATCH_OK',len(s))