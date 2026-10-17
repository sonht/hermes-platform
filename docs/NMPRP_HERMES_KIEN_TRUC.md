# NMPRP ⇄ Hermes Agent: sơ đồ kiến trúc tổng thể

Bản chỉnh từ sơ đồ phác thảo của chủ dự án (17/10/2026), đối chiếu với những gì đã xác minh, rồi bổ sung vòng phản hồi hai chiều theo kết quả thẩm định sơ đồ (cùng ngày). Phần có chữ «đề xuất» chưa được xây và chưa được chủ dự án duyệt. Nguồn vẽ: `docs/img/nmprp-hermes-kien-truc.mmd` (Mermaid); ảnh: `docs/img/nmprp-hermes-kien-truc.png`.

![Kiến trúc tổng thể](img/nmprp-hermes-kien-truc.png)

## Những chỗ đã chỉnh so với bản phác thảo
| # | Bản phác thảo | Bản chỉnh | Lý do |
|---|---|---|---|
| 1 | Sáu agent A1 đến A6 nằm trong khối Hermes | Nằm trong NMPRP (CPN-AI) | A1 đến A6 là worker của NMPRP, gọi mô hình qua `call_text` và chịu công tắc AI. Hermes ở ngoài, không chạy và không thay chúng. |
| 2 | Hermes nối thẳng vào cơ sở dữ liệu NMPRP và cổng ứng dụng | Hermes chỉ đọc qua API (danh sách đường cho phép) và chỉ ghi hai đường `goi-y`, `su-kien` vào bảng riêng | Tài khoản dịch vụ chỉ có `studio_cpt`; không đường duyệt, không bảng nguồn. |
| 3 | Hình thoi «Kết quả đủ tin cậy?»: Có thì chuyên gia duyệt, Không thì phản hồi | Mọi gợi ý đều chờ người duyệt; không có nút đủ căn cứ thì không gửi gợi ý và ghi sự kiện | Độ tin cậy chưa hiệu chuẩn (Gold Set = 0) nên không dùng làm cổng tự đi tiếp. |
| 4 | Telegram, Zalo, Discord, Web, Chat UI là kênh tương tác | Chỉ Dashboard `/agent`, Chat `/chat` (qua Tailscale) và tab Hermes trên NMPRP (admin) | Các kênh nhắn tin khác chưa được chủ dự án duyệt (brain dump câu 25: mặc định chỉ dashboard/admin). |
| 5 | Người dùng gồm chuyên gia, quản trị viên, cán bộ Cục/Bộ | Quản trị viên NMPRP | Chủ dự án chốt tab chỉ admin thấy. |
| 6 | Thiếu PL1 trong dữ liệu tham chiếu | Thêm PL1 (Phụ lục 1, hết hiệu lực 01/01/2028) | PL1 là danh mục kỹ thuật hiện hành, không phải danh mục giá. |
| 7 | Hệ thống mã tham chiếu ICD-9-CM, SNOMED CT | Bỏ khỏi sơ đồ | Chưa tích hợp; mã CPT không đi qua Hermes (bản quyền). |
| 8 | «Chạy agent chuyên môn», «Đọc file Excel/Word/PDF», «Tạo báo cáo» là công cụ của Hermes | Công cụ của Hermes là `nmprp_client` | Các khả năng kia chưa kiểm chứng hoặc không thuộc phạm vi thí điểm. |
| 9 | Vòng học: cập nhật quy tắc và prompt rồi ghi vào cơ sở dữ liệu | Hermes chỉ đề xuất bản vá kỹ năng; chủ dự án duyệt qua PR và đo trên nhãn vàng. Quyết định của người duyệt đi qua Studio | Học không được tự ghi vào dữ liệu hay đổi mặc định. |
| 10 | Thiếu Claude API và các phanh | Thêm Claude API (khoá riêng của Hermes) và khối «Phanh thật» | Công tắc AI của NMPRP không dừng được Hermes; phanh thật là `hermes pause`, tắt tài khoản dịch vụ, thu hồi hoặc đặt trần khoá Claude. |
| 11 | Hermes nằm trong NMPRP | Hermes chạy riêng trên Rocky (`hermes.kcb.vn`) | Hai hệ thống triển khai riêng, nối bằng API. |

Giữ nguyên từ bản phác thảo: khối Tri thức (Brain Dump), Ngữ cảnh phiên, chuỗi A1 đến A6, luồng dữ liệu nguồn đến ứng viên đến người duyệt, và vòng cải thiện có kiểm soát.

## Vòng phản hồi hai chiều (bổ sung theo thẩm định sơ đồ, 17/10/2026)

Bản trước mới có chiều đi (Hermes gợi ý, chuyên gia duyệt). Chiều về (Hermes biết gợi ý nào được nhận, bị sửa hay bị từ chối, và vì sao) được thêm như sau. Hermes không tự huấn luyện lại mô hình Claude: giá trị học nằm ở việc tích luỹ quyết định của chuyên gia, nhận ra lỗi lặp, và cải thiện quy trình suy luận qua kỹ năng có phiên bản.

