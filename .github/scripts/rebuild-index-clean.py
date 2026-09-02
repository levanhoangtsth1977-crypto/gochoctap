from pathlib import Path
p=Path('sua-giao-an/index.html')
p.write_text('''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Cache-Control" content="no-store,no-cache,must-revalidate,max-age=0"><meta http-equiv="Pragma" content="no-cache"><meta http-equiv="Expires" content="0"><title>Trang Sửa Giáo Án · v6.0 MASTER CLEAN</title></head><body style="margin:0"><iframe src="./v60.html?v=6.0&cb=202609021500" style="width:100%;height:100vh;border:0" title="Trang Sửa Giáo Án"></iframe></body></html>''',encoding='utf-8')
print('INDEX_CLEAN_OK')
