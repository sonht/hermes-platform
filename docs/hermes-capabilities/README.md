# Bàn giao Hermes capabilities — 24/10/2026

Đã sửa và kiểm tích hợp local; **chưa hoàn tất nghiệm thu runtime/model Rocky/P0–P6**. Không merge hoặc triển khai production.

- [Nguyên nhân và bằng chứng](ROOT_CAUSE.md)
- [Ma trận bốn năng lực](CAPABILITY_MATRIX.md)
- [Thay đổi, nhánh và commit](CHANGES.md)
- [Báo cáo kiểm thử T0–T11](TEST_REPORT.md)
- [Runbook Rocky, staging và rollback](DEPLOY_ROCKY_RUNBOOK.md)
- [Blockers và giới hạn](OPEN_ISSUES.md)

Hai repo dùng checkout có sẵn trong `/workspace`, nhánh `viec/hermes-worker-capabilities`. Không tạo worktree. Dữ liệu nguồn, M1 và QG-16 được bảo toàn. Thư mục `evidence` chứa kết quả local có ghi rõ phạm vi, không phải dữ liệu production hay chứng nhận chuyên môn.
