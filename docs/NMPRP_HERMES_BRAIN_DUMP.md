# NMPRP × Hermes Agent — Brain Dump: trả lời 32 câu hỏi

**Phiên bản:** v1.1 — 17/10/2026 (thống nhất với dữ liệu và quy ước của NMPRP)  
**Trạng thái:** các mục `[SOURCE]` đã đối chiếu; các mục `[PROPOSAL]` và `[OWNER]` **vẫn chờ chủ dự án duyệt** (xem bảng ở cuối). Không tự cài, không merge, không deploy.  
**Đích:** tài liệu dự án của `sonht/hermes-platform`; nội dung đã được chuyển vào profile `hermes/profiles/nmprp-mapping/` (xem cuối tài liệu).  
**Nhãn:** `[SOURCE]` xác nhận từ tài liệu; `[PROPOSAL]` đề xuất chưa duyệt; `[OWNER]` cần chủ dự án quyết; `[DATA]` cần kiểm tra dữ liệu gốc.

## Nguồn ưu tiên

1. `CPN_AI_MO_TA_DU_AN_CHO_HERMES_AGENT.md` (17/10/2026): trạng thái vận hành, kiến trúc, giới hạn an toàn.
2. `MASTER_PROMPT_V3_CHUAN_HOA_HO_KY_THUAT_PL2_CPT.md`: quy tắc ngữ nghĩa và kiểm chứng họ/kernel/biến thể.
3. `NMPRP_CLAUDE_CODE_HANDOFF_20261011.zip`: bàn giao lịch sử; không ghi đè nguồn mới hơn.
4. Gói «Hermes HA Profiles» v1 và v1.1: đã hợp nhất vào tài liệu này và vào profile `nmprp-mapping`; không phải cấu hình đã triển khai.

> **Phạm vi thuật ngữ:** Trong CPN-AI, PL2 là danh mục kỹ thuật đầu vào để ánh xạ sang **nút của khung CPT**; PL1 là Phụ lục 1. Chỉ có hai tên PL1 và PL2, không tạo định danh mới. Không xuất mã CPT qua API ngoài. Không đưa mật khẩu, token, API key, dữ liệu người bệnh vào prompt/log/memory. Không tự đặt mã chính thức.

## A. Thẩm quyền và người duyệt

### 1. ★ Ai duyệt, ai quyết khi bất đồng?
**[SOURCE]** AI chỉ đề xuất; `duyet` do admin hoặc chuyên gia có tác vụ `studio_cpt` và quyền chương thực hiện. Chỉ chủ dự án được thực hiện một số thao tác quản trị như cấp tác vụ, gán/duyệt nhãn vàng, bật công tắc AI. **[PROPOSAL]** Chuyên gia chuyên khoa duyệt nội dung, quản trị chuyên môn có thẩm quyền được chỉ định giải quyết bất đồng; trong lúc bất đồng, nhãn HA là `DISPUTED`; trạng thái NMPRP vẫn là chờ (`CHO_XEM` bên Hermes, `PENDING` bên NMPRP). **[OWNER]** Chỉ định danh sách người có thẩm quyền và cơ chế xử lý bất đồng; không tự cấp quyền mới.

### 2. ★ Ngưỡng tin cậy và số ứng viên?
**[SOURCE]** A1 xếp 1–3 vùng; truy hồi tất định tìm tối đa 30 nút ứng viên; A2 thẩm định từng cặp; độ tin cậy chưa hiệu chuẩn do Gold Set = 0. **[PROPOSAL]** Giao diện hiển thị tối đa 3 gợi ý xếp hạng mỗi PL2, giữ nguyên mọi ứng viên trong nhật ký để kiểm toán. Có thể thử ngưỡng 0,90 / 0,75 / 0,60 như mức *ưu tiên xem xét*, tuyệt đối không gọi là xác suất đúng hoặc điều kiện tự duyệt. **[OWNER]** Duyệt ngưỡng sau benchmark.

