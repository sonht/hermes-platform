# Skill — Clinical semantic normalization
## Mỗi PL2 phải được phân tích
ACTION_CORE, TARGET_CORE, APPROACH_METHOD, TECHNOLOGY_CORE, CLINICAL_PURPOSE, PROCEDURE_COMPONENTS, DEFINING_ATTRIBUTES, VARIANT_ATTRIBUTES, CONTEXT_ATTRIBUTES, PAYMENT_ATTRIBUTES, MISSING_INFORMATION, EVIDENCE_SOURCE.
Mỗi nhận định gắn EXPLICIT, SUPPORTED_INFERENCE hoặc UNKNOWN. Không đổi UNKNOWN thành giá trị mặc định; tên không nói mổ mở/nội soi/robot thì APPROACH_METHOD=UNKNOWN.
## Họ và hạt nhân
Family có tên, định nghĩa, Bao gồm, Loại trừ, kernel, modifier. Kernel phải giữ khác biệt cốt lõi về hành động/đích/phương pháp/công nghệ; modifier phân biệt biến thể; yếu tố giá, bệnh, tuổi, giới, bên không tự tạo kernel.
Kiểm chứng phản chứng trước gộp: cùng action, target, approach, technology, không có bước độc lập bị gộp, khác biệt chỉ là thuộc tính, có chứng cứ. Thiếu thông tin trọng yếu => giữ riêng, chuyển chuyên gia.
Đổi tên theo Hành động + Đối tượng + Phương pháp + Thuộc tính định danh quan trọng; không dùng tên thương mại, giá, ký hiệu ± hay 'và/hoặc' để gộp hành động độc lập.
Kiểm tra xuyên nút, không tự di chuyển nếu thiếu căn cứ. Trạng thái HIGH_CONFIDENCE_PROPOSAL, REVIEW_RECOMMENDED, EXPERT_REQUIRED, UNRESOLVED là trạng thái đề xuất, không phải phê duyệt.
