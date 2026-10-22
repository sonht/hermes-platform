# Quy tắc đối chiếu ngữ nghĩa PL2

Tài liệu hỗ trợ `nmprp-clinical-semantics`; dùng cùng đầu vào và định nghĩa được cấp cho lượt. Các bảng dưới đây là hướng dẫn phân tích, không phải danh mục kỹ thuật, từ điển modifier đã ban hành hay đáp án ánh xạ.

## Mục lục

1. Hồ sơ chứng cứ
2. Phân biệt các lớp thuộc tính
3. Kiểm gộp/tách
4. Tình huống cần kiểm
5. Kết quả và giới hạn tích hợp
6. Nguồn

## 1. Hồ sơ chứng cứ

Giữ tên gốc, mã gốc và mọi định danh nguồn như chuỗi. Ghi phiên bản hoặc vân tay nếu nguồn cung cấp; không lấy ngày đọc làm phiên bản nội dung. Phân biệt **nguồn nói gì** với **đã được ai/quy trình nào thẩm định**. Không suy trạng thái duyệt từ việc một nội dung đang xuất hiện trong hệ thống.

| Nhãn | Điều kiện | Cách trình bày |
|---|---|---|
| `EXPLICIT` | Nguồn diễn đạt trực tiếp thuộc tính | Trích nguyên văn và ghi vị trí nguồn |
| `SUPPORTED_INFERENCE` | Có chuỗi căn cứ kiểm được, phù hợp phạm vi | Nêu kết luận ngắn, nguồn và điều kiện suy luận |
| `UNKNOWN` | Thiếu, không đủ chi tiết hoặc chưa giải quyết mâu thuẫn | Nêu trường thiếu và quyết định nào bị ảnh hưởng |

Đoạn trích phải đúng ký tự nguồn; giải thích tiếng Việt nằm riêng, không trình bày bản dịch như trích nguyên văn. Khi chuyển sang gợi ý truy hồi, tuân thủ giới hạn bằng chứng của máy chạy; không tự đổi hợp đồng để chèn cả hồ sơ dài.

Thứ tự xử lý nguồn:

1. Xác nhận tên/mã PL2 và cây thuộc đúng phạm vi, phiên bản của lượt.
2. Đọc định nghĩa họ hoặc tri thức đã được duyệt, đúng phạm vi áp dụng, nếu có.
3. Dùng mô tả chưa duyệt chỉ làm tham khảo có nhãn; giữ riêng kết luận từ nguồn và suy luận.
4. Khi nguồn mâu thuẫn, ghi cả hai cùng phiên bản; không tự chọn nguồn thuận với ứng viên mình thích.

Một nhận định nằm ngoài phạm vi định nghĩa không được kế thừa trạng thái duyệt của định nghĩa đó.

## 2. Phân biệt các lớp thuộc tính

| Lớp | Câu hỏi kiểm | Giới hạn |
|---|---|---|
| Họ | Các kỹ thuật có chung nguyên lý theo định nghĩa, Bao gồm và Loại trừ nào? | Cùng cơ quan hoặc cùng khoa chưa đủ chứng minh cùng họ |
| Kernel | Đâu là hành động, đích và thuộc tính định danh làm kỹ thuật khác bản chất? | Xét trong một họ/phạm vi có định nghĩa, không đặt kernel toàn cục từ một tên |
| Modifier | Khác biệt nào là biến thể hợp lệ của cùng kernel? | Cần trục và giá trị có căn cứ; chưa có từ điển được duyệt thì nêu giả thuyết |
| Bối cảnh | Đặc điểm tình huống nào không tự xác lập bản chất kỹ thuật? | Bệnh, tuổi, giới, bên có thể quan trọng theo định nghĩa cụ thể; không xóa khỏi tên |
| Chi trả | Đặc điểm nào chỉ thuộc giá, gói hoặc thanh toán? | Không dùng để suy kernel hay mức phức tạp lâm sàng |