### 3. Không chắc thì sao?
**[SOURCE]** A2 có `MATCH`, `REJECT`, `ABSTAIN`, `EXPERT_REVIEW`; hợp đồng sai là `INVALID`; thiếu chứng cứ thì không `MATCH`. **[PROPOSAL]** Hợp đồng NMPRP trả `ABSTAIN` hoặc `EXPERT_REVIEW` kèm điều thiếu, nguồn cần kiểm và phương án nếu có; không ép chọn nút. Bên Hermes: không có nút đủ căn cứ thì nhãn HA là `NO_SAFE_MATCH`: **không gửi gợi ý**, chỉ ghi một sự kiện nêu mã PL2 và lý do.

## B. Thuật ngữ và quy ước

### 4. ★ PL1, PL2, nút, họ, kernel, modifier
**[SOURCE]** PL1: **Phụ lục 1**, danh mục kỹ thuật HIỆN HÀNH (mã theo TT23, giữ tiền tố `BS_`), hết hiệu lực 01/01/2028 khi PL2 có hiệu lực và thay thế PL1. PL1 **không phải danh mục giá**: danh mục giá hiện nay được cấp mã dựa trên PL1 (sau đó có tách gây mê, gây tê) nên dễ nhầm. PL1 không phải đầu ra đích của CPN-AI. **[SOURCE/PROPOSAL]** PL2: mã/tên kỹ thuật nguồn đang được chuẩn hóa và ánh xạ. Nút: vị trí phân loại của khung cây CPT, nhận diện bằng **khóa nhánh nguyên văn**, không dùng số thứ tự nút biến động. Họ: tập kỹ thuật có chung nguyên lý và tiêu chí bao gồm/loại trừ. Kernel: hạt nhân kỹ thuật, đặc biệt là hành động chính và đối tượng đích cùng các đặc điểm định danh. Modifier: thuộc tính biến thể không tự tạo ra một kernel khác, trừ khi thực sự thay đổi bản chất kỹ thuật.

### 5. Các từ viết tắt và phương pháp
**[PROPOSAL]** Xây từ điển có phiên bản cho nội soi, mổ mở, qua da, robot hỗ trợ, sinh thiết, dẫn lưu, cắt, bóc tách, tạo hình, chẩn đoán hình ảnh can thiệp; mỗi mục gồm dạng viết, đồng nghĩa được xác nhận, nghĩa lâm sàng và các trường hợp không tương đương. Không tự coi “nội soi” là “nội soi ổ bụng” hoặc “robot” là một hành động điều trị.

### 6. ★ PL2 không ghi phương pháp thì mặc định gì?
**[PROPOSAL]** `APPROACH_METHOD = UNKNOWN` (không mặc định mổ mở/nội soi/robot). Chỉ suy ra khi có nguồn xác thực; đánh dấu `EXPLICIT`, `SUPPORTED_INFERENCE` hoặc `UNKNOWN`. Thiếu phương pháp có tính quyết định thì chuyển chuyên gia.

### 7. Dùng “Bao gồm / Loại trừ” không?
**[SOURCE]** Có tùy chọn theo lượt; 1.491 dòng mô tả, phần “Loại trừ” chưa thẩm định. Prompt A2 v1.3 có chế độ đọc mô tả, không được âm thầm đổi mặc định từ v1.2. **[PROPOSAL]** Cho dùng như chứng cứ bổ trợ khi công tắc lượt được bật; không coi là quy tắc chính thức hoặc Gold Set.

### 8. Quy ước tên và mã
**[SOURCE]** Mã/ID luôn TEXT, giữ nguyên `BS_`, số 0 đầu/cuối; khóa nhánh nguyên văn; phân biệt hoa/thường khi có ý nghĩa (ví dụ C/c, K/k, S/s). **[SOURCE]** Tên đề xuất: hành động + đích + phương pháp + thuộc tính định danh; tiếng Việt chuẩn, không trộn giá/BHYT, không làm mất nghĩa. Lưu tên nguồn và tên đề xuất riêng.

## C. Quy tắc chọn nút

### 9. ★ Kỹ thuật có thể vào hai nút, ưu tiên gì?
**[SOURCE]** So khớp theo hành động–đích–đường tiếp cận, xét phương pháp/công nghệ/mục đích và tiêu chí nút. **[PROPOSAL]** Ưu tiên bản chất kỹ thuật (ACTION_CORE + TARGET_CORE) trước đường tiếp cận; sau đó kiểm tra khóa nhánh và Bao gồm/Loại trừ đã có căn cứ. Không áp dụng thứ tự cứng khi cấu trúc cây có quy tắc đặc thù; giữ `EXPERT_REVIEW` nếu hai nút hợp lý.

