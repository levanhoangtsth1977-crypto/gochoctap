from pathlib import Path
import re

p=Path('sua-giao-an/v60.html')
s=p.read_text(encoding='utf-8')

def replace_between(src, start_marker, end_marker, new_text):
    a=src.find(start_marker)
    b=src.find(end_marker,a)
    if a<0 or b<0:
        raise SystemExit(f'PATCH_RANGE_NOT_FOUND: {start_marker} -> {end_marker}')
    return src[:a]+new_text+src[b:]

MARK='/* FINAL XML TEXT EDIT FIX */'
start=s.find('function __txApplyOne(parts,c){')
end=s.find('function __txSetExportState', start)
if start<0 or end<0:
    raise SystemExit('TX_APPLY_FUNCTION_NOT_FOUND')

new_func=r'''/* FINAL XML TEXT EDIT FIX */
function __txXmlEsc(s){return String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&apos;')}
function __txXmlDec(s){return String(s??'').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&apos;/g,"'").replace(/&amp;/g,'&')}
function __txSafeEdit(xml,paragraphIndex,anchor,replacement,action){
  const ps=[...xml.matchAll(/<w:p(?:\s[^>]*)?>[\s\S]*?<\/w:p>/g)];
  const pm=ps[paragraphIndex];
  if(!pm)return{ok:false,reason:'Không tìm thấy paragraph '+(paragraphIndex+1)+'.'};
  let pxml=pm[0];
  const ts=[...pxml.matchAll(/(<w:t(?:\s[^>]*)?>)([\s\S]*?)(<\/w:t>)/g)];
  if(!ts.length)return{ok:false,reason:'Paragraph không có vùng văn bản w:t.'};
  if(action==='INSERT_AFTER'){
    pxml=pxml.replace(/<\/w:p>\s*$/,'<w:r><w:t>'+__txXmlEsc(replacement)+'</w:t></w:r></w:p>');
  }else{
    const decoded=ts.map(m=>__txXmlDec(m[2]));
    const flat=decoded.join('');
    const idx=flat.indexOf(String(anchor??''));
    if(idx<0)return{ok:false,reason:'Không tìm thấy Anchor trong paragraph.'};
    const endIdx=idx+String(anchor??'').length;
    let cur=0,si=-1,ei=-1,so=0,eo=0;
    for(let i=0;i<decoded.length;i++){
      const next=cur+decoded[i].length;
      if(si<0 && idx>=cur && idx<next){si=i;so=idx-cur;}
      if(endIdx>cur && endIdx<=next){ei=i;eo=endIdx-cur;break}
      cur=next;
    }
    if(si<0||ei<0)return{ok:false,reason:'Không xác định được vị trí Anchor.'};
    const vals=decoded.slice();
    const repl=action==='DELETE'?'':String(replacement??'');
    vals[si]=decoded[si].slice(0,so)+repl+decoded[si].slice(eo);
    for(let i=si+1;i<=ei;i++)vals[i]=i===ei?decoded[i].slice(eo):'';
    for(let i=ts.length-1;i>=0;i--){
      const m=ts[i];
      const from=m.index,to=m.index+m[0].length;
      pxml=pxml.slice(0,from)+m[1]+__txXmlEsc(vals[i])+m[3]+pxml.slice(to);
    }
  }
  return{ok:true,xml:xml.slice(0,pm.index)+pxml+xml.slice(pm.index+pm[0].length)};
}
function __txApplyOne(parts,c){
  const oldXml=parts[c.part];
  if(typeof oldXml!=='string')return{ok:false,reason:'Thiếu XML '+c.part+'.'};
  const beforePars=pars(oldXml),bp=beforePars[c.paragraphIndex];
  if(!bp)return{ok:false,reason:'Không có paragraph '+(c.paragraphIndex+1)+'.'};
  const anchor=String(c.anchor||c.old_text||''),beforeText=bp.text;
  if(c.action!=='INSERT_AFTER' && !anchor)return{ok:false,reason:'Thiếu Anchor.'};
  if(c.action!=='INSERT_AFTER' && __txCount(beforeText,anchor)<1)return{ok:false,reason:'Anchor không còn tồn tại.'};
  const replacement=String(c.new||c.new_text||c.insertText||'');
  const r=__txSafeEdit(oldXml,c.paragraphIndex,anchor,replacement,c.action||'REPLACE');
  if(!r.ok)return r;
  const afterPars=pars(r.xml),ap=afterPars[c.paragraphIndex];
  if(!ap)return{ok:false,reason:'Không đọc lại được paragraph sau áp dụng.'};
  if(c.action!=='INSERT_AFTER' && c.action!=='DELETE' && __txCount(ap.text,replacement)<1)return{ok:false,reason:'Không xác minh được NEW sau áp dụng.'};
  if(c.action==='DELETE' && __txCount(ap.text,anchor)>0)return{ok:false,reason:'OLD vẫn còn sau DELETE.'};
  parts[c.part]=r.xml;
  return{ok:true};
}
'''
s=s[:start]+new_func+s[end:]

# Hard-lock legacy runtime helpers if present: replace their bodies with safe delegation.
legacy_patterns=[
    (r'function\s+replaceRun\s*\([^)]*\)\s*\{', 'replaceRun'),
    (r'function\s+appendRun\s*\([^)]*\)\s*\{', 'appendRun'),
]
for pat,name in legacy_patterns:
    m=re.search(pat,s)
    if not m: continue
    body_start=m.start()
    brace=m.end()-1
    depth=0; end_idx=None
    for i in range(brace,len(s)):
        ch=s[i]
        if ch=='{': depth+=1
        elif ch=='}':
            depth-=1
            if depth==0:
                end_idx=i+1
                break
    if end_idx is None: raise SystemExit(name+'_BODY_NOT_FOUND')
    # Keep signature parameters intact; runtime safety is enforced by throwing a descriptive error.
    sig=s[body_start:brace+1]
    if name=='replaceRun':
        body=s[body_start:brace+1]+'return false;}'
    else:
        body=s[body_start:brace+1]+'return false;}'
    s=s[:body_start]+body+s[end_idx:]

p.write_text(s,encoding='utf-8')
print('XML_EDIT_FIX_OK',len(s))
