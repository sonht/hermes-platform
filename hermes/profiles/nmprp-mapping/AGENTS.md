# NMPRP ⇄ Hermes: bối cảnh dự án

NMPRP (dm.kcb.vn) chuẩn hoá danh mục kỹ thuật khám chữa bệnh của Bộ Y tế. Hermes hỗ trợ ánh xạ kỹ thuật vào cây CPT. NMPRP là nơi lưu dữ liệu và hiển thị; Hermes chỉ đọc qua API và gửi gợi ý CHƯA DUYỆT.

## Thuật ngữ
- **PL2**: danh mục kỹ thuật dự thảo, đối tượng xử lý. Tham số kỹ thuật `kind=pl3` của API NMPRP và tiền tố `PL3-PROC-` trong dữ liệu cũ đều chỉ PL2.
- **PL1**: Phụ lục 1, danh mục kỹ thuật HIỆN HÀNH (mã theo TT23, giữ tiền tố `BS_`), hết hiệu lực 01/01/2028 khi PL2 có hiệu lực và thay thế PL1. PL1 không phải danh mục giá: danh mục giá hiện nay được cấp mã dựa trên PL1 (sau đó có tách gây mê, gây tê) nên dễ nhầm. Không phải đích ánh xạ.
- **Nút cây CPT**: nút cuối của Khung cây CPT (Chương, Hệ, Vùng, Phân vùng). Khung không chứa mã CPT.
- **Khoá nhánh**: chuỗi dạng `Surgery > Nervous System > Skull, Meninges, and Brain > Neuroendoscopy`. Nối PL2 với nút bằng khoá nhánh, không bằng mã nút (số thứ tự nút có thể đổi).
- **Họ, kernel, modifier**: họ là tập kỹ thuật chung nguyên lý; kernel là hạt nhân (hành động chính, đối tượng đích, đặc điểm định danh); modifier là thuộc tính biến thể, không tự tạo kernel mới.

## Mô hình nút (chủ dự án chốt 02/10/2026)
1. Vị trí của một PL2 là một nút của cây CPT. Mỗi PL2 đúng một nút. Sang nút khác phải là mục khác có modifier khác.
2. Liên kết PL2 với mã CPT là tuỳ chọn; mã CPT chỉ để tham khảo.
3. Mã CPT lệch nút thì cảnh báo, không chặn.

## Ranh giới
- Chỉ ĐỀ XUẤT. Chỉ ghi qua `POST /admin/hermes/goi-y` (bảng riêng, trạng thái `CHO_XEM`). Không gọi đường duyệt hay áp dụng.
- Chỉ đọc qua các đường trong danh sách cho phép của `support/nmprp_client.py`. Không gọi `/admin/cpt-tree/khung/ma-cpt` và không dùng `kind=cpt`.
- Tài khoản dịch vụ chỉ có tác vụ `studio_cpt`, không phải admin.
- Fail closed: công tắc AI tắt hoặc không đọc được thì dừng; thiếu bằng chứng thì không đề xuất.
- Không `SELECT *` từ bảng có cột khoá (vd `app_ai_state`); không ghi khoá, prompt chứa bí mật hay dữ liệu bệnh nhân vào nhật ký.
- Prompt và kỹ năng đổi theo phiên bản; đổi mặc định phải có benchmark trên nhãn vàng và chủ dự án chốt. Chủ dự án giữ quyền deploy, cấp `studio_cpt`, duyệt nhãn vàng, bật công tắc và quản lý khoá.

## Hai lớp trạng thái (chủ dự án chốt 17/10/2026: nhãn ngoài NMPRP đổi theo HA nếu hợp lý)
**Lớp NMPRP** (Hermes không ghi vào các trường này): A2 `decision` ∈ {MATCH, REJECT, ABSTAIN, EXPERT_REVIEW}; A3 ∈ {KEEP_CURRENT, PROPOSE_PRIMARY, UNPLACED, EXPERT_REVIEW}; `review_status` mặc định `PENDING`; gợi ý của Hermes ghi `trang_thai` = `CHO_XEM`.

**Lớp HA** (nhãn của Hermes; ghi trong `bang_chung.muc_de_xuat` của gợi ý hoặc trong `chi_tiet` của sự kiện; KHÔNG ghi vào trường trạng thái của NMPRP):
- `HIGH_CONFIDENCE_PROPOSAL`: khớp cả cơ quan, hành động và đường tiếp cận. Chỉ là mức ưu tiên xem xét, không phải xác suất đúng; chưa hiệu chuẩn nên không được coi là điều kiện tự duyệt.
- `REVIEW_RECOMMENDED`: có đề xuất nhưng còn điểm cần người duyệt xem kỹ.
- `EXPERT_REQUIRED`: cần chuyên gia quyết (thiếu thông tin trọng yếu, hai nút đều hợp lý). Tương ứng `EXPERT_REVIEW` của NMPRP.
- `UNRESOLVED`: chưa quyết được; ghi điều còn thiếu.
- `NO_SAFE_MATCH`: không có nút đủ căn cứ. Không gửi gợi ý; ghi một sự kiện nêu mã PL2 và lý do.
- `PENDING_EXPERT_REVIEW`: đã chuyển chuyên gia, đang chờ. Tương ứng `PENDING` của NMPRP.
- `DISPUTED`: người duyệt bất đồng; giữ nguyên cho đến khi người có thẩm quyền quyết.
- `RULE_CANDIDATE`: bài học có từ 2 ca có nguồn; chưa phải quy tắc, chỉ là giả thuyết.
Nhãn HA không thay đổi hợp đồng NMPRP và không làm thay đổi `CHO_XEM`.

## Dạng một gợi ý
`pl2_code` (chuỗi), `branch_key` (nguyên văn), `ly_do`, `bang_chung` (đối tượng; ghi `muc_de_xuat` (nhãn HA), `hang`: 1, 2, 3 khi có nhiều phương án, và các đoạn trích nguyên văn), `do_tin_cay` (0 đến 1, chưa hiệu chuẩn, không phải xác suất đúng), `phien_ban` (phiên bản skill đã dùng), `run_id` (tuỳ chọn).

## Luồng NMPRP hiện có (Hermes không thay thế)
Truy hồi tất định, A1, A2, A3, A4, A5, A6, chuyên gia duyệt. Mọi lời gọi mô hình của NMPRP đi qua `matching/ai_client.call_text`. Hermes là bên ngoài: điều phối qua API, không thay worker.

## Việc thí điểm hiện tại
Kế hoạch: phương án B (Hermes điều phối ngoài, chỉ gửi gợi ý), sau đó C thí điểm (truy hồi có tác tử, chế độ shadow, một chương). Chương 6 Nội tiết: bốn PL2 chưa có ứng viên: 6.71, 6.107, 6.111, 6.120. Chưa có nhãn vàng nên độ chính xác là NOT_EVALUABLE; chỉ so được độ nhất quán và chi phí.
