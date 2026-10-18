# Chạy máy chạy Hermes ở chế độ NỀN (systemd) trên Rocky

Trạng thái: **viết 18/10/2026, CHƯA kiểm trên Rocky** — chủ dự án là người chạy lần đầu; kết quả từng bước ghi lại ở cuối tệp này.
Tệp mẫu dịch vụ: `deploy/rocky/hermes-nmprp-may-chay.service.example`.

## Vì sao
Chạy tay (`python3 -m support.nmprp_may_chay`) giữ một cửa sổ SSH mở: đóng cửa sổ, mất mạng hay máy khởi động lại là máy chạy dừng, lượt đang chạy bị bỏ dở.
Chạy nền thì tự khởi động cùng máy chủ, tự chạy lại khi lỗi, nhật ký xem bằng `journalctl`.

## Bốn điều phải biết trước
1. **Chỉ MỘT máy chạy tại một thời điểm.** Hai máy chạy cùng tên sẽ cùng nhận lại MỘT lượt đang dở và gọi mô hình hai lần (tốn gấp đôi). Phải dừng máy chạy chạy tay trước khi bật dịch vụ.
2. **Dừng/khởi động lại giữa lượt không mất dữ liệu** — khởi động lại thì máy chạy nhận lại đúng lượt của nó và bỏ qua PL2 đã xong; chỉ lô đang chạy dở lúc bị dừng phải làm lại (và lời gọi đó đã tính tiền). Vì vậy nên khởi động lại khi không có lượt đang chạy.
3. **Tệp dừng mềm `HERMES_RUNNER_DUNG` chỉ chặn việc MỚI**, không dừng lượt đang chạy: máy chạy kiểm tệp này giữa hai lượt (`mot_vong`), không kiểm giữa hai lô. Muốn dừng một lượt đang chạy an toàn thì bấm «Huỷ lượt» trên giao diện NMPRP; máy chạy dừng ở lần báo cáo kế tiếp.
4. **Mật khẩu tài khoản dịch vụ nằm trong `deploy/rocky/nmprp-service.env`** (quyền 600, không vào Git, không dán ra chat). Hướng dẫn dưới đây không in nội dung tệp này.

## Các bước (mỗi bước chạy trên Rocky, `rocky@byt1`)
1. Kiểm không có lượt nào đang chạy (giao diện NMPRP, khu Lượt chạy: không có «Đang chạy»/«Tạm dừng»). Nếu có thì chờ xong hoặc «Huỷ lượt».
2. Dừng máy chạy chạy tay: trong cửa sổ đang chạy bấm `Ctrl+C`. Nếu không biết cửa sổ nào, kiểm: `pgrep -af nmprp_may_chay` — phải KHÔNG còn dòng nào trước khi sang bước 3.
3. Kiểm đường dẫn Python: `command -v python3` — phải ra `/usr/bin/python3`. Ra đường dẫn khác thì sửa `ExecStart` trong tệp dịch vụ cho khớp.
4. Kiểm `docker` chạy được không cần `sudo` với tài khoản `rocky`: `docker ps` — phải ra bảng container. Báo lỗi quyền thì DỪNG, chưa cài dịch vụ.
5. Kéo mã mới: `git -C /home/rocky/hermes-platform pull`.
6. Chép tệp dịch vụ: `sudo cp /home/rocky/hermes-platform/deploy/rocky/hermes-nmprp-may-chay.service.example /etc/systemd/system/hermes-nmprp-may-chay.service`.
7. Kiểm cú pháp: `sudo systemd-analyze verify /etc/systemd/system/hermes-nmprp-may-chay.service` — không có dòng lỗi (cảnh báo về `docker.service` nếu có thì ghi lại).
8. Nạp lại và bật: `sudo systemctl daemon-reload`, rồi `sudo systemctl enable --now hermes-nmprp-may-chay`.
9. Kiểm trạng thái: `systemctl status hermes-nmprp-may-chay --no-pager` — phải thấy `active (running)`.
10. Xem nhật ký: `sudo journalctl -u hermes-nmprp-may-chay -n 30 --no-pager` — phải thấy dòng khởi động `may chay nmprp-may-chay@...`. Trên giao diện NMPRP đèn «máy chạy đang trực» bật sau vài giây.
11. Thử một lượt nhỏ (chương nhỏ, ít PL2) và xem nhật ký thời gian thực: `sudo journalctl -u hermes-nmprp-may-chay -f` (thoát bằng `Ctrl+C`; thoát xem nhật ký KHÔNG dừng dịch vụ).

## Vận hành hằng ngày
- Cập nhật mã máy chạy: kiểm không có lượt đang chạy → `git -C /home/rocky/hermes-platform pull` → `sudo systemctl restart hermes-nmprp-may-chay` → kiểm nhật ký có dòng khởi động.
- Dừng hẳn: `sudo systemctl stop hermes-nmprp-may-chay`. Tắt tự khởi động: `sudo systemctl disable hermes-nmprp-may-chay`.
- Không cho nhận việc mới nhưng vẫn để dịch vụ chạy: `touch /home/rocky/hermes-shadow-out/DUNG`; cho nhận lại: `rm /home/rocky/hermes-shadow-out/DUNG`.
- Dịch vụ tự chạy lại sau 30 giây nếu máy chạy thoát với lỗi (vd tài khoản bị từ chối) — nhật ký sẽ lặp dòng `DUNG: ...`; sửa nguyên nhân rồi `sudo systemctl restart`.
- SELinux: nếu `getenforce` ra `Enforcing` và dịch vụ không khởi động được, xem `sudo journalctl -u hermes-nmprp-may-chay -n 50` và `sudo ausearch -m avc -ts recent` rồi báo lại, đừng tắt SELinux.

## Vì sao tệp mẫu không dùng `EnvironmentFile=`
systemd đọc tệp `.env` khác bash (xử lý dấu nháy, `$`, khoảng trắng và tiền tố `export` khác nhau), nên mật khẩu có ký tự đặc biệt có thể bị đọc sai mà không báo lỗi. Tệp mẫu gọi `bash -c 'set -a; . tệp; set +a; exec python3 ...'` — đúng cách chạy tay đang dùng.

## Nhật ký kiểm trên Rocky
(chủ dự án điền sau khi chạy: ngày, bước nào đạt, lỗi nếu có)
