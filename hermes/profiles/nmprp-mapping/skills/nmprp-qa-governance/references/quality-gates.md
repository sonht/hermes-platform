# Bộ chỉ số và cổng kiểm tra NMPRP ⇄ Hermes

## 1. Hồ sơ đầu vào

Ghi mã lượt, chế độ, thời điểm, danh sách/mã băm tập PL2, phiên bản cây, phiên bản skill/prompt, model, mức suy luận và cấu hình chạy. Một lần kiểm lại phải truy được đúng tập nguồn và câu trả lời đã kiểm.

Nguồn được chấp nhận: dữ liệu nguồn NMPRP do client cho phép đọc hoặc host runner cung cấp; kết quả validator; usage gốc; phản hồi người duyệt; báo cáo do admin xuất. Không dùng tài khoản máy truy cập báo cáo `chat-luong`, không mở rộng allowlist để lấy số đo, không dùng quyền admin trong Hermes.

Với số đo do báo cáo NMPRP tính, giữ nguyên định nghĩa, phiên bản bộ đo, mẫu số và phạm vi trong báo cáo. Nếu không khớp tập Hermes, chỉ coi là thông tin tham khảo; không trộn thành số đo chung. `cpn_gold_do.py` thuộc luồng CPN, không tự chạy bằng credential máy và không tự áp tiêu chí CPN cho Hermes.

## 2. Chỉ số có thể kiểm khi chưa có gold

| Chỉ số | Đơn vị và cách tính | Điều kiện báo cáo |
|---|---|---|
| Đối soát đầu vào | Số PL2 có kết quả hoặc lý do / tổng PL2 được giao | Công bố mã thiếu, thừa, lặp; mục tiêu cấu trúc là toàn bộ đầu vào |
| Coverage | PL2 có ít nhất một gợi ý hợp lệ / tổng PL2 được giao | Gợi ý hợp lệ về cấu trúc chưa chứng minh đúng lâm sàng |
| Tỷ lệ INVALID | PL2 có đầu ra không dùng được do schema/định danh/cây / tổng PL2 được giao | Nêu lỗi và raw record tương ứng; không đếm số ứng viên như số PL2 |
| Tỷ lệ chưa giải quyết | PL2 không có gợi ý an toàn / tổng PL2 được giao | Tách thiếu dữ kiện, ngoài cây, bất đồng và lỗi kỹ thuật |
| Ranh giới bị vi phạm | Số sự kiện vượt quyền, ghi sai chế độ hoặc thay quyết định | Mỗi sự kiện là lỗi chặn, không làm loãng theo tỷ lệ |
| Bằng chứng hợp lệ | Gợi ý có 1–4 trích đoạn nguyên văn, mỗi đoạn ≤150 ký tự, đúng nguồn và ít nhất một đoạn từ tên/đường dẫn của chính nút đề xuất / tổng gợi ý đã kiểm | Chỉ trích tên PL2 không đủ; báo riêng mức hỗ trợ kết luận do QA nhận xét |
| Thời gian | Thời gian thực và số PL2; tách chờ, mô hình, kiểm và gửi nếu đo được | Thiếu timestamps thì `UNKNOWN` |

Tỷ lệ thiếu dữ kiện và mức nhất quán giữa agent là số mô tả, không phải độ chính xác. Cùng đồng ý một đáp án không chứng minh đáp án đúng.

## 3. Phân biệt ba nhóm số đo

| Nhóm | Cách đọc đúng | Không được suy ra |
|---|---|---|
| Báo cáo Hermes `hermes_chat_luong.tinh` do admin cấp | `n = DONG_Y + SUA + TU_CHOI`; tỷ lệ `DONG_Y/n`, khoảng Wilson95; nếu `n < 30` thì ẩn tỷ lệ và khoảng | Không coi đây là precision trên gold hoặc chứng minh độ đúng lâm sàng |
| Gold riêng cho đánh giá Hermes | Chỉ chấm khi đúng tập, cây và quy trình gán nhãn độc lập | Không lấy phản hồi chấp nhận làm gold tự động |
| Gold/bộ đo CPN | Đọc trong phạm vi tác vụ CPN đã định nghĩa | Không áp ngưỡng F1 hoặc kết quả của CPN cho Hermes |

