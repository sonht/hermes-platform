# NMPRP Brain Dump v1.0 — DRAFT, AWAITING OWNER APPROVAL

**Trạng thái: DRAFT – AWAITING OWNER APPROVAL.** Chưa có nội dung nào dưới đây được đưa vào `SOUL.md`, `AGENTS.md`, `MEMORY.md` hay kỹ năng.
Phần 1 là bản trả lời dự thảo do chủ dự án cung cấp ngày 17/10/2026 (giữ nguyên văn). Phần 2 là đối chiếu với dữ liệu và tài liệu thật trong `sonht/nmprp`
(đọc ở commit `c67f980`) và `sonht/hermes-platform`.

## Phần 1 — Bản trả lời dự thảo (nguyên văn)

Tôi đề xuất xây dựng Brain Dump v1.0 cho Hermes Agent – NMPRP theo hướng: Hermes phải hiểu được tư duy chuyên môn trong việc chuẩn hóa danh mục kỹ thuật, chứ không chỉ học thuộc các quy tắc ánh xạ PL2 → CPT.

Dưới đây là bản trả lời dự thảo đầy đủ 32 câu hỏi, dựa trên định hướng NMPRP mà chúng ta đang xây dựng. Tôi phân biệt rõ nội dung đã có cơ sở chuyên môn với những chính sách cần phê duyệt, tránh biến đề xuất của AI thành quyết định của chủ dự án.

### A. Thẩm quyền và người duyệt

**1. ★ Ai duyệt gợi ý của Hermes?** Đề xuất mô hình ba cấp:
- Hermes Agent: Phân tích, tìm kiếm, đề xuất và giải thích. Không có quyền tự phê duyệt.
- Chuyên gia chuyên khoa: Thẩm định tính chính xác về chuyên môn, kỹ thuật và vị trí phân loại.
- Quản trị viên chuyên môn NMPRP: Phê duyệt kết quả cuối cùng để đưa vào dữ liệu chuẩn.

Nếu hai chuyên gia bất đồng, chuyển trạng thái DISPUTED, tổ chức xem xét và để người có thẩm quyền chuyên môn được phân công quyết định. Hermes không tự phân xử.

**2. ★ Ngưỡng tin cậy và số lượng gợi ý.** Đề xuất:

| Độ tin cậy | Xử lý |
|---|---|
| ≥ 90% | Đề xuất ưu tiên để chuyên gia xem xét |
| 75–<90% | Đề xuất cần kiểm tra |
| 60–<75% | Chỉ hiển thị khi người duyệt yêu cầu |
| <60% | Không đề xuất ánh xạ, ghi thiếu căn cứ |

Tối đa ba ứng viên cho một PL2. Lưu ý: Các ngưỡng trên chỉ là giá trị khởi tạo, không được coi là xác suất đúng nếu chưa hiệu chuẩn bằng bộ dữ liệu chuyên gia xác nhận.

**3. Khi Hermes không chắc.** Hermes phải nói rõ không đủ căn cứ, chỉ ra thông tin còn thiếu và có thể đưa ra các hướng cần chuyên gia xác minh. Không được tạo ra kết luận chắc chắn từ dữ liệu mơ hồ.

### B. Thuật ngữ và quy ước

**4. ★ Định nghĩa thuật ngữ**

| Thuật ngữ | Định nghĩa đề xuất |
|---|---|
| PL1 | Danh mục kỹ thuật lịch sử, phục vụ truy xuất nguồn gốc, phân loại cũ và liên kết giá |
| PL2 | Danh mục kỹ thuật đang được tổ chức, chuẩn hóa và ánh xạ theo cây phân loại tham chiếu |
| Nút (Node) | Một vị trí xác định trong cây phân loại kỹ thuật |
| Họ (Family) | Nhóm kỹ thuật có chung bản chất chuyên môn, đích tác động hoặc nguyên lý thực hiện |
| Kernel | Hạt nhân kỹ thuật, thể hiện hành động chuyên môn cốt lõi và đối tượng tác động |
| Modifier | Thuộc tính bổ nghĩa làm rõ kỹ thuật như đường tiếp cận, phương pháp, phạm vi hoặc công nghệ |

