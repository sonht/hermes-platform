# Runbook Rocky — bản chuẩn bị, chưa triển khai

**Chỉ thực hiện phần production sau khi chủ dự án phê duyệt mã và thời điểm triển khai. Không tự merge.** Các commit trong báo cáo đang là commit local; cần đưa đúng commit lên remote theo quy trình review trước khi máy Rocky có thể fetch. Không dùng `git pull` để thay đổi production ngoài quy trình này.

## 1. Kiểm kê chỉ đọc trên Rocky

Chỉ chủ dự án có đường SSH/VPN byt1 theo quy định NMPRP. Không gửi token, `.env`, config provider hay DB dump vào chat. Ghi lại kết quả commit, image digest, runtime version, checksum skill và trạng thái dịch vụ, không ghi giá trị bí mật.

**ROCKY — commit worker.** Phải thấy commit đã duyệt.

```bash
git -C /home/rocky/hermes-platform rev-parse HEAD
```

**ROCKY — image và phiên bản runtime.** Phải thấy image/digest đang chạy, đối chiếu Compose; tên container lấy từ repo hiện tại.

```bash
docker inspect --format '{{.Image}}' hermes-platform-agent
```

```bash
docker exec -u hermes hermes-platform-agent hermes --version
```

```bash
systemctl status hermes-nmprp-may-chay --no-pager
```

**ROCKY — backend hiện hành.** Phải ghi được version trước thay đổi; GET này không đổi công tắc.

```bash
curl --fail --silent --show-error https://dm.kcb.vn/health
```

Không dump `docker inspect` đầy đủ, process environment hay config provider. Image Compose được ghim `sha256:36099926da316742423544e055d4734777105ffe6341873af5459b957d0c2919`; đây là cấu hình repo, **không phải kết quả đo Rocky**. Cloud pull image này thất bại do thiếu dung lượng Docker khi giải nén; phải kiểm tài nguyên máy đích trước khi kéo/build.

## 2. Backup và chuẩn bị

Đợi lượt đang chạy đóng hoặc tạm dừng đúng quy trình; không giết giữa lời gọi model. Ghi SHA worker/backend cũ, trạng thái QG-16 và cờ M0/M2/M3. **Không đổi QG-16.** Sao lưu DB bằng đường vận hành sẵn có, kiểm backup theo hướng dẫn repo; không restore production để thử. Bản vá này không thêm migration.

**ROCKY — backup DB theo script triển khai hiện hữu.** Phải có tệp sao lưu hợp lệ trong thư mục backup được bảo vệ.

```bash
bash /opt/nmprp/app/deploy/rocky/sao-luu.sh
```

Không thay profile `nmprp-mapping`, prompt M1, image Hermes hay config provider trong lần sửa này. Trước khi ghi một profile `nmprp-stages` đã tồn tại, backup riêng SOUL và thư mục skill vào kho lưu được bảo vệ, kiểm archive đọc được; không ghi đè profile không rõ nguồn. Profile mới hoàn toàn không cần backup bộ cũ.

## 3. Staging trước, không bật stage production

Chuẩn bị một NMPRP staging độc lập với tài khoản máy được giới hạn và allowlist tương ứng. Cài đúng commit backend NMPRP đã review trước worker: cần hai route mới `/may/nang-luc` (admin) và `/may/luot/{id}/nguon-m3` (đúng máy của lượt M3). Giữ dịch vụ worker production cũ chạy M1 khi staging chạy bằng tài khoản/lock/state riêng. Không dùng chung tên tài khoản, lock hoặc hàng đợi production.

**ROCKY — kiểm cú pháp tạo profile.** Phải xác minh option bằng runtime thực trước khi dùng lệnh tiếp.

```bash
docker exec -u hermes hermes-platform-agent hermes profile create --help
```

**ROCKY — chỉ khi profile chưa tồn tại.** Phải tạo được profile riêng, không đổi M1.

```bash
docker exec -u hermes hermes-platform-agent hermes profile create nmprp-stages --no-skills --no-alias --description "NMPRP M0 M2 M3 GD2 staging"
```