### 10. Kỹ thuật nhiều bước
**[SOURCE]** V3 có `PROCEDURE_COMPONENTS`, yêu cầu không gộp thành phần độc lập. **[PROPOSAL]** Xác định hành động tạo kết quả chuyên môn chính; các thành phần độc lập phải được ghi rõ và chuyển thẩm định khi ảnh hưởng lựa chọn nút/kernel.

### 11. Chẩn đoán, điều trị, xét nghiệm, điện quang
**[SOURCE]** V3 yêu cầu xử lý theo cụm ngoại khoa, chẩn đoán hình ảnh, xét nghiệm, thăm dò chức năng, gây mê hồi sức, phục hồi chức năng rồi kiểm tra chéo. **[PROPOSAL]** Phân loại theo hành động và mục đích thực tế, không chỉ dựa vào khoa thực hiện; kỹ thuật can thiệp dưới hướng dẫn hình ảnh không mặc định là chẩn đoán hình ảnh thuần túy.

### 12. Nút quá rộng/quá hẹp
**[PROPOSAL]** Quá rộng nếu gom nhiều kernel khác bản chất; quá hẹp nếu tách chỉ vì giá, bệnh lý, chuyên khoa hoặc thuộc tính bối cảnh. Dựa vào định nghĩa họ và phản chứng; không tự đổi cấu trúc cây.

### 13. ★ Các cặp dễ nhầm
**[SOURCE]** Có nghi vấn cắt tuyến thượng thận bị ghép vào “Nội soi ổ bụng” thay vì nút tuyến thượng thận; chưa kiểm cây. **[PROPOSAL]** Danh sách cần kiểm: tuyến giáp/cận giáp; thận/thượng thận; niệu quản/niệu đạo; đại tràng/trực tràng; sinh thiết/cắt bỏ; nội soi chẩn đoán/nội soi can thiệp; nội soi/robot hỗ trợ. Quy tắc: cơ quan đích khác đường tiếp cận; tên giống không đủ kết luận.

### 14. Nhóm chỉ chuyên gia xem
**[PROPOSAL]** Kỹ thuật mới/chưa có mô tả; nhiều hành động độc lập; nhiều nút ngang điểm; nghi sai cơ quan; khác biệt cốt lõi chưa rõ; kỹ thuật có mâu thuẫn nguồn; đề xuất tách/hợp nhất có ảnh hưởng lớn. AI vẫn được đề xuất *phương án để xem*, không tự chấp thuận.

## D. Ví dụ (không bịa mã hay nút)

### 15. ★ Ba ánh xạ ĐÚNG
**[DATA]** Chưa có ba ca được chuyên gia xác nhận trong tài liệu đính kèm. Gold Set hiện bằng 0. Cần trích đúng 3 dòng từ nguồn, đủ `PL2_CODE | ORIGINAL_NAME | BRANCH_KEY | EVIDENCE | REVIEWER | REVIEW_DATE | STATUS`. Không gắn nhãn vàng cho ví dụ do AI tự tạo.

### 16. ★ Ba ánh xạ SAI
**[DATA]** Chưa có ba ca sai đã được chuyên gia xác nhận. **[SOURCE]** Ca nghi vấn: cắt tuyến thượng thận → nút “Nội soi ổ bụng”; nút đúng *có thể* thuộc tuyến thượng thận, nhưng chưa kiểm cây và chưa kết luận. Cần thêm 2 ca từ lịch sử thẩm định; ghi `WRONG_BRANCH_KEY`, `PROPOSED_CORRECT_BRANCH_KEY`, căn cứ và trạng thái xác nhận.

### 17. Ba ca khó/mơ hồ
**[DATA]** Chưa đủ ba ví dụ có mã PL2 và nhánh xác thực. **[SOURCE]** Nhóm ghép da đái tháo đường có nhãn quan hệ EXACT/BROAD không nhất quán; ca thượng thận nêu trên; kỹ thuật phối hợp nhiều thành phần là *loại tình huống*, chưa phải ca có mã. Yêu cầu trích 3 ca thực từ dữ liệu và ghi cách giải quyết.