Phân biệt rõ kernel là bản chất kỹ thuật, còn modifier mô tả đặc điểm hoặc biến thể của kỹ thuật đó.

**5. Viết tắt và thuật ngữ.** Hermes phải xây dựng từ điển thuật ngữ y học tiếng Việt, gồm tên chuẩn, tên đồng nghĩa, chữ viết tắt và cách viết tương đương. Ví dụ: nội soi, nội soi can thiệp, mổ mở, qua da, robot hỗ trợ, sinh thiết, cắt bỏ, bóc tách, dẫn lưu, tạo hình. Không được coi các từ gần nghĩa là đồng nghĩa hoàn toàn khi có khác biệt về bản chất kỹ thuật.

**6. ★ PL2 không ghi phương pháp.** Không mặc định là mổ mở, nội soi hay robot. Khi tên kỹ thuật không xác định đường tiếp cận hoặc phương pháp, Hermes phải: giữ trạng thái APPROACH_UNSPECIFIED; tra cứu mô tả kỹ thuật và tài liệu chuyên môn; không tự bổ sung phương pháp chỉ vì đó là phương pháp thường gặp; chuyển chuyên gia xem xét nếu phương pháp quyết định vị trí phân loại.

**7. Văn bản Bao gồm / Loại trừ.** Cho phép Hermes sử dụng để tìm kiếm, giải thích và kiểm tra tính phù hợp. Tuy nhiên, nội dung chưa thẩm định chỉ là nguồn tham khảo, không được sử dụng làm quy tắc bắt buộc hoặc nhãn vàng.

**8. Quy ước tên.** Giữ nguyên mã định danh, dấu tiếng Việt, tên gốc và thông tin nguồn. Hermes có thể tạo trường tên chuẩn hóa riêng nhưng không được ghi đè tên gốc. Mọi mã PL1, PL2, PL3, CPT và ICD-9-CM phải được xử lý dưới dạng chuỗi ký tự.

### C. Quy tắc chọn nút

**9. ★ Ưu tiên lựa chọn nút.** Không áp dụng máy móc một thứ tự cơ quan → phương pháp. Đề xuất thứ tự xem xét: (1) Bản chất và mục đích kỹ thuật. (2) Hành động chuyên môn chính. (3) Cơ quan hoặc cấu trúc giải phẫu đích. (4) Đường tiếp cận và phương pháp thực hiện. (5) Phạm vi, mức độ và các thuộc tính bổ nghĩa. (6) Quy tắc Bao gồm / Loại trừ đã được phê duyệt. Cấu trúc cây phân loại đích là căn cứ quyết định vị trí cuối cùng.

**10. Kỹ thuật nhiều bước.** Xác định hành động chính tạo ra kết quả chuyên môn của kỹ thuật. Các bước chuẩn bị, tiếp cận, kiểm soát và kết thúc không tự động trở thành kỹ thuật chính. Nếu có nhiều hành động độc lập, phải đánh giá khả năng phân tách hoặc phân loại kỹ thuật phối hợp.

**11. Chẩn đoán, điều trị, xét nghiệm, điện quang.** Phân loại theo bản chất kỹ thuật và cấu trúc cây đích. Không dùng chuyên khoa thực hiện làm tiêu chí duy nhất. Ví dụ, sinh thiết dưới hướng dẫn siêu âm không tự động được xếp vào nhóm siêu âm chẩn đoán.

**12. Nút quá rộng hoặc quá hẹp.** Một nút quá rộng khi tập hợp các kỹ thuật khác nhau đáng kể về hành động, đích tác động hoặc nguyên lý chuyên môn. Một nút quá hẹp khi chỉ khác các thuộc tính bổ nghĩa không làm thay đổi bản chất kỹ thuật, trong khi cây đích không yêu cầu tách. Không tự động chia hoặc gộp nút khi chưa có quyết định chuyên môn.

**13. ★ Các cặp dễ nhầm.** Hermes cần đặc biệt kiểm tra: tuyến giáp và tuyến cận giáp; tuyến thượng thận và các kỹ thuật nội soi ổ bụng; thận và tuyến thượng thận; niệu quản và niệu đạo; đại tràng và trực tràng; động mạch và tĩnh mạch; sinh thiết và cắt bỏ tổn thương; nội soi chẩn đoán và nội soi can thiệp; phẫu thuật nội soi và phẫu thuật có robot hỗ trợ. Nguyên tắc: Không được đánh đồng đường tiếp cận với cơ quan đích hoặc hành động chính.

