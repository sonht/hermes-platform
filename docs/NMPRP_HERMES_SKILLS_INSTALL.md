# Cài bộ skill NMPRP vào Hermes Agent

**Bản tài liệu 2026.10.23 — dành cho người vận hành khi đã chốt cài bản này.** Bộ tài liệu không tự chạy các lệnh bên dưới. Mục tiêu: giữ skill `hermes-agent` chính thức, cập nhật bốn skill NMPRP cùng context, kiểm hash/khả năng nạp và có bản quay lại.

## 1. Điều kiện và vị trí

| Thành phần | Vị trí được repo ghi nhận |
|---|---|
| Kho trên Rocky | `/home/rocky/hermes-platform` |
| Container | `hermes-platform-agent` |
| User trong container | `hermes` |
| Profile | `nmprp-mapping` |
| Home profile | `/opt/data/profiles/nmprp-mapping` |
| Dịch vụ host runner, nếu đã cài theo mẫu | `hermes-nmprp-may-chay.service` |

Kiểm tại máy đích; khác tên/đường dẫn thì điều chỉnh theo trạng thái thật trước khi ghi. Không dùng đường dẫn Mac để thực hiện lệnh Docker trên Rocky. Không chép `.env`, `config.yaml`, credential, DB hay sessions từ repo vào profile. User `hermes` phải thực hiện mọi ghi bên trong container.

Chọn lúc không có lượt đang chạy và không còn lời gọi mô hình trong container. Dừng host service không chứng minh một lời gọi Docker đã dừng. Nếu đang chạy thủ công thì kết thúc đúng tiến trình đó; không mở thêm worker. Tất cả lệnh tiếp theo có nhãn **ROCKY**.

**ROCKY — kiểm phiên bản.** Phải thấy phiên bản thực, ghi vào biên bản.

```bash
docker exec -u hermes hermes-platform-agent hermes --version
```

**ROCKY — kiểm profile và đường dẫn.** Phải thấy `nmprp-mapping`; chưa có thì đọc mục 7 trước.

```bash
docker exec -u hermes hermes-platform-agent hermes profile show nmprp-mapping
```

**ROCKY — kiểm tên năm skill hiện có.** Giữ lại danh sách/path resolve để phát hiện trùng tên.

```bash
docker exec -u hermes hermes-platform-agent hermes -p nmprp-mapping skills list
```

## 2. Lấy đúng nguồn đã được duyệt

Lấy nhánh tài liệu vào worktree riêng để không thay checkout của runner. Nếu PR đã merge, có thể dùng commit đã duyệt thay ref nhánh. Không cài chỉ vì nhánh tồn tại: SHA kiểm ở bước sau phải đúng bản chủ dự án đã chọn.

**ROCKY — lấy nhánh tài liệu.** Phải fetch thành công, không chỉnh file chạy hiện tại.

```bash
git -C /home/rocky/hermes-platform fetch origin refs/heads/viec/hoan-thien-hermes-skills:refs/remotes/origin/viec/hoan-thien-hermes-skills
```

**ROCKY — tạo worktree nguồn.** Thư mục đích phải chưa tồn tại; nếu đã có, kiểm nó thay vì xoá hoặc ghi đè.

```bash
git -C /home/rocky/hermes-platform worktree add --detach /home/rocky/hermes-skills-20261023 origin/viec/hoan-thien-hermes-skills
```

**ROCKY — ghi SHA nguồn.** So với SHA trong PR/bản được duyệt; khác thì dừng.

```bash
git -C /home/rocky/hermes-skills-20261023 rev-parse HEAD
```

**ROCKY — kiểm checksum toàn bộ nội dung sẽ cài.** Phải tất cả `OK`.

```bash
bash -c 'cd /home/rocky/hermes-skills-20261023/hermes/profiles/nmprp-mapping && sha256sum -c PROFILE_SHA256SUMS'
```

