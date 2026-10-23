# Thay đổi để review — chưa release

Hai checkout có sẵn, cùng nhánh `viec/hermes-worker-capabilities`. Không tạo worktree, không reset, đã push nhánh riêng, chưa PR/merge/deploy. Gốc NMPRP `5c1f75598269953d4f51ef661f4ad257cfd0e631`; Hermes `d5b625aedc2c27309f31ed89e78178993dc40acc`. P0 chẩn đoán được commit trước sửa: Hermes `5bdd417`.

## NMPRP

- `backend/app/registry/hermes_nang_luc.py`: chỉ đọc readiness từng máy, TTL thực 180 giây; chọn capability + model + reasoning trên cùng máy. Dùng cho tạo M0/M2/M3 và kế hoạch chạy liền; kiểm cả chuỗi vẫn giữ khi chọn chạy liền.
- `hermes_m0_luot.py`, `hermes_m23_luot.py`, `hermes_chay_lien.py`: nối kiểm readiness mới. M3 thêm lựa chọn tường minh `de_xuat_ids`, `chay_lai`; thiếu tham số giữ hành vi cũ. Replay không lọc bỏ họ chỉ vì có gốc ở lượt trước; resume bỏ gốc đã ghi của chính lượt. Không đụng engine M1.
- `hermes_modifier_doc.py`: reader dictionary đã duyệt có trần, đúng máy/lượt M3; không dựng bảng, không ghi thuật ngữ, không chạy AI Studio.
- `api/hermes_admin.py`, `hermes_may_allowlist.py`: hai GET mới admin readiness và máy đọc dictionary; thêm hai field tùy chọn M3. Quyền/switch/ownership được test.
- `frontend/src/HermesChayLien.jsx`: tick M0 độc lập rõ ràng, POST đúng route; default Chạy liền giữ nghĩa. Readiness nhiều worker, refresh khi form mở.
- Tests mới readiness/HTTP quyền, test UI bấm→request; các bài ghim route liệt kê đúng route mới; một fixture thời gian được làm mới để không giả heartbeat từ tháng 2. Không hạ cổng để làm test xanh.
- `APP_VERSION` và mục đầu `VersionPanel.jsx`: **1.100.357**, ngày 24/10/2026. `frontend/public/so-do-ky-thuat.html`: endpoint 655→657 để sơ đồ khớp mã.

## Hermes platform

- `support/nmprp_stages.py`: dispatcher/QA/checkpoints cho M0, M2, M3; scope PL2/node/family, input hash, budget, cancel, no duplicate paid inference khi có result checkpoint. Đơn vị sai hợp đồng không tự XONG và không chặn các đơn vị độc lập khác.
- `support/nmprp_gd2.py`: adapter v2 riêng. GĐ1 dùng nguyên prompt và validator từ `nmprp_shadow`; GĐ2 đọc mô tả scoped, ghi hồ sơ/đối chiếu qua server trước gợi ý. Delivery marker xử lý restart giữa hai đường ghi.
- `support/nmprp_client.py`: allowlist hẹp và methods cho kết quả stage, mô tả nút, approved knowledge, input manifest, dictionary. Thân hello cũ giữ nguyên khi không dùng trường mới.
- `support/nmprp_may_chay.py`: dispatch trước M1 v1, hello/heartbeat có cap được probe, lỗi có mã an toàn. Worker version `nmprp-may-chay@0.2`. `_chay_luot` giữ nguyên từng byte.
- Profile **riêng** `hermes/profiles/nmprp-stages`: SOUL, bốn skill stage, checksum. Không sửa profile M1. Nạp bằng cơ chế CLI sẵn có; dynamic model tools/session/resume chưa được xác minh, nên dùng payload/reader adapters nhỏ, không tạo orchestrator thứ hai.
- `HERMES_RUNNER_STAGES` mặc định rỗng; `HERMES_RUNNER_STAGE_STATE` lưu journal. Env mẫu không có bí mật. Các capability chưa được bật ở runtime production.
- 10 unit tests mới, 5 cross-repo contract tests và 6 báo cáo + runbook.

Không migration mới. Không thay dependency/lockfile, nguồn CSV, dữ liệu duyệt, QG-16, mã A1–A6, engine M1 hoặc `nmprp_shadow.py`. Những phần đã có của thiết kế được tái dùng; không tuyên bố P0–P6 đã đạt khi còn canary/runtime/clinical blockers trong `OPEN_ISSUES.md`.

Cloud onboarding đã kiểm install/start lặp lại và lưu `install_script`, `start_skill` vào draft; không thay network policy, secret requirements hay repository membership. Chưa publish snapshot hoặc kiểm fresh task restoration.

## Commit bàn giao trên GitHub

- NMPRP: `d224fb1c` — readiness, M0 độc lập, reader M3, replay, tests, version 1.100.357.
- Hermes: `5bdd417` — P0 chẩn đoán trước sửa; `c66752d` — worker adapters, profile riêng, checkpoints và tests.
- Báo cáo/rulebook/evidence được commit riêng sau hai bản mã trên. SHA cuối xem `git log -1` của checkout; không ghi SHA tự tham chiếu vào chính commit.

Đã push nhánh `viec/hermes-worker-capabilities` vào cả hai remote GitHub. Không sửa `main`. GitHub từng chặn GH007; chỉ email tác giả/committer của các commit mới được đổi sang noreply đã dùng trong repo, nội dung mã giữ nguyên. Không dùng việc snapshot cloud đã lưu draft để khẳng định những commit này có thể fetch từ GitHub hoặc đã phục hồi được trong task mới.