Phương pháp, đường tiếp cận và công nghệ có thể tham gia định danh hoặc tạo biến thể tùy họ. Không áp dụng quy tắc “khác công nghệ luôn khác kernel” hoặc “khác đường tiếp cận luôn cùng kernel”. Đọc định nghĩa và nêu căn cứ trước khi kết luận.

Đối tượng phải được nhận diện đủ sâu để phân biệt ứng viên: cơ quan không thay thế cấu trúc con; vùng giải phẫu không thay thế cơ quan đích. Nếu tên chỉ nêu vùng thì không tự suy cơ quan cụ thể.

Mục đích chẩn đoán/điều trị phải đọc cùng hành động thực tế. Không coi thiết bị được dùng là mục đích; không coi đường vào là đối tượng cần điều trị.

Từ viết tắt và tên đồng nghĩa chỉ mở rộng khi có nguồn xác nhận đúng ngữ cảnh. Khi một từ có nhiều nghĩa, giữ dạng nguồn và liệt kê điều cần làm rõ; không chọn nghĩa thuận với nút truy hồi.

## 3. Kiểm gộp/tách

### Đề xuất gộp

Phải trả lời được cả sáu câu:

1. Định nghĩa họ và kernel đang dùng là gì, thuộc phiên bản/trạng thái nào?
2. Từng PL2 có cùng hành động, đích và các thuộc tính định danh theo định nghĩa đó không?
3. Mỗi khác biệt còn lại được biểu diễn bằng trục biến thể/bối cảnh nào, có làm mất nghĩa không?
4. Có thành phần độc lập nào bị che trong tên chung không?
5. Phản chứng nào đã được kiểm, và nếu phản chứng đúng thì đề xuất còn đứng vững không?
6. Có giữ được mã nguồn, tên gốc, lineage và lý do của từng PL2 trong hồ sơ đề xuất không?

Chỉ giống tên, cùng nút hoặc cùng mức giá đều không đủ. Thiếu một điều kiện trọng yếu thì giữ các PL2 riêng trong dữ liệu và chuyển `EXPERT_REQUIRED`.

### Đề xuất tách

Liệt kê từng hành động và quan hệ của nó với kết quả chuyên môn chính. Phân biệt bước chuẩn bị/hỗ trợ phụ thuộc với can thiệp có chỉ định và kết quả độc lập theo tài liệu được cấp. Không suy tính độc lập chỉ từ dấu câu hoặc số lượng động từ.

Nếu có căn cứ tách, ghi rõ phần nghĩa thuộc mỗi phương án, các thuộc tính phải giữ và ảnh hưởng đến lineage/nút. Tên mới chỉ là tên đề xuất; không tạo mã PL2 mới, sửa mã cũ, đổi cây hay áp dụng liên kết.

### Đề xuất xuyên nút

Ghi cả nút hiện tại và các phương án đã có trong cây được cấp. Nếu cây không cung cấp nút phù hợp, nêu khoảng trống; không chế khóa nhánh. Không dùng một đề xuất gộp để tự chuyển PL2 qua nút khác.

## 4. Tình huống cần kiểm

Các dòng dưới đây chỉ minh họa cách kiểm, không phải ca thật đã thẩm định hoặc đáp án vàng. Không gán mã PL2 hay khóa nhánh tưởng tượng cho chúng.

