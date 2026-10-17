# Profile Hermes "nmprp-mapping" (bộ tệp tri thức, BẢN NHÁP)

Trạng thái: **chưa cài lên Rocky, chưa chạy thử**. Đây là phần "State and knowledge" của dự án NMPRP ⇄ Hermes
(thiết kế: `docs/NMPRP_HERMES_MAPPING_DESIGN.md`).

| Tệp | Vai trò | Ghi chú đã đối chiếu tài liệu Hermes v0.22.2 |
|---|---|---|
| `SOUL.md` | Danh tính và nguyên tắc không vi phạm | Nằm ở thư mục profile, là phần đầu tiên của system prompt |
| `AGENTS.md` | Bối cảnh dự án | Hermes nạp từ thư mục làm việc; **chưa kiểm chứng** nó được nạp với phiên chạy qua cổng nhắn tin hay Dashboard |
| `memories/MEMORY.md`, `USER.md` | Sự thật ngắn, quy ước | Giới hạn 2.200 và 1.375 ký tự; các mục cách nhau bằng dòng `§` |
| `skills/nmprp-retrieval-assist/` | Quy trình truy hồi cho PL2 chưa có ứng viên | Định dạng `SKILL.md` có frontmatter `name`, `description` |
| `skills/nmprp-learn-from-review/` | Học từ quyết định người duyệt, chỉ đề xuất | Cổng duyệt ghi skill: tên khoá cấu hình chưa xác minh |

## Nguyên tắc
- Dữ liệu ánh xạ, quyết định và tiền lệ nằm ở CSDL NMPRP. Bộ nhớ Hermes chỉ giữ quy ước ngắn, không chứa bảng.
- Mỗi dự án một profile riêng. Tài liệu Hermes cảnh báo: không để hai tiến trình agent cùng ghi vào một thư mục Hermes.
- Không có mật khẩu, token hay mã CPT trong các tệp này (bài `tests/test_hermes_profile_files.py` canh).

## Cài đặt (CHƯA CHẠY, cần chủ dự án duyệt; chạy trên Rocky, tốt nhất do phiên Claude trên Rocky làm)
Theo tài liệu Hermes, một profile là một thư mục Hermes riêng, tạo bằng `hermes profile create <tên>`.
Các bước cụ thể (đường dẫn thư mục profile, cách sao chép tệp vào container, cách bật cron cho profile) **chưa xác minh trên máy thật**.
Phiên cài phải: (1) đọc `hermes profile --help` trên Rocky trước, (2) sao lưu theo `docs/BACKUP_RECOVERY.md`,
(3) không đụng profile mặc định đang chạy gateway và Dashboard, (4) báo lại từng bước đã kiểm chứng.

## Chưa kiểm chứng
- Cách Hermes gọi `support/nmprp_client.py` (terminal, MCP hay plugin).
- Cron của profile phụ có chạy khi gateway của profile mặc định đang chạy hay không.
- Dashboard `/agent` có chọn được profile này hay không.
