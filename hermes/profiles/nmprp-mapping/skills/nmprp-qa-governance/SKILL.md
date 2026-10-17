---
name: nmprp-qa-governance
description: Kiểm tra độc lập và quản trị thay đổi cho các lượt gợi ý của Hermes trên NMPRP, gồm bộ chỉ số, điều kiện dừng và quy trình đổi kỹ năng.
---

# NMPRP: kiểm tra độc lập và quản trị

## When to Use
- Khi rà một lượt chạy của Hermes, đo chất lượng, hoặc đề xuất đổi một kỹ năng.
- Chỉ báo cáo. Không tự phê duyệt và không tự áp dụng thay đổi.

## Procedure
1. Kiểm toàn bộ PL2 nguồn của lượt: mã là chuỗi, định danh ổn định, không nút ngoài cây, không gộp sai kernel, không trùng theo chuyên khoa hay giá, không mất lịch sử tách và gộp.
2. Số đo dùng bộ đo của NMPRP (`cpn_gold_do.py`), không viết bộ đo riêng: precision@1, recall@3, lỗi sai cơ quan nghiêm trọng, tỷ lệ INVALID, tỷ lệ ABSTAIN hợp lý, chi phí mỗi cặp, thời gian mỗi chương, hồi quy.
3. Chưa có nhãn vàng thì độ chính xác là NOT_EVALUABLE; chỉ báo độ nhất quán, chi phí và vi phạm ranh giới. Khi có nhãn vàng, ngưỡng của NMPRP áp dụng (ví dụ ΔF1 LOCKED tối thiểu +0,02, lỗi nghiêm trọng không tăng).
4. Một kỹ năng chỉ đổi qua bản vá văn bản có: phiên bản, nguồn, bộ kiểm trước và sau, đánh giá ngoại lệ, PR và chủ dự án duyệt. Hai ca tương tự chỉ tạo giả thuyết (nhãn HA `RULE_CANDIDATE`), không thành quy tắc tự động.
5. DỪNG và báo chủ dự án khi: nghi rò rỉ bí mật, vượt quyền, công tắc AI tắt hoặc lỗi, dữ liệu sai lược đồ, chi phí vượt hạn mức đã duyệt, ghi trái phép vào bảng nguồn.
6. Lỗi tạm (mạng, 429, 5xx) thử lại tối đa ba lần. Lỗi quyền hoặc lỗi hợp đồng thì không thử lại. Cấu hình thử lại của cron Hermes chưa xác minh.

## Pitfalls
- Nhiều vai trong cùng một mô hình không tương đương nhiều người kiểm chứng.
- Điểm truy hồi không phải độ chính xác; không suy ra cải thiện khi chưa có nhãn vàng.
- Không tự tạo nhãn vàng từ ca do agent đề xuất.

## Verification
- Báo cáo nêu rõ số đo nào tính được, số đo nào NOT_EVALUABLE, và vì sao.
- Mọi đề xuất đổi kỹ năng có đủ các mục ở bước 4.
