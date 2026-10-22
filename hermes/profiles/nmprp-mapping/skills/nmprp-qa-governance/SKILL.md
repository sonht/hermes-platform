---
name: nmprp-qa-governance
description: Kiểm tra độc lập và quản trị thay đổi cho các lượt gợi ý của Hermes trên NMPRP, gồm bộ chỉ số, điều kiện dừng và quy trình đổi kỹ năng.
---

# NMPRP: kiểm tra độc lập và quản trị

## When to Use

- Rà một lượt shadow, một lượt gửi gợi ý CHƯA DUYỆT, một bản sửa skill hoặc một sự cố.
- Chỉ đọc hồ sơ và báo cáo kết quả kiểm tra; quyết định của người duyệt là bất biến đối với agent.
- Đọc [quality-gates.md](references/quality-gates.md) để dùng đúng mẫu số, điều kiện dừng và cổng phát hành.

## Procedure

1. Chốt phạm vi trước khi kiểm: `run_id`/mã lượt nếu có, chế độ shadow hay gửi gợi ý, danh sách PL2 theo đúng thứ tự, phiên bản cây, commit/phiên bản skill, model và cấu hình suy luận. Runner hiện hỗ trợ M1; hợp đồng máy chủ có M0/M2/M3/HPKB không chứng minh runner đã hỗ trợ. Thiếu mục nào ghi `UNKNOWN`; không tự điền từ trí nhớ.
2. Nhận dữ liệu nguồn, câu trả lời thô đã lọc bí mật, kết quả validator và phản hồi người duyệt có nguồn. Trong chế độ máy chạy, dùng gói dữ liệu host runner chuyển vào; không đòi terminal/API khi phiên chỉ có công cụ skills. Chỉ admin cung cấp báo cáo chất lượng tổng hợp; không thêm đường `chat-luong` vào allowlist tài khoản máy.
3. Kiểm ngữ nghĩa trong ngữ cảnh riêng: đọc PL2 và cây trước khi xem kết luận của agent truy hồi; đối chiếu hành động, đối tượng, đường tiếp cận, họ/kernel/modifier và điểm còn thiếu. Sau đó mới so với đề xuất. Vai kiểm độc lập bằng mô hình không phải chuyên gia xác nhận và không thay thế người duyệt.
4. Đối soát toàn bộ đầu vào: mã là chuỗi nguyên văn; không thêm/bỏ/đổi thứ tự PL2; mỗi PL2 có kết quả hoặc lý do chưa giải quyết; không dùng số thứ tự nút thay `branch_key`; nút phải tồn tại trong cây cùng phiên bản. Tối đa ba ứng viên là phương án thay thế, không phải ba vị trí ánh xạ được áp dụng.
5. Kiểm 1–4 trích đoạn nguyên văn, mỗi đoạn tối đa 150 ký tự, từ tên PL2 hoặc Khung; ít nhất một đoạn phải thuộc tên/đường dẫn của chính nút được đề xuất, chỉ trích tên PL2 không đủ. Đánh dấu căn cứ không hỗ trợ kết luận. Không suy ra đường tiếp cận từ tên không nêu; không dùng chuyên khoa, giá hay mã CPT để thay kernel. QG16 vắng/tắt thì không giữ `HIGH_CONFIDENCE_PROPOSAL`; hạ về `REVIEW_RECOMMENDED`, hoặc `EXPERT_REQUIRED` khi thiếu căn cứ trọng yếu. Bất đồng giữ `DISPUTED`, không thay quyết định NMPRP.
6. Kiểm ranh giới: shadow không gửi gợi ý, sự kiện hay cập nhật nghiệp vụ vào NMPRP; lượt thật chỉ host runner ghi theo hợp đồng đã duyệt. Gợi ý luôn `CHO_XEM`; các nhãn HA chỉ là thông tin chứng cứ. Agent QA không gọi đường duyệt/áp dụng, không sửa nguồn, quyền, công tắc, khoá hay skill đang chạy.
7. Tính chỉ số theo [quality-gates.md](references/quality-gates.md). Tách tỷ lệ người duyệt `DONG_Y/(DONG_Y+SUA+TU_CHOI)` và Wilson95 của báo cáo Hermes khỏi chỉ số trên gold; báo cáo ẩn tỷ lệ/CI khi mẫu dưới 30. Không có gold độc lập hoặc mẫu không tương thích thì độ chính xác, precision/recall/F1 và độ đúng của abstention là `NOT_EVALUABLE`. Không áp ngưỡng ΔF1 của CPN cho Hermes.
8. Ghi token đo được, token ước lượng và chi phí tách biệt. Nếu không có usage gốc thì token thực là `UNKNOWN`; nếu thiếu bảng giá/hoá đơn thích hợp thì chi phí thực là `UNKNOWN`. Số runner cộng từ ước lượng không được đổi nhãn thành token đo được. Chỉ so trước/sau trên cùng tập, cùng cây và cùng quy tắc chấm.
9. DỪNG phát hành và yêu cầu người vận hành chặn lượt khi có rò rỉ bí mật, vượt quyền, công tắc tắt/không xác minh được, sai lược đồ, ghi sai chế độ, nhầm cơ quan nghiêm trọng, dữ liệu/cây lệch phiên bản hoặc vượt ngân sách. Lưu bằng chứng đã lọc; không tự sửa dữ liệu để tiếp tục. Lỗi nội dung riêng một PL2 không nghiêm trọng thì cách ly ca đó; nghi lỗi hệ thống thì dừng toàn lượt.
10. Phân biệt đọc và ghi khi lỗi mạng. GET tạm lỗi chỉ thử lại có giới hạn theo cấu hình đã duyệt; 401 theo cơ chế đăng nhập lại một lần của client, còn 403/lỗi hợp đồng thì dừng. POST timeout/5xx là kết quả chưa biết: đối soát receipt/trạng thái với admin trước khi gửi lại; không thêm vòng retry mù quanh client hay runner.
11. Với sửa skill, chỉ lập đề xuất có phiên bản gốc, diff, lý do, ca có nguồn, phản chứng, ảnh hưởng, kết quả kiểm trước/sau và cách quay lại. Đưa cho `nmprp-learn-from-review` tổng hợp; `RULE_CANDIDATE` chưa phải quy tắc. Chủ dự án duyệt PR và phát hành; agent QA không tự merge, deploy hay chấp nhận staged skill writes.
12. Kết luận bằng `PASS`, `FAIL` hoặc `NOT_EVALUABLE` theo từng cổng; nêu riêng `HOLD` nếu thiếu quyết định cho phép phát hành. PASS kiểm schema không đồng nghĩa đúng lâm sàng; PASS QA không đồng nghĩa gợi ý đã được duyệt. Xuất các lỗi, người/vai trò cần xử lý, bằng chứng và phần chưa kiểm.