**14. Nhóm phải chuyên gia xem xét.** Đề xuất bắt buộc chuyển chuyên gia đối với kỹ thuật mới, kỹ thuật phối hợp phức tạp, tên mơ hồ, thiếu mô tả, có nhiều nút cạnh tranh không phân giải được hoặc có mâu thuẫn giữa các nguồn tham chiếu.

### D. Ví dụ và dữ liệu chuẩn

**15–18. Các ví dụ đúng, sai, mơ hồ và bốn PL2 chưa có ứng viên.** Đây là phần không nên để AI tự sáng tác. Cần trích xuất trực tiếp từ dữ liệu NMPRP và cây CPT tham chiếu hiện hành để bảo đảm: mã PL2 có thật; tên kỹ thuật chính xác; khóa nhánh tồn tại; nút được chọn phù hợp; có tài liệu giải thích và người xác nhận. Đối với bốn mã 6.71, 6.107, 6.111, 6.120, giữ trạng thái PENDING_EXPERT_REVIEW cho đến khi đối chiếu dữ liệu nguồn. Hermes có thể tạo ứng viên để thẩm định nhưng không được tự coi các ứng viên đó là đáp án đúng.

### E. Học và chất lượng

**19. Hermes học như thế nào?** Ưu tiên kết hợp: quy tắc chuyên môn rõ ràng; ví dụ thực tế đã được thẩm định; phân tích các lỗi lặp lại; bộ kiểm thử hồi quy. Hermes có thể ghi nhận kinh nghiệm sau mỗi nhiệm vụ, nhưng không tự thay đổi quy tắc chuyên môn đang có hiệu lực. Đề xuất rà soát định kỳ hằng tháng.

**20. Bao nhiêu trường hợp thành quy tắc?** Hai trường hợp có nguồn chỉ đủ để hình thành một giả thuyết quy tắc. Muốn đưa vào vận hành phải có đánh giá chuyên môn, kiểm tra trường hợp ngoại lệ và kiểm thử hồi quy.

**21. ★ Ai duyệt thay đổi kỹ năng?** Quản trị viên chuyên môn NMPRP phê duyệt thay đổi quy tắc nghiệp vụ; người phụ trách kỹ thuật phê duyệt triển khai phần mềm. Các chỉ số đánh giá: Precision@1 (tỷ lệ ứng viên đứng đầu đúng); Recall@3 (tỷ lệ đáp án đúng xuất hiện trong ba ứng viên); Wrong-target rate (tỷ lệ ánh xạ sai cơ quan hoặc đích tác động); Abstention quality (khả năng từ chối khi thiếu căn cứ); Regression pass rate (tỷ lệ ca kiểm thử cũ vẫn đúng); Expert acceptance rate (tỷ lệ đề xuất được chuyên gia chấp nhận).

**22. ★ Nhãn vàng.** Chưa xác định số lượng nhãn vàng đã được chuyên gia xác nhận. Cần kiểm kê dữ liệu trước khi công bố con số. Một nhãn vàng phải có mã nguồn, mã đích, người xác nhận, thời điểm, phiên bản cây phân loại và căn cứ chuyên môn. Không được tự động chuyển dữ liệu AI đề xuất thành nhãn vàng.

### F. Vận hành

**23. ★ Ngân sách Claude API.** Chưa có hạn mức được anh phê duyệt. Đề xuất cấu hình hạn mức ngày/tháng, cảnh báo tại 50%, 80%, 100% và cơ chế ngừng tác vụ AI không thiết yếu khi vượt ngân sách.

**24. Lịch chạy.** Các tác vụ phân tích NMPRP nên chạy theo hàng đợi riêng, có giới hạn tài nguyên và ưu tiên ngoài giờ cao điểm. Không tự giả định giờ cao điểm của dm.kcb.vn; phải căn cứ số liệu vận hành.

**25. Kênh thông báo.** Ưu tiên thông báo trong giao diện quản trị Hermes. Email hoặc Telegram chỉ gửi thông tin vận hành đã được phép, không chứa dữ liệu nhạy cảm.