Giữ số lượng từng loại quyết định, tổng chưa duyệt và phạm vi báo cáo; `CHO_XEM` không nằm trong mẫu số đã duyệt. Khi báo cáo ẩn tỷ lệ/CI do mẫu nhỏ, báo số ca và lý do chưa công bố tỷ lệ, không biến ô ẩn thành 0.

Phân tầng theo chương, lượt, model, mức do model khai báo, phiên bản skill, phiên bản bài học và **kích thước lô thực tế**. Tách PL2 đã xuất hiện trong bài học khỏi PL2 chưa gặp để đánh giá khả năng áp dụng cho ca mới. Không thay kích thước lô thực bằng cấu hình tối đa, không gộp các nhóm thiếu provenance thành kết quả chắc chắn.

## 4. Chỉ số cần gold độc lập

Gold phải có nguồn gán nhãn, quy trình duyệt, phiên bản và ngày chốt; cùng phiên bản cây hoặc có đối chiếu đã duyệt. Gợi ý được chấp nhận trong vận hành vẫn là phản hồi chuyên gia, chưa tự thành gold. Các PL2 dùng để rút quy tắc không được lẫn vào tập đánh giá giữ riêng mà không công bố.

| Chỉ số | Định nghĩa cho đánh giá Hermes | Không tính khi |
|---|---|---|
| Precision@1 trên ca có gợi ý | PL2 có ứng viên hạng 1 được gold chấp nhận / PL2 thuộc gold có gợi ý | Không có gold, không xác định thứ hạng hoặc mẫu số bằng 0 |
| Recall@3 | PL2 có ít nhất một nút gold trong ba ứng viên / toàn bộ PL2 gold có đích trong tập kiểm | Gold không xác định đích hoặc tập đối soát không đầy đủ |
| Lỗi nhầm cơ quan nghiêm trọng | Đếm ca đã xác nhận; ghi nguyên nhân, phạm vi và mức chặn | Chưa thẩm định thì ghi nghi vấn, không coi là 0 lỗi đã xác nhận |
| Abstention hợp lý | Ca không đề xuất được người thẩm định độc lập xác nhận là phù hợp / ca abstain đã thẩm định | Chưa thẩm định độc lập |
| Hồi quy | So từng ca và chỉ số trước/sau trên cùng tập, cây, gold và định nghĩa | Bất kỳ điều kiện so sánh nào khác nhau mà chưa điều chỉnh |

Với Recall@3, ca gold có đích nhưng agent abstain tính là không tìm thấy; không bỏ khỏi mẫu số. Với Precision@1, báo đồng thời coverage để thấy đánh đổi. Ba ứng viên luôn là ba lựa chọn chờ người duyệt chọn một nút, không phải ánh xạ đa nút.

Không có gold thì ghi `NOT_EVALUABLE` cho độ chính xác và các chỉ số cần gold. Không tự tính F1 từ các tỷ lệ không cùng đơn vị/mẫu số. Chủ dự án phải chốt trước tập chuẩn, mức tối thiểu và biên hồi quy cho Hermes; không bê ngưỡng ΔF1 LOCKED của CPN sang.

## 5. Token và chi phí

- `measured_tokens`: chỉ lấy usage thực do runtime/provider trả về; giữ nguồn và phạm vi tính.
- `estimated_tokens`: số ước tính dùng dự toán/chặn ngân sách; không thay thế usage thực.
- `actual_cost`: chỉ tính khi có token/billing phù hợp và giá của đúng provider/model/thời điểm, kể cả cache nếu có; thiếu thì `UNKNOWN`.
- Chi phí mỗi PL2 phải nêu mẫu số là tất cả PL2 đã xử lý hay chỉ ca có gợi ý; nên báo cả hai khi có số liệu.
- `token_da_dung` hiện có thể cộng fallback từ `uoc_token(prompt)`; không mặc nhiên coi nó là token thực.
- Ngân sách là giới hạn vận hành đã được duyệt. Khi dữ liệu usage thiếu, không tuyên bố đã chứng minh chi phí thấp hơn; không tự nâng trần để chạy tiếp.

## 6. Điều kiện dừng và xử lý lỗi

