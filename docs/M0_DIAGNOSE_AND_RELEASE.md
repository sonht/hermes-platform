# M0 — chẩn đoán, kiểm thử và triển khai có kiểm soát

Bản vá này **chưa xác nhận sửa được lỗi thoát mã 1 trên Rocky**. Không merge/deploy từ phiên soạn bản vá. Batching là cải thiện riêng, không phải bằng chứng nguyên nhân. Báo cáo giao diện và rà soát tổng thể nằm ở `sonht/nmprp/docs/hermes-agent/BAO_CAO_M0_VA_GIAO_DIEN_2026-10-24.md`.

## A. Một lần thu thông tin — không cần triển khai, không gọi model

**ROCKY.** Lấy script từ nhánh review và chạy trực tiếp, không đổi working tree hoặc restart. Phải thấy metadata của cấu hình chung, `nmprp-mapping` và `nmprp-stages`, trạng thái nguồn credential, CLI flags, quyền ghi workspace và có `timeout` hay không. Không được thấy giá trị key, hash key hoặc raw config. Không cần tạo key mới.

```bash
bash -o pipefail -c 'git -C /home/rocky/hermes-platform fetch origin viec/m0-batch-resume && git -C /home/rocky/hermes-platform show FETCH_HEAD:scripts/nmprp-profile-diagnostics.py | python3 -'
```

Kết quả là kiểm kê nguồn cấu hình, không phải bằng chứng provider đã cho phép inference. `.env` có/không có key chưa đủ để kết luận. Nguồn có thể là config profile, config chung, env container hoặc auth store. So sánh provider/model và nguồn M1 đang dùng trước khi chọn cách cấu hình M0. Không chép nguyên `.env` M1 vì có thể chứa thông tin ngoài phạm vi model. Chỉ khi có bằng chứng mới dùng cơ chế cấu hình được Hermes runtime đang cài hỗ trợ để cấp cùng provider/credential phù hợp.

Các nguyên nhân được log theo allowlist: `CLI_ARGUMENT_REJECTED`, `CREDENTIAL_NOT_FOUND`, `AUTHENTICATION_FAILED`, `MODEL_NOT_AVAILABLE`, `RATE_LIMITED`, `PROFILE_NOT_FOUND`, `FILESYSTEM_PERMISSION`, `RUNTIME_DEPENDENCY_MISSING`, `CONNECTION_FAILED`, hoặc lỗi chưa phân loại. Không coi một nhãn suy từ stderr là kết luận đầy đủ về nguồn credential.

## B. Cổng trước triển khai

- Review/CI hai nhánh: `sonht/nmprp:viec/kcb-agent-m0-output` và `sonht/hermes-platform:viec/m0-batch-resume`.
- Chỉ chủ dự án phê duyệt merge/deploy. Không chạy lệnh phần C trước khi phê duyệt.
- Ghi SHA hiện tại của từng repo, image digest và phiên bản `/health`; bảo toàn backup và journal stage. Không xóa lượt hoặc `.pending`.
- Không chuyển mã worker trong lúc còn inference chưa đối soát; huỷ UI không chứng minh tiến trình model đã dừng. Kiểm tiến trình/log thực tế trước. Không restart lặp để thử.
- Hai repo phải sạch; thay đổi local phải được xử lý riêng. Không dùng reset --hard hoặc clean trên máy chủ.
- Bản NMPRP tăng từ nền main 1.100.359 lên bản vá 1.100.360; không có migration mới trong bản vá này. Nếu main đã tiến thêm, tích hợp và kiểm lại thay vì ép lùi phiên bản.

## C. Lệnh triển khai sau khi đã phê duyệt và merge

**ROCKY — NMPRP.** Repo phải đang theo nhánh phát hành đã chứa bản vá. Kịch bản dùng upstream của repo và tự đối chiếu health. Nếu có thay đổi mới khác ở upstream, review phạm vi trước khi chạy. Phải thấy phiên bản khớp mã nguồn và cổng Caddy không bị bỏ qua.

```bash
bash /opt/nmprp/app/deploy/rocky/cap-nhat.sh
```

**ROCKY — dừng worker một lần khi đã xác nhận không còn lượt suy luận chưa đối soát.** Đây là thao tác triển khai, không phải phép chẩn đoán để lặp lại.

```bash
sudo systemctl stop hermes-nmprp-may-chay
```

**ROCKY — cập nhật worker.** Repo phải ở nhánh được phê duyệt, upstream đã chứa bản vá. Phải pull fast-forward thành công; lỗi thì dừng, không ghi đè local changes.

```bash
git -C /home/rocky/hermes-platform pull --ff-only
```