**ROCKY — kiểm checksum nguồn đã review.** Phải tất cả OK.

```bash
bash -c 'cd /home/rocky/hermes-platform/hermes/profiles/nmprp-stages && sha256sum -c PROFILE_SHA256SUMS'
```

**ROCKY — chép đúng SOUL/skills từ commit đã review; profile mới hoặc đã backup.** Pipeline dừng nếu một vế lỗi. Không chuyển `.env`, config, sessions, DB hay credential từ repo.

```bash
bash -o pipefail -c 'git -C /home/rocky/hermes-platform archive HEAD:hermes/profiles/nmprp-stages SOUL.md skills PROFILE_SHA256SUMS | docker exec -i -u hermes hermes-platform-agent tar -xf - -C /opt/data/profiles/nmprp-stages'
```

```bash
docker exec -u hermes -w /opt/data/profiles/nmprp-stages hermes-platform-agent sha256sum -c PROFILE_SHA256SUMS
```

```bash
docker exec -u hermes hermes-platform-agent hermes -p nmprp-stages skills list
```

Phải thấy `nmprp-stage-m0`, `nmprp-stage-m2`, `nmprp-stage-m3`, `nmprp-stage-gd2`. Cấu hình provider/model/hạn mức cho profile mới bằng cơ chế runtime được hỗ trợ và kênh nhập bí mật riêng của máy; không chép key vào tài liệu hay chat. `skills list` và checksum **không chứng minh model được cấp quyền**. Canary mới chứng minh đường suy luận.

Tệp staging env riêng `/home/rocky/hermes-shadow-out/staging-runner.env` do người vận hành cấp: `NMPRP_BASE_URL` trỏ staging, `NMPRP_SERVICE_USER`, `NMPRP_SERVICE_PASSWORD`, `HERMES_RUNNER_MODELS`, `HERMES_RUNNER_REASONING`; thêm `HERMES_RUNNER_LOCK`, `HERMES_RUNNER_DUNG`, `HERMES_RUNNER_STAGE_STATE` trỏ các đường staging riêng. Không ghi đè env production. Mặc định `HERMES_RUNNER_STAGES` rỗng: chỉ M1 v1. Thử từng stage đã chuẩn bị: `m0`, rồi `v2`, `m2`, `m3`; danh sách dùng dấu phẩy. Không khai capability thủ công. Mô hình/mức suy luận phải có thực trong runtime, không dùng giá trị fixture `cao` của test.

**ROCKY — kiểm năng lực được phép khai, không poll và không gọi model.** Chạy từ gốc repo. Kết quả chỉ có tên năng lực; thiếu skill/runtime/hash sai phải cho danh sách rỗng.

```bash
bash -c 'cd /home/rocky/hermes-platform && set -a && . /home/rocky/hermes-shadow-out/staging-runner.env && set +a && python3 -c "from support.nmprp_may_chay import CauHinh; from support.nmprp_stages import ready; print(ready(CauHinh.tu_moi_truong()))"'
```

**ROCKY — chỉ staging đã kiểm URL/tài khoản/lock.** Phải thấy handshake mới, đúng capability/version và chỉ nhận job staging đã tạo có chủ đích.

```bash
bash -c 'cd /home/rocky/hermes-platform && set -a && . /home/rocky/hermes-shadow-out/staging-runner.env && set +a && python3 -m support.nmprp_may_chay --mot-lan'
```

## 4. Canary và nghiệm thu

