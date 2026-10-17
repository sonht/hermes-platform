# Thiết kế: Hermes Agent hỗ trợ ánh xạ PL2/PL1 vào cây CPT cho NMPRP (dm.kcb.vn)

**Trạng thái: THIẾT KẾ, chưa triển khai, chưa sửa gì ở `sonht/nmprp` hay trên Rocky.**
Ngày 17/10/2026. Chủ dự án chốt hướng: **giai đoạn B trước, rồi C thí điểm chế độ shadow** (mục 5).
Căn cứ đọc mã `sonht/nmprp` @ `c67f980` (chỉ đọc) và tài liệu upstream Hermes Agent v0.22.2 (`d923a5eb`).
Ô nào chưa chạy thật ghi "chưa kiểm chứng".

## 1. Bài toán

Dữ liệu đọc từ NMPRP, Hermes xử lý, kết quả hiển thị lại trên NMPRP (màn hình AI Studio hiện có).

- **PL2**: danh mục kỹ thuật đang dự thảo (trước đây gọi PL3; đã đổi tên 03/09/2026, `docs/doi-ten-pl3-pl2/KE_HOACH.md`).
- **PL1**: danh mục phẫu thuật, thủ thuật (PT/TT).
- Mô hình chốt 02/10/2026: **vị trí của một PL2 là một nút của cây CPT**; mã CPT chỉ để tham khảo; mỗi PL2 đúng một nút.
  Lớp lưu vị trí nút **chưa có trên `main`** của NMPRP (theo `CLAUDE.md` của NMPRP).
- Trong từng nút: xếp PL2 và PL1 theo họ kỹ thuật, theo Kernel + Modifier.

## 2. Vì sao làm lại: hiện trạng đã ghi nhận ở NMPRP

| Vấn đề (chủ dự án nêu) | Bằng chứng |
|---|---|
| Tốn kém | Bước A2 gọi mô hình một lần cho mỗi cặp (PL2, nút), mỗi lần gửi lại toàn bộ prompt. Lượt thử 6 Nội tiết: 543 tác vụ, A2 = 388 lời gọi. Mã nguồn không dùng prompt caching. (`BAN_GIAO_CHUYEN_AGENT_KHAC_2026-10-16.md` mục 7) |
| Chậm | Mỗi lần bấm "Chạy tiếp" tối đa 3 lời gọi; chạy hết phải để tab mở. Bộ chạy nền phía máy chủ chưa làm. |
| Chưa hoàn chỉnh | Lượt `run_53b4c8…`: A3 hỏng 2/126 tác vụ do model trả JSON hợp lệ kèm chữ thừa (`Extra data`), `_parse_json_chat` (`cpn_ai_worker.py:234`) không xử lý; luật fail-closed chặn A4, A5, A6. 0 họ, 89 xung đột chưa giải. |
| Độ chính xác thấp | **Chưa đo được**: bàn giao 12/10 ghi 0 nhãn vàng xác nhận, benchmark trả `NOT_EVALUABLE`. Con số này cần kiểm lại. |

## 3. Ràng buộc từ NMPRP (Hermes phải giữ nguyên)

Nguồn: `BAN_GIAO_CHUYEN_AGENT_KHAC_2026-10-16.md` mục 4.

1. Chỉ **đề xuất**; không tự phê duyệt, không ghi lớp nguồn (`cpn_pl2`, `catalog_amendment`, `map_catalog_pairs`, `pair_curation`).
2. Mọi lời gọi mô hình trong NMPRP đi qua `ai_client.call_text` (công tắc AI). Thêm đường gọi mô hình khác phải hỏi chủ dự án.
3. Mã/ID luôn là TEXT; đặt tên chỉ "PL2".
4. Phản hồi sai hình dạng ⇒ `INVALID`, không đoán.
5. Prompt ghim theo phiên bản + SHA-256; không đổi mặc định khi chưa có benchmark trên nhãn vàng và chưa được chủ dự án chốt.
6. Một model không tự duyệt kết quả của chính nó.
7. Khoá API không bao giờ vào kho, log, prompt.

## 4. Nguyên tắc thiết kế

**Tách dữ liệu, tri thức và thủ tục.** Bộ nhớ gốc của Hermes rất nhỏ (`MEMORY.md` 2.200 ký tự, `USER.md` 1.375, không tự nén), nên không lưu bảng ánh xạ ở đó.

| Cần lưu | Nơi lưu | Tính năng Hermes |
|---|---|---|
| PL2, PL1, cây CPT, đề xuất, quyết định duyệt | CSDL NMPRP (nguồn sự thật) | Công cụ gọi API NMPRP |
| Bối cảnh: cấu trúc dữ liệu, mô hình nút, ranh giới | `AGENTS.md` của dự án | Context files |
| Vai trò: chỉ đề xuất, luôn nêu bằng chứng | `SOUL.md` | Context files |
| Quy trình ánh xạ, quy tắc Kernel + Modifier, tiêu chí họ | Skills (Git) | Skills, `skill_manage`, Curator |
| Quy ước ngắn đã chốt | `MEMORY.md`, `USER.md` | Bộ nhớ bền vững |
| Tiền lệ: "ca tương tự lần trước người duyệt chọn gì" | `state.db` + tìm toàn văn, hoặc tra API NMPRP | Tìm kiếm phiên |
| Chạy theo lịch, giám sát | Cron | `cronjob_manage` |
| Xử lý song song nhiều nút | Subagent | `delegate_task` |

