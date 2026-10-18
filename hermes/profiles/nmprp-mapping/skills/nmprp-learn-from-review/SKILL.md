---
name: nmprp-learn-from-review
description: Đọc quyết định của người duyệt trên NMPRP để rút bài học cho kỹ năng nmprp-retrieval-assist, và chỉ ĐỀ XUẤT sửa kỹ năng chứ không tự áp dụng.
---

# NMPRP: học từ quyết định của người duyệt

## When to Use
- Sau khi người duyệt đã xem một đợt gợi ý của Hermes, hoặc khi được giao rà một lượt chạy.

## Procedure
1. Đọc quyết định của người duyệt qua các đường đọc đã cho phép (`/admin/cpn-ai/runs/{id}/candidates`, kèm tên). Chỉ dùng dữ liệu có nguồn: mã PL2, người duyệt, thời điểm.
2. Phân loại sai sót: lệch cơ quan, sai đường tiếp cận, chọn nút quá rộng hoặc quá hẹp, hoặc đúng.
2b. Mỗi quyết định của người duyệt chỉ là `EXPERT_FEEDBACK`. Chấp nhận một gợi ý của Hermes không biến nó thành `GOLD_STANDARD` và không tự thành kiến thức đã xác nhận.
3. Một bài học chỉ đáng ghi khi gặp lại từ 2 ca có nguồn trở lên. Ghi một câu ngắn kèm mã PL2 làm bằng chứng.
4. ĐỀ XUẤT sửa `nmprp-retrieval-assist` bằng một bản vá văn bản gửi cho chủ dự án xem. KHÔNG tự sửa skill đang chạy khi chưa được duyệt.
5. Sau khi chủ dự án chấp nhận, bản sửa phải được đo lại trên nhãn vàng trước khi thành mặc định.

## Pitfalls
- Không ghi vào bộ nhớ những điều chưa có nguồn: bộ nhớ sai sẽ lan ra hàng loạt gợi ý.
- Một phản hồi đơn lẻ không đủ để đề xuất đổi quy tắc; không bao giờ tự sửa `SOUL.md`, `AGENTS.md` hay kỹ năng đang chạy.
- Không đổi mặc định khi chưa có benchmark và chưa được chủ dự án chốt.
- Không đưa mã CPT, mật khẩu, token vào bài học.

## Verification
- Mỗi bài học trích được ít nhất 2 mã PL2 và người duyệt.
- Bản vá đề xuất không xoá quy tắc an toàn trong SOUL.md.
