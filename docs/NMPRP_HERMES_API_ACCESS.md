# Hermes đọc dữ liệu NMPRP qua API (chủ dự án đồng ý 17/10/2026)

**Trạng thái: client và tài liệu đã viết, CHƯA cấp tài khoản, CHƯA chạy với dm.kcb.vn.**

## Phạm vi
Giai đoạn thí điểm chỉ **ĐỌC**. Code: `support/nmprp_client.py`, test: `tests/test_nmprp_client.py` (offline, máy chủ giả).

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

## Chưa kiểm chứng
- Đường mạng từ container Hermes tới NMPRP (địa chỉ nội bộ hay qua `dm.kcb.vn`); client nhận `NMPRP_BASE_URL`.
- Tên trường thật của từng phản hồi; client không giả định, chỉ xoá khoá CPT.
- Hạn token phiên và giới hạn tốc độ đăng nhập (`limiter_dep(auth_login)`) của NMPRP.