- T0–T2: M0 thiếu PHAN_RA bị chặn; worker chỉ PHAN_RA chạy được **M0 độc lập**, Chạy liền vẫn nêu thiếu M2/M3. Ghi worker/version/heartbeat, request và lỗi đã bỏ bí mật.
- M0: thử dựng từ S1 trên staging trước (không gọi model); đếm thực tế Chương 6, không hardcode 129/130; hồ sơ thiếu phải báo thiếu, không tự READY. Chỉ gọi Hermes cho PL2 cần phân tích bằng job phạm vi rõ.
- M1 v1: so snapshot/QA với mốc trước; `_chay_luot` và engine server không đổi. M1 v2: phải có hai lời gọi thật và hồ sơ/đối chiếu lưu được; nguồn Loại trừ có thật, sai trích bị từ chối. Không bật v2 khi provider/cấu hình mới chưa chạy được.
- M2: chọn một `khoa_nhanh` thuộc snapshot M1 đã ghim; kiểm đủ thành viên hoặc chưa vào họ kèm lý do, không sửa M1. Ghi token/latency/correlation ID.
- M3: họ đã Đồng ý của đúng bộ M2; chỉ ID modifier ACTIVE/EXPERT_APPROVED. Tái dựng ngữ nghĩa hiện còn giới hạn: không có M0 đầy đủ ghim cho M3 nên adapter **từ chối PASS**, chỉ nhận FAIL/UNCERTAIN có giải thích; không công nhận nghiệm thu lâm sàng.
- Replay M3 qua `/m23/luot` với `quy_trinh=m3`, snapshot/chương/bộ M2 rõ, `de_xuat_ids=[một họ]`, `chay_lai=true`: bản cũ còn, chỉ một họ tạo gốc mới. Xem trước dùng cùng tham số. Không gọi lại upstream.
- Thử mất mạng sau khi GĐ2 ghi hồ sơ nhưng trước gửi gợi ý: restart dùng checkpoint để gửi tiếp gợi ý, không bỏ qua vì `pl2_da_xong`, không trả tiền lại hai lời gọi đã có kết quả.
- Không xem XONG là đã duyệt. Chuyên gia chấm riêng trước khi đề nghị rollout. Không đổi lựa chọn artifact/tri thức tự động.

Đối chiếu `TEST_REPORT.md`; kiểm local có fixture không thay thế canary model thật. Khi canary đạt mới trình bằng chứng để chủ dự án duyệt rollout production.

## 5. Production sau phê duyệt và rollback

Chủ dự án triển khai backend theo lệnh chuẩn hiện có, sau backup và kiểm SHA. Không có migration mới trong bản vá; nếu DB production đang tụt migration cũ, đó là thay đổi cần kiểm và duyệt riêng.

**ROCKY — chỉ sau phê duyệt rollout backend.** Phải có health/version 1.100.357 và UI mới.

```bash
bash /opt/nmprp/app/deploy/rocky/cap-nhat.sh
```

Cập nhật worker tới commit đã duyệt bằng quy trình phát hành hiện tại, giữ image và profile M1. Chỉ cấu hình stage đã qua canary trong env của dịch vụ sau khi phê duyệt; trạng thái mặc định vẫn rỗng. Đợi lượt an toàn rồi restart dịch vụ.

**ROCKY — chỉ sau phê duyệt, đã xử lý lượt đang chạy.** Phải thấy lời chào mới trong 60 giây; TTL server 180 giây.

```bash
sudo systemctl restart hermes-nmprp-may-chay
```

**ROCKY — log dịch vụ, không in cấu hình bí mật.** Phải có đúng job/stage/worker-version/token/thời gian hoặc mã lỗi an toàn.

```bash
journalctl -u hermes-nmprp-may-chay -n 80 --no-pager
```

Rollback: ngừng cấp job stage mới, đợi/tạm dừng lượt an toàn, bỏ stage khỏi `HERMES_RUNNER_STAGES`, restart runner để lời chào xóa năng lực đó. Giữ checkpoints/artifacts để điều tra; không xoá volume/DB, không `reset --hard` trên checkout có việc địa phương. Khôi phục release worker/backend cũ đã ghi ở bước 1 bằng quy trình release hiện có, không restore DB chỉ vì rollback mã. Không có schema mới cần downgrade. Profile stage riêng có thể giữ nhưng bị vô hiệu; không sửa M1 hoặc QG-16. Chọn lại artifact cũ qua UI quản trị có audit thay vì xoá bản mới.
