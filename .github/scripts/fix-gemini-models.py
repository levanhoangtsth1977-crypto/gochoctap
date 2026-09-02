from pathlib import Path
import re

p = Path('sua-giao-an/v60.html')
s = p.read_text(encoding='utf-8')

# Force exactly two selectable Gemini models, regardless of earlier patches.
s = re.sub(
    r'<select id="gemModel" class="input">.*?</select>',
    '<select id="gemModel" class="input"><option value="gemini-3.7-flash">Gemini 3.7 Flash — khuyên dùng</option><option value="gemini-3.6-flash">Gemini 3.6 Flash — dự phòng ổn định</option></select>',
    s,
    flags=re.S,
)

# Remove obsolete model identifiers from the runtime.
s = s.replace('gemini-2.5-flash', 'gemini-3.6-flash')
s = s.replace('Gemini 2.5 Flash', 'Gemini 3.6 Flash')
s = s.replace('gemini-3.5-flash-lite', 'gemini-3.6-flash')
s = s.replace('Gemini 3.5 Flash-Lite', 'Gemini 3.6 Flash')

# Repair fallback expressions that previously pointed back to 2.5.
s = s.replace("fallback=primary==='gemini-3.7-flash'?'gemini-2.5-flash':'gemini-3.7-flash'", "fallback=primary==='gemini-3.7-flash'?'gemini-3.6-flash':'gemini-3.7-flash'")
s = s.replace("fallback=primary==='gemini-3.7-flash'?'gemini-3.6-flash':'gemini-3.7-flash'", "fallback=primary==='gemini-3.7-flash'?'gemini-3.6-flash':'gemini-3.7-flash'")

# Strong source assertions.
if 'gemini-2.5-flash' in s:
    raise SystemExit('GEMINI_2_5_STILL_PRESENT')
if 'gemini-3.5-flash-lite' in s:
    raise SystemExit('GEMINI_3_5_STILL_PRESENT')
if s.count('value="gemini-3.7-flash"') != 1:
    raise SystemExit('PRIMARY_MODEL_SELECTOR_INVALID')
if s.count('value="gemini-3.6-flash"') != 1:
    raise SystemExit('FALLBACK_MODEL_SELECTOR_INVALID')

p.write_text(s, encoding='utf-8')
print('GEMINI_MODEL_FIX_OK')