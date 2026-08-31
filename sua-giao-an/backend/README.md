# TRANG SỬA GIÁO ÁN — BACKEND

## Trạng thái
Prototype kỹ thuật của Document Engine/Format Engine. Chưa phải production backend.

## Mục tiêu
- Nhận DOCX mà không ghi đè file gốc.
- Chuẩn hóa A4, Times New Roman 13 pt, lề 2/2/2.5/1.5 cm, line spacing 1.15.
- Giữ cấu trúc paragraph/table/section/inline image ở mức thư viện hỗ trợ.
- Kiểm tra mất paragraph/table/image và thay đổi số section.
- Chặn xuất khi validation lỗi.

## Chưa bật
- ZIP cả tuần.
- AI Analyzer/Gemini.
- Change Set thật từ AI.
- Duyệt từng thay đổi.
- Highlight phần nội dung AI thêm.
- Export persistent qua HTTP.
- Preview trực quan DOCX.

## Chạy cục bộ
```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Health: `GET /health`
Inspect: `POST /inspect` với multipart field `file`.
