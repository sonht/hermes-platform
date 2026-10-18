# Ô chat hướng dẫn dùng phần mềm — thiết kế

Trạng thái: **thiết kế, chưa triển khai**. Phần mềm làm thử: `dm.kcb.vn` (NMPRP). Mở rộng: msa-report, icd10-training.

## Mục tiêu
Mỗi phần mềm có một ô chat nổi ở góc dưới phải, trả lời câu hỏi về **cách dùng** và **lỗi**, dựa trên mã nguồn GitHub và tài liệu đã duyệt, có dẫn nguồn.

## Quyết định đã chốt
- Bot **không giữ tài khoản truy cập phần mềm** của ai. Không hỏi, không lưu mật khẩu/OTP/token. Người dùng dán nội dung lỗi (không bí mật) nếu cần.
- Nhúng bằng **một thẻ script**: `<script src="https://hermes.kcb.vn/widget.js" data-app="dm" defer>`. Giao diện trong Shadow DOM.
- Bot chỉ tìm trong **kho tri thức đã duyệt** của đúng app đó; không đọc repo trực tiếp khi trả lời.

## Thành phần
| Đơn vị | Việc | Phụ thuộc |
|---|---|---|
| `website/widget.js` | Nút nổi, khung chat, gửi `{app, message, session}` | `/api/public/chat` |
| Platform `/api/public/chat` | Kiểm `app` + `Origin`, giới hạn tần suất, gọi Hermes | `apps.json`, kho tri thức |
| `apps.json` | Mỗi app: `origins` được phép, thư mục tri thức, tên hiển thị | — |
| Bộ quét (`support/code_explorer.py`) | Đọc repo chỉ đọc → bản ghi hành trình + nguồn + commit | token GitHub chỉ đọc |
| Kho tri thức `knowledge/<app>/` | Chỉ nội dung **đã duyệt**; mỗi mục: `intent, steps, failure_modes, source_paths, source_commit, verification_status` | — |

## Luồng
1. Widget → `POST /api/public/chat` kèm `app`.
2. Platform từ chối nếu `app` lạ hoặc `Origin` không thuộc `origins` của app.
3. Truy xuất theo ý định trong `knowledge/<app>/`, gọi Hermes với đúng các mục đó.
4. Trả lời ngắn, từng bước, kèm nguồn. Không đủ căn cứ → xin nội dung lỗi hoặc chuyển người hỗ trợ.

## Bảo mật (bắt buộc)
- Token GitHub: fine-grained, chỉ đọc `Contents`+`Metadata`, một repo; chỉ nằm trong env trên Rocky, không tới trình duyệt, không vào prompt/log.
- Lọc bí mật khi sinh tri thức (khoá, hash, token, dữ liệu cá nhân, chi tiết quản trị).
- Không công khai `/agent`; rào Tailscale giữ nguyên.
- **Giới hạn tần suất:** hiện tính theo `client_address`, mà mọi yêu cầu đi qua Caddy nên đều là `127.0.0.1` → hạn mức 5 lần/phút là **chung toàn hệ thống**. Với nhiều app và nhiều người dùng, phải đổi: hạn mức theo `app` (tổng) + theo `session` ẩn danh do widget tạo, cộng ngân sách chi phí/ngày cho mỗi app. IP thật không có (NAT `10.11.1.213`).
- Prompt-injection: nội dung người dùng và repo là dữ liệu, không phải lệnh; bot không có công cụ ghi.

## Cập nhật tri thức
Khi app phát hành: quét phần file thay đổi → tạo bản nháp → **người duyệt** → công bố. Không tự công bố theo từng lần push. Mục chưa kiểm chứng trên bản đang chạy (`/health`) gắn nhãn `chua-xac-minh` và không dùng để trả lời chắc chắn.

## Kiểm thử / nghiệm thu (slice đầu: đăng nhập dm.kcb.vn)
- ≥ 20 câu hỏi đăng nhập/đăng ký có đáp án đã duyệt; bộ chấm CLI so với nguồn.
- Mọi khẳng định thao tác có đường dẫn nguồn + commit + trạng thái kiểm chứng; không bịa tên nút.
- Test: `app` lạ → 4xx; `Origin` lạ → 4xx; vượt hạn mức → 429; không có token/PII trong index, prompt, log.
- Widget: hiển thị đúng trên dm.kcb.vn, không đè CSS trang, dùng được trên điện thoại.

## Ngoài phạm vi (YAGNI)
Đăng nhập thay người dùng, trình duyệt tự động vào phần mềm, tự học từ hội thoại, Zalo/Telegram (làm sau, thiết kế riêng).

## Việc cần anh làm
Tạo token GitHub chỉ đọc cho repo NMPRP, đặt trong env trên Rocky (không dán vào chat).

## Câu hỏi mở
Trang nào của dm.kcb.vn được phép nhúng widget (toàn bộ hay chỉ trang đăng nhập/trợ giúp) và danh sách `Origin` thật.
