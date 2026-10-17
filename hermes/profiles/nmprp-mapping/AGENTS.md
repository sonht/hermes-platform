# NMPRP ⇄ Hermes: bối cảnh dự án

NMPRP (dm.kcb.vn) chuẩn hoá danh mục kỹ thuật khám chữa bệnh của Bộ Y tế. Hermes hỗ trợ ánh xạ kỹ thuật vào cây CPT. NMPRP là nơi lưu dữ liệu và hiển thị; Hermes chỉ đọc qua API và gửi gợi ý CHƯA DUYỆT.

## Thuật ngữ
- **PL2**: danh mục kỹ thuật đang dự thảo (trước đây gọi PL3; API cũ còn tham số `kind=pl3`).
- **PL1**: danh mục phẫu thuật, thủ thuật (PT/TT).
- **Nút cây CPT**: nút cuối của Khung cây CPT (Chương, Hệ, Vùng, Phân vùng). Khung không chứa mã CPT.
- **Khoá nhánh**: chuỗi dạng `Surgery > Nervous System > Skull, Meninges, and Brain > Neuroendoscopy`. Nối PL2 với nút bằng khoá nhánh, không bằng mã nút.

## Mô hình nút (chủ dự án chốt 02/10/2026)
1. Vị trí của một PL2 là một nút của cây CPT. Mỗi PL2 đúng một nút. Sang nút khác phải là mục khác có modifier khác.
2. Liên kết PL2 với mã CPT là tuỳ chọn; mã CPT chỉ để tham khảo.
3. Mã CPT lệch nút thì cảnh báo, không chặn.

## Ranh giới
- Chỉ ĐỀ XUẤT. Chỉ ghi qua `POST /admin/hermes/goi-y` (bảng riêng, trạng thái `CHO_XEM`). Không gọi đường duyệt hay áp dụng.
- Chỉ đọc qua các đường trong danh sách cho phép của `support/nmprp_client.py`. Không gọi `/admin/cpt-tree/khung/ma-cpt` và không dùng `kind=cpt`.
- Tài khoản dịch vụ chỉ có tác vụ `studio_cpt`, không phải admin.

## Dạng một gợi ý
`pl2_code` (chuỗi), `branch_key` (nguyên văn), `ly_do`, `bang_chung` (danh sách hoặc đối tượng; ghi cả `hang`: 1, 2, 3 khi có nhiều phương án), `do_tin_cay` (0 đến 1), `phien_ban` (phiên bản skill đã dùng), `run_id` (tuỳ chọn).

## Việc thí điểm hiện tại
Chương 6 Nội tiết. Bốn PL2 chưa có ứng viên nào: 6.71, 6.107, 6.111, 6.120. Chưa có nhãn vàng, nên chỉ so được độ nhất quán và chi phí, chưa kết luận độ chính xác.
