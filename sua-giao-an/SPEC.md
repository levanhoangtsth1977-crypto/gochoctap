# 🛠️ TRANG SỬA GIÁO ÁN — ĐẶC TẢ CHÍNH THỨC

**Phiên bản đặc tả:** 1.0  
**Phạm vi:** Document Engine + Format Engine + AI/Rules + Validator + Export  
**Nguyên tắc:** Nội dung gốc được bảo toàn; định dạng đầu ra phải được chuẩn hóa, cân đối và kiểm tra trước khi xuất.

## 1. NGUYÊN TẮC BẤT BIẾN

1. Không tự ý xóa nội dung gốc.
2. Không rút gọn giáo án.
3. Không viết lại toàn bộ giáo án.
4. Không tự ý đảo thứ tự hoạt động.
5. Không tự ý thay đổi mục tiêu, câu hỏi, đáp án hoặc nội dung chuyên môn ngoài phạm vi được phép.
6. Không làm mất bảng, hình ảnh, chú thích, tiêu đề, phụ lục hoặc cấu trúc tài liệu.
7. Mọi thay đổi nội dung phải tạo **Change Set** và ghi rõ vị trí, nội dung cũ, nội dung mới, lý do và trạng thái duyệt.
8. File gốc luôn được giữ nguyên; file xuất là một bản mới.

## 2. TIÊU CHUẨN ĐỊNH DẠNG WORD — BẮT BUỘC

Format Engine **phải** áp dụng hoặc kiểm tra các chuẩn sau khi xuất DOCX:

| Hạng mục | Chuẩn bắt buộc |
|---|---|
| Khổ giấy | A4 |
| Font nội dung | Times New Roman |
| Cỡ chữ nội dung | 13 pt |
| Tiêu đề chính | Times New Roman, 14 pt, đậm |
| Tiêu đề mục | Times New Roman, 13 pt, đậm |
| Căn lề trên | 2,0 cm |
| Căn lề dưới | 2,0 cm |
| Căn lề trái | 2,5 cm |
| Căn lề phải | 1,5 cm |
| Giãn dòng | 1,15 |
| Khoảng cách đoạn | Đồng nhất, tránh khoảng trắng thừa |
| Đầu dòng/indent | Đồng nhất theo cấp mục |
| Đánh số mục | Đồng nhất, không nhảy cấp |
| Bullet | Đồng nhất kiểu và thụt lề |
| Bảng | Không tràn lề, không méo tỷ lệ |
| Căn dọc ô | Top |
| Căn ngang nội dung bảng | Trái, trừ tiêu đề/ô cần căn giữa |
| Bảng GV–HS | Cân đối chiều rộng cột, mặc định 50%–50% |
| Chiều rộng bảng | Vừa vùng soạn thảo A4 sau khi tính lề |
| Ngắt trang | Không để tiêu đề cô độc hoặc bảng vỡ bất hợp lý |
| Header/Footer | Đồng nhất nếu tài liệu có sử dụng |
| Trang mới giữa các bài | Theo cấu trúc bài/tiết, không ngắt tùy tiện |

## 3. CHẾ ĐỘ CHUẨN HÓA

### A. GIỮ NGUYÊN
Chỉ sửa nội dung được phép; không can thiệp định dạng ngoài mức cần thiết.

### B. CHUẨN HÓA NHẸ — MẶC ĐỊNH
Chuẩn hóa font, cỡ chữ, lề, giãn dòng, khoảng cách đoạn, bảng và các lỗi trình bày rõ ràng nhưng giữ tối đa bố cục gốc.

### C. CHUẨN HÓA TOÀN BỘ
Đưa tài liệu về chuẩn định dạng thống nhất của hệ thống khi người dùng chủ động chọn chế độ này.

## 4. CÂN ĐỐI CỘT VÀ BẢNG — BẮT BUỘC

Document/Format Engine phải:

