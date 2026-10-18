# Chạy máy chạy Hermes ở chế độ NỀN (systemd) trên Rocky

Trạng thái: **viết 18/10/2026, CHƯA kiểm trên Rocky** — chủ dự án là người chạy lần đầu; kết quả từng bước ghi lại ở cuối tệp này.
Tệp mẫu dịch vụ: `deploy/rocky/hermes-nmprp-may-chay.service.example`.

## Vì sao
Chạy tay (`python3 -m support.nmprp_may_chay`) giữ một cửa sổ SSH mở: đóng cửa sổ, mất mạng hay máy khởi động lại là máy chạy dừng, lượt đang chạy bị bỏ dở.
Chạy nền thì tự khởi động cùng máy chủ, tự chạy lại khi lỗi, nhật ký xem bằng `journalctl`.

## Bốn điều phải biết trước
1. **Chỉ MỘT máy chạy tại một thời điểm — từ 19/10/2026 máy chạy TỰ CHẶN điều này bằng khoá tệp, nhưng vẫn phải kiểm tay trước khi bật dịch vụ.** Máy chạy giữ một khoá `flock(2)` trên một tệp khoá (env `HERMES_RUNNER_LOCK`, mặc định cạnh tệp dừng mềm: `/home/rocky/hermes-shadow-out/may-chay.lock`) suốt vòng đời tiến trình. Bản THỨ HAI thấy khoá đã bị giữ thì in «da co may chay khac dang chay (PID ...)» và thoát ngay với mã **3** — **KHÔNG hỏi NMPRP một lần nào, không gọi mô hình** (khác với sự cố 19/10/2026: hai bản cùng tên cùng nhận lại một lượt `DANG_CHAY` và gọi mô hình hai lần). Khoá tự nhả khi tiến trình giữ nó chết vì bất kỳ lý do gì (Ctrl+C, kill -9, mất điện) — không có tệp PID cũ kẹt lại phải dọn tay.
   - **Thấy báo trùng thì xử lý thế nào:** đọc PID trong thông báo (hoặc `cat /home/rocky/hermes-shadow-out/may-chay.lock`), kiểm bản ĐANG giữ khoá còn sống không và đúng là bản bạn muốn chạy không (`ps -p <PID> -o pid,etime,cmd`). Nếu đúng là bản đang chạy bình thường (vd dịch vụ đã bật) — không cần làm gì, bỏ bản vừa báo trùng là đủ, dữ liệu không mất gì (xem điều 2 dưới đây). Nếu PID đó KHÔNG còn tồn tại mà vẫn báo trùng (chỉ xảy ra khi tệp khoá nằm trên một hệ tệp mạng không khoá đúng chuẩn POSIX `flock`, không phải trường hợp thường gặp trên Rocky) thì báo lại, **đừng tự xoá tệp khoá**.
   - **`RestartPreventExitStatus=3` trong tệp mẫu dịch vụ** làm systemd KHÔNG lặp khởi động lại khi gặp đúng mã thoát này — dịch vụ thoát ĐÚNG MỘT LẦN với mã 3 rồi ĐỨNG YÊN ở trạng thái `failed` (`systemctl status` ra `failed … status=3`), **KHÔNG tự chạy lại dù bản tay sau đó có dừng**. Đây là hành vi CỐ Ý (tránh dịch vụ cố giành khoá liên tục trong lúc có bản khác đang chạy song song), nhưng nghĩa là: dừng bản tay xong KHÔNG đủ — phải chạy tay thêm `sudo systemctl restart hermes-nmprp-may-chay` để dịch vụ chạy lại. Mọi lỗi khác (vd lỗi xác thực `NmprpError` mã 2) vẫn lặp lại như trước (`Restart=on-failure`).
   - **ĐỪNG GỠ `RestartPreventExitStatus=3`** để "sửa" cho dịch vụ tự chạy lại — đó đúng là hành vi yêu cầu đòi (không cho dịch vụ giành khoá liên tục khi có bản khác đang giữ).
   - **KHÔNG xoá tệp khoá để "giải phóng" khi còn một bản đang chạy.** Tệp khoá không phải thứ giữ trạng thái khoá — chính `flock` trên *file description* đang mở mới giữ. Xoá tệp đang bị một bản khác giữ không làm bản đó mất khoá; nó chỉ làm bản MỚI mở lại đường dẫn đó tạo ra một tệp (inode) khác, lấy khoá trên tệp mới dễ dàng — kết quả là HAI bản cùng chạy, đúng điều cơ chế này phải chặn.
   - **Bước `pgrep` ở mục "Các bước" dưới đây vẫn CẦN làm, khoá không thay thế nó.** Khoá chỉ chặn được hai TIẾN TRÌNH cùng xử lý một lượt tại ĐÚNG thời điểm giành khoá (lúc khởi động) — nó không dừng êm một bản đang chạy. Bỏ qua bước này trước khi bật dịch vụ thì dịch vụ sẽ thoát MỘT lần với mã 3 và đứng ở trạng thái `failed` (KHÔNG tự lặp lại, xem gạch đầu dòng trên) — phải dừng bản tay cho đàng hoàng RỒI chạy tay `sudo systemctl restart hermes-nmprp-may-chay` để dịch vụ thật sự chạy.
