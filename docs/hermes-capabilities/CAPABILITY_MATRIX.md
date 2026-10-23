# Ma trận trước sửa

| Năng lực | NMPRP yêu cầu | Backend nhận | Worker khai | Handler | Skill/tool | Hành động |
|---|---|---|---|---|---|---|
| PHAN_RA | M0 hoặc chuỗi có M0 | Có, `KHA_NANG_HOP_LE` | Không | Không | clinical skill có, adapter M0 chưa có | thêm adapter thực, cổng sẵn sàng |
| DE_XUAT_HO | M2 hoặc chuỗi có M2 | Có | Không | Không | clinical skill có, transport M2 thiếu | một node/input pin/QA |
| DE_XUAT_GOC | M3 hoặc chuỗi có M3 | Có | Không | Không | clinical skill có, transport M3 thiếu | một họ/typed modifiers/QA |
| THAM_DINH_GD2 | M1 v2 | Có | Không | Không | route đọc mô tả có bên NMPRP, client chưa có | adapter GĐ2 riêng, giữ M1 v1 |

Mỗi dòng: runtime Rocky **BLOCKED: chưa được cấp quyền**. Hướng dẫn/skill không được coi là handler hoặc bằng chứng model chạy. M1 v1 hiện có runner; baseline model/token/latency production chưa đo được.

## Sau sửa — trạng thái được chứng minh

| Capability | Dispatcher và skill thực | Vận chuyển/QA/lưu | Bằng chứng local | Runtime/model Rocky |
|---|---|---|---|---|
| PHAN_RA | `nmprp_stages.execute`, `nmprp-stage-m0` | `m0-1` → `m0-phan-ra`; coverage/quotes; bảng M0 hiện có | unit + HTTP integration; M0 tách khỏi M1 | BLOCKED |
| DE_XUAT_HO | một `m23.nut`/lần, `nmprp-stage-m2` | M1 snapshot + M0 đã chọn/S1 trong payload + HPKB ACTIVE; coverage đủ hoặc chưa vào họ có lý do → `m2-ho` | 2 node → 2 họ fixture; không ghi M1 | BLOCKED |
| DE_XUAT_GOC | một `m23.ho`/lần, `nmprp-stage-m3` | họ đã duyệt + dictionary đã duyệt; typed modifier có trích nguồn; `m3-goc`; reconstruction không giả PASS | 2 gốc + 1 replay giữ nguyên bản cũ; typed modifier lưu thật qua API | BLOCKED; semantic PASS chưa mở |
| THAM_DINH_GD2 | `nmprp_gd2.execute`, `nmprp-stage-gd2` | GĐ1 dùng nguyên prompt/validator cũ; đọc mô tả đúng job → GĐ2 → hồ sơ/đối chiếu server → gợi ý | 1 hồ sơ, 1 đối chiếu fixture; giả mất mạng sau hồ sơ, restart không trả tiền lại | BLOCKED; abstention không có ứng viên dừng rõ |

Khả năng khai báo được tính từ dispatcher đã cài + stage được người vận hành opt-in + runtime/skill discovery chạy được + hash SOUL/skill khớp. Mặc định `HERMES_RUNNER_STAGES` rỗng. Hello không có năng lực mới khi stage chưa bật hoặc probe lỗi. Đây vẫn là readiness khai báo có kiểm tra điều kiện cục bộ; không thay canary provider/chuyên môn. Profile M1 `nmprp-mapping`, `nmprp_shadow.py`, `_chay_luot` không bị thay.
