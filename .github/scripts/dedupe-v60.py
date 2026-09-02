from pathlib import Path
p=Path('sua-giao-an/v60.html')
s=p.read_text(encoding='utf-8')

marker='data-v60-dedupe-approved="1"'
if marker not in s:
    needle='function render(){'
    if needle not in s:
        raise SystemExit('RENDER_HANDLER_NOT_FOUND')
    inject=r'''function render(){/* data-v60-dedupe-approved="1" */const __seenApproved=new Set();for(const __c of S.changes){if(!__c.approved||__c.rejected)continue;const __k=[__c.document,__c.part,__c.paragraphIndex,__c.matchStart,__c.matchLength,norm(__c.anchor||''),norm(__c.new||__c.replacement||__c.insertText||'')].join('|');if(__seenApproved.has(__k)){__c.approved=false;__c.rejected=true;__c.applyNote='Tự động loại vì trùng Change Set đã duyệt.'}else __seenApproved.add(__k)}'''
    s=s.replace(needle,inject,1)

# Show dedupe reason in each Change Set card without changing the existing engine.
old="<div>'+esc(c.reason||'')+'</div><button class=\"btn g\""
new="<div>'+esc(c.reason||'')+'</div>'+(c.applyNote?'<div class=\"muted\">⚠️ '+esc(c.applyNote)+'</div>':'')+'<button class=\"btn g\""
if old in s:
    s=s.replace(old,new,1)

for bad in ('value="TIENG_ANH"','value="TIN_HOC"','value="MI_THUAT"','value="AM_NHAC"'):
    if bad in s:
        raise SystemExit('EXCLUDED_SUBJECT_PRESENT: '+bad)
if marker not in s:
    raise SystemExit('DEDUPE_MARKER_MISSING')
if s.count('function render(){')!=1:
    raise SystemExit('RENDER_HANDLER_COUNT_FAIL')

p.write_text(s,encoding='utf-8')
print('DEDUPE_PATCH_OK',len(s))