**26. Lỗi liên tiếp.** Đề xuất thử lại tối đa ba lần với thời gian chờ tăng dần đối với lỗi tạm thời. Lỗi xác thực, lỗi quyền truy cập, sai cấu trúc dữ liệu hoặc nguy cơ mất dữ liệu phải dừng ngay.

**27. ★ Dừng khẩn cấp.** Chủ dự án và quản trị viên vận hành được phân quyền có thể dừng Hermes. Các dấu hiệu cần dừng gồm: nguy cơ rò rỉ dữ liệu; thực hiện hành động ngoài phạm vi được phép; chi phí vượt giới hạn; ghi sai dữ liệu nguồn; vòng lặp tác vụ bất thường; ảnh hưởng đến dịch vụ production. Lệnh hermes pause phải được kiểm tra về phạm vi tác động và hiệu lực thực tế trước khi coi là cơ chế dừng khẩn cấp đáng tin cậy.

### G. Ranh giới dữ liệu

**28. ★ Dữ liệu bị cấm.** Không đưa vào prompt, bộ nhớ hoặc nhật ký: mật khẩu, API key, access token, private key; dữ liệu định danh người bệnh và thông tin bệnh án cá nhân; thông tin xác thực hoặc bí mật hạ tầng; dữ liệu thuộc phạm vi hạn chế chia sẻ; nội dung CPT có bản quyền khi chưa xác định quyền sử dụng phù hợp. Các bí mật kỹ thuật phải được quản lý bằng cơ chế chuyên dụng, không lưu trực tiếp trong tài liệu hướng dẫn Agent.

**29. Tên người duyệt.** Có thể lưu tên hoặc định danh công vụ của người duyệt trong nhật ký nghiệp vụ có kiểm soát truy cập. Không cần đưa thông tin này vào bộ nhớ hội thoại dài hạn của Hermes.

**30. ★ Công tắc CPT.** Đề xuất giữ tắt trong giai đoạn thí điểm, trừ khi đã xác định rõ phạm vi và quyền sử dụng dữ liệu CPT. Hermes vẫn có thể xử lý cấu trúc phân loại nội bộ, kernel, family và modifier do dự án xây dựng hợp pháp. Cần phân biệt quyền truy cập dữ liệu CPT với quyền sử dụng, sao chép hoặc phân phối nội dung CPT.

### H. Giọng văn

**31. Lý lẽ của Hermes.** Ngắn gọn, chính xác, ưu tiên tiếng Việt chuyên ngành. Mỗi gợi ý nên có: nút đề xuất; căn cứ chuyên môn; điểm phù hợp và điểm chưa chắc chắn; nguồn tham chiếu; mức độ tin cậy hoặc trạng thái thiếu căn cứ. Không cần trình bày dài dòng nếu chuyên gia không yêu cầu.

**32. Những điều phải loại bỏ.** Hermes cần tránh tuyệt đối: hỏi đi hỏi lại thông tin đã có; kiểm tra lan man, không đi đến hành động; tự suy đoán rồi trình bày như sự thật; tự ý sửa production hoặc merge PR; đưa ra quá nhiều phương án mà không có đề xuất ưu tiên; viết hướng dẫn kỹ thuật quá dài cho những việc đơn giản; tuyên bố hoàn thành khi chưa kiểm chứng; quên bối cảnh và các quyết định đã được thống nhất; tự động thay đổi quy tắc nghiệp vụ khi chưa được duyệt.

### Định hướng: ba tầng tri thức

| Tầng | Nội dung | Khả năng tự cập nhật |
|---|---|---|
| Project Knowledge | Kiến trúc NMPRP, mô hình PL1/PL2/PL3, thuật ngữ, dữ liệu tham chiếu | Cập nhật có kiểm soát |
| Expert Knowledge | Quy tắc phân loại, ca mẫu, ngoại lệ, quyết định chuyên gia | Phải được chuyên gia phê duyệt |
| Agent Experience | Lỗi gặp phải, phương pháp tìm kiếm hiệu quả, bài học vận hành | Có thể đề xuất cải tiến tự động |