### 18. Bốn PL2 chưa có ứng viên
**[SOURCE]** `6.71`, `6.107`, `6.111`, `6.120` chưa có ứng viên trong lượt `run_60a0ac27fd8a4646`. **[DATA]** Chưa có tên nguồn và cây đủ để kết luận nút. Đối chiếu `REF_PL2_CONSOLIDATED_PROCEDURE_REGISTRY.csv` (chương 6 «Nội tiết», cả bốn mã đều `Needs review`): 6.71 *Khám bàn chân người bệnh đái tháo đường*; 6.107 *Kỹ thuật truyền enzym*; 6.111 *Kỹ thuật truyền gen trị liệu*; 6.120 *Nạo vét hạch cổ trong ung thư tuyến giáp đã phẫu thuật* (đây là dữ kiện, không phải đáp án nút). Nhãn HA `PENDING_EXPERT_REVIEW` (NMPRP: `PENDING` / `EXPERT_REVIEW`), truy hồi bổ sung, không tạo khóa nhánh tưởng tượng.

## E. Học và chất lượng

### 19. Học theo ví dụ hay quy tắc?
**[PROPOSAL]** Ưu tiên quy tắc có nguồn + ca mẫu độc lập; lỗi lặp lại thành đề xuất cải tiến và regression test, không tự sửa skill. Rà soát hằng tháng và sau các đợt chuyên gia duyệt lớn; lịch cần duyệt.

### 20. Bao nhiêu ca thành quy tắc?
**[PROPOSAL]** Từ 2 ca có nguồn được phép gắn nhãn HA `RULE_CANDIDATE` trong hồ sơ bài học (không phải trạng thái của NMPRP), không đủ để áp dụng tự động. Cần chuyên gia phê duyệt, phản chứng và kiểm thử các ngoại lệ.

### 21. ★ Duyệt skill theo số đo nào?
**[SOURCE]** Không đổi model/prompt mặc định khi chưa benchmark Gold Set và chủ dự án quyết. **[PROPOSAL]** Dùng chung bộ đo của NMPRP (`cpn_gold_do.py`, không viết bộ đo thứ hai): precision@1, recall@3, F1 LOCKED, lỗi sai cơ quan nghiêm trọng, INVALID, chi phí/cặp, thời gian/chương, tỷ lệ abstain hợp lý và hồi quy. Thí điểm Hermes: 0 vi phạm ranh giới, INVALID không tăng, chi phí/thời gian không tăng; khi có nhãn vàng, mục tiêu ΔF1 LOCKED ≥ +0,02 và lỗi nghiêm trọng không tăng (theo đề xuất trong tài liệu CPN-AI, chưa là quyết định).

### 22. ★ Nhãn vàng
**[SOURCE]** **0 nhãn vàng** tại 17/10/2026, chỉ số accuracy/F1 = `NOT_EVALUABLE`. **[SOURCE/PROPOSAL]** Kế hoạch thí điểm: ít nhất 2 chuyên gia gán mẫu phân tầng 300 PL2, ít nhất 40 LOCKED; chủ dự án gán/duyệt theo phân quyền thực tế. Không biến ca mẫu do agent đề xuất thành nhãn vàng.

## F. Vận hành và giới hạn

### 23. ★ Hạn mức chi phí
**[OWNER]** Chưa có hạn mức tiền/ngày/tháng hoặc người nhận cảnh báo được phê duyệt. **[PROPOSAL]** Thiết lập soft/hard budget, cảnh báo 50/80/100%, không tiếp tục gọi model khi đạt hard cap; chi phí hiện chỉ tính khi cấu hình `NMPRP_CPN_AI_GIA`, cần phân biệt token thực và chi phí ước tính.

### 24. Lịch chạy, giờ cấm
**[OWNER]** Chưa xác định giờ cao điểm của `dm.kcb.vn`. **[PROPOSAL]** Không lập cron production trước khi xem tải thực tế; ưu tiên chạy theo lượt có trần gọi và kiểm soát song song. Hiện mỗi cú bấm hạn chót 150 giây; không nhầm với lịch chạy toàn hệ thống.