### Bảy bước
1. Hermes gửi gợi ý kèm `run_id`, căn cứ, `phien_ban` kỹ năng (đã có).
2. Chuyên gia chấp nhận, sửa hoặc từ chối trên NMPRP, kèm lý do. **Chưa có:** gợi ý của Hermes hiện chỉ có trạng thái `CHO_XEM`, chưa có hàm duyệt gắn lý do.
3. NMPRP ghi quyết định, lý do, người duyệt, thời điểm vào kho phản hồi. **Chưa có.**
4. Hermes định kỳ đọc phản hồi mới qua API. **Chưa có đường đọc phù hợp:** `GET /admin/hermes/goi-y` yêu cầu quyền admin, còn tài khoản dịch vụ chỉ có `studio_cpt`; client cũng chưa cho phép đường này. Cần một đường đọc phản hồi riêng, chỉ đọc, ở mức `studio_cpt`.
5. Hermes so đề xuất với quyết định chuyên gia, phân loại sai sót (kỹ năng `nmprp-learn-from-review`, đã có).
6. Hermes đề xuất bản vá tri thức hoặc kỹ năng bằng văn bản. Một phản hồi đơn lẻ không đủ để đổi gì; cần từ 2 ca có nguồn. Hermes không tự sửa `SOUL.md`, `AGENTS.md` hay kỹ năng đang chạy.
7. Chủ dự án duyệt qua PR, đo trên nhãn vàng trước và sau, rồi mới dùng phiên bản mới.

### Ba loại bộ nhớ (không nhồi kết quả ánh xạ vào MEMORY.md)
| Loại | Nội dung | Nơi lưu |
|---|---|---|
| Project Memory | Kiến trúc, thuật ngữ, quy tắc, mục tiêu | `SOUL.md`, `AGENTS.md`, `MEMORY.md` của profile (ngắn, có ngày) |
| Expert Knowledge | Quy tắc chuyên môn, ví dụ đã xác nhận, ngoại lệ | Cơ sở dữ liệu NMPRP, có phiên bản; Hermes chỉ truy hồi phần liên quan khi xử lý |
| Learning History | Lịch sử đề xuất, phản hồi, sai sót, kết quả cải tiến | Kho gợi ý và kho phản hồi ở NMPRP; Hermes giữ thêm lịch sử phiên của riêng nó |

### Ba nhãn cho phản hồi (nhãn HA, không phải trường của NMPRP)
| Nhãn | Ý nghĩa | Ai và khi nào |
|---|---|---|
| `EXPERT_FEEDBACK` | Ý kiến thẩm định của chuyên gia (chấp nhận, sửa, từ chối, lý do) | Mọi quyết định của người duyệt |
| `VERIFIED_KNOWLEDGE` | Kiến thức đã kiểm tra lại và xác nhận | Cần kiểm tra bổ sung: từ 2 ca có nguồn, hoặc người thứ hai, kèm phản chứng và ngoại lệ |
| `GOLD_STANDARD` | Chuẩn dùng để đo chất lượng AI | Chỉ do quy trình nhãn vàng của NMPRP, gán độc lập; **không** lấy từ gợi ý Hermes đã được chấp nhận (tránh vòng tròn tự củng cố) |

Chấp nhận một gợi ý của Hermes chỉ tạo `EXPERT_FEEDBACK`, không tự thành nhãn vàng.

### Giao việc tự động (giai đoạn 2, đề xuất)
Hiện quản trị viên giao việc qua giao diện Hermes. Để xử lý hàng loạt PL2, đề xuất mô hình **Hermes tự kéo việc** (không để NMPRP đẩy vào Hermes, vì Hermes chỉ mở qua Tailscale): NMPRP giữ một hàng đợi tác vụ; Hermes dùng tài khoản dịch vụ để nhận việc, xử lý, gửi gợi ý.
- Trường của một tác vụ: `job_id`, `source_snapshot`, `task_type`, `pl2_codes`, `ruleset_version`, `agent_version`, `status`, `result`, `evidence`.
- Chống xử lý trùng (khoá `pl2_code`, `branch_key`, `phien_ban`, `run_id` đã có ở bảng gợi ý), thuê việc có thời hạn, giới hạn số tác vụ đồng thời, thử lại an toàn, khôi phục sau lỗi.
- **Điểm lợi về an toàn:** máy chủ NMPRP chỉ phát việc khi công tắc AI bật (không bật thì không có việc để nhận). Nhờ vậy công tắc AI có hiệu lực thật với luồng Hermes, thay vì chỉ là việc Hermes tự đọc. Phanh `hermes pause` và tắt tài khoản dịch vụ vẫn giữ.

### Việc cần xây (mỗi việc là một PR riêng ở `sonht/nmprp`, cần chủ dự án duyệt trước)
1. Hàm duyệt gợi ý có lý do và trạng thái mới; kho phản hồi; đường đọc phản hồi cho `studio_cpt`. Có thể kèm migration, nên chủ dự án triển khai và sao lưu theo quy trình.
2. Hàng đợi tác vụ (giai đoạn 2), sau khi phương án B chạy ổn.
3. Nhãn `EXPERT_FEEDBACK`, `VERIFIED_KNOWLEDGE` ở kho phản hồi; `GOLD_STANDARD` dùng nhãn vàng sẵn có.
4. Bộ kiểm thử và đánh giá trước khi đổi kỹ năng, dùng bộ đo `cpn_gold_do.py` của NMPRP.

Giai đoạn thí điểm giữ nguyên: CPN-AI A1 đến A6 chạy độc lập như hiện nay; Hermes là luồng đề xuất song song để đánh giá, không thay thế.
