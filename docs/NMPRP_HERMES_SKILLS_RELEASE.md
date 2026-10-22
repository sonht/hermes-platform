# Bàn giao bộ tài liệu skill Hermes — 2026.10.23

## Kết quả và phạm vi

Bộ tài liệu cho năm skill đã được hoàn thiện ở kho `hermes-platform`: giữ dependency `hermes-agent` chính thức; cập nhật bốn skill NMPRP, reference, mẫu đề xuất thay đổi, context profile, hướng dẫn cài và rollback. Không đổi client, runner, API, database, dữ liệu PL2 hoặc ánh xạ.

Đọc từ [mục lục profile](../hermes/profiles/nmprp-mapping/README.md), sau đó [hướng dẫn cài](NMPRP_HERMES_SKILLS_INSTALL.md). Skill nền có [hướng dẫn riêng](HERMES_AGENT_SKILL.md) cho sử dụng, cấu hình, theme, mở rộng và điều phối.

## 1. Mốc nguồn đã đối chiếu

| Nguồn | Mốc | Phạm vi dùng |
|---|---|---|
| [sonht/hermes-platform](https://github.com/sonht/hermes-platform/tree/ec42f1098c6a350026df92071a1df6b7b92ace8a) | `ec42f1098c6a350026df92071a1df6b7b92ace8a` | Profile gốc, client, prompt, validator, runner và bộ kiểm |
| [sonht/nmprp](https://github.com/sonht/nmprp/tree/0addd2d56676a215b8b9d92f9188f2c706cccacd) | `0addd2d56676a215b8b9d92f9188f2c706cccacd` | API máy chạy, phản hồi, QA, QG-16, năng lực server mới |
| [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent/tree/41dfcf2c1bd7146d4ad46aea08b7dd007900602e) | `41dfcf2c1bd7146d4ad46aea08b7dd007900602e` | Skill nền 3.2.0 và tài liệu cấu hình/skill/profile |

Các mốc này là nguồn đọc khi soạn; không khẳng định production đang chạy đúng các commit. Commit của **bộ tài liệu mới** lấy từ PR hoặc `git rev-parse HEAD`, còn `PROFILE_SHA256SUMS` xác minh nội dung profile. Phiên bản skill upstream 3.2.0 khác phiên bản runtime Hermes và khác nhãn `phien_ban` do runner gửi.

## 2. Nội dung từng skill

| Skill | Nội dung hoàn thiện | Tài liệu đi kèm |
|---|---|---|
| `hermes-agent` | Giữ nguyên skill chính thức; hướng dẫn dùng đúng profile, kiểm runtime, kiểm soát tự sửa, theme, MCP và điều phối | `docs/HERMES_AGENT_SKILL.md`; lấy nguyên references/templates từ upstream nếu cần cài |
| `nmprp-clinical-semantics` | Phân tích hành động, đích, đường tiếp cận, phương pháp, công nghệ, mục đích; nhãn chứng cứ; họ/kernel/modifier theo định nghĩa; điều kiện gộp/tách | `references/clinical-rules.md` |
| `nmprp-retrieval-assist` | Ba chế độ runner/shadow/tương tác; bảo toàn mã; chọn nút thật; JSON mô hình khác payload API; cổng QG-16; từ chối có lý do; chống gửi lại mù | `references/contracts.md`, `references/retrieval-rules.md` |
| `nmprp-learn-from-review` | Đọc phản hồi Hermes đúng endpoint; cursor/dấu vết; hai PL2 độc lập; phản chứng; đề xuất diff và kiểm chứng; không tự áp dụng | `references/review-contract.md`, `templates/change-proposal.md` |
| `nmprp-qa-governance` | Kiểm độc lập; mẫu số chỉ số; tách phản hồi khỏi gold; chi phí thực/ước lượng; điều kiện dừng; cổng phát hành | `references/quality-gates.md` |

Frontmatter bốn skill giữ `name`, `description` để tương thích hợp đồng kiểm của repo hiện có. Đây là lựa chọn của gói này, không khẳng định Hermes chỉ hỗ trợ hai trường; upstream còn có metadata/version/platforms.

`SOUL.md` thêm bất biến không tự sửa tri thức và hợp đồng M1. `AGENTS.md` phân biệt ghi trong lượt với legacy, phân vai năm skill và giới hạn khả năng thực. `MEMORY.md` bỏ số lượng/phiên bản/chương thí điểm thay đổi theo ngày, giữ quy ước bền vững. Không thay USER hoặc cấu hình bí mật.

## 3. Các sai lệch trong tài liệu cũ đã xử lý

| Điểm cũ | Hướng dẫn mới |
|---|---|
| Học từ candidates CPN-AI, đòi tên người duyệt | Dùng `/admin/hermes/phan-hoi`; API không trả tên người; dẫn `goi_y_id` + `luc` |
| Mô hình dễ xin terminal để tự kiểm AI trong M1 | Runner kiểm trước; mô hình chỉ trả JSON và không tự gọi HTTP |
| Chưa phân biệt `bang_chung` của mô hình với API | Mô hình trả mảng trích dẫn; runner tạo object chứa `muc_de_xuat`, `hang`, `trich` |
| Ghi gợi ý không tách luồng hàng đợi | Hàng đợi dùng đường theo `luot_id`; legacy không được dùng để né phạm vi |
| Không có nút vẫn dễ tạo gợi ý rỗng | Kết quả không có ứng viên vào `/ket-qua`; không bịa nhánh để qua `/goi-y` |
| Nói hai phản hồi là đủ học một quy tắc | Cần hai PL2 khác nhau, cùng nguyên nhân và nguồn; vẫn chỉ RULE_CANDIDATE |
| Áp ngưỡng CPN/F1 cho skill Hermes | Tách bộ đo theo tác vụ; ngưỡng phát hành Hermes cần chốt riêng |
| Số liệu cũ trong MEMORY thành bối cảnh mặc định | Lấy phạm vi, số lượng và tình trạng gold từ nguồn/lượt hiện tại |
| Skill tự mô tả khả năng là bằng chứng đã tích hợp | Có bảng client/server; M0/M2/M3/HPKB chưa nối trong runner ở mốc nguồn |
| Nhãn báo cáo có thể bị hiểu là mức gợi ý gửi API | Tách năm mức được API chấp nhận khỏi DISPUTED/RULE_CANDIDATE/PENDING_EXPERT_REVIEW |
| Helper phản hồi trả rỗng có thể che lỗi trong phong bì HTTP 200 | Đọc từng trang, kiểm `ok is True`, mảng phản hồi và cursor; không suy đọc đủ từ helper trả rỗng |
| Cài chồng có thể giữ reference cũ ngoài checksum | Sao lưu rồi chuyển bốn thư mục cũ ra ngoài discovery trước giải nén; rollback cũng chuyển thư mục trước khôi phục |

## 4. Bằng chứng kiểm trước bàn giao

| Kiểm tra | Kết quả | Giới hạn |
|---|---|---|
| Bộ kiểm của repo, `python3 -m unittest discover -s tests -q` | **206 tests — OK** | Offline, có HTTP localhost giả lập; không gọi NMPRP hoặc Hermes thật |
| Profile contract trong bộ kiểm | **10 tests — OK** | Frontmatter, thuật ngữ, ranh giới, giới hạn memory và mẫu bí mật/CPT |
| Checksum profile | **14/14 tệp — OK** | Gồm context và toàn bộ bốn thư mục skill; không gồm dependency upstream hoặc cấu hình bí mật |
| Liên kết nội bộ và cú pháp ví dụ | **Đạt** | Kiểm đường dẫn tài liệu, `bash -n`, parse Python nhúng và JSON; không thực thi lệnh Docker/cài đặt |
| Tình huống M1 bằng agent độc lập | **Đạt các bất biến đã thử** | Giữ hai mã khác số 0; chọn hành động/đích chính; bỏ qua chỉ thị trong dữ liệu; JSON đầy đủ |
| Tình huống học từ hai phản hồi cùng PL2 | **Không tạo RULE_CANDIDATE/patch, không tự sửa** | Chỉ tình huống kiểm, không phải phản hồi vận hành thực |
| Tình huống QA không gold/usage/version | **Không báo độ chính xác/chi phí; không PASS toàn lượt** | Mẫu nhỏ giữ số ca, ẩn tỷ lệ/CI; usage thực UNKNOWN |

Lần chạy trong sandbox hạn chế ban đầu không mở được socket localhost; bộ kiểm được chạy lại trong môi trường cho phép localhost và đạt. Log còn `ResourceWarning` về đóng file/socket từ bài kiểm hiện có; không có test failure ở lần hoàn tất. Không sửa runtime/tests chỉ để che cảnh báo.

Các fixture kiểm hành vi không được đưa vào danh mục, nhãn vàng hoặc ví dụ ánh xạ trong skill. Kiểm trên agent soạn tài liệu không thay kiểm loader và model thực trên Rocky. Không có kết luận rằng độ chính xác lâm sàng đã tăng.

## 5. Giới hạn phải chuyển tiếp cho người vận hành

1. **Chưa cài bộ mới lên Rocky trong lần bàn giao này.** Cần làm runbook và ghi bằng chứng nguồn/đích khớp hash.
2. Runtime v0.22.2 chỉ là ghi nhận cũ; chưa xác minh runtime/image đang chạy. Các config upstream mới phải kiểm trước khi đặt.
3. Máy chạy hiện gọi M1, chưa khai/nối đầy đủ cấu hình profile, fingerprint, bài học, HPKB và M0/M2/M3. Không thêm API tưởng tượng vào skill.
4. `PHIEN_BAN_GOI_Y` và nhãn shadow vẫn tĩnh; thay nội dung skill chưa làm API tự có hash mới. Biên bản cài phải giữ commit/checksum để tránh trộn kết quả; tự động hoá fingerprint là thay đổi runtime riêng.
5. Runner hiện không đặt working directory khi `docker exec`; chưa kiểm `AGENTS.md` được nạp trên máy đích. Các luật quan trọng có trong SOUL/skill, nhưng vẫn phải kiểm loader.
6. Hợp đồng skill yêu cầu kiểm công tắc trước lời gọi tiếp theo; mã runner hiện kiểm lúc bắt đầu lượt, còn ngân sách được kiểm từng lô. Không khẳng định tài liệu này đã làm công tắc cưỡng chế giữa mọi lời gọi. Khi cần dừng thật, người vận hành dùng cơ chế của runner/service và credential đúng quyền.
7. Quy tắc không tự sửa là hướng dẫn; quyền filesystem/tool/server mới thực thi ranh giới cứng. `skills.write_approval`, curator pin hay external_dirs không tự chặn mọi đường ghi.
8. Cài skill không tự cấp quyền, không tự duyệt gợi ý/bài học, không thay nhãn vàng và không triển khai ứng dụng NMPRP.

## 6. Nguồn hợp đồng cụ thể

- [Client và phản hồi](https://github.com/sonht/hermes-platform/blob/ec42f1098c6a350026df92071a1df6b7b92ace8a/support/nmprp_client.py): allowlist, AI switch, cursor, API convenience.
- [Prompt và validator M1](https://github.com/sonht/hermes-platform/blob/ec42f1098c6a350026df92071a1df6b7b92ace8a/support/nmprp_shadow.py): handles N…, JSON, trích dẫn, limits, shadow.
- [Runner M1](https://github.com/sonht/hermes-platform/blob/ec42f1098c6a350026df92071a1df6b7b92ace8a/support/nmprp_may_chay.py): orchestration, labels, ngân sách, khóa một worker.
- [API Hermes NMPRP](https://github.com/sonht/nmprp/blob/0addd2d56676a215b8b9d92f9188f2c706cccacd/backend/app/api/hermes_admin.py) và [gợi ý/phản hồi](https://github.com/sonht/nmprp/blob/0addd2d56676a215b8b9d92f9188f2c706cccacd/backend/app/registry/hermes_goi_y.py): trạng thái CHO_XEM, quyền, schema, chống trùng.
- [Báo cáo chất lượng](https://github.com/sonht/nmprp/blob/0addd2d56676a215b8b9d92f9188f2c706cccacd/backend/app/registry/hermes_chat_luong.py): acceptance, Wilson, cỡ mẫu, phân tầng.
- [Cổng QG-16](https://github.com/sonht/nmprp/blob/0addd2d56676a215b8b9d92f9188f2c706cccacd/backend/app/registry/hermes_qg16.py), [công cụ theo lượt](https://github.com/sonht/nmprp/blob/0addd2d56676a215b8b9d92f9188f2c706cccacd/backend/app/registry/hermes_cong_cu.py), [allowlist server](https://github.com/sonht/nmprp/blob/0addd2d56676a215b8b9d92f9188f2c706cccacd/backend/app/registry/hermes_may_allowlist.py): giới hạn năng lực/quyền phía máy chủ.
