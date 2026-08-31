# TEST CASE CHUẨN — GIÁO ÁN TUẦN 2

## 1. Nguồn kiểm thử
Bộ kiểm thử được tạo từ chính nội dung giáo án ông chủ đã cung cấp trong cuộc trò chuyện, gồm:
- TOÁN — Chủ đề 1, Bài 01: Ôn tập số tự nhiên (T1)
- TIẾNG VIỆT — Chủ đề 1, Bài 01: Thanh âm của gió (Tiết 1: Đọc; Tiết 2: Luyện từ và câu)
- LỊCH SỬ - ĐỊA LÍ — Chủ đề 1, Bài 1: Vị trí địa lí, lãnh thổ, đơn vị hành chính, Quốc kì, Quốc huy, Quốc ca (Tiết 1)
- KHOA HỌC — Chủ đề 1, Bài 1: Thành phần và vai trò của đất đối với cây trồng (T1)

Đây là fixture chuẩn để kiểm thử parser, rule engine, format engine, validator và export.

## 2. Mục tiêu kiểm thử nội dung
### 2.1. Bảo toàn nội dung
- Không được mất đoạn văn.
- Không được mất bảng GV–HS.
- Không được làm mất câu hỏi, đáp án, ví dụ, hoạt động, lời dặn dò.
- Không được chuyển toàn bộ tài liệu thành plain text rồi dựng lại theo cách làm mất định dạng.
- File gốc phải độc lập với file xuất.

### 2.2. Các nhóm nội dung được phép kiểm tra
- Địa giới hành chính.
- Năng lực số.
- Công dân số.
- Biển đảo.
- Môi trường/BĐKH.
- CTGDPT 2018 + TT27.

## 3. CASE ĐỊA GIỚI HÀNH CHÍNH — LỊCH SỬ, ĐỊA LÍ

### CASE ADM-001 — Số đơn vị hành chính cấp tỉnh
**Nội dung cũ trong giáo án:** “Hiện nay, nước ta có 63 tỉnh, thành phố trực thuộc Trung ương.”

**Kỳ vọng:** Phát hiện đây là dữ liệu hành chính cũ; đề xuất cập nhật thành **34 đơn vị hành chính cấp tỉnh, gồm 28 tỉnh và 6 thành phố** theo Nghị quyết 202/2025/QH15.

**Không được làm:** tự viết lại toàn bộ mục; không thay đổi phần kiến thức địa lí không liên quan.

### CASE ADM-002 — Số thành phố trực thuộc Trung ương
**Nội dung cũ:** “5 thành phố trực thuộc Trung ương là Hà Nội, Hải Phòng, Đà Nẵng, Thành phố Hồ Chí Minh và Cần Thơ.”

**Kỳ vọng:** Phát hiện dữ liệu cũ; đề xuất cập nhật danh sách **6 thành phố** hiện hành: Hà Nội, Hải Phòng, Huế, Đà Nẵng, Thành phố Hồ Chí Minh, Cần Thơ.

### CASE ADM-003 — Hà Giang / Tuyên Quang
**Nội dung cũ:** “Cột cờ Lũng Cú ở tỉnh Hà Giang”.

**Kỳ vọng:** Phát hiện địa danh cấp tỉnh đã thay đổi và đề xuất: **Cột cờ Lũng Cú thuộc xã Lũng Cú, tỉnh Tuyên Quang** nếu cần thể hiện đơn vị hành chính hiện hành.

**Nguồn đối chiếu:** Nghị quyết 202/2025/QH15 và Nghị quyết 1684/NQ-UBTVQH15.

### CASE ADM-004 — Mũi Cà Mau / huyện Ngọc Hiển
**Nội dung cũ:** “thuộc ấp Đất Mũi, xã Đất Mũi, huyện Ngọc Hiển”.

**Kỳ vọng:** Phát hiện cấp huyện “Ngọc Hiển” không còn phù hợp với mô hình chính quyền địa phương 2 cấp; **xã Đất Mũi vẫn là đơn vị hành chính hiện hành của tỉnh Cà Mau**.