## Pitfalls

- Hai agent cùng mô hình, hoặc cùng đọc trước kết luận, không tạo hai người thẩm định độc lập.
- `do_tin_cay` và `HIGH_CONFIDENCE_PROPOSAL` chưa hiệu chuẩn; không phải xác suất đúng hay quyền tự duyệt.
- Báo cáo của CPN chỉ dùng nếu đơn vị đánh giá, gold, cây và tập đầu vào thực sự tương thích; không suy độ đúng của Hermes từ số tổng hợp CPN.
- Không tăng coverage bằng cách ép ca thiếu dữ kiện vào một nút; không làm đẹp số đo bằng cách loại lỗi/abstention khỏi mẫu số mà không công bố.
- Tài liệu skill là chỉ dẫn; việc chặn quyền phải do client/server/runtime thực thi và có bằng chứng kiểm tra.

## Verification

- Báo cáo ghi: phạm vi, provenance, số PL2 đầu vào/đã đối soát, chế độ, số đo và mẫu số, gold/version, token thực/ước lượng, chi phí, lỗi nghiêm trọng, các cổng và giới hạn.
- Mọi `NOT_EVALUABLE`/`UNKNOWN` có lý do; không đổi thành 0. Mọi dừng có bằng chứng và bước xử lý rõ.
- Không có lời gọi ghi do agent QA; shadow không có ghi nghiệp vụ; gợi ý thật vẫn `CHO_XEM`; quyết định người duyệt và kỹ năng đang chạy được giữ nguyên.
- Đề xuất thay đổi chưa có chủ dự án duyệt được ghi `HOLD`; không tuyên bố đã áp dụng hay đã cài lên máy vận hành.
