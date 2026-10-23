# Chẩn đoán trước sửa — 24/10/2026

Gốc NMPRP: `5c1f75598269953d4f51ef661f4ad257cfd0e631`; Hermes: `d5b625aedc2c27309f31ed89e78178993dc40acc`. Cả hai ban đầu sạch, nhánh `work`; làm trên `viec/hermes-worker-capabilities` trong checkout hiện hữu.

1. `support/nmprp_client.py:233` (`may_chao`) không gửi `kha_nang`. `api/hermes_admin.py:438` mặc định danh sách rỗng; `registry/hermes_luot.py:580` lưu danh sách rỗng. Đây là mismatch có bằng chứng mã nguồn, không phải lỗi từ vựng: backend chấp nhận đủ bốn mã.
2. `support/nmprp_may_chay.py:_chay_luot` chỉ gọi prompt/validator M1 rồi ghi `goi-y`/`ket-qua`; không dispatcher M0/M2/M3/GĐ2. Client allowlist cũng không có route `m0-phan-ra`, `m2-ho`, `m3-goc`, `mo-ta-nut`. Thiếu cả thực thi và vận chuyển; cài skill không tự giải quyết.
3. `frontend/src/HermesChayLien.jsx:nangLucThieu` và `registry/hermes_chay_lien.py:_kiem_tham_so` kiểm suffix M0→M3. Ảnh đúng là biểu mẫu **Chạy liền**. Kiểm cả chuỗi đúng với ý nghĩa này; cần bổ sung lựa chọn M0 độc lập rõ ràng, không đổi ngầm nút Bắt đầu.
4. `hermes_luot._ly_do_khong_giao_v2` đã recheck từng máy và TTL 180s khi claim/resume. Tuy nhiên readiness lúc tạo M0/M2/M3 và UI dựa vào lời chào mới nhất của bất kỳ máy nào; không chứng minh máy phù hợp đang online.
5. M1 độc lập vẫn tạo qua `/luot` v1, không đọc M0. Cổng trên canvas M0→M1 không phải điều kiện của API M1 độc lập.

Baseline local Hermes: 216 tests, OK. Kiểm Git HTTPS cả hai repository thành công. Docker local chưa có container production. Biến `NMPRP_*`/`HERMES_*` không được cấp trong instance; không có cấu hình SSH/VPN Rocky được cấp qua chat. Runtime Rocky, digest ảnh, nội dung profile cài thật, heartbeat DB production, model provider và số PL2 live: **BLOCKED: không có quyền truy cập được cung cấp**. Không suy ra nguyên nhân deploy/runtime cụ thể từ source hoặc ảnh. Không truy cập DB production.

Ảnh bằng chứng giữ nguyên trong gói bàn giao. QG-16 trong ảnh là ĐÃ ĐẠT; không đổi công tắc, không suy nguyên nhân từ nó. Thiết kế cũ ghi phải tắt không ghi đè yêu cầu hiện tại.
