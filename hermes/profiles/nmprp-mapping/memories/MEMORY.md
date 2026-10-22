Vị trí của một PL2 là MỘT nút cây CPT; mỗi PL2 đúng một nút. Mã CPT chỉ để tham khảo.
§
Nối PL2 với nút bằng khoá nhánh nguyên văn, không bằng mã nút. Mã luôn là chuỗi (giữ số 0, BS_).
§
PL2 = danh mục kỹ thuật dự thảo. PL1 = Phụ lục 1, danh mục kỹ thuật hiện hành (TT23), hết hiệu lực 01/01/2028 khi PL2 thay thế; KHÔNG phải danh mục giá. Tham số kind=pl3 của API nghĩa là PL2.
§
Chỉ đề xuất, trạng thái CHO_XEM. Hàng đợi do runner ghi qua /may/luot/{id}/goi-y và /ket-qua; luồng legacy được cấp quyền qua POST /admin/hermes/goi-y. Không gọi đường duyệt. Nhãn HA chỉ ghi trong bang_chung, không thay trạng thái NMPRP.
§
Không đưa mã CPT vào bộ nhớ hay nhật ký (bản quyền) trừ khi chủ dự án bật công tắc.
§
Phạm vi, số lượng PL2/nút, phiên bản và tình trạng nhãn vàng lấy từ lượt/nguồn hiện tại. Không giữ số liệu thay đổi theo ngày trong bộ nhớ. Không có Gold Set phù hợp thì độ chính xác NOT_EVALUABLE.
§
Phản hồi là EXPERT_FEEDBACK. Hai PL2 khác nhau có nguồn và cùng nguyên nhân mới đủ đề xuất RULE_CANDIDATE; vẫn cần phản chứng và người duyệt. Không tự sửa skill/bộ nhớ hoặc tự tạo nhãn vàng. Điểm truy hồi không phải độ chính xác.
