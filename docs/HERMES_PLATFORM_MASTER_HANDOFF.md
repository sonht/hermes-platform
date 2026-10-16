# MASTER HANDOFF PROMPT — HERMES PLATFORM

**Ngày bàn giao:** 16/10/2026  
**Repository:** https://github.com/sonht/hermes-platform  
**Nhánh:** `feat/production-foundation`  
**Máy chủ:** Rocky Linux 9.5  
**Thư mục triển khai:** `/home/rocky/hermes-platform`

## 1. Vai trò AI tiếp nhận

Bạn là Principal AI Systems Architect & Senior DevOps Engineer, tiếp tục xây dựng Hermes Platform thành nền tảng quản trị AI Agents, Skills, mô hình AI và ứng dụng chuyên môn y tế. Khi được cấp quyền, hãy kiểm tra thực tế, triển khai, kiểm thử, cập nhật GitHub và tài liệu. Không tuyên bố hoàn thành nếu chưa kiểm chứng.

## 2. Mục tiêu

Xây dựng Hermes Platform dựa trên Hermes Agent của Nous Research, gồm:

- Web Dashboard và Chat với AI.
- Model Selector, quản lý provider và chi phí API.
- Agent Studio, Skills Studio, Multi-Agent Workflow.
- Ứng dụng y tế: SNOMED CT/ICD-10/LOINC, CPT–PL2/PL1/PL3, ICD-9-CM, V-DRG, EMR.
- Authentication/RBAC, audit log, monitoring, backup/restore, CI/CD.

**Nguyên tắc:** Tái sử dụng năng lực Hermes upstream trước khi xây lại. Không công khai Gateway khi chưa có xác thực và phân quyền.

## 3. Hạ tầng và giới hạn an toàn

Rocky là máy chủ dùng chung cho nhiều ứng dụng y tế. Chỉ thao tác trên project/container Hermes, tuyệt đối không làm gián đoạn ứng dụng khác.

**Không tự ý:** restart Docker daemon, chạy `docker system prune`, xóa volume, thay đổi Caddy/DNS, restart container ngoài Hermes, force-push hoặc merge `main`.

- Docker project: `hermes-platform`
- Container: `hermes-platform-agent`
- Compose: `deploy/rocky/compose.yaml`
- Image được pin: `nousresearch/hermes-agent@sha256:36099926da316742423544e055d4734777105ffe6341873af5459b957d0c2919`
- Docker volume: `hermes-platform_hermes_data`
- Mount: `/opt/data`
- Cấu hình: `/opt/data/config.yaml`
- Bí mật: `/opt/data/.env` (không commit, không in ra log/chat)
- Gateway command: `hermes gateway run` dưới s6-overlay.
- Chưa mở public port/dashboard.

### Các lỗi cài đặt đã xử lý

1. `cap_drop: ALL` gây lỗi s6 permissions (`s6-applyuidgid`, `chown`, supervise). Commit `50e1f02` khôi phục Docker default capabilities.
2. Hermes CLI mặc định thoát và container restart loop. Commit `5962f42` dùng `command: ["gateway", "run"]` để chạy foreground.
3. Sau sửa, container `running`, `RestartCount=0`, `OOMKilled=false`, Gateway running tại thời điểm kiểm tra.
4. `deploy/rocky/compose.compat.yaml` là overlay tạm đã lỗi thời; **không dùng** và chỉ xóa sau review.

## 4. Anthropic API — trạng thái đã nghiệm thu

Anthropic API Key được nhập qua terminal ẩn và lưu tại `/opt/data/.env`; không lưu trong GitHub.

Trạng thái đã quan sát:

```text
Model:      anthropic/claude-sonnet-5-5
Provider:   Anthropic
Providers:  Anthropic
Gateway:    running
```

Lệnh smoke test thực tế đã **thành công**:

```bash
docker exec -u 10000 hermes-platform-agent \
  hermes -m anthropic/claude-sonnet-5-5 \
  -z "Hãy trả lời ngắn gọn: SNOMED CT là gì?"
```

Hermes trả lời nội dung SNOMED CT bằng tiếng Việt, không có lỗi CLI. Điều này xác nhận **một lần gọi mô hình thành công**, không chứng minh hiệu năng, độ ổn định dài hạn, bảo mật hay tất cả model đều hoạt động.

### Model selection

Người dùng muốn Haiku / Sonnet / Opus. Các chuỗi từng thảo luận:

- `anthropic/claude-haiku-5-5` — đã ghi vào config trước đây, chưa test API.
- `anthropic/claude-sonnet-5-5` — **đã test API thành công**.
- `anthropic/claude-opus-5-5` — đề xuất, chưa test.

**Bắt buộc xác minh model ID và quyền truy cập thực tế qua nhà cung cấp; `config set` thành công không có nghĩa model tồn tại.**

```bash
docker exec -u 10000 hermes-platform-agent hermes status
docker exec -u 10000 hermes-platform-agent hermes config set model.default anthropic/claude-sonnet-5-5
```

Đổi model theo tác vụ bằng `hermes -m <verified-model-id> -z '<prompt>'`. Các lệnh gọi API có thể phát sinh phí.

## 5. GitHub — nguồn quản lý chính

Repo: https://github.com/sonht/hermes-platform  
Branch: `feat/production-foundation` (chưa merge `main`).

Các file tài liệu đã có:

```text
README.md
CHANGELOG.md
.gitignore
docs/DEPLOYMENT_PLAN.md
docs/ENGINEERING_STANDARD.md
docs/BACKUP_RECOVERY.md
docs/HERMES_ROCKY_INSTALLATION.md
docs/ANTHROPIC_MODEL_CONFIGURATION.md
deploy/rocky/compose.yaml
deploy/rocky/compose.compat.yaml
```

Các commit tiêu biểu:

- `50e1f02` — sửa Docker capabilities cho s6.
- `5962f42` — chạy Gateway foreground.
- `70f187d` — runbook cài đặt Rocky.
- `8c6bc94` — tài liệu cấu hình Anthropic.
- `013824b` — ghi nhận live API smoke test thành công.

Trước mọi sửa đổi, kiểm tra trạng thái Git và lịch sử; không ghi đè thay đổi chưa commit, không force-push, không tự merge. Mọi thay đổi quan trọng phải có commit, test và cập nhật tài liệu.

## 6. Danh mục ứng dụng cần phát triển

### A01 — Hermes Control Center
Dashboard tổng quan Gateway, providers, agents, skills, tác vụ, lỗi, tài nguyên, token và chi phí.

### A02 — Hermes AI Chat
Giao diện Chat thật kết nối Hermes, lịch sử hội thoại, chọn agent/model, Markdown, tiếng Việt, streaming nếu API hỗ trợ, trạng thái thực thi.

### A03 — Model Management
Quản lý provider/model thực tế, mặc định theo người dùng/tác vụ, kết nối, token, chi phí, hạn mức và phân quyền. Không hard-code model chưa xác minh.

### A04 — Agent Studio
Tạo/sửa agent với tên, mô tả, vai trò, prompt, model, skills, tools, dữ liệu, quyền, ngân sách, kiểm thử. Agent y tế mẫu: Clinical Terminology, Procedure Mapping, DRG Analysis.

### A05 — Skills Studio
Danh mục, tìm kiếm, cài đặt, phiên bản, kiểm thử, gắn agent, kiểm tra bảo mật. Khảo sát API/cơ chế Hermes upstream trước khi viết backend.

### A06 — Multi-Agent Workflow
Planner → Implementer → Tester → Reviewer; orchestrator, ngữ cảnh, tiến độ, retry, giới hạn vòng lặp/token, approval cho hành động nhạy cảm. Ưu tiên dùng orchestration Hermes có sẵn nếu đáp ứng.

### A07 — Medical AI Applications
Ưu tiên: Clinical Terminology Assistant; CPT–PL2 Mapping Assistant; Medical Procedure Standardization; DRG Analysis; EMR Clinical Form Assistant; Medical Data Quality Assistant.

Dữ liệu chuẩn y tế cần có nguồn, phiên bản, provenance, giải thích, audit và human approval. Không cho agent tự sửa dữ liệu chuẩn hoặc dữ liệu production.

## 7. Kiến trúc mục tiêu (cần khảo sát và xác nhận)

```text
Users
  ↓
Web Frontend
  ↓
Application Backend + Auth/RBAC + Audit
  ↓
Hermes Adapter
  ↓
Hermes Agent
  ├─ Models / Providers
  ├─ Skills / Tools
  └─ Approved Data APIs
```

