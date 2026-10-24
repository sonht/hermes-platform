# Chẩn đoán trước sửa — 24/10/2026

Gốc NMPRP: `5c1f75598269953d4f51ef661f4ad257cfd0e631`; Hermes: `d5b625aedc2c27309f31ed89e78178993dc40acc`. Cả hai ban đầu sạch, nhánh `work`; làm trên `viec/hermes-worker-capabilities` trong checkout hiện hữu.

1. `support/nmprp_client.py:233` (`may_chao`) không gửi `kha_nang`. `api/hermes_admin.py:438` mặc định danh sách rỗng; `registry/hermes_luot.py:580` lưu danh sách rỗng. Đây là mismatch có bằng chứng mã nguồn, không phải lỗi từ vựng: backend chấp nhận đủ bốn mã.
2. `support/nmprp_may_chay.py:_chay_luot` chỉ gọi prompt/validator M1 rồi ghi `goi-y`/`ket-qua`; không dispatcher M0/M2/M3/GĐ2. Client allowlist cũng không có route `m0-phan-ra`, `m2-ho`, `m3-goc`, `mo-ta-nut`. Thiếu cả thực thi và vận chuyển; cài skill không tự giải quyết.
3. `frontend/src/HermesChayLien.jsx:nangLucThieu` và `registry/hermes_chay_lien.py:_kiem_tham_so` kiểm suffix M0→M3. Ảnh đúng là biểu mẫu **Chạy liền**. Kiểm cả chuỗi đúng với ý nghĩa này; cần bổ sung lựa chọn M0 độc lập rõ ràng, không đổi ngầm nút Bắt đầu.
4. `hermes_luot._ly_do_khong_giao_v2` đã recheck từng máy và TTL 180s khi claim/resume. Tuy nhiên readiness lúc tạo M0/M2/M3 và UI dựa vào lời chào mới nhất của bất kỳ máy nào; không chứng minh máy phù hợp đang online.
5. M1 độc lập vẫn tạo qua `/luot` v1, không đọc M0. Cổng trên canvas M0→M1 không phải điều kiện của API M1 độc lập.

Baseline local Hermes: 216 tests, OK. Kiểm Git HTTPS cả hai repository thành công. Docker local chưa có container production. Biến `NMPRP_*`/`HERMES_*` không được cấp trong instance; không có cấu hình SSH/VPN Rocky được cấp qua chat. Runtime Rocky, digest ảnh, nội dung profile cài thật, heartbeat DB production, model provider và số PL2 live: **BLOCKED: không có quyền truy cập được cung cấp**. Không suy ra nguyên nhân deploy/runtime cụ thể từ source hoặc ảnh. Không truy cập DB production.

Ảnh bằng chứng giữ nguyên trong gói bàn giao. QG-16 trong ảnh là ĐÃ ĐẠT; không đổi công tắc, không suy nguyên nhân từ nó. Thiết kế cũ ghi phải tắt không ghi đè yêu cầu hiện tại.

## Bằng chứng sau sửa để đối chiếu

- `support/nmprp_client.py:236`: hello thêm trường tùy chọn `kha_nang`, giữ thân cũ khi không dùng stage.
- `support/nmprp_may_chay.py:382`: lời chào foreground/heartbeat dùng chung `chao`, capability lấy từ probe, không lấy từ một danh sách tên tự do.
- `support/nmprp_stages.py:37`, `:88`, `:266`: probe → validators → dispatcher/real result routes; `support/nmprp_gd2.py:36` tách khỏi M1 v1.
- NMPRP `registry/hermes_nang_luc.py:14`, `:36`: từng worker/TTL/model; `api/hermes_admin.py:479`, `:625`: route đọc có quyền riêng. Claim/resume vẫn kiểm worker theo engine hiện có.
- Các khẳng định AS-IS trong thiết kế ngày 20/10 được đối chiếu lại: ở HEAD nhận ngày 23/10, server đã có M0/S1 backfill/M2 node replay/typed fields/composite/manifest; thiếu chính ở worker và integration. Không xây lại những phần server đã có.
- Ảnh lỗi ở biểu mẫu Chạy liền đúng suffix capability; lỗi không phải do QG-16. Lựa chọn M0 độc lập được thêm rõ ràng và có bài bấm nút→POST; không tự đổi nghĩa Chạy liền.

Kết luận giới hạn: nguyên nhân thiếu hợp đồng và thực thi ở **mã nguồn worker** đã xác thực và có bản sửa local. Có đang chạy đúng bản cũ trên Rocky hay còn lỗi deployment/provider/heartbeat khác phải đo tại máy đích; hiện BLOCKED, không suy diễn đã được khắc phục production.
