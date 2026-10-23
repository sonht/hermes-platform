# Bộ skill Hermes cho NMPRP

**Bản tài liệu: 2026.10.23.** Bộ này hoàn thiện hướng dẫn cho năm skill được yêu cầu: một skill Hermes chính thức và bốn skill NMPRP. Đây là mã nguồn/tài liệu cài đặt; không xác nhận bản trên Rocky đã được cập nhật.

## Đọc và cài

1. [Hướng dẫn cài, kiểm và quay lại](../../../docs/NMPRP_HERMES_SKILLS_INSTALL.md).
2. [Sử dụng/configure/theme/extend/orchestrate với hermes-agent](../../../docs/HERMES_AGENT_SKILL.md).
3. [Nguồn, mức tương thích và giới hạn](../../../docs/NMPRP_HERMES_SKILLS_RELEASE.md).

| Skill | Tệp chính | Sản phẩm và quyền |
|---|---|---|
| `hermes-agent` | [Bản chính thức NousResearch](https://github.com/NousResearch/hermes-agent/blob/41dfcf2c1bd7146d4ad46aea08b7dd007900602e/skills/autonomous-ai-agents/hermes-agent/SKILL.md) | Quản trị Hermes; giữ cả references/templates, không viết bản thay thế cùng tên |
| `nmprp-clinical-semantics` | [SKILL.md](skills/nmprp-clinical-semantics/SKILL.md) | Hồ sơ ngữ nghĩa, họ/kernel/modifier; đề xuất có căn cứ |
| `nmprp-retrieval-assist` | [SKILL.md](skills/nmprp-retrieval-assist/SKILL.md) | JSON M1 hoặc gợi ý qua client được cấp quyền, vẫn `CHO_XEM` |
| `nmprp-qa-governance` | [SKILL.md](skills/nmprp-qa-governance/SKILL.md) | Báo cáo độc lập, chỉ số, điều kiện dừng; không duyệt hay áp dụng |
| `nmprp-learn-from-review` | [SKILL.md](skills/nmprp-learn-from-review/SKILL.md) | Phân tích phản hồi và bản vá đề nghị; không sửa skill đang dùng |

## Thành phần cài vào profile

- `SOUL.md`: nguyên tắc chung, bao gồm chỉ đề xuất và không tự sửa tri thức.
- `AGENTS.md`: thuật ngữ, trạng thái, ranh giới và hợp đồng thực thi.
- `memories/MEMORY.md`, `memories/USER.md`: quy ước bền vững; không nhồi danh mục hay số lượng biến động.
- Bốn thư mục `skills/nmprp-*`: phải chép **cả thư mục**, gồm `references/` và `templates/` nếu có.
- `PROFILE_SHA256SUMS`: checksum nội dung profile của bản tài liệu; không phải fingerprint đã tích hợp vào API.

`hermes-agent` là dependency upstream. Không đặt bản sao rút gọn trong `skills/` của gói này vì có thể che skill chính thức đang cài. Hướng dẫn cài có bước kiểm và cách bổ sung đầy đủ nếu thiếu.

## Phối hợp

Người giao việc/máy chạy cấp PL2 và cây → clinical phân tích → retrieval đề xuất → QA kiểm → runner gửi gợi ý CHƯA DUYỆT → chuyên gia quyết định → learn-from-review lập đề xuất thay đổi → người có thẩm quyền duyệt, kiểm và phát hành.

Đây là phân vai nghiệp vụ, không tuyên bố máy chạy hiện đã tự gọi cả bốn skill thành pipeline nhiều agent. M1 hiện gọi skill retrieval qua `hermes -z -t skills`; các skill khác được nạp khi tác vụ/công cụ cho phép.

## Những điều phải giữ

- Mỗi PL2 là mã chuỗi; giữ thứ tự, tên nguồn và số 0. Nhiều ứng viên là phương án để chọn một nút.
- `CHO_XEM` là trạng thái thật; `HIGH_CONFIDENCE_PROPOSAL` không là quyền tự duyệt.
- Trong M1, mô hình không giữ credential hoặc trực tiếp gọi NMPRP. Trong shadow, không có ghi nghiệp vụ.
- Phản hồi người duyệt không tự thành gold; không có gold phù hợp thì độ chính xác là `NOT_EVALUABLE`.
- Phiên bản skill upstream, phiên bản runtime, commit bộ tài liệu và `phien_ban` gửi API là các thông tin khác nhau.
- `AGENTS.md` có thể phụ thuộc thư mục làm việc của runtime. Các bất biến quan trọng cũng nằm trong SOUL và skill; vẫn phải kiểm loader trên máy đích.

## Ghi nhận lịch sử

Repo ghi nhận profile đã được chép lên Rocky ngày 18/10/2026 bằng user `hermes`, tại `/opt/data/profiles/nmprp-mapping`. Không dùng `hermes profile install` cho bộ này vì không có `distribution.yaml`. Các ghi nhận cũ không xác nhận runtime hay nội dung profile tại ngày cài mới; xem lại tại máy đích theo runbook.