2. **Dừng/khởi động lại giữa lượt không mất dữ liệu** — khởi động lại thì máy chạy nhận lại đúng lượt của nó và bỏ qua PL2 đã xong; chỉ lô đang chạy dở lúc bị dừng phải làm lại (và lời gọi đó đã tính tiền). Vì vậy nên khởi động lại khi không có lượt đang chạy.
3. **Tệp dừng mềm `HERMES_RUNNER_DUNG` chỉ chặn việc MỚI**, không dừng lượt đang chạy: máy chạy kiểm tệp này giữa hai lượt (`mot_vong`), không kiểm giữa hai lô. Muốn dừng một lượt đang chạy an toàn thì bấm «Huỷ lượt» trên giao diện NMPRP; máy chạy dừng ở lần báo cáo kế tiếp.
4. **Mật khẩu tài khoản dịch vụ nằm trong `deploy/rocky/nmprp-service.env`** (quyền 600, không vào Git, không dán ra chat). Hướng dẫn dưới đây không in nội dung tệp này.

## Các bước (mỗi bước chạy trên Rocky, `rocky@byt1`)
1. Kiểm không có lượt nào đang chạy (giao diện NMPRP, khu Lượt chạy: không có «Đang chạy»/«Tạm dừng»). Nếu có thì chờ xong hoặc «Huỷ lượt».
2. Dừng máy chạy chạy tay: trong cửa sổ đang chạy bấm `Ctrl+C`. Nếu không biết cửa sổ nào, kiểm: `pgrep -af nmprp_may_chay` — phải KHÔNG còn dòng nào trước khi sang bước 3. **Đừng bỏ qua bước này vì tin vào khoá tệp (điều 1 ở trên)**: khoá chỉ làm bản THỨ HAI tự thoát sạch sẽ (mã 3, không gọi NMPRP) khi có bản khác đang giữ — nó không ép bản đang chạy dừng lại — nếu bỏ qua bước này thì dịch vụ mới bật sẽ thoát MỘT lần với mã 3 và đứng yên ở `failed` (KHÔNG tự chạy lại khi bản tay dừng) — phải dừng bản tay rồi chạy tay `sudo systemctl restart hermes-nmprp-may-chay` (xem bước 9).
3. Kiểm đường dẫn Python: `command -v python3` — phải ra `/usr/bin/python3`. Ra đường dẫn khác thì sửa `ExecStart` trong tệp dịch vụ cho khớp.
4. Kiểm `docker` chạy được không cần `sudo` với tài khoản `rocky`: `docker ps` — phải ra bảng container. Báo lỗi quyền thì DỪNG, chưa cài dịch vụ.
5. Kéo mã mới: `git -C /home/rocky/hermes-platform pull`.
6. Chép tệp dịch vụ: `sudo cp /home/rocky/hermes-platform/deploy/rocky/hermes-nmprp-may-chay.service.example /etc/systemd/system/hermes-nmprp-may-chay.service`.
7. Kiểm cú pháp: `sudo systemd-analyze verify /etc/systemd/system/hermes-nmprp-may-chay.service` — không có dòng lỗi (cảnh báo về `docker.service` nếu có thì ghi lại).
8. Nạp lại và bật: `sudo systemctl daemon-reload`, rồi `sudo systemctl enable --now hermes-nmprp-may-chay`.
9. Kiểm trạng thái: `systemctl status hermes-nmprp-may-chay --no-pager` — phải thấy `active (running)`. Nếu thấy `failed … status=3` (và nhật ký có dòng «da co may chay khac dang chay (PID …)») thì KHÔNG phải lỗi dịch vụ — nghĩa là còn một bản khác đang giữ khoá lúc dịch vụ khởi động: quay lại **bước 2** (`pgrep -af nmprp_may_chay`, dừng đúng bản đang giữ), rồi chạy `sudo systemctl restart hermes-nmprp-may-chay` và kiểm lại bước này. Dịch vụ sẽ KHÔNG tự thử lại mã 3 (xem điều 1), nên bỏ qua việc restart tay là để dịch vụ đứng yên ở trạng thái `failed` mãi.
10. Xem nhật ký: `sudo journalctl -u hermes-nmprp-may-chay -n 30 --no-pager` — phải thấy dòng khởi động `may chay nmprp-may-chay@...`. Trên giao diện NMPRP đèn «máy chạy đang trực» bật sau vài giây.
11. Thử một lượt nhỏ (chương nhỏ, ít PL2) và xem nhật ký thời gian thực: `sudo journalctl -u hermes-nmprp-may-chay -f` (thoát bằng `Ctrl+C`; thoát xem nhật ký KHÔNG dừng dịch vụ).

