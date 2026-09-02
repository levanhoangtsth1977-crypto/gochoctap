from pathlib import Path
p = Path('sua-giao-an/index.html')
s = p.read_text(encoding='utf-8')
old = "if(word)word.disabled=false;if(zip)zip.disabled=false;if(log)log.disabled=false;"
if old in s:
    s = s.replace(old, "if(log)log.disabled=false;", 1)
else:
    raise SystemExit('BRIDGE_EXPORT_UNLOCK_NOT_FOUND')
# Remove bridge click handlers that only report UI state; real download stays owned by v60.html.
import re
s2, n = re.subn(r"if\(word&&!word\.dataset\.inlineBridge\)\{.*?\}if\(zip&&!zip\.dataset\.inlineBridge\)\{.*?\}", "", s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('BRIDGE_EXPORT_HANDLER_BLOCK_NOT_FOUND')
if 'word.disabled=false' in s2 or 'zip.disabled=false' in s2:
    raise SystemExit('BRIDGE_EXPORT_UNLOCK_REMAINS')
p.write_text(s2, encoding='utf-8')
print('EXPORT_BRIDGE_LOCK_OK', len(s2))
