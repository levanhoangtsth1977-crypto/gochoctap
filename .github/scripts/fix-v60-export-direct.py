from pathlib import Path
import re

P=Path('sua-giao-an/v60.html')
s=P.read_text(encoding='utf-8')
MARK='/* DIRECT WORKING-DOC EXPORT FIX */'
if MARK in s:
    print('DIRECT_EXPORT_ALREADY_PRESENT')
    raise SystemExit(0)

js=r'''/* DIRECT WORKING-DOC EXPORT FIX */
(function(){
  const __directExportMsg = (text, bad=false) => {
    const el=document.getElementById('out');
    if(el){ el.textContent=(bad?'❌ ':'✅ ')+text; }
  };
  const __syncZipParts = (d) => {
    if(!d || !d.zip || !d.parts) throw new Error('Không có tài liệu làm việc để xuất.');
    for(const [name,xml] of Object.entries(d.parts)) d.zip.file(name,xml);
    return d.zip;
  };
  const __downloadBlob = (blob,name) => {
    const u=URL.createObjectURL(blob),a=document.createElement('a');
    a.href=u;a.download=name;document.body.appendChild(a);a.click();a.remove();
    setTimeout(()=>URL.revokeObjectURL(u),1000);
  };
  const __exportWordDirect = async () => {
    try{
      if(!S.docs.length) throw new Error('Chưa có tài liệu làm việc.');
      if(!S.applied) throw new Error('Chưa áp dụng thay đổi hợp lệ.');
      const d=S.docs[0],z=__syncZipParts(d);
      const blob=await z.generateAsync({type:'blob',mimeType:'application/vnd.openxmlformats-officedocument.wordprocessingml.document'});
      const base=(d.name||'giao_an').replace(/\.docx$/i,'')+'_DA_SUA.docx';
      __downloadBlob(blob,base);
      __directExportMsg('Xuất Word thành công: '+base);
      audit('Xuất Word trực tiếp từ tài liệu làm việc.');
      step(7);
    }catch(e){__directExportMsg(e.message||String(e),true);audit('Xuất Word lỗi: '+(e.message||String(e)));}
  };
  const __exportZipDirect = async () => {
    try{
      if(!S.docs.length) throw new Error('Chưa có tài liệu làm việc.');
      if(!S.applied) throw new Error('Chưa áp dụng thay đổi hợp lệ.');
      const outZip=new JSZip();
      for(const d of S.docs){
        const z=__syncZipParts(d);
        const buf=await z.generateAsync({type:'arraybuffer'});
        const safe=(d.name||'giao_an.docx').replace(/[\\/:*?"<>|]/g,'_');
        outZip.file(safe,buf);
      }
      const blob=await outZip.generateAsync({type:'blob',mimeType:'application/zip'});
      __downloadBlob(blob,'GIAO_AN_DA_SUA.zip');
      __directExportMsg('Xuất ZIP thành công: '+S.docs.length+' tài liệu.');
      audit('Xuất ZIP trực tiếp từ '+S.docs.length+' tài liệu làm việc.');
      step(7);
    }catch(e){__directExportMsg(e.message||String(e),true);audit('Xuất ZIP lỗi: '+(e.message||String(e)));}
  };
  $('word').onclick=__exportWordDirect;
  $('zip').onclick=__exportZipDirect;
  $('log').onclick=()=>{
    try{
      const rows=[...S.changes.filter(c=>c.applied||c.approved&&!c.rejected),...S.integration.filter(c=>c.applied)];
      const text=rows.length?rows.map((c,i)=>(i+1)+'. '+(c.id||'')+' | '+(c.document||'')+' | '+(c.part||'')+' | '+(c.anchor||c.old||'')+' -> '+(c.new||c.insertText||'')).join('\n'):'Không có Change Set đã áp dụng.';
      const blob=new Blob([text],{type:'text/plain;charset=utf-8'});__downloadBlob(blob,'CHANGE_LOG.txt');
      __directExportMsg('Đã xuất Change Log.');
    }catch(e){__directExportMsg(e.message||String(e),true);}
  };
  $('word').disabled=true;$('zip').disabled=true;$('log').disabled=true;
  window.__V60_DIRECT_EXPORT_READY__=()=>{const ready=!!S.applied; if(document.getElementById('word'))document.getElementById('word').disabled=!ready; if(document.getElementById('zip'))document.getElementById('zip').disabled=!ready; if(document.getElementById('log'))document.getElementById('log').disabled=!S.changes.length&&!S.integration.length;};
  const __oldApply=document.getElementById('apply')?.onclick;
  if(__oldApply){
    document.getElementById('apply').onclick=async function(ev){
      const r=await __oldApply.call(this,ev);
      setTimeout(()=>window.__V60_DIRECT_EXPORT_READY__(),0);
      return r;
    };
  }
})();
'''

m=re.search(r'\n\s*\}\)\(\);\s*</script>',s)
if not m:
    m=re.search(r'\}\)\(\);\s*</script>',s)
if not m:
    raise SystemExit('V60_IIFE_END_NOT_FOUND')
s=s[:m.start()]+'\n'+js+s[m.start():]
P.write_text(s,encoding='utf-8')
print('DIRECT_EXPORT_FIX_OK',len(s))