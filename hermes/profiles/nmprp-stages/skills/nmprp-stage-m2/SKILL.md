---
name: nmprp-stage-m2
description: Thực thi M2 NMPRP theo snapshot đã ghim, chỉ đề xuất.
---

# Hợp đồng worker v1

Đầu vào đúng một khoa_nhanh + pl2 + snapshot_id và có thể phan_ra đã ghim. Không truy upstream. Trả {"items":[{"khoa_nhanh":"nguyên văn","pl2_codes":["mã"],"ten":"tên họ","dinh_nghia":"hạt nhân","ranh_gioi_noi_bo":"bao gồm/loại trừ nội bộ, không phải CPT","ly_do":"căn cứ","ly_do_thanh_vien":{"mã":"lý do"},"thu_tu":"000010","co":[]}]}.
Mọi mã trong node đúng một lần trong họ hoặc mục riêng {khoa_nhanh,chua_vao_ho:[{pl2_code,trang_thai:CHUA_VAO_HO|CAN_XEM,ly_do}]}. Không tạo pl2_codes rỗng. Họ một thành viên hợp lệ. Cờ chỉ M1_REVIEW_FLAG,M0_REVIEW_FLAG,GIONG_NUT_KHAC,KHOANG_HO,CHUA_CO_HO_SO. Không sửa M1; không coi PROVISIONAL là chuyên gia duyệt. Không đủ thông tin: CAN_XEM kèm lý do thay vì gộp theo tên.

## Quy tắc tham chiếu nguyên văn

Bản khởi đầu từ thiết kế 20/10/2026; không phải nhãn vàng hay tri thức đã duyệt.

### 6c. Hướng dẫn sắp xếp PL2 theo cây CPT (M2)

| Số | Quy tắc |
|---|---|
| M2-01 | Đơn vị = MỘT nút tận trong Bản chốt M1 đang dùng. Họ không vượt ra ngoài nút. |
| M2-02 | Mọi PL2 của nút phải có mặt đúng MỘT lần: trong một họ, hoặc `CHUA_VAO_HO`/`CAN_XEM` kèm lý do. Đếm vào = đếm ra. |
| M2-03 | Cùng họ ⇔ cùng hành động chính + cùng đích + cùng mục đích + cùng phương pháp mang tính bản chất (theo M0). Tên giống chưa đủ; tên khác không bắt buộc khác họ. |
| M2-04 | Khác biệt chỉ ở thuộc tính (diện tích, bên, số lượng, bối cảnh, vị trí trong cùng hệ) ⇒ CÙNG họ, thành biến thể ở M3. |
| M2-05 | Khác biệt đổi bản chất (tạm thời ↔ vĩnh viễn, lấy mẫu ↔ điều trị, nong ↔ đặt stent đơn thuần) ⇒ KHÁC họ. |
| M2-06 | **Họ một thành viên là hợp lệ**. Không ép PL2 lẻ vào họ khác cho «gọn». |
| M2-07 | Không mặc định một nút = một họ. |
| M2-08 | Cùng hạt nhân mà ở nút khác ⇒ chỉ cờ `GIONG_NUT_KHAC` + `M1_REVIEW_FLAG`; không chuyển PL2 sang nút khác. |
| M2-09 | Mỗi họ có: tên Việt, định nghĩa hạt nhân, ranh giới «Bao gồm/Loại trừ NỘI BỘ HỌ» (ghi rõ là của M2, KHÔNG phải nguyên văn CPT), lý do từng thành viên, phản ví dụ khi có tranh chấp. |
| M2-10 | **Thứ tự trong nút** (BUILD): (1) họ xếp theo độ phức tạp tăng dần của hành động chính, cùng mức thì theo mã PL2 nhỏ nhất; (2) thành viên trong họ xếp theo trục biến thể chính tăng dần (diện tích, số lượng, phần cơ quan, bên), cùng mức thì theo mã PL2 so từng đoạn như số nhưng LƯU là chuỗi (`6.9` trước `6.10`). Lưu `thu_tu` dạng chuỗi đệm 0 bước 10 (khuôn `studio_thu_tu`: `BUOC = 10`, `RONG = 6`) trong sản phẩm M2 — **không ghi sang `studio_thu_tu`**. |
| M2-11 | Nút quá lớn cho một lời gọi ⇒ chia theo hạt nhân rồi đối soát, không mất PL2 (ĐK §5). |
| M2-12 | Thành viên `PROVISIONAL` (chưa duyệt ở M1) được vào họ nhưng họ ấy không đẩy sang tri thức được (`day_hpkb_duoc = False`, Q1). |

**Ca thử (cùng nút giả định):**

| Ca | ĐÚNG | SAI |
|---|---|---|
| 6.64, 6.65, 6.66, 6.67 | Một họ «Cắt lọc vết loét, hoại tử chi dưới do đái tháo đường», thứ tự 6.64 → 6.65 → 6.66 → 6.67 theo diện tích | Bốn họ riêng; hoặc gộp bốn mã thành một mã |
| 6.74, 6.75, 6.76, 6.77 | Ba họ: chọc hút dịch điều trị (6.74) · lấy tế bào (6.75, 6.76 — đích khác ⇒ chuyên gia quyết cùng hay khác họ) · tiêm cồn (6.77) | Một họ «thủ thuật tuyến giáp có siêu âm» |
| 2.254, 2.337, 2.338 | Một họ IVUS (nếu cùng nút); vị trí là modifier | Ba họ theo vị trí |
| 1.3 và 1.258 | Cùng hạt nhân «dẫn lưu não thất ra ngoài» (tên CSV của 1.258 là «Dẫn lưu não thất ra ngoài», KHÔNG phải shunt) ⇒ ứng viên cùng họ, chuyên gia xác nhận | Đưa 1.246 (dẫn lưu não thất **ổ bụng** = shunt trong) vào cùng họ |
| 2.277 và 2.303 | Khác họ (tạm thời ↔ vĩnh viễn) | Cùng họ, «tạm thời» là modifier |

**Ghi chú về ca 1.3/1.258 của tài liệu đính kèm:** ĐK §13 viết «dẫn lưu não thất ngoài vs shunt». Tra CSV: 1.258 là «Dẫn lưu não thất
ra ngoài» — cùng nghĩa với 1.3, không phải shunt. Ca so với shunt đúng nghĩa là 1.246 «Phẫu thuật dẫn lưu não thất ổ bụng trong dãn
não thất» (đã tra CSV). Bộ ca kiểm (mục 9.3) đã sửa theo dữ liệu.

