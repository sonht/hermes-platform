# Máy chạy lượt Hermes cho NMPRP (`support/nmprp_may_chay.py`)

Nửa còn lại của tab **Hermes Agent** ở NMPRP (v1.100.231, nhánh `viec/hermes-hang-doi` của `sonht/nmprp`; hợp đồng phía máy chủ:
`docs/hermes-agent/DIEU_PHOI_LUOT.md` trong kho đó). **NMPRP không gọi ra Hermes**; máy chạy ở Rocky tự hỏi NMPRP.

## 1. Việc nó làm

Mỗi nhịp (30 giây khi rảnh): `chao` (khai còn sống + mô hình/mức suy luận máy cho phép) → `nhan` (xin lượt `CHO_CHAY` cũ nhất; máy
khởi động lại thì nhận lại đúng lượt `DANG_CHAY` của chính nó) → với từng lô PL2: kiểm ngân sách → gọi `hermes -z` (cùng hàm `goi_hermes`
của shadow) → kiểm định câu trả lời (cùng `kiem_ket_qua`) → gửi gợi ý + kết quả theo PL2 → báo tiến độ. Hết lô: `XONG`.
Hết số lời gọi của đợt hoặc chạm trần token: `TAM_DUNG` (admin bấm «Chạy tiếp»/«Chạy hết»; chạm trần thì phải nâng trần).

Một luồng phụ chào mỗi 60 giây bằng client riêng, để lời gọi mô hình dài (tới 15 phút) không làm máy trông như đã tắt.

## 2. Quy tắc an toàn (có bài kiểm khoá)

- Mọi gợi ý gửi đi đều CHƯA DUYỆT. Danh sách đường POST của client chỉ có sáu đường hàng đợi + hai đường gợi ý/sự kiện cũ;
  không đường nào ghi ánh xạ hay danh mục. Mã id lượt phải là `HL_` + đúng 12 hex.
- Mô hình/mức suy luận của lượt được kiểm với danh sách **máy chạy** khai (`HERMES_RUNNER_MODELS`, `HERMES_RUNNER_REASONING`), không tin
  danh sách phía NMPRP; tên mô hình chỉ nhận `[A-Za-z0-9._:/@-]` và đi vào lệnh dạng danh sách (không qua shell). Danh sách mô hình
  mặc định RỖNG = chỉ dùng mô hình mặc định của profile — **không ghi cứng tên mô hình nào**.
- Ngân sách kiểm TRƯỚC mỗi lời gọi: lời gọi sẽ vượt trần thì không gọi, lượt tạm dừng. Số đếm gửi lên là LUỸ KẾ (cộng vào số nền
  của lượt), vì máy chủ không chấp nhận số lùi.
- Lỗi mạng/NMPRP **không** kết thúc lượt: lượt vẫn `DANG_CHAY`, máy chờ gấp đôi rồi hỏi lại và tiếp tục. Lỗi bất ngờ khác: `LOI`,
  thông điệp chỉ ghi TÊN LỚP lỗi (không nội dung, không bằng chứng).
- Công tắc AI của NMPRP tắt ⇒ `TAM_DUNG` kèm lời nhắn, không gọi mô hình.
- Tệp dừng mềm `HERMES_RUNNER_DUNG` (mặc định `/home/rocky/hermes-shadow-out/DUNG`): còn tệp thì không nhận việc, không chào.
  `hermes pause` vẫn là nút dừng khẩn cho mọi thứ khác.

## 3. Cấu hình

Dùng chung `deploy/rocky/nmprp-service.env` (chmod 600, không vào git): `NMPRP_BASE_URL`, `NMPRP_SERVICE_USER`, `NMPRP_SERVICE_PASSWORD`,
thêm ba biến tuỳ chọn ở `nmprp-service.env.example`. **Tài khoản dịch vụ phải trùng `NMPRP_HERMES_MAY` ở NMPRP** (mặc định
`hermes-nmprp`); lệch tên thì mọi đường hàng đợi trả 403 — đóng chứ không mở.

## 4. Chạy thử (CHƯA làm trên Rocky — mới có bài kiểm giả lập)

Thứ tự đề nghị khi triển khai: (1) NMPRP 1.100.231 lên dm.kcb.vn (có migration 0068, sao lưu trước) và `NMPRP_HERMES_MAY` đã khai;
(2) kéo mã kho này về `/home/rocky/hermes-platform`; (3) chạy MỘT nhịp bằng tay để xem nó chào được:

```bash
cd /home/rocky/hermes-platform && set -a && . deploy/rocky/nmprp-service.env && set +a && python3 -m support.nmprp_may_chay --mot-lan
```

Phải thấy dòng khởi động, không có `DUNG:`; ở tab NMPRP đèn "máy chạy đang trực" bật. (4) Tạo một lượt NHỎ (chương 6, 5 PL2, 1 lời gọi,
trần token thấp) ở tab rồi chạy `python3 -m support.nmprp_may_chay` (không `--mot-lan`) trong một cửa sổ riêng để xem tận mắt.
(5) Chỉ sau đó mới cân nhắc chạy nền bằng systemd (`deploy/rocky/hermes-nmprp-may-chay.service.example`, chưa kiểm).

## 5. Việc chưa làm

Chưa đo chất lượng; chưa nạp bài học vào bộ nhớ/skill của Hermes (đợt 3); chưa kiểm trên Python 3.9 thật của Rocky (chỉ kiểm cú pháp 3.9).