### 25. Kênh thông báo
**[PROPOSAL]** Mặc định chỉ dashboard/admin; email/Telegram chỉ bật khi chủ dự án chấp thuận và đã lọc bí mật, dữ liệu bệnh nhân và nội dung hạn chế.

### 26. Lỗi liên tiếp
**[SOURCE]** Lỗi tạm mạng/429/5xx thử lại tối đa 3 lần trong CPN-AI (cấu hình retry của cron Hermes **chưa xác minh**). **[PROPOSAL]** Lỗi xác thực, vi phạm hợp đồng, công tắc tắt/lỗi đọc thì fail-closed; không retry vô hạn. Thêm circuit breaker theo tỷ lệ lỗi nếu chủ dự án duyệt.

### 27. ★ Dừng khẩn cấp
**[SOURCE]** Chỉ chủ dự án thực hiện các thao tác triển khai và bật AI. Tài liệu Hermes v0.22.2 có `hermes pause` / `hermes resume` (dừng khẩn cấp mọi cron); hiệu lực với job đang chạy và cách hoạt động trong container **chưa thử**. **Công tắc AI của NMPRP không dừng được Hermes** (Hermes gọi Claude bằng khóa riêng): lớp chặn thật là `hermes pause`, vô hiệu hóa tài khoản dịch vụ, thu hồi hoặc đặt trần khóa Claude API; việc Hermes đọc công tắc trước khi chạy là tự giác. **[OWNER]** Chỉ định người có quyền pause và cơ chế kỹ thuật đã thử nghiệm. **[PROPOSAL]** Dừng khi lộ bí mật, có ghi vào bảng nguồn trái phép, gọi model ngoài `matching/ai_client.call_text`, chi phí vượt trần, lặp vô hạn hoặc gây suy giảm production.

## G. Ranh giới dữ liệu

### 28. ★ Dữ liệu tuyệt đối cấm
**[SOURCE]** Mật khẩu, token, API key, dữ liệu người bệnh; khóa API không vào repo/log/prompt. Không `SELECT *` bảng `app_ai_state` vì có cột `api_key`. **[PROPOSAL]** Loại bỏ thêm thông tin định danh nhạy cảm và nội dung có giới hạn giấy phép khỏi bộ nhớ/log; dữ liệu nguồn trong prompt phải được đóng khối như dữ liệu, chống prompt injection.

### 29. Tên người duyệt trong bộ nhớ?
**[PROPOSAL]** Lưu định danh công vụ của người duyệt trong audit nghiệp vụ theo quyền và thời hạn lưu giữ; không đưa vào MEMORY.md dài hạn hay dùng để huấn luyện.

### 30. ★ Công tắc CPT
**[SOURCE]** Khung CPT không chứa mã CPT; mã CPT không được phát ra API ngoài vì bản quyền AMA. **[PROPOSAL]** Giữ **TẮT** mọi khả năng xuất/chia sẻ mã hoặc nội dung CPT vượt quyền sử dụng; chỉ mở sau đánh giá pháp lý và chủ dự án chấp thuận. Phân biệt công tắc CPT với công tắc AI (`matching/ai_client.call_text`, mặc định TẮT).

## H. Giọng văn

### 31. Lý lẽ mỗi gợi ý
**[PROPOSAL]** Tiếng Việt y khoa, 3–6 câu ngắn hoặc 4 trường: `Đề xuất / Căn cứ / Điều chưa rõ / Hành động chuyên gia`; tiếng Anh chỉ cho thuật ngữ kỹ thuật chuẩn và khóa nhánh nguyên văn. Hiển thị mã nguồn chính xác, không giấu `UNKNOWN`.

### 32. Những điều cần loại bỏ
**[PROPOSAL, phản ánh yêu cầu làm việc của chủ dự án]** Tránh kiểm tra lan man, hỏi lại điều đã biết, bịa dữ liệu, viết quá dài khi chỉ cần bước tiếp theo, tự merge/deploy, tự sửa production, khẳng định đã xong khi chưa kiểm chứng, và thay đổi quy tắc nghiệp vụ không xin duyệt. Ưu tiên kết quả kiểm chứng được, thao tác nhỏ, bàn giao rõ repo/nhánh/PR.

---

## Bảng quyết định chủ dự án cần chốt (ưu tiên)