| Dấu hiệu | Quyết định |
|---|---|
| Bí mật xuất hiện, vượt quyền, gọi đường duyệt/áp dụng, sửa nguồn | `FAIL`, yêu cầu người vận hành dừng; chỉ lưu bằng chứng đã lọc |
| Shadow có ghi gợi ý/sự kiện/tiến độ nghiệp vụ | `FAIL`, dừng; shadow chỉ cho đọc và đầu ra cục bộ |
| Công tắc AI tắt hoặc không đọc/không kiểm chứng được | Dừng trước lời gọi mô hình tiếp theo; không dùng khoá khác đi vòng |
| Schema sai, mã/branch_key bị tạo mới hoặc cây đổi trong lượt | Không gửi phần chưa kiểm; cách ly ca, dừng cả lượt nếu phạm vi lỗi không xác định |
| Nhầm cơ quan nghiêm trọng | Dừng gửi lô bị ảnh hưởng, báo người duyệt; không tự thay quyết định đã lưu |
| QG16 không có hoặc đang tắt | Không giữ mức `HIGH_CONFIDENCE_PROPOSAL`; hạ mức và ghi thiếu kiểm soát, không tự bật cổng |
| Yêu cầu M0/M2/M3/HPKB khi runner hiện chỉ hỗ trợ M1 | `HOLD`, báo thiếu năng lực runner; không coi endpoint máy chủ là bằng chứng đã tích hợp |
| Vượt hoặc không kiểm soát được ngân sách đã duyệt | Tạm dừng; người vận hành quyết điều chỉnh, không tự tăng |
| GET tạm lỗi mạng/429/5xx | Chỉ retry có giới hạn theo policy đã duyệt; hết hạn thì dừng |
| 401/403 | Client chỉ đăng nhập lại một lần cho 401; 403 hoặc 401 tiếp diễn thì dừng, không tăng quyền |
| POST timeout/5xx/mất kết nối sau gửi | Đánh dấu kết quả chưa biết; yêu cầu đối soát phía máy chủ trước gửi lại |

Đăng nhập là POST kỹ thuật cần cho đọc có xác thực; không coi nó là ghi nghiệp vụ trong shadow. Không nhân thêm vòng retry quanh client. Chỉ retry POST khi hợp đồng từng endpoint chứng minh an toàn/idempotent và đã đối soát; `run_id` tự nó không chứng minh idempotency. Agent QA không tự gọi API để chữa lỗi hoặc phát sự kiện trong shadow.

## 7. Cổng phát hành thay đổi skill

1. Chốt bản gốc, diff, tác giả đề xuất, phạm vi và vấn đề có nguồn; không nhét log phiên hay quyết định riêng lẻ vào quy tắc chung.
2. Kiểm cấu trúc/frontmatter, references, schema, ca âm tính và trường hợp prompt injection; xác minh không mở rộng quyền.
3. Đánh giá ngữ nghĩa trên tập giữ riêng có gold nếu có; nếu chưa có, báo `NOT_EVALUABLE` và chỉ kết luận những cổng cấu trúc thực sự kiểm được.
4. So trước/sau cùng tập và cấu hình; công bố thay đổi coverage, lỗi nghiêm trọng, token/chi phí và giới hạn đo.
5. Kiểm bằng ngữ cảnh độc lập; bất đồng giữ `DISPUTED` và chuyển người có thẩm quyền, không bỏ phiếu đa số giữa agent để thay người duyệt.
6. Chủ dự án duyệt PR, phiên bản, phạm vi thí điểm, kế hoạch rollback và việc đồng bộ profile. Chưa có quyết định thì `HOLD`; không tự merge, deploy, chạy lại lượt hay áp staged writes.
7. Sau phát hành, người vận hành xác nhận mã băm file, version và smoke task đúng profile; QA ghi bằng chứng. Không suy “đã cài” từ việc merge Git.

`PASS` = cổng đã kiểm đáp ứng tiêu chí chốt trước; `FAIL` = vi phạm; `NOT_EVALUABLE` = chưa đủ điều kiện đo; `HOLD` = chưa được phép phát hành. Các nhãn này nằm trong báo cáo QA, không ghi đè trạng thái A2/A3 hay `CHO_XEM` của NMPRP.