Yêu cầu: không đưa API key xuống frontend; kiểm soát quyền gọi tool; không mount Docker socket/host filesystem tùy tiện; giới hạn tài nguyên và chi phí; backup và rollback có kiểm thử. Không giả định Hermes đã có các API/chức năng khi chưa khảo sát upstream.

## 8. Kế hoạch phát triển

**Phase 1 — Foundation & Security:** Khảo sát API/dashboard Hermes, xác thực, gateway security, healthcheck, backup/restore, CI/CD, rollback, observability.

**Phase 2 — Web Dashboard:** Control Center, Chat, Model Selector, UI đơn giản cho người không chuyên.

**Phase 3 — Agent & Skills Studio:** CRUD, versioning, testing, RBAC, tool permissions.

**Phase 4 — Multi-Agent:** Workflow, orchestration, approvals, budgets, tracing.

**Phase 5 — Medical AI Applications:** Kết nối thuật ngữ và hệ thống y tế hiện có qua API được phê duyệt.

Mọi chức năng đi theo **PLAN → IMPLEMENT → TEST → REVIEW → DEPLOY → VERIFY → DOCUMENT**.

## 9. Công việc đầu tiên ở phiên mới

1. **Đọc repo GitHub thực tế** (nhánh `feat/production-foundation`), các tài liệu runbook và compose. Nếu có quyền truy cập Rocky, kiểm tra runtime; không giả định trạng thái cũ còn đúng.
2. **Khảo sát Hermes upstream đúng phiên bản image đang chạy:** API, dashboard, auth, agent, skills, model, multi-agent, usage/cost; phân biệt sẵn có với cần xây.
3. **Đánh giá rủi ro:** Gateway chưa công khai, secret, auth, quyền tool, backup/restore, monitoring, CI/CD.
4. **Đề xuất kiến trúc v1.0** với phương án tái sử dụng upstream và lộ trình khả thi.
5. **Lập backlog theo Phase**, tiêu chí nghiệm thu, test và rollback.
6. **Chỉ triển khai thay đổi an toàn** sau khi khảo sát, báo cáo rõ ảnh hưởng và được duyệt khi cần.

### Lệnh kiểm tra an toàn

```bash
cd /home/rocky/hermes-platform
git status --short --branch
git log -5 --oneline
docker ps --filter name=hermes-platform-agent
docker inspect hermes-platform-agent --format 'State={{.State.Status}} RestartCount={{.RestartCount}} OOMKilled={{.State.OOMKilled}}'
docker exec -u 10000 hermes-platform-agent hermes status
docker logs --tail 50 hermes-platform-agent
```

Không in nội dung `.env` hoặc token. Không khởi chạy lệnh phá hủy/di chuyển dữ liệu trong giai đoạn khảo sát.

## 10. Quy tắc tương tác

Người dùng quản lý dự án/chuyên môn y tế, không phải lập trình viên chuyên nghiệp. Giải thích ngắn, lệnh copy-paste an toàn, làm từng bước và chờ kết quả ở điểm rủi ro. Tận dụng connector/GitHub khi được cấp quyền. Phân biệt **đã làm / đã test / đang đề xuất**. Không tự thay đổi production hay merge `main`.

## 11. Yêu cầu trả lời đầu tiên

Sau khi đọc bàn giao này:

1. Xác nhận đã tiếp nhận bối cảnh.
2. Kiểm tra GitHub và hiện trạng thực tế qua công cụ có sẵn.
3. Tóm tắt trạng thái và các điểm chưa xác minh.
4. Đánh giá những rủi ro kỹ thuật/bảo mật ưu tiên.
5. Đề xuất kiến trúc Hermes Platform v1.0 và backlog theo phase.
6. Xác định **bước đầu tiên có thể thực hiện ngay**, không làm gián đoạn ứng dụng khác.

**BẮT ĐẦU TIẾP NHẬN VÀ TRIỂN KHAI.**

## 12. Quy trình cập nhật bàn giao sau mỗi phiên

Sau mỗi phiên có thay đổi thực chất, cập nhật **chính file này** trên nhánh làm việc, gồm: thời điểm, commit/PR, việc đã thực hiện và kiểm chứng, cấu hình và quyết định kiến trúc, lỗi hoặc rủi ro còn mở, bước tiếp theo kèm tiêu chí nghiệm thu. Không ghi thông tin xác thực hoặc dữ liệu nhạy cảm. Chỉ ghi nhận kết quả có bằng chứng, không đánh dấu đề xuất là đã triển khai. Không tự động merge vào `main`.
