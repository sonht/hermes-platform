# Gói «Hermes HA Profiles» v1 và v1.1 (DRAFT): nạp và đối chiếu

**Trạng thái: DRAFT – AWAITING OWNER APPROVAL.** Gói được nạp NGUYÊN VĂN vào `hermes/drafts/Hermes_HA_Profiles_v1/` để lưu nguồn gốc và để review.
**Chưa** đưa vào `hermes/profiles/nmprp-mapping/` (profile sẽ được cài), **chưa** cài lên Rocky, **chưa** đổi `SOUL.md`/`AGENTS.md`/`MEMORY.md`/kỹ năng đang có.

Nguồn: hai gói do chủ dự án cung cấp 17/10/2026:
- `Hermes_HA_Profiles_v1_DRAFT.zip` (SHA-256 `4832a28c41a3bbbe183de01b3178745505ea2f9009d768a3749740c595c92b78`, 11 tệp nội dung);
- `Hermes_HA_Profiles_with_Brain_Dump_v1_1_DRAFT.zip` (SHA-256 `9f88586fae3946eb371b64da4610a89701a9e3cb64d1d8298f834c5467473ef5`, 12 tệp nội dung). **Bản v1.1 thay thế v1:** so sánh từng tệp, chỉ khác `README.md` và có thêm `docs/NMPRP_BRAIN_DUMP_ANSWERS_v1_DRAFT.md`. Thư mục nạp ở `hermes/drafts/` là bản v1.1.
README của gói nói nó dựng từ ba nguồn: `CPN_AI_MO_TA_DU_AN_CHO_HERMES_AGENT.md` (17/10), `MASTER_PROMPT_V3_CHUAN_HOA_HO_KY_THUAT_PL2_CPT.md` và `NMPRP_CLAUDE_CODE_HANDOFF_20261011.zip` (handoff cũ 11/10).
Hai nguồn sau **chưa được đưa cho phiên này**, nên chưa đối chiếu được nội dung gốc của chúng.

## 1. Bố cục gói so với bố cục Hermes cài được
Tài liệu Hermes v0.22.2: một profile là một thư mục có `SOUL.md`, `memories/` (`MEMORY.md`, `USER.md`) và `skills/<tên>/SKILL.md` (frontmatter `name`, `description`).
Gói dùng tệp phẳng `profiles/nmprp/SKILL_*.md`, **không** đúng định dạng kỹ năng của Hermes, và không có `USER.md`. Muốn cài phải chuyển đổi (xem mục 4).

| Tệp trong gói | Vai trò | Tương ứng trong profile đang dùng |
|---|---|---|
| `SOUL.md`, `AGENTS.md`, `MEMORY.md` (gốc) | Luật chung cho mọi ứng dụng y tế | Chưa có tương đương; `SOUL.md` của nmprp-mapping hiện cụ thể cho NMPRP |
| `profiles/nmprp/SOUL.md`, `AGENTS.md`, `MEMORY.md` | Bối cảnh NMPRP | `hermes/profiles/nmprp-mapping/SOUL.md`, `AGENTS.md`, `memories/MEMORY.md` |
| `SKILL_RETRIEVAL_REVIEW.md` | Rà truy hồi/ánh xạ | Trùng một phần với `skills/nmprp-retrieval-assist` |
| `SKILL_CLINICAL_SEMANTICS.md` | Chuẩn hoá ngữ nghĩa lâm sàng, họ, kernel, modifier | Chưa có (mới) |
| `SKILL_QA_GOVERNANCE.md` | QA độc lập và quản trị thay đổi | Gần với `skills/nmprp-learn-from-review` |
| `docs/OWNER_DECISIONS_REQUIRED.md` | 10 điểm cần chủ dự án duyệt | Trùng và bổ sung cho Phần 3 của `docs/NMPRP_BRAIN_DUMP_DRAFT_v1.md` |
| `docs/NMPRP_BRAIN_DUMP_ANSWERS_v1_DRAFT.md` (chỉ có ở v1.1) | Trả lời 32 câu, gắn nhãn SOURCE / PROPOSAL / OWNER / DATA | Bản thứ hai của brain dump; xem mục 6 |

## 2. Chỗ LỆCH so với dữ liệu và quyết định đã xác minh (cần sửa trước khi nạp vào profile)
1. **`profiles/nmprp/SOUL.md`: «PL3 thuộc kiến trúc rộng hơn».** Sai theo NMPRP. Theo `CLAUDE.md` (bất biến 5) và `docs/doi-ten-pl3-pl2/KE_HOACH.md` của `sonht/nmprp`: **PL3 là tên cũ của PL2**
   (đổi 03/09/2026; không tạo thêm định danh `pl3`). Dữ liệu còn dấu vết: `PROCEDURE_ID` bắt đầu `PL3-PROC-…`; tham số API `kind=pl3` chỉ PL2.
   Phần đúng của dòng này: *không tạo định danh `pl3` mới trong tên hay schema CPN-AI.* Nhiều khả năng đây là hệ quả của handoff cũ 11/10 (trước hoặc ngay quanh lúc đổi tên); chưa kiểm chứng vì chưa có tệp đó.
