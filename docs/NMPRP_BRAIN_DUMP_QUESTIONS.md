# Danh sách câu hỏi "brain dump" cho Hermes (dự án NMPRP)

Trả lời MỘT lần, ngắn gọn (một hai câu mỗi ý là đủ). Dấu ★ = quan trọng nhất; nếu ít thời gian, trả lời các câu ★ trước.
**Không đưa vào câu trả lời:** mật khẩu, token, khoá API, dữ liệu bệnh nhân, mã CPT (trừ khi bạn đã quyết bật công tắc CPT).
Câu trả lời sẽ được Claude biên thành nội dung cho `SOUL.md`, `AGENTS.md`, các kỹ năng và bộ nhớ, rồi bạn đọc lại trước khi cài.

## A. Thẩm quyền và người duyệt (→ AGENTS.md, SOUL.md)
1. ★ Ai là người duyệt gợi ý của Hermes, và ai quyết định cuối khi hai người duyệt khác ý nhau?
2. ★ Gợi ý đạt mức nào thì đáng đưa cho người duyệt? (ví dụ chỉ gửi khi độ tin cậy từ bao nhiêu trở lên; tối đa mấy gợi ý cho một PL2)
3. Khi Hermes không chắc: bỏ qua và ghi "không đủ căn cứ", hay vẫn gửi kèm độ tin cậy thấp?

## B. Thuật ngữ và quy ước (→ AGENTS.md, MEMORY.md)
4. ★ Giải thích bằng lời của bạn, mỗi từ một hai câu: PL1, PL2, nút, họ, kernel, modifier.
5. Các từ hay viết tắt trong tên kỹ thuật và nghĩa (nội soi, robot, qua da, mổ mở, ...).
6. ★ Khi tên PL2 không ghi phương pháp (mổ mở hay nội soi hay robot), hiểu mặc định là gì? (NMPRP đang để ngỏ câu hỏi này)
7. Có cho Hermes dùng văn bản "Bao gồm / Loại trừ" của nút khi đề xuất không? (NMPRP ghi đây là hướng dẫn chưa thẩm định)
8. Quy ước đặt tên, chữ hoa chữ thường, dấu mà Hermes phải giữ.

## C. Quy tắc chọn nút (→ kỹ năng nmprp-retrieval-assist)
9. ★ Một kỹ thuật có thể vào hai nút (theo cơ quan, theo hệ cơ quan, theo phương pháp): ưu tiên theo thứ tự nào?
10. Kỹ thuật gồm nhiều bước: đặt theo bước chính, hay theo tiêu chí khác?
11. Chẩn đoán, điều trị, xét nghiệm, điện quang nằm ở đâu?
12. Tiêu chí để nói một nút là "quá rộng" hoặc "quá hẹp".
13. ★ Các cặp cơ quan hay bị nhầm (ví dụ tuyến giáp và cận giáp; tuyến thượng thận và nội soi ổ bụng) và cách phân biệt.
14. Nhóm kỹ thuật nào luôn để chuyên gia tự xem, không để Hermes đề xuất?

## D. Ví dụ (→ kỹ năng, dùng làm ca mẫu; có thể trở thành nhãn vàng sau khi chuyên gia xác nhận)
15. ★ Ba ví dụ ánh xạ ĐÚNG: mã PL2, tên, khoá nhánh của nút, vì sao đúng.
16. ★ Ba ví dụ ánh xạ SAI hay gặp: mã PL2, nút sai, nút đúng, vì sao sai.
17. Ba ví dụ khó, mơ hồ, và bạn xử lý thế nào.
18. Bốn PL2 chưa có ứng viên (6.71, 6.107, 6.111, 6.120): theo bạn nút nào là đúng? (đây là ý kiến của bạn, sẽ ghi rõ là chưa thẩm định)

## E. Học và chất lượng (→ nmprp-learn-from-review)
19. Bạn muốn Hermes học theo kiểu nào: nhiều ví dụ nhỏ hay quy tắc rõ ràng? Bao lâu rà một lần?
20. Bao nhiêu ca lặp lại thì thành một quy tắc? (đề xuất: từ 2 ca có nguồn)
21. ★ Ai duyệt một thay đổi kỹ năng, và dựa vào số đo nào để chấp nhận (ví dụ độ chính xác trên nhãn vàng không giảm)?
22. ★ Nhãn vàng: đã có bao nhiêu mục chuyên gia xác nhận, ai gán, kế hoạch ra sao?

## F. Vận hành và giới hạn (→ cấu hình cron, README)
23. ★ Hạn mức chi phí cho khoá Claude API của Hermes (theo ngày, tuần hoặc tháng) và ai nhận cảnh báo.
24. Lịch chạy mong muốn (hằng đêm, theo yêu cầu) và các khung giờ KHÔNG được chạy (cao điểm của dm.kcb.vn).
25. Kênh nhận thông báo (chỉ trong tab, Telegram, email) và loại nội dung được gửi qua kênh đó.
26. Khi lỗi liên tiếp: dừng hay thử lại, và dừng sau mấy lần?
27. ★ Ai được phép dừng khẩn cấp Hermes (`hermes pause`), và dấu hiệu nào thì phải dừng?

## G. Ranh giới dữ liệu (→ SOUL.md)
28. ★ Dữ liệu nào tuyệt đối không được vào lời nhắc, bộ nhớ hay nhật ký của Hermes?
29. Có cho Hermes ghi tên người duyệt vào bộ nhớ không?
30. ★ Mã CPT: giai đoạn thí điểm bạn bật công tắc cho phép, hay giữ tắt?

## H. Giọng văn (→ SOUL.md)
31. Độ dài và giọng của phần "lý lẽ" trong mỗi gợi ý (ngắn một hai câu?), dùng thuật ngữ tiếng Việt hay tiếng Anh?
32. Điều gì ở các trợ lý trước làm bạn bực nhất, để loại ngay từ đầu?

## Cách tôi dùng câu trả lời
- A, B, G, H thành `SOUL.md`, `AGENTS.md`, `MEMORY.md` (đúng giới hạn ký tự).
- C và D thành kỹ năng `nmprp-retrieval-assist` (quy trình và ca mẫu). Ca mẫu KHÔNG tự thành nhãn vàng; nhãn vàng cần người gán độc lập.
- E, F thành cấu hình học và cron. Mọi thay đổi chỉ là đề xuất cho đến khi bạn duyệt.