## Vận hành hằng ngày
- Cập nhật mã máy chạy: kiểm không có lượt đang chạy → `git -C /home/rocky/hermes-platform pull` → `sudo systemctl restart hermes-nmprp-may-chay` → kiểm nhật ký có dòng khởi động.
- Dừng hẳn: `sudo systemctl stop hermes-nmprp-may-chay`. Tắt tự khởi động: `sudo systemctl disable hermes-nmprp-may-chay`.
- Không cho nhận việc mới nhưng vẫn để dịch vụ chạy: `touch /home/rocky/hermes-shadow-out/DUNG`; cho nhận lại: `rm /home/rocky/hermes-shadow-out/DUNG`.
- Dịch vụ tự chạy lại sau 30 giây nếu máy chạy thoát với lỗi (vd tài khoản bị từ chối) — nhật ký sẽ lặp dòng `DUNG: ...`; sửa nguyên nhân rồi `sudo systemctl restart`. **Ngoại lệ: mã thoát 3** ("đã có bản khác giữ khoá") KHÔNG lặp lại — dịch vụ đứng yên ở `failed`, phải tự chạy tay `sudo systemctl restart hermes-nmprp-may-chay` sau khi dừng bản kia (xem bước 9). Mã 4 (không tạo/mở được tệp khoá — thư mục hỏng, quyền sai…) VẪN lặp lại mỗi 30 giây như lỗi thường.
- SELinux: nếu `getenforce` ra `Enforcing` và dịch vụ không khởi động được, xem `sudo journalctl -u hermes-nmprp-may-chay -n 50` và `sudo ausearch -m avc -ts recent` rồi báo lại, đừng tắt SELinux.

## Vì sao tệp mẫu không dùng `EnvironmentFile=`
systemd đọc tệp `.env` khác bash (xử lý dấu nháy, `$`, khoảng trắng và tiền tố `export` khác nhau), nên mật khẩu có ký tự đặc biệt có thể bị đọc sai mà không báo lỗi. Tệp mẫu gọi `bash -c 'set -a; . tệp; set +a; exec python3 ...'` — đúng cách chạy tay đang dùng.

## Nhật ký kiểm trên Rocky
(chủ dự án điền sau khi chạy: ngày, bước nào đạt, lỗi nếu có)
