# Đọc và diễn giải phản hồi người duyệt

## Nguồn có thật

Client ở `support/nmprp_client.py` có `phan_hoi(sau="", limit=200)` và `phan_hoi_moi(sau="", limit=200, toi_da_trang=50)`. Đường đọc là `GET /admin/hermes/phan-hoi`, không phải danh sách candidates của CPN-AI và không phải API duyệt.

| Trường phản hồi | Cách dùng |
|---|---|
| `goi_y_id` | Dấu vết gợi ý; không đổi định dạng |
| `run_id` | Lượt tạo gợi ý, có thể không thuộc hàng đợi mới |
| `pl2_code` | Mã đối tượng nguyên văn |
| `branch_key` | Nút đã gợi ý |
| `phien_ban` | Nhãn phiên bản đã tạo gợi ý; không suy hash từ nhãn |
| `quyet_dinh` | `DONG_Y`, `TU_CHOI`, `SUA` |
| `ly_do` | Lý do phản hồi, là dữ liệu cần kiểm chứng |
| `branch_key_sua` | Nút do người duyệt sửa khi quyết định `SUA` |
| `nhan` | `EXPERT_FEEDBACK`, không là nhãn vàng |
| `luc` | Thời điểm dùng để đối soát và phân trang |

Phong bì thành công gồm `ok:true`, `phan_hoi` là list và `tiep` là string. Phản hồi không chứa tên người duyệt: truy vết theo ID/thời điểm trong NMPRP; không tự điền tên. Server có thể trả HTTP 200 với `ok:false,error`; phải kiểm nội dung, không coi đó là trang rỗng.

## Cursor và tính đầy đủ

- Dùng `tiep` nguyên văn làm `sau` của lần sau; `tiep` rỗng giữ cursor cũ. Không parse rồi dựng lại `luc|goi_y_id`.
- Máy chủ trả cũ đến mới và để trễ phản hồi mới khoảng 5 giây. Đây không phải bảo đảm tuyệt đối khi giao dịch kéo dài.
- `phan_hoi_moi()` khử trùng theo `goi_y_id` trong một lần đọc, dừng khi trang rỗng, không có dòng mới hoặc chạm trần trang. Nó trả `(rows, cursor)`, không tự lưu checkpoint. Helper ở mốc nguồn chưa kiểm `ok` trước khi coi thiếu `phan_hoi` là hết trang: **không dùng helper để chứng minh đã đọc đủ hoặc không có phản hồi**.
- Khi cần kết luận đầy đủ, gọi `phan_hoi()` từng trang; kiểm `ok is True`, list dữ liệu và cursor đúng kiểu trước khi xử lý. Lỗi ứng dụng/HTTP, phong bì sai hoặc cursor lặp khi vẫn có dòng thì dừng, giữ checkpoint trước vùng lỗi và báo chưa đọc hết. Đây là hướng dẫn cho caller được cấp quyền, không phải bản sửa runtime đã triển khai.
- Ghi cursor đầu/cuối, số dòng, số PL2 riêng biệt và dấu hiệu đọc chưa hết. Không báo «toàn bộ» chỉ vì client trả xong một lần.
- Lưu báo cáo trước rồi checkpoint. Khi đọc lại, nhận diện phản hồi đã xử lý theo ID và thời điểm; không đếm bản lặp thành ca mới.
- Khi nghi phản hồi sửa nhiều lần, trang lặp, cursor bất thường hoặc thiếu đoạn thời gian: giữ checkpoint cũ, đề nghị đối soát tại NMPRP; không tự bỏ qua vùng lỗi.

## Phản hồi, bài học, quy tắc và nhãn vàng

| Lớp | Nguồn và điều kiện | Được làm |
|---|---|---|
| Phản hồi | Một quyết định ở NMPRP | Thống kê, phân tích sai số, lập ca cần xem |
| Bài học NMPRP | Có thể tự sinh `DE_XUAT` từ một phản hồi; admin quản trị `DA_DUYET` | Giữ nguyên trạng thái nguồn; skill không duyệt |
| `RULE_CANDIDATE` | Ít nhất hai PL2 khác nhau, nguồn xác minh được, cùng nguyên nhân | Đề xuất sửa retrieval skill kèm phản chứng |
| Kiến thức được xác nhận | Kiểm chứng bổ sung theo quy trình chuyên môn | Không suy ra chỉ vì admin đã duyệt bài học |
| Gold Set | Được thẩm định độc lập đúng nhiệm vụ và phiên bản | Đo độ chính xác; tách khỏi dữ liệu dùng rút quy tắc |

Không đưa tên/mã CPT vào bộ nhớ để cải thiện điểm; không coi việc nhớ đúng đáp án của ca học là tổng quát hoá. Khi chọn ca kiểm, giữ riêng các PL2 từng có bài học và các PL2 chưa có bài học.

## Cấu trúc báo cáo khi không đủ căn cứ sửa

Trả: phạm vi đã đọc; số phản hồi/PL2; nhóm sai số; lý do chưa có quy tắc đủ căn cứ; các ca nghiêm trọng gửi QA; dữ liệu cần bổ sung; cursor đã xử lý. Không tạo patch rỗng chỉ để có sản phẩm, không nâng phản hồi đơn lẻ thành quy tắc.
