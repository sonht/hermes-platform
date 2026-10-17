---
name: nmprp-retrieval-assist
description: Tìm nút cây CPT phù hợp cho một PL2 mà truy hồi tự động của NMPRP chưa có hoặc chỉ có ứng viên yếu, rồi gửi gợi ý CHƯA DUYỆT về NMPRP.
---

# NMPRP: truy hồi có tác tử cho PL2 chưa có ứng viên

## When to Use
- Được giao một danh sách mã PL2 (ví dụ 6.71, 6.107, 6.111, 6.120) chưa có ứng viên nút, hoặc chỉ có ứng viên ở tầng dự phòng.
- Không dùng để duyệt, áp dụng hay sửa ánh xạ. Skill này chỉ ĐỀ XUẤT.

## Procedure
1. Đọc đầu vào: mã PL2 là CHUỖI nguyên văn. Lấy tên PL2 từ `/review/search` (tham số `kind=pl3` nghĩa là PL2).
2. Lấy Khung cây CPT một lần cho cả phiên (`/admin/cpt-tree/khung`, chỉ tên và khoá nhánh, không mã CPT). Dùng đúng các hàm trong `support/nmprp_client.py`; không gọi đường nào ngoài danh sách cho phép.
3. Phân rã tên PL2 thành ba thành phần: hành động (cắt, nội soi, sinh thiết...), đối tượng (cơ quan, hệ cơ quan), đường tiếp cận (mổ mở, nội soi, qua da...). Thiếu đường tiếp cận thì ghi rõ là chưa xác định, không tự điền.
4. Duyệt cây theo thứ tự Chương, Hệ, Vùng, Phân vùng. Chọn tối đa 3 nút. Với mỗi nút, đọc các nút anh em để chắc không lệch cơ quan (lệch cơ quan là lỗi nặng nhất).
5. Mỗi gợi ý ghi: `pl2_code`, `branch_key` NGUYÊN VĂN, `ly_do` (một hai câu), `bang_chung` (các từ của tên PL2 khớp với các đoạn của khoá nhánh, kèm `hang`: 1, 2, 3), `do_tin_cay`, `phien_ban` = phiên bản skill này.
6. Hiệu chỉnh `do_tin_cay`: tối đa 0,5 khi chỉ khớp theo từ chung chung; cao hơn chỉ khi khớp cả cơ quan và hành động.
7. Không có nút nào đủ căn cứ thì KHÔNG gửi gợi ý cho PL2 đó. Ghi một sự kiện `LOI`/`NHIP` nêu mã PL2 và lý do, để người duyệt biết là đã thử.
8. Gửi theo lô tối đa 200 gợi ý bằng `POST /admin/hermes/goi-y`. Gửi `BAT_DAU` trước và `KET_THUC` sau qua `POST /admin/hermes/su-kien`.

## Pitfalls
- Mã PL2 `6.1` khác `6.10`; không cắt hay ép số.
- Không đoán khoá nhánh: chép từ dữ liệu Khung.
- Không đưa mã CPT vào lý do, bằng chứng hay bộ nhớ.
- Công tắc AI của NMPRP tắt thì dừng và báo lại.
- Đừng gọi đường duyệt, và đừng đổi trạng thái gợi ý.

## Verification
- Mỗi `branch_key` gửi đi phải có trong dữ liệu Khung vừa đọc.
- Số gợi ý gửi cho mỗi PL2 không quá 3; không PL2 nào trùng (pl2_code, branch_key, phien_ban).
- Đối chiếu danh sách PL2 đầu vào với danh sách đã gửi hoặc đã ghi "không đủ căn cứ": không PL2 nào bị bỏ sót im lặng.
