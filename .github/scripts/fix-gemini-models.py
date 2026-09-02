from pathlib import Path
import re
p = Path('sua-giao-an/v60.html')
s = p.read_text(encoding='utf-8')
s = s.replace('value="gemini-2.5-flash">Gemini 2.5 Flash — tiết kiệm', 'value="gemini-3.6-flash">Gemini 3.6 Flash — dự phòng ổn định')
s = s.replace('gemini-2.5-flash', 'gemini-3.6-flash')
s = s.replace('Gemini 2.5 Flash', 'Gemini 3.6 Flash')
s = s.replace('Gemini 3.7 Flash — ổn định', 'Gemini 3.7 Flash — khuyên dùng')
if 'gemini-2.5-flash' in s: raise SystemExit('GEMINI_2_5_STILL_PRESENT')
if 'gemini-3.7-flash' not in s or 'gemini-3.6-flash' not in s: raise SystemExit('REQUIRED_GEMINI_MODELS_MISSING')
p.write_text(s, encoding='utf-8')
print('GEMINI_MODEL_FIX_OK')