2. **`profiles/nmprp/SOUL.md`: PL1 «nguồn liên hệ lịch sử/giá».** Thiếu: PL1 là **Phụ lục 1** (danh mục phẫu thuật, thủ thuật, mã theo TT23, giữ `BS_`), nguồn của phân loại PT/TT; giá là lớp ghép theo mã.
3. **Trạng thái không có ở NMPRP.** `SKILL_RETRIEVAL_REVIEW` dùng `NO_SAFE_MATCH`; `SKILL_CLINICAL_SEMANTICS` dùng `HIGH_CONFIDENCE_PROPOSAL`, `REVIEW_RECOMMENDED`, `EXPERT_REQUIRED`, `UNRESOLVED`.
   Hợp đồng A2 thực tế: `decision ∈ {MATCH, REJECT, ABSTAIN, EXPERT_REVIEW}`; A3: `{KEEP_CURRENT, PROPOSE_PRIMARY, UNPLACED, EXPERT_REVIEW}`; `review_status` mặc định `PENDING`.
   Bảng `hermes_goi_y` (PR nmprp#696) chỉ có `CHO_XEM`. Dùng các trạng thái mới thì phải sửa NMPRP và giao diện; trước mắt dùng giá trị hiện có.
4. **Phạm vi thí điểm khác với hướng đã chốt.** `profiles/nmprp/AGENTS.md`: «chỉ tích hợp thí điểm A2 trước», cắm «qua `call_text` như provider» hoặc điều phối API.
   Hướng chủ dự án chốt ngày 17/10 (PR hermes-platform#5): **B trước (Hermes điều phối ngoài), rồi C thí điểm shadow cho truy hồi có tác tử** ở các PL2 chưa có ứng viên. Hai hướng chưa thống nhất; gói tự ghi mục 7 trong `OWNER_DECISIONS_REQUIRED.md` là còn mở. Không ghi đè.
5. **Chỉ số QA** (`precision@1`, `recall@3`, `wrong-target rate`, …) trùng ý với đề xuất trước nhưng khác bộ đo sẵn có của NMPRP (`cpn_gold_do.py`: precision/recall/F1, coverage, abstain, lỗi nghiêm trọng, ngưỡng `NGUONG`).
   Đề nghị dùng đúng bộ đo của NMPRP (một bản cài đặt), chỉ thêm chỉ số chưa có nếu cần.
6. **«Retry tối đa ba lần theo cơ chế hiện có»** (`SKILL_QA_GOVERNANCE`): cơ chế hiện có là của NMPRP «Chạy hết» cho lỗi tạm; cấu hình thử lại của cron Hermes **chưa xác minh**.
7. **Quy tắc trích dẫn nguyên văn** của prompt A2 (evidence 1–4 đoạn, tối đa 150 ký tự, đúng chữ đúng dấu) **không có** trong gói; nên bổ sung khi chuyển thành kỹ năng.
8. **Công tắc AI.** Gói chỉ nhắc «công tắc tắt thì dừng» như luật chung. Thực tế Hermes gọi Claude API bằng khoá riêng nên công tắc của NMPRP **không tự chặn được Hermes**: kỹ năng phải gọi `ai_cong_tac_bat()` của client trước khi chạy (đã có ở PR hermes-platform#6, #7).

## 3. Điều gói làm tốt, nên giữ khi duyệt
- Phân lớp rõ: SOUL = nguyên tắc ổn định; AGENTS = hành vi; MEMORY = bối cảnh; nghiệp vụ nằm ở profile dự án; nguồn sự thật là tài liệu và CSDL.
- Chế độ `READ_ONLY` / `PROPOSE` / `REVIEW`, mặc định không tự APPROVE.
- Chống tiêm lệnh: dữ liệu nguồn, workbook, mã kỹ thuật là dữ liệu không đáng tin về chỉ dẫn.
- Tách `EXPLICIT` / `SUPPORTED_INFERENCE` / `UNKNOWN`; thiếu phương pháp thì `APPROACH_METHOD=UNKNOWN` (khớp quy tắc A2 hiện có).
- «Hai ca tương tự chỉ tạo giả thuyết» (khớp thiết kế vòng học có duyệt) và «nhiều vai trong một mô hình không bằng nhiều người kiểm chứng».
- Dặn dò nhận biết dữ liệu lỗi thời: `MEMORY` ghi snapshot 17/10 có thể cũ, kiểm chứng lại mỗi phiên.

## 4. Kế hoạch nạp (chờ chủ dự án duyệt)
1. Chủ dự án xác nhận các chỗ sửa ở mục 2 (đặc biệt 1, 2, 4).
2. Chuyển `SKILL_CLINICAL_SEMANTICS` và `SKILL_QA_GOVERNANCE` sang định dạng `skills/<tên>/SKILL.md` (frontmatter, When to Use / Procedure / Pitfalls / Verification), áp các sửa ở mục 2; gộp `SKILL_RETRIEVAL_REVIEW` vào `nmprp-retrieval-assist`.
3. Hợp nhất `SOUL.md`/`AGENTS.md`/`MEMORY.md` của gói với bản đang có theo hướng: SOUL ngắn (luật cứng); bối cảnh nghiệp vụ ở AGENTS và kỹ năng; MEMORY trong giới hạn ký tự.
4. Chạy `tests/test_hermes_profile_files.py` (giới hạn bộ nhớ, frontmatter, không bí mật, không mã CPT); bài mới phải kiểm ngược.
5. Chỉ sau đó mới nhờ phiên Claude trên Rocky cài, và chỉ sau khi xác minh `hermes profile --help` trên máy thật (mục 10 của `OWNER_DECISIONS_REQUIRED.md`).

## 5. Quyết định cần chủ dự án: hợp nhất danh sách
Mười điểm của gói (`hermes/drafts/Hermes_HA_Profiles_v1/docs/OWNER_DECISIONS_REQUIRED.md`) khớp với các mục NEEDS_OWNER_DECISION của `docs/NMPRP_BRAIN_DUMP_DRAFT_v1.md`
(người duyệt và xử lý bất đồng, ngưỡng, Bao gồm/Loại trừ, ngân sách, danh tính người duyệt, CPT, chế độ tích hợp, Gold Set, ca mẫu, kiểm tra cú pháp profile). Không có điểm nào mâu thuẫn; cần trả lời MỘT lần cho cả hai danh sách.

## 6. Brain dump có nhãn (v1.1) so với bản brain dump đã lưu
Hiện có **hai** bản trả lời 32 câu, đều DRAFT: (a) `docs/NMPRP_BRAIN_DUMP_DRAFT_v1.md` (bản chủ dự án dán ngày 17/10, nguyên văn) và (b) `hermes/drafts/Hermes_HA_Profiles_v1/docs/NMPRP_BRAIN_DUMP_ANSWERS_v1_DRAFT.md` (v1.1).
Bản (b) cẩn trọng hơn: từng ý gắn nhãn nguồn, không bịa ví dụ (câu 15–18 ghi `[DATA]`), nhận rõ `hermes pause` chưa xác minh (câu 27), chưa có hạn mức chi phí (câu 23), Gold Set = 0 (câu 22).
Các dữ kiện (b) trích từ tài liệu mô tả dự án ngày 17/10 (150 giây mỗi cú bấm, tối đa 30 nút truy hồi, 1.491 mô tả Bao gồm/Loại trừ, ΔF1 LOCKED ≥ +0,02, 300 PL2 và ≥ 40 mục LOCKED, thử lại 3 lần) **khớp** những gì tôi đã đọc ở `sonht/nmprp`.
Đề nghị: khi chủ dự án duyệt, lấy **(b) làm bản gốc** vì có nhãn nguồn; giữ (a) làm hồ sơ lịch sử. Không xoá bản nào khi chưa được chỉ định.

Chỗ (b) **vẫn cần sửa** (cùng loại lỗi với mục 2):
1. Câu 4 và phạm vi thuật ngữ: «PL1: danh mục lịch sử … không phải đầu ra đích»; «không đổi nhãn PL2 thành PL3». Hướng đổi tên thật là **PL3 → PL2** (PL3 là tên cũ của PL2); PL1 là **Phụ lục 1 (PT/TT, mã theo TT23)**.
2. Câu 1, 6, 18 dùng trạng thái `DISPUTED`, `RULE_CANDIDATE`, `PENDING_EXPERT_REVIEW`: **không có ở NMPRP**; giá trị thật là `PENDING` (review_status) và `EXPERT_REVIEW` (decision).
3. Câu 18 chỉ ghi bốn mã, chưa có tên. Dữ kiện từ `REF_PL2_CONSOLIDATED_PROCEDURE_REGISTRY.csv` (chương 6 «Nội tiết») đã nằm ở `docs/NMPRP_BRAIN_DUMP_DRAFT_v1.md` mục 2.3: 6.71 *Khám bàn chân người bệnh đái tháo đường*; 6.107 *Kỹ thuật truyền enzym*; 6.111 *Kỹ thuật truyền gen trị liệu*; 6.120 *Nạo vét hạch cổ trong ung thư tuyến giáp đã phẫu thuật* (cả bốn `Needs review`). Đây là dữ kiện, không phải đáp án.
4. Câu 21 dùng bộ chỉ số tự đặt (precision@1, recall@3, …) bên cạnh ngưỡng ΔF1 +0,02 của NMPRP; nên dùng đúng bộ đo `cpn_gold_do.py` (một bản cài đặt).
5. Câu 30 đề nghị giữ TẮT mã CPT «cho tới khi đánh giá pháp lý»; chủ dự án đã nói tự lo bản quyền CPT, nên cần xác nhận rõ chọn bật hay tắt cho giai đoạn thí điểm (công tắc `NMPRP_ALLOW_CPT` của client mặc định tắt).
6. Bảng O-09 «mặc định an toàn: shadow A2» khác hướng đã chốt ngày 17/10 (B trước, rồi C thí điểm shadow cho truy hồi có tác tử); xem mục 2.4.
