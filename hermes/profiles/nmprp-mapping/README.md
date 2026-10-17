# Profile Hermes "nmprp-mapping" (bộ tệp tri thức)

Trạng thái: **chưa cài lên Rocky, chưa chạy thử**. Đây là phần "State and knowledge" của dự án NMPRP ⇄ Hermes
(thiết kế: `docs/NMPRP_HERMES_MAPPING_DESIGN.md`; brain dump: `docs/NMPRP_HERMES_BRAIN_DUMP.md`).

| Tệp | Vai trò | Ghi chú đã đối chiếu tài liệu Hermes v0.22.2 |
|---|---|---|
| `SOUL.md` | Danh tính và nguyên tắc không vi phạm | Nằm ở thư mục profile, là phần đầu tiên của system prompt |
| `AGENTS.md` | Bối cảnh dự án | Hermes nạp từ thư mục làm việc; **chưa kiểm chứng** nó được nạp với phiên chạy qua cổng nhắn tin hay Dashboard |
| `memories/MEMORY.md`, `USER.md` | Sự thật ngắn, quy ước | Giới hạn 2.200 và 1.375 ký tự; các mục cách nhau bằng dòng `§` |
| `skills/nmprp-retrieval-assist/` | Quy trình truy hồi cho PL2 chưa có ứng viên | Định dạng `SKILL.md` có frontmatter `name`, `description` |
| `skills/nmprp-clinical-semantics/` | Phân tích ngữ nghĩa, họ, kernel, modifier | Hợp nhất từ gói «Hermes HA Profiles» |
| `skills/nmprp-qa-governance/` | Kiểm tra độc lập, số đo, điều kiện dừng | Dùng bộ đo `cpn_gold_do.py` của NMPRP |
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

## Điều đã đối chiếu tài liệu Hermes v0.22.2 về vận hành
- **Cron mặc định chạy tách khỏi mọi thư mục dự án: KHÔNG nạp `AGENTS.md`** (chỉ nạp khi job có `--workdir`). Vì vậy job thí điểm phải
  (a) gắn skill `nmprp-retrieval-assist` vào job, (b) đặt `--workdir` trỏ tới thư mục có `AGENTS.md`, hoặc dựa vào `SOUL.md` cho các luật cứng.
- **Cron do cổng (gateway) của profile gõ nhịp.** Profile phụ muốn chạy lịch thì phải có gateway riêng (`<profile> gateway install` tạo dịch vụ
  `hermes-gateway-<profile>` trên máy dùng systemd/launchd). Trên Rocky Hermes chạy trong Docker: cách chạy gateway của profile phụ **chưa xác minh**.
- **Điều khiển có sẵn:** `hermes pause` / `hermes resume` (dừng khẩn cấp mọi cron), tạm dừng, sửa, chạy ngay, xoá từng job. Thêm: vô hiệu hoá tài khoản dịch vụ trên NMPRP; thu hồi khoá Claude API của Hermes.
- **Công tắc AI của NMPRP không dừng được Hermes** (Hermes gọi Claude API bằng khoá riêng): skill có bước 0 đọc công tắc qua client (tự giác).

## Chưa kiểm chứng
- Cách Hermes gọi `support/nmprp_client.py` (terminal, MCP hay plugin).
- Cron của profile phụ có chạy khi gateway của profile mặc định đang chạy hay không.
- Dashboard `/agent` có chọn được profile này hay không.