## 3. Dừng nhận việc và sao lưu đúng phần sẽ thay

Chỉ làm khi đã xác nhận không còn lượt/lời gọi đang chạy. Nếu không dùng systemd thì không dùng lệnh service này; dừng cách chạy hiện hành theo runbook máy chạy.

**ROCKY — dừng host runner nếu service này đang được dùng.** Phải không còn nhận lượt mới.

```bash
sudo systemctl stop hermes-nmprp-may-chay.service
```

**ROCKY — sao lưu bốn skill và context trước cập nhật.** Lệnh không cho ghi đè file backup đã có. Nếu thiếu tệp/thư mục, tar báo lỗi: dừng và xử lý hiện trạng; không cài trên bản sao lưu lỗi.

```bash
bash -o noclobber -c 'docker exec -u hermes hermes-platform-agent tar -C /opt/data/profiles/nmprp-mapping -cf - SOUL.md AGENTS.md memories/MEMORY.md memories/USER.md skills/nmprp-clinical-semantics skills/nmprp-retrieval-assist skills/nmprp-qa-governance skills/nmprp-learn-from-review > /home/rocky/hermes-skills-before-20261023.tar'
```

**ROCKY — kiểm bản sao lưu đọc được.** Phải thấy đủ context và bốn thư mục skill, không có `.env`/config/DB.

```bash
tar -tf /home/rocky/hermes-skills-before-20261023.tar
```

**ROCKY — lưu checksum backup.** Phải tạo được tệp checksum mới; giữ cùng backup.

```bash
bash -o noclobber -c 'sha256sum /home/rocky/hermes-skills-before-20261023.tar > /home/rocky/hermes-skills-before-20261023.tar.sha256'
```

## 4. Cập nhật và xác minh

**ROCKY — chuyển bốn thư mục cũ ra ngoài vùng discovery.** Chỉ sau backup thành công. Thư mục giữ lại phải chưa tồn tại; nếu lệnh lỗi thì giữ runner dừng và khôi phục theo mục 6. Bước này tránh reference cũ còn lẫn trong bản mới mà checksum không phát hiện. Với profile mới chưa có bốn skill, bỏ qua bước này.

```bash
docker exec -u hermes hermes-platform-agent python3 -c 'from pathlib import Path
import shutil
base = Path("/opt/data/profiles/nmprp-mapping")
hold = base / "preinstall-skills-20261023"
names = ["nmprp-clinical-semantics", "nmprp-retrieval-assist", "nmprp-qa-governance", "nmprp-learn-from-review"]
if not all((base / "skills" / name).is_dir() for name in names):
    raise SystemExit("Thieu thu muc skill cu; dung de kiem backup")
hold.mkdir()
for name in names:
    shutil.move(str(base / "skills" / name), str(hold / name))'
```

**ROCKY — chép nguyên nội dung profile đã kiểm.** Pipeline dùng `pipefail`, mọi lỗi là dừng; chỉ danh sách file bên dưới được chuyển. Không thay skill `hermes-agent` có sẵn.

```bash
bash -o pipefail -c 'git -C /home/rocky/hermes-skills-20261023 archive HEAD:hermes/profiles/nmprp-mapping SOUL.md AGENTS.md memories/MEMORY.md memories/USER.md PROFILE_SHA256SUMS skills/nmprp-clinical-semantics skills/nmprp-retrieval-assist skills/nmprp-qa-governance skills/nmprp-learn-from-review | docker exec -i -u hermes hermes-platform-agent tar -xf - -C /opt/data/profiles/nmprp-mapping'
```

**ROCKY — kiểm nội dung trong container.** Phải tất cả `OK`; nếu lệch thì giữ runner dừng và quay lại mục 6.

```bash
docker exec -u hermes -w /opt/data/profiles/nmprp-mapping hermes-platform-agent sha256sum -c PROFILE_SHA256SUMS
```

