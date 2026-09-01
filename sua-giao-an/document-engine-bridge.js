(function(){'use strict';
function dec(s){return String(s||'').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&apos;/g,"'").replace(/&amp;/g,'&')}
function xmlText(xml){let out='';for(const m of String(xml||'').matchAll(/<w:t(?: [^>]*)?>([\s\S]*?)<\/w:t>/gi))out+=dec(m[1]);return out}
window.DOC_ENGINE_API={
  version:'1.3-bridge',
  getFiles:function(){const el=document.getElementById('files');return el?[...el.files]:[]},
  getState:function(){return S},
  getDocuments:function(){return S.docs.map(d=>({name:d.name,kind:d.kind,xml:d.xml,originalXml:d.originalXml,text:xmlText(d.xml)}))},
  getChanges:function(){return S.changes.map(x=>({...x}))},
  setChanges:function(changes){S.changes=Array.isArray(changes)?changes.map(x=>({...x,ui:x.ui||''})):[];if(typeof renderChanges==='function')renderChanges();if(typeof st==='function')st();},
  refresh:function(){if(typeof renderChanges==='function')renderChanges();if(typeof renderIntegration==='function')renderIntegration();if(typeof st==='function')st();},
  analyzeFiles:function(){const el=document.getElementById('analyze');if(el&&!el.disabled)el.click();},
  getText:function(){return S.docs.map(d=>({name:d.name,text:xmlText(d.xml)}))}
};
document.getElementById('files')?.addEventListener('change',function(){setTimeout(function(){window.parent.postMessage({type:'DOC_ENGINE_FILES',count:document.getElementById('files')?.files?.length||0},'*')},50)});
})();
