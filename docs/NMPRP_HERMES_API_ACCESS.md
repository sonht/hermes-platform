# Hermes đọc dữ liệu NMPRP qua API (chủ dự án đồng ý 17/10/2026)

**Trạng thái: client và tài liệu đã viết, CHƯA cấp tài khoản, CHƯA chạy với dm.kcb.vn.**


## Phạm vi
Giai đoạn thí điểm: **ĐỌC** (gồm phản hồi của người duyệt, `GET /admin/hermes/phan-hoi`) cộng **HAI đường ghi hẹp** (`POST /admin/hermes/goi-y`, `POST /admin/hermes/su-kien`, vào bảng riêng `hermes_*` của NMPRP, gợi ý luôn CHƯA DUYỆT). Mọi POST khác bị từ chối trước khi gọi mạng. Code: `support/nmprp_client.py`, test: `tests/test_nmprp_client.py` (offline, máy chủ giả).

## Tài khoản dịch vụ (việc của chủ dự án trên NMPRP)
- Tạo một tài khoản riêng cho Hermes, cấp tác vụ **`studio_cpt`**, **không** phải admin.
  Lý do (đọc mã NMPRP): router `/admin/cpn-ai/*` gác bằng `require_studio` = admin HOẶC tác vụ `studio_cpt`;
  các đường đọc cần cho thí điểm không đòi admin. Tạo/chạy lượt mới đòi admin nên Hermes **không** làm được và không cần làm.
- Mật khẩu chỉ đặt vào `deploy/rocky/nmprp-service.env` (mẫu: `nmprp-service.env.example`), `chmod 600`, ngoài Git.
  Đăng nhập: `POST /admin/auth/login`, token phiên nằm trong bộ nhớ tiến trình, hết hạn thì đăng nhập lại một lần.

## Đường đọc được cho phép (allowlist; còn lại bị từ chối trước khi gọi mạng)
`/admin/cpt-tree/khung` · `/admin/cpn-ai/runs` · `/admin/cpn-ai/runs/{id}/(tien-do|candidates|conflicts|families|qa)` ·
`/review/search?kind=pl3|pl1` · `/review/chapters?kind=pl3|pl1` · `/review/map?kind=pl1`
(API NMPRP vẫn gọi PL2 là `pl3` ở tham số `kind`.)

## Bản quyền CPT (AMA)
Chủ dự án nhận trách nhiệm về bản quyền CPT (17/10/2026). Vì vậy client có **công tắc**: `NMPRP_ALLOW_CPT=1` (hoặc `allow_cpt=True`)
cho phép đọc nội dung CPT. **Mặc định TẮT**; chỉ chủ dự án bật, và việc bật nghĩa là mã CPT có thể đi vào lời gọi mô hình, bộ nhớ và log của Hermes.
Quy tắc riêng của NMPRP («mã CPT không được phát ra API ngoài») là của NMPRP; đổi nó là quyết định của chủ dự án ở kho NMPRP.

Mặc định (công tắc tắt):
- Chặn `/admin/cpt-tree/khung/ma-cpt` và `kind=cpt`.
- Khi đã đăng nhập, `/admin/cpt-tree/khung` trả thêm `dai_ma` (dải mã CPT): client **xoá** `dai_ma`, `ma_cpt`, `cpt_code`, `cpt_codes`, `cpt_range` ở mọi cấp trước khi dữ liệu tới Hermes.
  Danh sách khoá là phòng thủ thêm, chưa kiểm chứng đầy đủ với mọi đầu ra của NMPRP.
- `/admin/cpt-tree/khung/bao-gom` («Bao gồm/Loại trừ», từ gói `CPT_Danh_muc_dich`) **chưa** được cho phép: cần chủ dự án xác nhận nội dung có chứa văn bản bản quyền hay không.

## Đọc phản hồi của người duyệt (vòng phản hồi)
- Client có `phan_hoi(sau, limit)` (một trang) và `phan_hoi_moi(sau)` (đọc hết phần mới, trả `(các dòng, con trỏ mới)`). Job tự lưu con trỏ giữa hai lần chạy; con trỏ rỗng = đọc từ đầu.
- Chỉ đường `GET /admin/hermes/phan-hoi` được thêm. `GET /admin/hermes/goi-y`, `/tom-tat`, `/su-kien` là đường của tab (chỉ admin) nên **không** nằm trong danh sách cho phép. Hermes **không** gọi được đường duyệt (`POST .../duyet`): quyết định là của người.
- Mỗi dòng phản hồi là `EXPERT_FEEDBACK` (ý kiến thẩm định), **không** phải nhãn vàng; một dòng đơn lẻ không đủ để đề xuất đổi quy tắc (cần từ 2 ca có nguồn). Quyết định `SUA` kèm `branch_key_sua` (nút đúng do chuyên gia nhập). Không có tên người duyệt.
- Đọc theo con trỏ cần máy chủ NMPRP có bản đọc theo con trỏ (nhánh `viec/hermes-phan-hoi-sua` của `nmprp`, xếp chồng trên #697). Với bản cũ chưa có con trỏ, client dừng khi trang lặp lại thay vì lặp vô hạn.

## Chưa kiểm chứng
- Đường mạng từ container Hermes tới NMPRP (địa chỉ nội bộ hay qua `dm.kcb.vn`); client nhận `NMPRP_BASE_URL`.
- Tên trường thật của từng phản hồi; client không giả định, chỉ xoá khoá CPT.
- Hạn token phiên và giới hạn tốc độ đăng nhập (`limiter_dep(auth_login)`) của NMPRP.

## Công tắc AI của NMPRP KHÔNG tự dừng được Hermes (đã xác nhận 17/10/2026)
Công tắc AI toàn cục của NMPRP chỉ chặn các lời gọi mô hình **bên trong NMPRP** (`ai_client.call_text`). Hermes đã được nối Claude API
bằng khoá riêng của nó nên tự gọi mô hình, ngoài `call_text`. Hệ quả:
- Client có `ai_cong_tac_bat()`: đọc `GET /admin/ai/status`, **FAIL-CLOSED** (lỗi, thiếu trường hay giá trị khác `True` đều coi là TẮT).
  Job của Hermes **phải gọi nó đầu tiên và dừng khi False**. Đây là sự TỰ GIÁC của Hermes, không phải cưỡng chế từ NMPRP.
- Cưỡng chế thật nằm ở phía Hermes và các khoá: `hermes pause` (dừng khẩn cấp toàn bộ cron, tài liệu Hermes), tạm dừng từng job,
  vô hiệu hoá tài khoản dịch vụ trên NMPRP (Hermes mất khả năng đọc và ghi), thu hồi hoặc đặt hạn mức cho khoá Claude API của Hermes.
- Chi phí mô hình của Hermes tính theo khoá của Hermes, tách khỏi NMPRP: đặt hạn mức chi tiêu ở nhà cung cấp.