**Không được làm:** xóa địa danh Đất Mũi nếu không có căn cứ; chỉ cập nhật phần cấp hành chính đã thay đổi.

### CASE ADM-005 — Bản đồ năm 2021
**Nội dung cũ:** “Bản đồ hành chính Việt Nam năm 2021”.

**Kỳ vọng:** Phát hiện đây là tài liệu bản đồ lịch sử/cũ. Hệ thống phải cảnh báo **cần thay bản đồ sang phiên bản phù hợp với chương trình/năm học hiện hành** nếu dùng để dạy đơn vị hành chính hiện tại.

**Không tự động xóa:** phải tạo Change Set để người dùng duyệt.

### CASE ADM-006 — Tên địa danh biển đảo
**Nội dung:** Hoàng Sa, Trường Sa.

**Kỳ vọng:** Không tự ý thay đổi tên gọi nếu không có lỗi hành chính. Giữ nguyên và có thể kiểm tra tính nhất quán cách viết.

## 4. CASE BẢNG GV–HS

### CASE TABLE-001
Phát hiện bảng có tiêu đề “Hoạt động của giáo viên” / “Hoạt động của học sinh”.

**Kỳ vọng Format Engine:**
- Bảng nằm trong vùng in A4.
- Mặc định tỷ lệ 50%–50%.
- Tiêu đề cột căn giữa, đậm.
- Nội dung ô căn trái, căn dọc Top.
- Không tràn lề phải.
- Không làm mất các bullet trong ô.
- Không làm mất các đoạn xuống dòng trong ô.

### CASE TABLE-002 — Hàng dài qua trang
Nếu một ô chứa nhiều đoạn như phần “GV diễn giải tích hợp NLS” hoặc “GV diễn giải tích hợp tiết kiệm và bảo vệ nguồn nước”, hệ thống phải:
- giữ nguyên nội dung;
- hạn chế tách hàng gây khó đọc;
- tránh làm mất tiêu đề/câu dẫn;
- không thu nhỏ font một cách tùy tiện để ép bảng vừa trang.

### CASE TABLE-003 — Cân đối cột
Nếu cột GV/Học sinh có kích thước lệch bất hợp lý, Format Engine phải chuẩn hóa về 50/50 hoặc tỷ lệ được cấu hình thống nhất.

## 5. CASE ĐỊNH DẠNG WORD

Bắt buộc kiểm tra:
- Khổ A4.
- Times New Roman.
- Nội dung 13 pt.
- Tiêu đề chính 14 pt, đậm.
- Tiêu đề mục 13 pt, đậm.
- Lề trên 2,0 cm.
- Lề dưới 2,0 cm.
- Lề trái 2,5 cm.
- Lề phải 1,5 cm.
- Giãn dòng 1,15.
- Khoảng cách đoạn đồng nhất.
- Đầu dòng thống nhất.
- Đánh số/bullet thống nhất.
- Không tạo trang trắng bất thường.
- Không để tiêu đề cô độc ở cuối trang khi có thể tránh.

## 6. CASE CÁC BÀI LIÊN TIẾP

### CASE SEQ-001
Tài liệu chứa nhiều bài/môn nối tiếp nhau và có dòng phân cách.

**Kỳ vọng:**
- Parser phải xác định đúng ranh giới từng bài/tiết.
- Không gộp nội dung của Toán, Tiếng Việt, Lịch sử–Địa lí, Khoa học thành một bài.
- Không làm mất phần “BUỔI CHIỀU”.
- Giữ thứ tự bài xuất hiện trong tài liệu.

### CASE SEQ-002
Nếu một môn có nhiều tiết liên tiếp (ví dụ Tiếng Việt), mỗi tiết phải được nhận diện riêng nhưng vẫn giữ đúng thứ tự trong cùng tài liệu.