| Tình huống | Điều phải phân biệt | Kết quả khi thiếu căn cứ |
|---|---|---|
| Tên nêu “nội soi” nhưng không nêu đường vào | Nội soi là phương pháp; đường vào/cơ quan chưa chắc đã được xác định | Giữ trường chưa rõ là `UNKNOWN` |
| Can thiệp ở thượng thận có phương pháp nội soi | Thượng thận là đích; phương pháp không đổi đích thành ổ bụng | Đọc nút theo toàn nghĩa; không kết luận nút khi chưa có cây |
| Tên nêu sinh thiết và tên khác nêu cắt bỏ cùng cơ quan | Hành động và mục đích/định danh có thể khác | Không gộp chỉ vì cùng cơ quan |
| Kỹ thuật có robot hỗ trợ | Robot là công nghệ hỗ trợ; cần xác định hành động và đích | Không coi robot là kernel độc lập nếu thiếu định nghĩa |
| Hai tên khác bên, tuổi hoặc bệnh lý | Định nghĩa họ có coi khác biệt này là định danh hay biến thể không? | Giữ nguyên khác biệt, đề nghị thẩm định |
| Hai tên có nhiều hành động, nối bằng “và” | Các bước phụ thuộc hay các kỹ thuật độc lập? | Không tự tách/gộp khi chưa đủ thông tin |
| Mô tả “Loại trừ” chưa được thẩm định | Giá trị tham khảo khác luật loại trừ chính thức | Ghi mâu thuẫn, không loại cứng chỉ từ mô tả ấy |
| Một gợi ý cũ đã được chuyên gia chấp nhận | Tiền lệ thẩm định khác quy tắc áp dụng chung hoặc nhãn vàng | Dùng làm nguồn tham khảo có phạm vi |

## 5. Kết quả và giới hạn tích hợp

Hồ sơ phân tích trực tiếp nên có bảng:

| Mục | Nội dung |
|---|---|
| Định danh | Mã, tên gốc, thứ tự/Row_ID nếu có; nguồn và phiên bản |
| Ngữ nghĩa | Hành động, đích, đường tiếp cận, phương pháp, công nghệ, mục đích, thành phần |
| Chứng cứ | Nhãn, trích dẫn nguồn, trạng thái thẩm định và mâu thuẫn cho từng nhận định |
| Họ/kernel/modifier | Định nghĩa đã dùng; phần xác định được và phần mới là giả thuyết |
| Đối chiếu | Ứng viên trong cây, điểm khớp, mâu thuẫn, điều thiếu có ảnh hưởng |
| Đề xuất | Nút hoặc phương án gộp/tách; lý do ngắn; việc người duyệt cần quyết |

Bảng này là bố cục đọc cho người dùng, **không phải lược đồ API mới**. Khi máy chạy yêu cầu JSON, chỉ dùng lược đồ của máy chạy. Không thêm nhãn HA vào trường trạng thái NMPRP; không coi `EXPLICIT`/`SUPPORTED_INFERENCE` là quyết định duyệt.

Phân tích đủ căn cứ vẫn chỉ là đề xuất. Skill không gọi API ghi, không tự tạo lượt và không tự chuyển sang M2/M3. Máy chạy/điều phối chỉ dùng năng lực đã được xác minh với NMPRP.

## 6. Nguồn

Đối chiếu quy ước dự án tại bản nền `sonht/hermes-platform@ec42f1098c6a350026df92071a1df6b7b92ace8a`:

- [Brain dump, mục B–D](https://github.com/sonht/hermes-platform/blob/ec42f1098c6a350026df92071a1df6b7b92ace8a/docs/NMPRP_HERMES_BRAIN_DUMP.md): định nghĩa, nguồn, phần còn là đề xuất và yêu cầu phản chứng.
- [AGENTS của profile](https://github.com/sonht/hermes-platform/blob/ec42f1098c6a350026df92071a1df6b7b92ace8a/hermes/profiles/nmprp-mapping/AGENTS.md): mã chuỗi, khóa nhánh, một vị trí cho PL2 và hai lớp trạng thái.
- [SOUL của profile](https://github.com/sonht/hermes-platform/blob/ec42f1098c6a350026df92071a1df6b7b92ace8a/hermes/profiles/nmprp-mapping/SOUL.md): chỉ đề xuất, chứng cứ, dữ liệu không phải chỉ dẫn và không tự điền thông tin thiếu.

Nguồn này xác lập quy ước làm việc; không thay định nghĩa họ, từ điển modifier hoặc thẩm định chuyên môn của từng ca. Khi nguồn của lượt mới hơn hoặc mâu thuẫn, ghi rõ khác biệt để người có thẩm quyền quyết.