**ROCKY — sao lưu riêng skill/SOUL/checksum trước khi thay.** Không đưa config/credential vào Git hoặc chat. Phải tạo archive đọc được; đây là profile backup, không phải backup DB.

```bash
bash -o pipefail -c 'umask 077 && mkdir -p /home/rocky/hermes-backups && docker exec -u hermes -w /opt/data/profiles/nmprp-stages hermes-platform-agent tar -cf - SOUL.md skills PROFILE_SHA256SUMS > /home/rocky/hermes-backups/nmprp-stages-truoc-m0-$(date +%Y%m%d-%H%M%S).tar'
```

**ROCKY — kiểm các archive vừa tạo.** Phải liệt kê được SOUL/skills/checksum; không tiếp tục nếu archive lỗi.

```bash
bash -c 'for f in /home/rocky/hermes-backups/nmprp-stages-truoc-m0-*.tar; do tar -tf "$f" >/dev/null || exit 1; done'
```

**ROCKY — cài đúng nội dung profile từ commit đã duyệt.** Không chuyển config.yaml, .env, sessions hoặc auth. Phải chép đủ SOUL/skills/checksum. M1 không đổi.

```bash
bash -o pipefail -c 'git -C /home/rocky/hermes-platform archive HEAD:hermes/profiles/nmprp-stages SOUL.md skills PROFILE_SHA256SUMS | docker exec -i -u hermes hermes-platform-agent tar -xf - -C /opt/data/profiles/nmprp-stages'
```

**ROCKY — checksum.** Phải tất cả OK.

```bash
docker exec -u hermes -w /opt/data/profiles/nmprp-stages hermes-platform-agent sha256sum -c PROFILE_SHA256SUMS
```

**ROCKY — readiness.** Với env đã bật bốn stage, phải có đủ bốn capability. Không bật thêm stage tự động nếu env trước đó chỉ cho phép một phần. Readiness không thay canary provider.

```bash
bash -c 'cd /home/rocky/hermes-platform && set -a && . /home/rocky/hermes-platform/deploy/rocky/nmprp-service.env && set +a && python3 -c "from support.nmprp_may_chay import CauHinh; from support.nmprp_stages import ready; print(ready(CauHinh.tu_moi_truong()))"'
```

**ROCKY — chỉ khởi động lại sau khi đã xử lý lượt cũ chưa đối soát và cấu hình thực tế.** Worker có thể nhận ngay lượt đang chờ, vì vậy chưa tạo lượt cả chương. Phải thấy service active và không có worker thứ hai.

```bash
sudo systemctl start hermes-nmprp-may-chay
```

**ROCKY — log.** Phải có số lô, mã PL2 hoặc mã lỗi an toàn khi có công việc; không chỉ dòng nhận lượt. Không mặc định đã thành công từ trạng thái active.

```bash
journalctl -u hermes-nmprp-may-chay --since "10 minutes ago" --no-pager -l
```

## D. Canary và pending

Sau khi so cấu hình và sửa theo bằng chứng: trên UI chọn M0 riêng, đúng một mã PL2, mẻ 1 và trần token nhỏ phù hợp. Không dùng cả 130 PL2 để thử. Canary đạt khi có lời gọi thực, usage hoặc nhãn ước tính rõ ràng, JSON hợp lệ, một bản phân rã lưu đúng endpoint M0 và trạng thái kết thúc đúng. Nếu thất bại, giữ journal và chỉ xử lý nguyên nhân được ghi; không restart lặp, không tạo key mới theo phỏng đoán.

`timeout` trả 124 chứng minh nhánh giới hạn đã kết thúc theo cơ chế tương ứng; host timeout, Docker lỗi, exit khác hoặc `.pending` cũ vẫn phải đối soát. Không tự xóa pending. Đối chiếu file usage, tiến trình container và log provider/phiên Hermes của chính call trước khi quyết định. Kết quả cache hợp lệ được dùng lại; input/profile khác fingerprint dừng để người vận hành xử lý.

Khi canary 1 PL2 đạt, thử lô 5 có giới hạn, kiểm heartbeat và chạy tiếp từ phần đã lưu; sau đó mới cân nhắc 10. Các test offline không chứng minh thời gian/chi phí hoặc chất lượng lâm sàng của model thật.

## E. Rollback

Giữ lại SHA cũ và archive profile trước triển khai. Nếu cần rollback, dừng worker ở điểm an toàn đã đối soát, phục hồi **mã worker và profile stage cùng phiên bản** từ SHA/archive đã ghi nhận. Không rollback schema, không xóa journal/usage/kết quả sản phẩm và không ghi đè credential. NMPRP rollback theo quy trình phát hành hiện hữu với phiên bản tương thích. Không coi rollback là cách làm mất `.pending` để gọi lại model.
