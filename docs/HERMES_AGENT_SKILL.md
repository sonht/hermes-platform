# Skill `hermes-agent`: vận hành cùng bộ NMPRP

## Phạm vi và phiên bản

`hermes-agent` là skill chính thức của Nous Research, đúng mô tả “Use, configure, theme, extend, and orchestrate Hermes Agent.” Bộ NMPRP dùng skill này làm nền cùng bốn skill chuyên môn; không tạo bản rút gọn cùng tên để che bản chính thức.

Nguồn đã đối chiếu ngày 23/10/2026: [SKILL.md chính thức](https://github.com/NousResearch/hermes-agent/blob/41dfcf2c1bd7146d4ad46aea08b7dd007900602e/skills/autonomous-ai-agents/hermes-agent/SKILL.md), phiên bản **skill 3.2.0**, commit **`41dfcf2c1bd7146d4ad46aea08b7dd007900602e`**, giấy phép MIT. Giữ nguyên `references/` và `templates/` đi kèm; không chỉ chép `SKILL.md`.

Repo này ghi nhận Hermes **v0.22.2** trên Rocky. Các khả năng upstream nêu dưới đây chưa được chạy kiểm trên máy vận hành trong lần soạn này; phiên bản skill không phải phiên bản runtime. Kiểm `--help` và config hiện hành trước khi dùng. Tài liệu này không xác nhận đã nâng runtime, cài skill hay triển khai.

Profile đang dùng: **`nmprp-mapping`**; container: **`hermes-platform-agent`**; home của profile trong Docker: **`/opt/data/profiles/nmprp-mapping`**. Thư mục tương ứng trong repo: `hermes/profiles/nmprp-mapping/`.

## 1. Kiểm trước khi cài hoặc cập nhật

Chạy từ máy chủ có Docker; mọi thao tác trong container dùng user `hermes`, không để root tạo file mà runtime không đọc được. Không khởi động thêm gateway hoặc tiến trình cùng ghi profile chỉ để kiểm tài liệu.

```bash
docker exec -u hermes hermes-platform-agent hermes --version
```

```bash
docker exec -u hermes hermes-platform-agent hermes -p nmprp-mapping --help
```

```bash
docker exec -u hermes hermes-platform-agent hermes -p nmprp-mapping skills list
```

Đối chiếu đủ năm tên: `hermes-agent`, `nmprp-clinical-semantics`, `nmprp-retrieval-assist`, `nmprp-qa-governance`, `nmprp-learn-from-review`. Đếm thư mục không chứng minh cả năm skill đã nạp đúng. Kiểm `hermes-agent` có support files và không bị skill cùng tên ở project che mất.

Nếu thiếu skill chính thức, người vận hành lấy nguyên thư mục tại commit nêu trên vào một bản checkout đã kiểm, rồi cài/copy đúng profile theo hướng dẫn cài của repo. Kiểm license và mã băm, sao lưu bản hiện tại trước khi thay. Không dùng `reset --restore` nếu chưa xem phần sửa cục bộ; không mặc nhiên chạy `hermes update` để chữa một skill thiếu.

Thứ tự discovery ở upstream: project `.hermes/skills`/`.agents/skills` → profile-local → `skills.create_dir` → `skills.external_dirs`. Skill project cần trust; `external_dirs` không tạo quyền chỉ đọc. Trên v0.22.2 chỉ sử dụng các chế độ đã kiểm tại máy đích. Việc copy vào đúng profile là phương án đã có trong [README profile](../hermes/profiles/nmprp-mapping/README.md).

## 2. Sử dụng và phân vai

| Nhu cầu | Skill hoặc thành phần |
|---|---|
| Cấu hình Hermes, theme, mở rộng, điều phối | `hermes-agent`, tải reference đúng chủ đề |
| Phân tích hành động/đối tượng/tiếp cận, họ/kernel/modifier | `nmprp-clinical-semantics` |
| Tìm nút có căn cứ và tạo gợi ý CHƯA DUYỆT | `nmprp-retrieval-assist` |
| Kiểm độc lập, chỉ số và cổng phát hành | `nmprp-qa-governance` |
| Rút bài học, tạo đề xuất sửa skill | `nmprp-learn-from-review` |

Trong một phiên vận hành đã được mở, gọi skill rồi nêu việc cần làm:

```text
/hermes-agent
```

Hoặc tải skill kiểm tra hồ sơ QA:

```text
/nmprp-qa-governance
```

Lệnh slash tải hướng dẫn, không tự cấp quyền API hoặc biến một quyết định thành đã duyệt. Mở phiên mới sau cập nhật để xác minh phiên bản thật đang nạp.

Máy chạy hiện tại do `support/nmprp_may_chay.py` điều phối trên host, tái sử dụng `support/nmprp_shadow.py`. Lời gọi Hermes dùng `-p nmprp-mapping -t skills`, có `-s` để nạp skill và prompt dữ liệu. Trong phiên này, mô hình chỉ xử lý gói đầu vào và trả hợp đồng JSON; không xin terminal hoặc tự đăng nhập NMPRP.

Quyền người duyệt giữ nguyên: mỗi PL2 có một vị trí đích; ứng viên là phương án chờ chọn; gợi ý Hermes lưu `CHO_XEM`. QA hoặc “độ tin cậy cao” không thay quyền duyệt.

## 3. Cấu hình và kiểm soát tự sửa

Đặt settings ở config của đúng profile; dùng CLI `config set` sau khi kiểm cú pháp thay vì tự sửa YAML của gateway. Không dùng config của profile mặc định thay cho `nmprp-mapping`.

```bash
docker exec -u hermes hermes-platform-agent hermes -p nmprp-mapping config --help
```

Upstream tại commit đã chốt có ba thiết lập dưới đây. Đây là cấu hình đề nghị cho người vận hành sau kiểm tương thích v0.22.2; không phải bằng chứng chúng đã được đặt.

```bash
docker exec -u hermes hermes-platform-agent hermes -p nmprp-mapping config set skills.write_approval true
```

```bash
docker exec -u hermes hermes-platform-agent hermes -p nmprp-mapping config set curator.enabled false
```

```bash
docker exec -u hermes hermes-platform-agent hermes -p nmprp-mapping config set auxiliary.background_review.enabled false
```

`skills.write_approval` stage ghi qua `skill_manage`; không chặn ghi trực tiếp bằng shell/file tools. Tắt background review không tắt `/refine` thủ công. Pin curator chủ yếu chặn xoá/archive, vẫn có thể cho sửa nội dung. Không dùng các cơ chế này như bằng chứng skill hoàn toàn bất biến.

Trong phiên quản trị có hỗ trợ tính năng, người vận hành xem đề xuất đang chờ:

```text
/skills pending
```

Xem diff theo ID thật trả về:

```text
/skills diff <id>
```

Chỉ người có thẩm quyền quyết định apply/reject. `nmprp-learn-from-review` phải tạo bản đề xuất bên ngoài skill đang chạy, không tự duyệt staged write. Nếu runtime cũ chưa hỗ trợ cổng ghi, giữ skill phát hành ở vùng chỉ đọc bằng quyền OS/container và không mở công cụ sửa cho phiên ánh xạ.

## 4. Theme

Theme không ảnh hưởng ánh xạ; chỉ cấu hình khi có nhu cầu giao diện. Tải `references/themes.md` của skill chính thức, kiểm các lệnh mà runtime hỗ trợ.

```bash
docker exec -u hermes hermes-platform-agent hermes -p nmprp-mapping skin --help
```

Cú pháp upstream, cần thay placeholder bằng skin/key/màu thật trước khi thực hiện:

```text
docker exec -u hermes hermes-platform-agent hermes -p nmprp-mapping config set display.skin <name>
```

```text
docker exec -u hermes hermes-platform-agent hermes -p nmprp-mapping skin set <key> <hex>
```

Chỉnh active skin khi chỉ đổi màu; không tạo bản mới từ default làm mất palette đang dùng. Hiệu lực trên gateway/Desktop của v0.22.2 phải kiểm riêng.

## 5. Mở rộng kết nối

Skill chính thức có hướng dẫn MCP, plugin, tool, webhook và giao diện. Chỉ dùng phần cần cho tác vụ, kiểm nguồn và version trước khi cài phần mở rộng. Repo này hiện dùng REST client/host runner; chưa có bằng chứng NMPRP cung cấp MCP server. Không nhập REST base URL vào `mcp_servers.url` để giả lập MCP.

**Credential NMPRP thuộc host runner**, ở tệp ngoài Git `deploy/rocky/nmprp-service.env`, quyền theo runbook hiện hành; session token chỉ trong bộ nhớ client. Không chép tệp này, mật khẩu hoặc token vào container Hermes, profile, prompt, skill hay log. Khoá nhà cung cấp mô hình là lớp riêng; không dùng nó thay tài khoản dịch vụ NMPRP.

Mở rộng API phải sửa hợp đồng/client/server và kiểm quyền bằng PR riêng. Không mở `terminal`, MCP hoặc đường admin cho mô hình để vượt lỗi allowlist. Nếu triển khai MCP sau này, dùng tên tool thật từ server và allowlist tối thiểu; filter phía Hermes không thay quyền cưỡng chế ở NMPRP.

Tham chiếu: [API access](NMPRP_HERMES_API_ACCESS.md), [máy chạy](NMPRP_HERMES_MAY_CHAY.md), `support/nmprp_client.py`. Ưu tiên code và hợp đồng đã kiểm khi tài liệu cũ chưa cập nhật.

## 6. Điều phối và QA

`delegate_task` phù hợp phân tích ngắn khi runtime/công cụ đã cho phép; process/profile riêng phù hợp nhiệm vụ dài. Không thêm delegate hoặc worker chỉ vì skill nền mô tả tính năng. Luồng NMPRP hiện dùng một host runner có khoá; không mở process thứ hai cùng nhận lượt để tăng tốc.

QA nhận source và proposal artifact trong ngữ cảnh riêng, đọc nguồn trước khi xem kết luận; agent kiểm không phải người xác nhận. Phản hồi người duyệt chỉ thành bài học đề xuất; gold phải qua quy trình độc lập. Tách artifact đầu ra khỏi skill đang hoạt động.

Shadow chỉ đọc NMPRP và ghi kết quả cục bộ; không gửi gợi ý, sự kiện hay cập nhật nghiệp vụ. Host runner khi chạy thật chỉ ghi đường đã cho phép, gợi ý luôn chưa duyệt. POST mất phản hồi cần đối soát kết quả phía máy chủ, không lặp gửi mù.

Chưa có gold ghi `NOT_EVALUABLE`; chưa đo token/chi phí thực ghi `UNKNOWN`. Không lấy token ước lượng của runner làm usage đo được. Dừng khi sai schema, nhầm cơ quan nghiêm trọng, vượt quyền, bí mật lộ, công tắc tắt/không xác minh được hoặc mất kiểm soát ngân sách; người vận hành xử lý trước khi tiếp tục.

Profile là ranh giới trạng thái, không phải sandbox filesystem. Không chạy hai process cùng ghi một `HERMES_HOME`. Cơ chế cron/gateway phụ chưa kiểm trên Rocky phải giữ là chưa kiểm; không tạo lịch hay bật gateway từ hướng dẫn này.

## 7. Bằng chứng nghiệm thu

- Ghi runtime/image/commit thật, profile/container, mã băm skill và danh sách support files đã cài.
- Kiểm tên skill resolve đúng đường dẫn; thực hiện smoke task phù hợp chế độ, không ghi NMPRP khi kiểm shadow.
- Ghi cấu hình nào được runtime nhận, cổng ghi nào thật sự có hiệu lực và các quyền đã kiểm; không suy từ nội dung `SKILL.md`.
- Kiểm mã PL2, `branch_key`, schema, trích dẫn; ghi rõ phần chất lượng lâm sàng chưa đánh giá.
- Chủ dự án duyệt phát hành; đồng bộ profile và rollback theo runbook. Merge Git không chứng minh container đã cập nhật.

## Nguồn đối chiếu

Các link sau cố định cùng commit upstream để có thể kiểm lại; hướng dẫn CLI mới phải đối chiếu với runtime máy đích.

- [Creating Skills](https://github.com/NousResearch/hermes-agent/blob/41dfcf2c1bd7146d4ad46aea08b7dd007900602e/website/docs/developer-guide/creating-skills.md): định dạng và support files.
- [Skills System](https://github.com/NousResearch/hermes-agent/blob/41dfcf2c1bd7146d4ad46aea08b7dd007900602e/website/docs/user-guide/features/skills.md): discovery, ưu tiên, approval và cập nhật bundled skill.
- [Profiles](https://github.com/NousResearch/hermes-agent/blob/41dfcf2c1bd7146d4ad46aea08b7dd007900602e/website/docs/user-guide/profiles.md): `HERMES_HOME` và giới hạn cách ly.
- [Persistent Memory](https://github.com/NousResearch/hermes-agent/blob/41dfcf2c1bd7146d4ad46aea08b7dd007900602e/website/docs/user-guide/features/memory.md): background review.
- [Curator](https://github.com/NousResearch/hermes-agent/blob/41dfcf2c1bd7146d4ad46aea08b7dd007900602e/website/docs/user-guide/features/curator.md): pin và bảo trì.
- [MCP](https://github.com/NousResearch/hermes-agent/blob/41dfcf2c1bd7146d4ad46aea08b7dd007900602e/website/docs/user-guide/features/mcp.md): transport, tool filter và reload. Nội dung này cập nhật hơn một số reference bundled; không suy tính năng runtime cũ từ docs mới.
