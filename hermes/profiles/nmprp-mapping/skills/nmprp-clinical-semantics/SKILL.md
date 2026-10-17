---
name: nmprp-clinical-semantics
description: Phân tích ngữ nghĩa lâm sàng của một PL2 (hành động, đối tượng, đường tiếp cận) và kiểm tra họ, kernel, modifier trước khi đề xuất nút hoặc đề xuất gộp, tách.
---

# NMPRP: chuẩn hoá ngữ nghĩa lâm sàng

## When to Use
- Trước khi đề xuất nút cho một PL2, hoặc khi được hỏi PL2 nào cùng họ, cùng kernel.
- Chỉ phân tích và ĐỀ XUẤT. Không tự gộp, tách hay di chuyển PL2.

## Procedure
1. Với mỗi PL2, ghi các thành phần: hành động chính, đối tượng đích, đường tiếp cận/phương pháp, công nghệ, mục đích lâm sàng, các bước cấu thành, thuộc tính định danh, thuộc tính biến thể, thuộc tính bối cảnh, thuộc tính chi trả, thông tin còn thiếu, nguồn chứng cứ.
2. Gắn mỗi nhận định một nhãn: EXPLICIT (tên nói rõ), SUPPORTED_INFERENCE (suy ra có căn cứ, nêu căn cứ) hoặc UNKNOWN. Không đổi UNKNOWN thành giá trị mặc định.
3. Họ có tên, định nghĩa, Bao gồm, Loại trừ, kernel, modifier. Kernel giữ khác biệt cốt lõi về hành động, đích, phương pháp, công nghệ. Modifier phân biệt biến thể. Giá, bệnh, tuổi, giới, bên không tự tạo kernel.
4. Kiểm chứng phản chứng trước khi đề xuất gộp: cùng hành động, đối tượng, phương pháp, công nghệ; không có bước độc lập bị gộp; khác biệt chỉ là thuộc tính; có chứng cứ. Thiếu thông tin trọng yếu thì giữ riêng và gắn nhãn HA `EXPERT_REQUIRED`.
5. Đặt tên đề xuất theo Hành động + Đối tượng + Phương pháp + Thuộc tính định danh quan trọng. Không dùng tên thương mại, giá, ký hiệu ± hay «và/hoặc» để gộp các hành động độc lập. Lưu tên nguồn và tên đề xuất riêng.
6. Kiểm tra xuyên nút; không tự di chuyển khi thiếu căn cứ.

## Pitfalls
- Xếp loại theo hành động và mục đích thực tế, không chỉ theo khoa thực hiện. Can thiệp dưới hướng dẫn hình ảnh không mặc định là chẩn đoán hình ảnh thuần tuý.
- Các cặp dễ nhầm cần kiểm: tuyến giáp và cận giáp; thận và thượng thận; niệu quản và niệu đạo; đại tràng và trực tràng; sinh thiết và cắt bỏ; nội soi chẩn đoán và nội soi can thiệp; nội soi và robot hỗ trợ.
- Chỉ dùng các nhãn HA đã liệt kê trong AGENTS.md; mọi nhãn chỉ là đề xuất, không phải phê duyệt.

## Verification
- Mỗi nhận định có nhãn EXPLICIT, SUPPORTED_INFERENCE hoặc UNKNOWN và nguồn.
- Đề xuất gộp nào cũng có đủ các điều kiện ở bước 4.