## 7. CASE NĂNG LỰC SỐ / CÔNG DÂN SỐ

### CASE DIGITAL-001
Đoạn tích hợp NLS 3.1.CB2a trong bài Khoa học và các nội dung sử dụng Canva/PowerPoint.

**Kỳ vọng:**
- Nhận diện là nội dung tích hợp đã có.
- Không chèn thêm một đoạn trùng lặp nếu nội dung đã đáp ứng yêu cầu.
- Có thể đề xuất kiểm tra bản quyền, nguồn hình ảnh và kiểm chứng thông tin nếu thiếu.

### CASE DIGITAL-002
Trong bài đọc Tiếng Việt, nếu có nội dung về quyền vui chơi/quyền học tập thì coi đây là tích hợp công dân/quyền trẻ em đã có; không tự chèn nội dung dư thừa.

## 8. CASE VALIDATOR

Một bản xuất từ fixture này chỉ đạt khi:
- số bài/tiết không giảm;
- số bảng không giảm;
- nội dung trong bảng không bị mất;
- các thay đổi ADM-001 đến ADM-005 chỉ được thực thi khi đã được duyệt hoặc cấu hình tự động cho phép;
- Format Engine đạt toàn bộ chuẩn định dạng;
- file mở được;
- bản gốc vẫn tồn tại độc lập;
- có Change Log.

## 9. EXPECTED CHANGE SET MẪU

| ID | Loại | Vị trí | Cũ | Mới/Đề xuất | Trạng thái mặc định |
|---|---|---|---|---|---|
| ADM-001 | Hành chính | LS-ĐL, Hoạt động 2 | 63 tỉnh, thành phố | 34 đơn vị cấp tỉnh: 28 tỉnh + 6 thành phố | CHỜ DUYỆT |
| ADM-002 | Hành chính | LS-ĐL, Hoạt động 2 | 5 thành phố | 6 thành phố hiện hành | CHỜ DUYỆT |
| ADM-003 | Hành chính | LS-ĐL, Khởi động | Hà Giang | Tuyên Quang; xã Lũng Cú nếu cần cấp xã | CHỜ DUYỆT |
| ADM-004 | Hành chính | LS-ĐL, Khởi động | huyện Ngọc Hiển | bỏ cấp huyện / cập nhật theo địa chỉ 2 cấp hiện hành | CHỜ DUYỆT |
| ADM-005 | Tài liệu | LS-ĐL, Hoạt động 1 | Bản đồ năm 2021 | Cảnh báo cần cập nhật bản đồ phù hợp | CHỜ DUYỆT |

## 10. TIÊU CHÍ THÀNH CÔNG

Fixture này dùng để xác nhận rằng hệ thống có thể:
1. Đọc đúng tài liệu nhiều môn/bài liên tiếp.
2. Bảo toàn bảng GV–HS.
3. Chuẩn hóa Word theo SPEC.md.
4. Phát hiện đúng các dữ liệu hành chính lỗi thời.
5. Không tự ý sửa nội dung không liên quan.
6. Tạo Change Set minh bạch.
7. Chỉ xuất khi Validator đạt.

## 11. NGUỒN HÀNH CHÍNH DÙNG ĐỂ TEST
- Báo điện tử Chính phủ: Chi tiết 34 đơn vị hành chính cấp tỉnh, công bố năm 2026.
- Nghị quyết 202/2025/QH15 của Quốc hội về sắp xếp đơn vị hành chính cấp tỉnh.
- Nghị quyết 1684/NQ-UBTVQH15 về sắp xếp đơn vị hành chính cấp xã của tỉnh Tuyên Quang.
- Nghị quyết 1655/NQ-UBTVQH15 về sắp xếp đơn vị hành chính cấp xã của tỉnh Cà Mau.

**Ghi chú:** Đây là bộ kiểm thử kỹ thuật; không phải bản giáo án đã sửa. Mọi đề xuất thực thi trên giáo án thật phải qua Rule Engine/Review theo SPEC.md.