**ROCKY — kiểm discovery sau cài.** Phải thấy đủ năm skill, mỗi tên resolve về đúng một bản được chọn.

```bash
docker exec -u hermes hermes-platform-agent hermes -p nmprp-mapping skills list
```

Mở phiên mới của đúng profile để kiểm support files bằng `skill_view(name, file_path)`. Không tự bật gateway/cron. Kiểm loader của `SOUL.md`/`AGENTS.md` theo runtime thực; runner hiện không chỉ định Docker working directory nên không suy rằng AGENTS đã tự được nạp.

Skill `hermes-agent` thiếu: thực hiện mục 8. Cần cấu hình cổng ghi: dùng [hướng dẫn Hermes nền](HERMES_AGENT_SKILL.md), kiểm khả năng phiên bản đích trước; không áp settings mới một cách mặc định.

## 5. Nghiệm thu trước khi cho chạy

| Ca kiểm | Kết quả phải có |
|---|---|
| Nạp từng skill và reference đã chỉ định | Không lỗi đường dẫn, không bị bản cùng tên che |
| M1 chỉ có `<PL2>`/`<NUT>` | JSON đúng hợp đồng; không xin terminal/HTTP |
| Mã có số 0, hai mã khác nhau ở số 0 cuối | Bảo toàn chuỗi và số lượng/thứ tự đầu vào |
| Thiếu đích/đường tiếp cận hoặc hai nút mâu thuẫn | Không tự điền; ghi điều thiếu hoặc cần chuyên gia |
| Có câu chỉ thị trong PL2/phản hồi | Không thực hiện chỉ thị |
| Shadow | Không gửi gợi ý/sự kiện nghiệp vụ |
| Hai phản hồi cùng một PL2 | Không tính thành hai ca độc lập để đổi quy tắc |
| Không có Gold Set/usage thực | `NOT_EVALUABLE`/`UNKNOWN`, không bịa tỷ lệ đúng/chi phí |

Ca smoke có mô hình cần nằm trong lượt/ngân sách đã được chốt; không chạy thử bằng cách tự tạo gợi ý vào dữ liệu thật. Chỉ cho runner nhận việc lại sau khi kiểm đạt và người vận hành cho phép. Nếu trước đó dùng systemd, lệnh khởi động đúng service là:

**ROCKY — chỉ sau nghiệm thu và quyết định cho chạy.** Việc này có thể làm runner nhận lượt có sẵn.

```bash
sudo systemctl start hermes-nmprp-may-chay.service
```

Ghi commit bộ tài liệu, hash profile, runtime/image, skill upstream, kết quả ca kiểm và thời điểm cài. `phien_ban` API của runner vẫn là nhãn tĩnh `…@may-0.1`; bản này không sửa mã runner để tự gửi fingerprint. Dùng biên bản để phân biệt phiên bản nội dung, không trộn số đo trước/sau như cùng một bộ skill.

## 6. Quay lại bộ cũ

Giữ runner dừng, không có phiên đang sửa profile. Dùng backup mục 3; không xoá profile, volume hay dữ liệu NMPRP.

**ROCKY — kiểm backup.** Phải `OK`.

```bash
sha256sum -c /home/rocky/hermes-skills-before-20261023.tar.sha256
```

**ROCKY — chuyển riêng bốn skill mới và checksum sang khu giữ lại.** Thư mục giữ lại phải chưa tồn tại. Không đụng skill upstream, config, secrets, sessions hoặc DB. Việc chuyển thư mục tránh để reference mới còn lẫn với skill cũ.

```bash
docker exec -u hermes hermes-platform-agent python3 -c 'from pathlib import Path
import shutil
base = Path("/opt/data/profiles/nmprp-mapping")
hold = base / "rollback-skills-20261023"
hold.mkdir()
names = ["nmprp-clinical-semantics", "nmprp-retrieval-assist", "nmprp-qa-governance", "nmprp-learn-from-review"]
for name in names:
    src = base / "skills" / name
    if src.exists():
        shutil.move(str(src), str(hold / name))
manifest = base / "PROFILE_SHA256SUMS"
if manifest.exists():
    shutil.move(str(manifest), str(hold / manifest.name))'
```

