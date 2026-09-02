from pathlib import Path
import re

p=Path('sua-giao-an/v60.html')
s=p.read_text(encoding='utf-8')
MARK='/* FINAL XML TEXT EDIT FIX */'
if MARK in s:
    print('XML_EDIT_FIX_ALREADY_PRESENT')
    raise SystemExit(0)

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
    const insert=''+__txXmlEsc(replacement);
    pxml=pxml.replace(/<\/w:p>\s*$/,'<w:r><w:t>'+insert+'</w:t></w:r></w:p>');
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
    if(action==='DELETE')replacement='';
    vals[si]=decoded[si].slice(0,so)+String(replacement??'')+decoded[si].slice(eo);
    for(let i=si+1;i<=ei;i++)vals[i]=i===ei?decoded[i].slice(eo):'';
    for(let i=ts.length-1;i>=0;i--){
      const m=ts[i];
      const from=m.index, to=m.index+m[0].length;
      pxml=pxml.slice(0,from)+m[1]+__txXmlEsc(vals[i])+m[3]+pxml.slice(to);
    }
  }
  const from=pm.index,to=pm.index+pm[0].length;
  return{ok:true,xml:xml.slice(0,from)+pxml+xml.slice(to)};
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
  if(c.action==='REPLACE' && __txCount(ap.text,anchor)!==Math.max(0,__txCount(beforeText,anchor)-1))return{ok:false,reason:'OLD/Anchor sau REPLACE không đúng.'};
  parts[c.part]=r.xml;
  return{ok:true};
}
'''
s=s[:start]+new_func+s[end:]
p.write_text(s,encoding='utf-8')
print('XML_EDIT_FIX_OK',len(s))