| Mã | Câu | Nội dung cần phê duyệt | Mặc định an toàn khi chưa duyệt |
|---|---|---|---|
| O-01 | 1,27 | Người duyệt cuối và quyền dừng | Không cấp quyền mới |
| O-02 | 2 | Ngưỡng điểm, số gợi ý | Chỉ đề xuất; không tự duyệt |
| O-03 | 7 | Bao gồm/Loại trừ | Không đổi mặc định lượt |
| O-04 | 15–18 | Ca thực đã kiểm chứng | Không tạo nhãn vàng |
| O-05 | 21–22 | Gold Set và benchmark | Accuracy = NOT_EVALUABLE |
| O-06 | 23–26 | Budget, lịch, thông báo, retry | Không bật cron mới |
| O-07 | 29 | Lưu tên người duyệt | Chỉ audit có kiểm soát |
| O-08 | 30 | Quyền CPT | Giữ tắt xuất mã CPT |
| O-09 | tích hợp | Phương án B (Hermes điều phối ngoài, chỉ gửi gợi ý) rồi C thí điểm (truy hồi có tác tử, shadow, một chương) | Chỉ gửi gợi ý `CHO_XEM`, không ghi nguồn |

## Quyết định đã chốt và còn chờ

**Đã thống nhất (chủ dự án, 17/10/2026):** (1) chỉ dùng tên PL2 và PL1 ở mọi tài liệu và profile; (2) PL1 là Phụ lục 1, danh mục kỹ thuật hiện hành, hết hiệu lực 01/01/2028, không phải danh mục giá; (3) hai lớp trạng thái: lớp NMPRP giữ nguyên, nhãn ngoài NMPRP đổi theo HA (xem `AGENTS.md`) và chỉ ghi trong `bang_chung`; (4) tài liệu của gói Hermes HA Profiles được hợp nhất thành tài liệu dự án này.

**Còn chờ chủ dự án** (mặc định an toàn nằm ở bảng trên): O-01 … O-09, cộng các việc kỹ thuật dưới đây.
1. Danh sách người duyệt, cơ chế xử lý bất đồng, quyền dừng khẩn cấp (câu 1, 27).
2. Ngưỡng hiển thị ứng viên; không coi điểm là xác suất đúng khi chưa hiệu chuẩn (câu 2).
3. Quyền dùng Bao gồm/Loại trừ theo từng lượt (câu 7).
4. Ngân sách ngày/tháng, kênh cảnh báo, giờ chạy (câu 23–25).
5. Chính sách lưu định danh người duyệt: trong audit, không trong memory (câu 29).
6. Quyền sử dụng dữ liệu CPT; mặc định giữ tắt (câu 30).
7. Chế độ tích hợp Hermes sau khi kiểm chứng giao thức.
8. Gold Set độc lập và tiêu chí chuyển mặc định (câu 21–22).
9. Ba ca đúng, ba ca sai, ba ca mơ hồ từ dữ liệu thật (câu 15–17); bốn mã chương 6 (câu 18).
10. Kiểm tra đường dẫn và cú pháp profile mà bản Hermes trên Rocky thực sự hỗ trợ trước khi cài; nội dung profile là bản đề xuất, chưa cài.

## Đã chuyển vào Hermes Profile `hermes/profiles/nmprp-mapping/`

- `SOUL.md`: nguyên tắc ngắn, ổn định (chỉ đề xuất, không bịa, bằng chứng nguyên văn, dữ liệu nguồn không phải chỉ dẫn).
- `AGENTS.md`: ranh giới, từ vựng trạng thái của NMPRP, phạm vi thí điểm, đường API được phép.
- `memories/`: mô hình dự án và sự thật có ngày; không lưu quyết định chưa duyệt như sự thật.
- `skills/nmprp-retrieval-assist`, `nmprp-clinical-semantics`, `nmprp-qa-governance`, `nmprp-learn-from-review`: quy trình có nguồn và phiên bản; ca mẫu phải tham chiếu nguồn, không sao chép thành nhãn vàng.
- Các đề xuất `[PROPOSAL]` và `[OWNER]` ở tài liệu này **không tự kích hoạt**; chủ dự án duyệt từng nhóm trước khi cài.