Không nên biến toàn bộ 32 câu trả lời thành bộ nhớ cố định của Hermes. Chỉ những nguyên tắc ổn định mới đưa vào SOUL/AGENTS; quy tắc chuyên môn, dữ liệu tham chiếu và ca mẫu phải được quản lý theo phiên bản, có nguồn và có khả năng truy vết.

---

## Phần 2 — Đối chiếu với dữ liệu và tài liệu thật

Nhãn: **CONFIRMED** = đã có trong quy tắc/tài liệu/mã của dự án · **PROPOSED** = đề xuất hợp lý, chưa có căn cứ trong kho, cần chủ dự án duyệt ·
**NEEDS_DATA** = cần đo hoặc trích dữ liệu thật · **NEEDS_OWNER_DECISION** = chính sách do chủ dự án quyết.

### 2.1. Ba chỗ cần SỬA trong bản dự thảo
1. **"PL3" không phải một danh mục thứ ba.** Bảng "Project Knowledge" ghi "mô hình PL1/PL2/PL3" và câu 8 liệt kê PL3 như một loại mã. Theo `CLAUDE.md` của NMPRP (bất biến 5, kế hoạch `docs/doi-ten-pl3-pl2/KE_HOACH.md`):
   PL3 là **tên cũ của PL2** (đổi 03/09/2026, "đừng viết thêm định danh `pl3` nào nữa"). Dữ liệu vẫn còn dấu vết: `PROCEDURE_ID` trong `REF_PL2_CONSOLIDATED_PROCEDURE_REGISTRY.csv` bắt đầu bằng `PL3-PROC-…`, và tham số API `kind=pl3` chỉ PL2.
2. **Định nghĩa PL1.** Bản dự thảo viết "danh mục kỹ thuật lịch sử". Theo NMPRP, PL1 là **Phụ lục 1 (danh mục phẫu thuật, thủ thuật, mã theo TT23, giữ tiền tố `BS_`)**; PL1 là nguồn gốc của phân loại PT/TT và cầu nối PL2 → PL1 → giá. Tên tệp nguồn `REF_PL1_LEGACY_SOURCE.csv` có chữ "legacy", nhưng đó là tên tệp, không phải nghĩa của PL1.
3. **Trạng thái `DISPUTED` và `PENDING_EXPERT_REVIEW` chưa tồn tại ở NMPRP.** NMPRP dùng `PENDING` cho `review_status` và `EXPERT_REVIEW` cho `decision` (`cpn_ai_store`, prompt A2). Muốn thêm trạng thái mới thì cần sửa NMPRP; trước mắt dùng đúng các giá trị đang có.

### 2.2. Bảng đối chiếu 32 câu

