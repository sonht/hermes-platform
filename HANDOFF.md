# HANDOFF — dự án NMPRP ⇄ Hermes Agent (cập nhật 17/10/2026)

Chủ dự án (sonht) không phải dân IT: trả lời tiếng Việt, ngắn, từng bước. Không dán bí mật, mã CPT, dữ liệu bệnh nhân vào chat hay tệp.

## Mục tiêu
Hermes Agent (Rocky, `hermes.kcb.vn`) đọc dữ liệu NMPRP (`dm.kcb.vn`) qua API, đề xuất nút cây CPT cho từng PL2, ghi gợi ý CHƯA DUYỆT vào bảng riêng; chuyên gia duyệt trên NMPRP; kết quả duyệt quay lại cho Hermes học (chỉ đề xuất sửa kỹ năng, có người duyệt).

## Đã xong
- `/agent` đã triển khai và chạy (PR hermes-platform#4 đã gộp).
- hermes-platform PR#7 (nháp, nhánh `feat/nmprp-hermes-profile`, head `58d7dbe`): profile `hermes/profiles/nmprp-mapping/` (SOUL, AGENTS, memories, 4 kỹ năng), `docs/NMPRP_HERMES_BRAIN_DUMP.md`, `docs/NMPRP_HERMES_KIEN_TRUC.md` + sơ đồ `docs/img/`, bản gốc ở `docs/lich-su/`. 21 bài kiểm chạy local đạt; kho chưa có CI.
- Nhánh `feat/nmprp-readonly-client` (PR#6): `support/nmprp_client.py`. Nhánh `feat/nmprp-mapping-design` (PR#5): thiết kế.
- nmprp PR#696 (nháp, nhánh `viec/hermes-tab`, head `0dfc6fd`, v1.100.227): Alembic `0065_hermes_goi_y`, bảng `hermes_goi_y`/`hermes_su_kien`, `/admin/hermes/*` (5 route).

## Quyết định đã chốt (không bàn lại)
- Phương án B (Hermes điều phối ngoài, chỉ gửi gợi ý), sau đó C thí điểm (shadow, một chương). CPN-AI A1–A6 của NMPRP chạy độc lập.
- Tab Hermes trên NMPRP chỉ admin thấy. Tài khoản dịch vụ chỉ có `studio_cpt`, không phải admin.
- Hermes chỉ đọc qua danh sách API cho phép; ghi duy nhất `POST /admin/hermes/goi-y` và `/su-kien`. Chủ dự án lo bản quyền CPT; Hermes không phát mã CPT.
- Chỉ dùng tên PL2 và PL1. PL1 = Phụ lục 1, danh mục kỹ thuật hiện hành, hết hiệu lực 01/01/2028, KHÔNG phải danh mục giá. Tham số `kind=pl3` của API và tiền tố `PL3-PROC-` chỉ PL2.
- Hai lớp trạng thái: NMPRP giữ nguyên (`MATCH/REJECT/ABSTAIN/EXPERT_REVIEW`, `PENDING`, `CHO_XEM`); nhãn HA (`HIGH_CONFIDENCE_PROPOSAL`…, `EXPERT_FEEDBACK/VERIFIED_KNOWLEDGE/GOLD_STANDARD`) chỉ ghi trong `bang_chung`.
- Công tắc AI của NMPRP không dừng được Hermes; phanh thật: `hermes pause`, tắt tài khoản dịch vụ, thu hồi/đặt trần khoá Claude.

## Việc dở / chặn
1. **nmprp PR#696 đang xung đột với `main`** (mergeable_state `dirty`, main nay ở `a8601065`; nhánh dựng trên `c67f980`). Cần gộp `main` vào nhánh (không rebase), đánh số lại Alembic nếu trùng `0065`, nâng lại `APP_VERSION`/CHANGELOG, chạy lại bài so sánh `FAILED` với `origin/main` cùng venv. PR chạm schema và phân quyền nên chờ bot trả kết quả mới gộp; chủ dự án tự triển khai.
2. Việc 1 của vòng phản hồi (hàm duyệt gợi ý có lý do, kho phản hồi, đường đọc phản hồi mức `studio_cpt`; hiện `GET /admin/hermes/goi-y` đòi admin) **CHƯA được chủ dự án duyệt**. Hỏi trước khi làm; nếu duyệt thì mở PR nháp riêng ở nmprp.
3. Các mục `[OWNER]` trong `docs/NMPRP_HERMES_BRAIN_DUMP.md` (người duyệt, ngưỡng, ngân sách, quyền dừng, công tắc CPT, ca mẫu từ dữ liệu thật). Gold Set hiện = 0.
4. Chưa cài profile lên Rocky: phiên Claude trên Rocky phải kiểm `hermes profile --help` trước. Chưa tạo tài khoản dịch vụ NMPRP; chưa đặt trần chi tiêu khoá Claude.
5. Giao diện tab Hermes trên NMPRP: PR riêng (`App.jsx`, `menuCay.js`, `duongDan.js`, Caddy `@spa`, `so-do-ky-thuat.html`, vitest).

## Kiểm thử / bẫy
- hermes-platform: `python3 -m unittest discover -s tests -q` (21 bài). nmprp: chạy từ gốc kho `PYTHONPATH=backend python -m pytest backend/app/tests -q` trong venv có fastapi; so danh sách FAILED/ERROR với `origin/main` cùng venv. Venv cũ: `/tmp/venv-nmprp` (có thể đã mất).
- Stop-hook báo "chưa push" có thể sai khi clone nông: kiểm bằng `git ls-remote`.
- Lệnh xoá hàng loạt (`git rm -r`) từng bị bộ phân loại từ chối; dùng `git mv` để lưu trữ.

## Bước kế tiếp đầu tiên
Mở nmprp, `git fetch`, xử lý xung đột PR#696 (mục 1). Không làm gì khác khi chưa có lệnh của chủ dự án.
