# Quy tắc chọn nút và từ chối có lý do

## Thứ tự xét

1. Giữ bản gốc và xác nhận phạm vi đầu vào.
2. Phân rã ngữ nghĩa trước khi xem điểm truy hồi.
3. Tìm nhóm/nút theo hành động và đối tượng; dùng đường tiếp cận, phương pháp, mục đích để phân biệt.
4. So đối thủ thật trong cùng cây. Nếu chỉ có một nút liên quan thì ghi điều đó, không tạo đối thủ để đủ biểu mẫu.
5. Chọn, nêu xung đột hoặc từ chối; không lấy điểm làm bằng chứng thay cho diễn giải.

## Bảng quyết định

| Tình huống | Hành vi |
|---|---|
| Cùng từ nhưng khác cơ quan | Loại ứng viên; không dùng điểm ngôn ngữ để bù lỗi |
| Đúng cơ quan nhưng khác hành động (sinh thiết/cắt bỏ…) | Kiểm định nghĩa và nút cạnh tranh; thiếu căn cứ thì không nâng mức |
| Không có thông tin đường tiếp cận | Ghi UNKNOWN; không mặc định mổ mở, nội soi, qua da hoặc robot |
| Can thiệp có hướng dẫn hình ảnh | Xác định hành động chính; không tự lấy nút hướng dẫn làm vị trí chính |
| Phẫu thuật có nhiều thành phần | Liệt kê thành phần; không làm mất thành phần hoặc tự chia mã |
| Hai nút đều có căn cứ, thiếu dữ kiện phân biệt | `EXPERT_REQUIRED`; ghi câu hỏi người duyệt cần quyết |
| Không có nút đủ căn cứ sau khi đã xét dữ liệu | `NO_SAFE_MATCH`, mảng đề xuất rỗng, giải thích phạm vi đã xét |
| Thiếu cây, tên bị cắt hoặc nguồn mâu thuẫn khiến chưa xét được | `UNRESOLVED`, mảng rỗng; không ghi như đã truy hồi thất bại |
| Chỉ thiếu từ khoá trùng nguyên văn | Chưa đủ lý do loại nút; xem quan hệ giải phẫu/ngữ nghĩa có trong dữ liệu |
| Có mô tả Bao gồm/Loại trừ được adapter cung cấp | Ghi nguồn và tình trạng duyệt; phân biệt nguồn trống, chưa rõ, không xung đột và bị loại trừ |

## Bảo toàn khi có nhiều phương án

Mỗi PL2 vẫn là một đối tượng nguồn. Ba ứng viên là danh sách xếp hạng để người duyệt chọn một vị trí, không là thao tác tạo ba bản ghi danh mục. Không đổi mã/tên gốc, không gộp các mã có số gần nhau, không chuẩn hoá số 0 đầu/cuối. Tên kháng nguyên phải giữ phân biệt hoa/thường.

## Cổng mức cao

Mức cao cần căn cứ đầy đủ và xác nhận cổng QG-16 của lượt. Có điểm cao không thay điều kiện cổng. Không thấy QG-16 trong đầu vào M1 hiện có thì dùng mức thấp hơn; không yêu cầu công cụ không tồn tại để tìm cổng. Chấp nhận bị máy chủ hạ mức và lưu đúng mức thực nhận khi đối soát.

## Những gì không được suy từ kết quả

- Trích dẫn hợp lệ chỉ chứng minh nguồn có câu đó, không tự chứng minh ánh xạ đúng.
- Một gợi ý được chuyên gia đồng ý vẫn là phản hồi; chỉ bộ nhãn vàng được thẩm định riêng dùng để đo độ chính xác.
- Nút đúng không chứng minh hai PL2 cần gộp; cùng họ/kernel không cho quyền sửa danh mục.
- Skill viết đúng không chứng minh runtime đã nạp đúng; phải kiểm file, reference và phiên chạy.
