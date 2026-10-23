# Ma trận trước sửa

| Năng lực | NMPRP yêu cầu | Backend nhận | Worker khai | Handler | Skill/tool | Hành động |
|---|---|---|---|---|---|---|
| PHAN_RA | M0 hoặc chuỗi có M0 | Có, `KHA_NANG_HOP_LE` | Không | Không | clinical skill có, adapter M0 chưa có | thêm adapter thực, cổng sẵn sàng |
| DE_XUAT_HO | M2 hoặc chuỗi có M2 | Có | Không | Không | clinical skill có, transport M2 thiếu | một node/input pin/QA |
| DE_XUAT_GOC | M3 hoặc chuỗi có M3 | Có | Không | Không | clinical skill có, transport M3 thiếu | một họ/typed modifiers/QA |
| THAM_DINH_GD2 | M1 v2 | Có | Không | Không | route đọc mô tả có bên NMPRP, client chưa có | adapter GĐ2 riêng, giữ M1 v1 |

Mỗi dòng: runtime Rocky **BLOCKED: chưa được cấp quyền**. Hướng dẫn/skill không được coi là handler hoặc bằng chứng model chạy. M1 v1 hiện có runner; baseline model/token/latency production chưa đo được.
