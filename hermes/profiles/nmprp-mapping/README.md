# Profile Hermes "nmprp-mapping" (bộ tệp tri thức)

Trạng thái: **đã cài lên Rocky ngày 18/10/2026 (profile trống, gateway dừng, chưa có cron, chưa chạy thử)**. Đây là phần "State and knowledge" của dự án NMPRP ⇄ Hermes
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

## Cài đặt (ĐÃ CHẠY trên Rocky 18/10/2026; các điểm dưới đây đã kiểm chứng trên Hermes v0.22.2 dạng Docker)
- **Không dùng `hermes profile install`**: nó đòi thư mục có `distribution.yaml` ở gốc, bộ tệp này không có. Dùng `hermes profile create` rồi chép tệp vào.
- **Mọi lệnh ghi phải chạy bằng `docker exec -u hermes`** (gateway và Dashboard chạy bằng người dùng `hermes`, `/opt/data` thuộc `hermes` quyền 700). `docker exec` mặc định là root và tạo tệp root mà gateway không đọc được.
- Tên volume thật là `hermes-platform_hermes_data` (tiền tố của dự án compose), gắn vào `/opt/data`; thư mục profile là `/opt/data/profiles/nmprp-mapping`.
- **Sao lưu trước khi cài:** `bash scripts/backup/run-hermes-backup.sh` (cùng script với dịch vụ `hermes-backup`, đồng bộ NAS), rồi kiểm `sha256sum -c SHA256SUMS` trong thư mục `completed/` mới nhất. Script chụp từng SQLite trong `/opt/data` bằng sao lưu trực tuyến và nén phần còn lại vào `non_sqlite.tar`.
- Các lệnh đã chạy (từ thư mục chứa bản giải nén `hermes/profiles/nmprp-mapping`, lấy bằng `git archive origin/main` để không đổi bản sao đang chạy):
  1. `docker exec -u hermes hermes-platform-agent hermes profile create nmprp-mapping --no-skills --no-alias --description "..."`
  2. `tar -C <thư mục nguồn> --exclude=README.md -cf - . | docker exec -i -u hermes hermes-platform-agent tar -x -C /opt/data/profiles/nmprp-mapping`
  3. So mã băm từng tệp bên ngoài với bên trong container (kết quả: khớp hoàn toàn), rồi `hermes profile show` / `hermes profile list`.
- Kết quả: profile `default` vẫn `running`; `nmprp-mapping` ở `stopped`, `Skills: 5` (bốn skill của dự án và thư mục `autonomous-ai-agents` có sẵn khi tạo profile).
- Cách quay lại: `hermes profile delete nmprp-mapping` xoá đúng profile này (chạy bằng `-u hermes`).
- Profile mới có tệp `.env` riêng (nội dung chưa đọc). Hermes cảnh báo profile trống dùng khoá từ biến môi trường của container: chưa bật gateway hay cron cho profile này cho tới khi có quyết định về khoá và hạn mức chi phí.

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