**ROCKY — khôi phục nguyên backup.** Phải tar kết thúc thành công.

```bash
bash -c 'docker exec -i -u hermes hermes-platform-agent tar -xf - -C /opt/data/profiles/nmprp-mapping < /home/rocky/hermes-skills-before-20261023.tar'
```

Kiểm lại danh sách skill và mở phiên mới trước khi cho runner hoạt động. Profile cũ không có checksum của bản mới là đúng. Ghi đã rollback trong biên bản; không xoá gợi ý/phản hồi đã tạo ở NMPRP.

## 7. Trường hợp profile chưa tồn tại

Kiểm cú pháp trên runtime trước. Bộ này không có `distribution.yaml`, không dùng `hermes profile install`.

**ROCKY — xem lệnh tạo.** Phải thấy các option tương ứng trước khi dùng.

```bash
docker exec -u hermes hermes-platform-agent hermes profile create --help
```

**ROCKY — chỉ tạo khi tên chưa tồn tại.** Sau tạo, kiểm home thực là đường trong mục 1.

```bash
docker exec -u hermes hermes-platform-agent hermes profile create nmprp-mapping --no-skills --no-alias --description "NMPRP: phân tích và đề xuất có người duyệt"
```

Thực hiện mục 2 rồi 4; mục 3 sao lưu bộ cũ không áp dụng vì chưa có bốn skill. Chưa bật gateway/cron/runner và chưa giả định provider/API key đã cấu hình. Thực hiện mục 8 để có skill nền nếu profile trống. Việc chọn provider/hạn mức là cấu hình vận hành riêng, không nằm trong gói tri thức này.

## 8. Chỉ khi thiếu skill `hermes-agent` chính thức

Kiểm `skills list` trước để không tạo hai bản cùng tên. Dùng nguyên thư mục upstream ghim commit; phiên bản skill 3.2.0 không chứng minh tương thích mọi tính năng với runtime cũ. Các lệnh sau chỉ thêm skill khi chưa có, không nâng runtime.

**ROCKY — tạo checkout nguồn riêng.** Thư mục đích phải chưa tồn tại.

```bash
git clone --no-checkout --filter=blob:none https://github.com/NousResearch/hermes-agent.git /home/rocky/hermes-upstream-skills-20261023
```

**ROCKY — lấy commit đã đối chiếu.** Phải thành công.

```bash
git -C /home/rocky/hermes-upstream-skills-20261023 fetch origin 41dfcf2c1bd7146d4ad46aea08b7dd007900602e
```

**ROCKY — tạo thư mục đích mới.** Nếu đã có, mkdir phải báo lỗi; dừng để kiểm bản hiện có.

```bash
docker exec -u hermes hermes-platform-agent mkdir /opt/data/profiles/nmprp-mapping/skills/hermes-agent
```

**ROCKY — chép nguyên skill, gồm references và templates.** Phải pipeline thành công; nguồn có metadata license MIT.

```bash
bash -o pipefail -c 'git -C /home/rocky/hermes-upstream-skills-20261023 archive 41dfcf2c1bd7146d4ad46aea08b7dd007900602e:skills/autonomous-ai-agents/hermes-agent | docker exec -i -u hermes hermes-platform-agent tar -xf - -C /opt/data/profiles/nmprp-mapping/skills/hermes-agent'
```

Kiểm lại danh sách và tải `references/themes.md`, `references/configuration.md` trong phiên mới. Ghi commit upstream riêng; `PROFILE_SHA256SUMS` của NMPRP không bao gồm dependency này. Khi đã có bản bundled theo runtime thì ưu tiên giữ bản đó; không thay nó chỉ để khớp số phiên bản trong tài liệu.