| # | Nhãn | Căn cứ / ghi chú |
|---|---|---|
| 1 | PROPOSED + NEEDS_OWNER_DECISION | Ba cấp khớp luật "AI chỉ đề xuất, chuyên gia duyệt" của NMPRP. `DISPUTED` là trạng thái mới (xem 2.1.3); quy trình xử lý bất đồng giữa hai người duyệt cần chủ dự án chốt. |
| 2 | PROPOSED + NEEDS_DATA | Ngưỡng 90/75/60 chưa hiệu chuẩn (đúng như bản dự thảo ghi). Tối đa 3 ứng viên khớp skill hiện tại. |
| 3 | CONFIRMED | Khớp quy tắc prompt A2 (đóng băng): thiếu căn cứ ⇒ `ABSTAIN`/`EXPERT_REVIEW`; không có nút phù hợp thì không đẩy về nút "Other/Unlisted". |
| 4 | PROPOSED (kèm sửa) | Xem 2.1.1 và 2.1.2. Định nghĩa Nút/Họ/Kernel/Modifier cần chủ dự án xác nhận bằng lời của mình. |
| 5 | PROPOSED | NMPRP có tệp liên quan `registry/cpn_ai_thuat_ngu.py`; **cần đọc trước khi dựng từ điển mới** (không dựng bản cài đặt thứ hai). Chưa đọc nội dung. |
| 6 | CONFIRMED + NEEDS_OWNER_DECISION | Prompt A2 v1.2 mục 3: tên PL2 không nêu phương pháp mà nút phân biệt theo phương pháp ⇒ `ABSTAIN`/`EXPERT_REVIEW`, không đoán phương pháp. NMPRP còn để ngỏ câu "không ghi nội soi/robot thì hiểu là mổ mở"; bản dự thảo chọn **không mặc định**, cần chủ dự án xác nhận để đóng câu hỏi mở đó. |
| 7 | CONFIRMED + NEEDS_OWNER_DECISION | Khớp luật NMPRP: "Loại trừ" chưa thẩm định, chỉ để LOẠI, không sinh ứng viên. Nhưng gói nguồn `CPT_Danh_muc_dich` ghi "chưa rà bản quyền", nên việc gửi nội dung này sang mô hình của Hermes cần chủ dự án quyết. |
| 8 | CONFIRMED | Bất biến 1 (mã luôn TEXT, giữ số 0, `BS_`), giữ tên gốc. Đã sửa PL3 (2.1.1). |
| 9 | PROPOSED + NEEDS_DATA | Thứ tự đề xuất đặt cơ quan ở bước 3, trong khi bất biến 3 của NMPRP "phạt nặng khớp sai cơ quan" và cây đích tổ chức theo hệ cơ quan. Không nhất thiết mâu thuẫn, nhưng cần thử trên ca mẫu thật trước khi đưa vào kỹ năng. |
| 10 | PROPOSED | Chưa có căn cứ trong kho. |
| 11 | PROPOSED | Chưa có căn cứ trong kho (quy tắc phạm vi PT/TT của NMPRP là việc khác). |
| 12 | PROPOSED | NMPRP có nguyên tắc "không tự gộp/tách nút khi chưa có quyết định"; tiêu chí rộng/hẹp là đề xuất. |
| 13 | NEEDS_DATA | Chỉ hai cặp có dấu vết trong tài liệu NMPRP (cắt tuyến thượng thận bị xếp vào nút nội soi ổ bụng; tuyến giáp/cận giáp) và **đều ghi là nghi vấn chưa kiểm cây**. Bảy cặp còn lại là đề xuất, chưa có số đo sai. |
| 14 | PROPOSED | Khớp cách dùng `EXPERT_REVIEW` hiện có. |
| 15–17 | NEEDS_DATA | Cần ca thật do chuyên gia xác nhận; AI không tự sáng tác (đúng như bản dự thảo). Gợi ý nguồn: tệp nhãn vàng `GOLD_REVIEW_24_TAI_SAN_KHOA.xlsx` và `GOLD_HARD_NEGATIVES_…xlsx` (chờ chuyên gia gán). |
| 18 | NEEDS_DATA | Bốn PL2 có thật (xem 2.3). Trạng thái dùng giá trị NMPRP (`EXPERT_REVIEW`/`PENDING`), không dùng `PENDING_EXPERT_REVIEW`. |
| 19 | PROPOSED | Khớp thiết kế vòng học có duyệt. Rà soát hằng tháng là đề xuất. |
| 20 | PROPOSED | Khớp ngưỡng "2 ca có nguồn" của kỹ năng học; đã tách giả thuyết khỏi quy tắc vận hành. |
| 21 | PROPOSED + NEEDS_OWNER_DECISION | NMPRP **đã có** bộ đo và ngưỡng: precision/recall/F1, coverage, abstain, lỗi nghiêm trọng; ngưỡng `NGUONG` (`cpn_gold_do.py`): DEV ≥60 mục, LOCKED ≥40 mục, đồng thuận ≥0,6, ΔF1 LOCKED ≥ +0,02, F1 DEV giảm tối đa 0,01, coverage giảm tối đa 0,05, abstain tăng tối đa 0,05, lỗi nghiêm trọng không tăng. **Đề nghị dùng đúng bộ đo này** (một bản cài đặt), chỉ thêm chỉ số chưa có (ví dụ Recall@3) nếu cần. |
| 22 | NEEDS_DATA | Tài liệu NMPRP ngày 17/10 ghi **0 nhãn vàng được xác nhận** (mọi chỉ số chính xác là `NOT_EVALUABLE`). **Chưa kiểm kê trên CSDL thật** (cần quyền admin/studio; phiên này không với tới). |
| 23 | NEEDS_OWNER_DECISION | Không tìm thấy cấu hình hạn mức nào trong repo `hermes-platform`. Cần đặt hạn mức ở nhà cung cấp và/hoặc trong Hermes. |
| 24 | NEEDS_DATA | Chưa có số đo tải của `dm.kcb.vn`; không đặt khung giờ khi chưa có số liệu. |
| 25 | PROPOSED | Hợp lý; kênh nhắn tin (Telegram…) chưa cấu hình. |
| 26 | PROPOSED | NMPRP "Chạy hết" đã thử lại tối đa 3 lần cho lỗi tạm (mạng, 429, 5xx) — tiền lệ tốt. Cấu hình thử lại của cron Hermes **chưa xác minh**. |
| 27 | PROPOSED + NEEDS_DATA | Tài liệu Hermes có `hermes pause` ("dừng khẩn cấp": không cron nào bắt đầu khi đang bật). **Chưa xác minh** nó có dừng được tác vụ đang chạy dở và có hiệu lực trong container Rocky. Nên thử có kiểm soát trước khi tin. |
| 28 | CONFIRMED | Khớp `SOUL.md` hiện có và bất biến khóa API của NMPRP. Điều kiện về CPT đi với câu 30. |
| 29 | PROPOSED | Hợp lý; hiện `hermes_goi_y.tao_boi` chỉ lưu tên tài khoản dịch vụ, tên người duyệt nằm ở nhật ký của NMPRP. |
| 30 | NEEDS_OWNER_DECISION | Bản dự thảo đề xuất giữ TẮT khi thí điểm; client đang mặc định TẮT. Chủ dự án từng nói tự lo bản quyền CPT, nên cần nói rõ chọn bật hay tắt cho giai đoạn thí điểm. |
| 31 | PROPOSED (kèm bổ sung) | Prompt NMPRP đòi `evidence` là 1–4 đoạn trích **nguyên văn** (tối đa 150 ký tự) từ tên PL2 hoặc tên nút. Kỹ năng của Hermes nên theo đúng quy tắc này. |
| 32 | PROPOSED | Khớp sở thích đã ghi của chủ dự án (không bịa, chưa kiểm thì nói chưa kiểm). |