- phát hiện bảng có cột quá rộng hoặc quá hẹp;
- tính vùng soạn thảo thực tế sau khi trừ lề;
- tự cân đối chiều rộng cột GV–HS;
- mặc định 50%–50% cho bảng hai cột khi không có lý do rõ ràng để dùng tỷ lệ khác;
- cho phép cấu hình tỷ lệ khác như 55%–45% nhưng phải áp dụng nhất quán trong cùng tài liệu;
- không để chữ tràn khỏi ô;
- hạn chế việc một hàng bị tách gây mất nghĩa khi sang trang;
- không làm bảng vượt khổ giấy;
- giữ đường viền, tiêu đề bảng và cấu trúc ô;
- giữ nội dung trong ô nguyên vẹn.

## 5. PHẦN NỘI DUNG AI BỔ SUNG

Tất cả nội dung mới do AI/hệ thống thêm vào phải:

- **in nghiêng**;
- **tô màu toàn bộ phần được thêm**;
- được ghi vào Change Log;
- không được trộn lẫn khiến người dùng không nhận biết đâu là nội dung gốc.

## 6. DOCUMENT ENGINE

Document Engine phải đọc và bảo toàn tối đa:

- paragraph;
- run và character formatting;
- heading/style;
- table/row/cell;
- ảnh và vị trí ảnh khi có thể;
- header/footer;
- page break;
- section;
- numbering/bullets;
- hyperlinks và chú thích khi công nghệ xử lý hỗ trợ.

Không dùng thao tác "chuyển toàn bộ văn bản thành plain text rồi tạo Word mới" làm phương án mặc định, vì có nguy cơ phá bố cục và định dạng gốc.

## 7. AI + RULE ENGINE

AI chỉ được **phân tích và tạo đề xuất/Change Set**. Rule Engine quyết định đề xuất nào được phép thực thi.

AI không được phép tự ghi trực tiếp vào DOCX khi chưa qua Rule Engine.

## 8. VALIDATOR — ĐIỀU KIỆN BẮT BUỘC TRƯỚC KHI XUẤT

Validator phải kiểm tra tối thiểu:

- file mở được;
- không mất đoạn văn;
- không mất bảng;
- không mất nội dung trong bảng;
- không mất hình/đối tượng được hỗ trợ;
- số section hợp lệ;
- font/cỡ chữ/lề/giãn dòng theo cấu hình;
- bảng không tràn vùng in;
- cột không méo;
- không tạo trang trắng bất thường;
- các Change Set đã được duyệt hoặc loại bỏ theo trạng thái;
- bản gốc và bản xuất tồn tại độc lập.

Nếu Validator không đạt, **không cho phép nút Xuất hoàn tất**.

## 9. ĐẦU RA

Hệ thống phải hỗ trợ:

- `DOCX` giáo án sau sửa và chuẩn hóa;
- `ZIP` chứa toàn bộ giáo án của một tuần;
- giáo án điện tử theo định dạng được hỗ trợ;
- `CHANGE_LOG` ghi toàn bộ thay đổi;
- tên file đầu ra có hậu tố rõ ràng, không ghi đè file gốc.

## 10. LUỒNG CHUẨN

```text
FILE GỐC
  ↓
DOCUMENT PARSER
  ↓
CONTENT PROTECTION
  ↓
AI ANALYZER
  ↓
RULE ENGINE
  ↓
CHANGE SET
  ↓
USER REVIEW / AUTO APPROVAL THEO LUẬT
  ↓
DOCUMENT ENGINE
  ↓
FORMAT ENGINE ⭐ BẮT BUỘC
  ↓
LAYOUT VALIDATOR
  ↓
EXPORT DOCX / ZIP / HTML
```

## 11. TIÊU CHÍ NGHIỆM THU

Một bản xuất chỉ được coi là **ĐẠT** khi đồng thời đạt:

**Đúng nội dung được duyệt + bảo toàn nội dung không liên quan + đúng định dạng chuẩn + bảng/cột cân đối + Validator đạt + có Change Log.**

**Format Engine không phải chức năng tùy chọn khi xuất DOCX; đây là tiêu chuẩn bắt buộc của hệ thống.**