Mọi điều Hermes "học" phải có nguồn (mã PL2, người duyệt, ngày).
Mỗi dự án một profile Hermes riêng; không để hai tiến trình agent ghi chung một thư mục Hermes.

## 5. Kiến trúc theo giai đoạn

### Giai đoạn 0: nền đo lường (làm trước, không cần Hermes)
- Chuyên gia gán nhãn vàng (24 mã chương Tai, 153 cặp âm khó đang chờ; `docs/cay-phan-nhom-ky-thuat-cpt/gold-set/`).
- Chốt chương thí điểm (đề xuất: 6 Nội tiết, đã có dữ liệu chạy) và đo mốc của dây chuyền hiện tại: độ chính xác trên nhãn vàng, token, chi phí, thời gian mỗi nút.
- **Không có bước này thì không chứng minh được bản Hermes tốt hơn.**

### Giai đoạn B: Hermes là bộ điều phối ngoài (theo "Cách B" của NMPRP)
- Hermes gọi API NMPRP: `POST /admin/cpn-ai/runs`, `POST …/runs/{id}/chay-me?n=`, `GET …/tien-do`, `/candidates`, `/conflicts`, `/families`, `/qa`, `/benchmark`, `/chi-phi`. Lời gọi mô hình vẫn nằm trong NMPRP; công tắc AI, kiểm hợp đồng, lease và ghi usage còn nguyên.
- Việc Hermes làm: chạy nền theo lịch cho tới hết lượt (không cần tab), thử lại tác vụ lỗi theo cách phù hợp ranh giới, báo tiến độ và chi phí, cảnh báo khi lỗi hoặc vượt hạn mức, và đọc quyết định duyệt để **đề xuất** phiên bản prompt mới.
- Quyền token dịch vụ: tối thiểu. Tạo và chạy lượt đang yêu cầu `require_admin` ở NMPRP; **không cấp quyền duyệt** (`require_studio`).
  Rủi ro cần xử lý: quyền admin rộng hơn việc cần làm; đề xuất NMPRP thêm một vai hẹp cho tạo/chạy lượt.
- Tiêu chí đạt: một lượt cho chương thí điểm chạy tới hết không cần tab; lỗi từng tác vụ không chặn các tác vụ khác; có báo cáo chi phí.

### Giai đoạn C thí điểm: Hermes xử lý theo nút, chế độ shadow, một chương
- Hermes xử lý mỗi nút: lấy ứng viên PL2/PL1, gọi bộ so khớp tất định của NMPRP như công cụ, gom mọi ứng viên của một PL2 vào một lần, dùng skill thay cho prompt lặp, tự kiểm lược đồ và tự sửa.
- **Cần ngoại lệ có kiểm soát từ chủ dự án** (phá "Cách C không khuyến nghị" và ràng buộc 2 ở mục 3): thêm một endpoint hẹp ở NMPRP để nhận đề xuất từ Hermes, mọi đề xuất đi qua `validate_proposal` và `cpn_ai_store` như agent trong nhà; không đường ghi tắt vào bảng nguồn.
- Chế độ shadow: đề xuất của Hermes chỉ được so với nhãn vàng và với dây chuyền hiện tại, chưa hiện cho người duyệt.
- Tiêu chí đạt (đặt trước khi chạy, chốt cùng chủ dự án): độ chính xác trên nhãn vàng không thấp hơn mốc; token mỗi PL2 giảm; không lỗi chặn dây chuyền.

### Vòng học (từ giai đoạn B)
Cron đọc quyết định duyệt → đề xuất sửa skill/prompt → cổng duyệt ghi skill (tài liệu nhắc cấu hình `skills.write_approval`, **chưa xác minh tên khóa trên máy thật**) → benchmark nhãn vàng → chủ dự án chốt → mới thành mặc định.

## 6. Đòn bẩy chi phí sẽ thử (mỗi cái đo trên nhãn vàng)
- Prompt caching cho phần hướng dẫn cố định.
- Gom A2 theo PL2 (NMPRP đã có cờ `limits.gom_a2`, mặc định tắt, chất lượng chưa đo).
- Chọn mô hình theo loại việc (Hermes cho ghim mô hình riêng theo job).
- Skill thay cho prompt dài lặp lại.

## 7. Rủi ro
- Chưa có nhãn vàng ⇒ mọi kết luận chất lượng đều vô căn cứ.
- Lớp lưu vị trí nút chưa có ⇒ Hermes chỉ đề xuất, chưa có nơi lưu kết quả cuối.
- Hermes và NMPRP cùng máy Rocky: cần giới hạn tải; Hermes và NMPRP tính chi phí mô hình riêng.
- Bộ nhớ sai lan ra hàng loạt: mọi quy tắc "học" phải có nguồn và qua benchmark.
- Quyền admin rộng cho token dịch vụ (mục 5, giai đoạn B).

## 8. Việc mở / quyết định cần chủ dự án
1. Số nhãn vàng đã xác nhận hiện nay và chương thí điểm.
2. Có sửa lỗi phân tích JSON (`_parse_json_chat`, đọc object đầu tiên + thử lại một lần) ở NMPRP bằng PR nhỏ riêng hay không. Việc này độc lập với Hermes.
3. Đồng ý ngoại lệ endpoint hẹp cho giai đoạn C hay không.
4. Có thêm vai hẹp "chạy lượt" ở NMPRP hay không.

## 9. Chưa kiểm chứng
- Cách Hermes gọi API NMPRP (terminal, MCP hay plugin) và nơi đặt token.
- Tên khóa cấu hình cổng duyệt ghi skill.
- Hiệu năng/chi phí thật của mọi đề xuất ở mục 6.