### 2.3. Bốn PL2 chưa có ứng viên (dữ kiện từ `REF_PL2_CONSOLIDATED_PROCEDURE_REGISTRY.csv`, chương 6 «Nội tiết»)
| Mã | Tên | Ghi chú trong dữ liệu |
|---|---|---|
| 6.71 | Khám bàn chân người bệnh đái tháo đường | `REGISTRY_STATUS = Needs review` |
| 6.107 | Kỹ thuật truyền enzym | `REGISTRY_STATUS = Needs review`; kernel ghi "cần phân rã thủ công" |
| 6.111 | Kỹ thuật truyền gen trị liệu | `REGISTRY_STATUS = Needs review`; kernel ghi "cần phân rã thủ công" |
| 6.120 | Nạo vét hạch cổ trong ung thư tuyến giáp đã phẫu thuật | `REGISTRY_STATUS = Needs review` |

Đây là **dữ kiện, không phải đáp án**. Có thể một số mã này đúng là không có nút phù hợp (`UNPLACED`); điều đó do chuyên gia quyết.

### 2.4. Tóm tắt trạng thái
- CONFIRMED: 3, 6 (một phần), 7 (một phần), 8, 28.
- NEEDS_DATA: 13, 15–18, 22, 24 (và một phần 2, 9, 27).
- NEEDS_OWNER_DECISION: 1, 6, 7, 21, 23, 30.
- Còn lại: PROPOSED.

## Phần 3 — Việc chờ chủ dự án duyệt trước khi cập nhật tệp của Hermes
1. Xác nhận ba chỗ sửa ở 2.1 (PL3 là tên cũ của PL2; định nghĩa PL1; dùng trạng thái hiện có của NMPRP).
2. Quyết các mục NEEDS_OWNER_DECISION (1, 6, 7, 21, 23, 30).
3. Cho phép kiểm kê nhãn vàng và cấu hình vận hành trên máy thật (do phiên Claude trên Rocky hoặc chủ dự án làm).
4. Sau khi duyệt, mới cập nhật `SOUL.md`, `AGENTS.md`, `MEMORY.md` và kỹ năng `nmprp-retrieval-assist` (kể cả quy tắc trích dẫn nguyên văn ở câu 31 và quy tắc "không đẩy về nút Other/Unlisted").
