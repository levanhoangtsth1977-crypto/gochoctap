from pathlib import Path
import re

p = Path('sua-giao-an/index.html')
s = p.read_text(encoding='utf-8')

# 1) Remove bridge-side attempts to unlock/export Word/ZIP.
s = s.replace("if(word)word.disabled=false;if(zip)zip.disabled=false;if(log)log.disabled=false;", "if(log)log.disabled=false;")

# 2) Remove bridge click handlers that only fake a successful export message.
s, _ = re.subn(
    r"if\(word&&!word\.dataset\.inlineBridge\)\{.*?\}if\(zip&&!zip\.dataset\.inlineBridge\)\{.*?\}",
    "",
    s,
    count=1,
    flags=re.S,
)

# The patch is intentionally idempotent: already-clean source is valid.
if 'word.disabled=false' in s or 'zip.disabled=false' in s:
    raise SystemExit('BRIDGE_EXPORT_UNLOCK_REMAINS')

p.write_text(s, encoding='utf-8')
print('EXPORT_BRIDGE_LOCK_OK', len(s))
