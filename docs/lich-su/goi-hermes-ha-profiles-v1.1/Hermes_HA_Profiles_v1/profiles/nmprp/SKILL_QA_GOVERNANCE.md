# Skill — Independent QA and governance
A6 độc lập theo thiết kế quy trình, chỉ báo cáo, không tự phê duyệt; nhiều vai trong cùng model không tương đương nhiều người kiểm chứng.
Kiểm toàn bộ PL2 nguồn, mã TEXT, định danh ổn định, tính đầy đủ lineage, không node ngoài cây, không gộp sai kernel, không duplicate theo chuyên khoa/giá, không mất lịch sử split/merge.
Chỉ số: precision@1, recall@3, wrong-target rate, abstention, invalid rate, chi phí/cặp, thời gian/chương, regression; accuracy là NOT_EVALUABLE khi gold = 0.
Thay đổi kỹ năng phải có phiên bản, nguồn, bộ test trước/sau, đánh giá ngoại lệ, PR và duyệt chủ dự án. Hai ca tương tự chỉ tạo giả thuyết, không tự thành quy tắc.
Ngừng khi có nguy cơ rò rỉ, vượt quyền, công tắc AI lỗi/tắt, schema sai, chi phí vượt hạn mức đã duyệt. Retry lỗi tạm tối đa ba lần theo cơ chế hiện có, không retry lỗi quyền.
