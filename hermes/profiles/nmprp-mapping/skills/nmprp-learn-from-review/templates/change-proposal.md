# Đề xuất sửa nmprp-retrieval-assist

**Nhãn:** RULE_CANDIDATE — CHỜ DUYỆT. **Tự áp dụng:** không.

Mẫu này là tài liệu bàn giao, không phải payload API hoặc lệnh thực thi. Điền từ nguồn thực; thiếu thông tin ghi UNKNOWN. Không sửa tệp đang hoạt động khi điền mẫu.

## 1. Phạm vi và baseline

- Mã hồ sơ đề xuất:
- Lượt/chương/khoảng thời gian đã đọc:
- Cursor đầu/cuối; số trang; còn dữ liệu chưa đọc:
- Commit và SHA-256 của skill/reference gốc:
- Phiên bản cây, PL2, model và bộ bài học nếu nguồn có:
- Tệp/đoạn được đề nghị đổi:

## 2. Vấn đề và cơ chế gây sai

Mô tả một quy tắc tổng quát có phạm vi rõ; phân biệt sai ngữ nghĩa, sai nguồn và sai công cụ.

| PL2 nguyên văn | goi_y_id | luc | Quyết định | Nút cũ / nút sửa | Lý do có nguồn |
|---|---|---|---|---|---|

Ít nhất hai PL2 khác nhau. Không điền dữ liệu mẫu vào hàng bằng chứng.

## 3. Phản chứng và giới hạn

- Ca tương tự mà quy tắc không được áp dụng:
- Thông tin thiếu hoặc phản hồi mâu thuẫn:
- Phạm vi họ/kernel/modifier bị tác động:
- Rủi ro làm hỏng ca đang đúng:

## 4. Thay đổi văn bản đề nghị

- Đoạn hiện tại (trích đủ ngữ cảnh):
- Đoạn thay thế hoặc unified diff:
- Căn cứ vì sao thay đổi xử lý đúng nguyên nhân:
- Bất biến giữ nguyên: bảo toàn mã; chỉ đề xuất; đúng nguồn; không tự học/duyệt/ghi danh mục.

## 5. Kiểm chứng

| Bộ ca / kiểm tra | Baseline | Bản đề nghị | Đã chạy hay chỉ đề nghị | Nguồn kết quả |
|---|---|---|---|---|

- Tập rút quy tắc và tập kiểm riêng:
- Có Gold Set độc lập phù hợp hay NOT_EVALUABLE:
- Ca hồi quy cũ, phản ví dụ và lỗi nghiêm trọng:
- Reviewer độc lập / kết luận QA:
- Ngưỡng phát hành được chủ dự án chốt (nếu chưa có, ghi chưa chốt):

## 6. Quyết định và thu hồi

- Quyết định của người có thẩm quyền (để trống tới khi có thật):
- PR/commit bản được duyệt:
- Bản trước để quay lại; dấu hiệu phải thu hồi:
- Người vận hành / thời điểm cài và hash thực tế:

Phê duyệt nội dung, merge mã và cài vào runtime là các việc riêng. Không ghi đã hoàn thành việc nào khi chưa có bằng chứng tương ứng.
