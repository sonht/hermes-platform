---
name: nmprp-stage-m3
description: Thực thi M3 NMPRP theo snapshot đã ghim, chỉ đề xuất.
---

# Hợp đồng worker v1

Đầu vào một họ de_xuat_id + thanh_vien đã được NMPRP cho phép, snapshot_id và modifier_dictionary đã ghim (chỉ ACTIVE/EXPERT_APPROVED). Không gọi M0/M1/M2. Trả {"items":[{"de_xuat_id":"nguyên văn","action":"hành động","target":"đích","method":"","ly_do":"căn cứ","bien_the":[{"pl2_code":"mã","modifier_ids":[],"gia_tri_modifier":[],"thanh_phan_phoi_hop":[],"tai_dung_dac_diem":{"ket_qua":"UNCERTAIN","thieu":[],"thua":[],"ghi_chu":"thiếu so sánh M0 được ghim"}}]}]}.
Mỗi PL2 đúng một biến thể. Modifier IDs chỉ từ dictionary đầu vào. Mỗi ID phải có một gia_tri_modifier {modifier_id,loai:LM_...,gia_tri,don_vi,trich_nguon,anh_huong:NONE|POSSIBLE|CHANGES_NODE|UNKNOWN,vai_tro:NON_KERNEL_MODIFIER|KERNEL_DEFINING|CLINICAL_CONTEXT|OBSERVATION_RESULT|PRICE_ONLY|UNCERTAIN}. trich_nguon nguyên văn trong tên. Thành phần phối hợp là {ten,ghi_chu}, không làm phẳng thành modifier. Thiếu từ điển: không bịa ID, nêu UNCERTAIN và đặc điểm chưa diễn đạt. Giao thức hiện chưa cấp đủ M0/luật tái dựng tất định cho M3 nên KHÔNG trả PASS. FAIL phải có thieu/thua. Không tự khai đã nghiệm thu.

## Quy tắc tham chiếu nguyên văn

Bản khởi đầu từ thiết kế 20/10/2026; không phải nhãn vàng hay tri thức đã duyệt.

### 6d. Hướng dẫn kỹ thuật gốc + modifier (M3)

| Số | Quy tắc |
|---|---|
| M3-01 | Đơn vị = MỘT họ trong Bộ họ đang dùng, họ ở trạng thái Đồng ý. Xét đủ mọi thành viên của họ. |
| M3-02 | Gốc = phần chung không bỏ được mà vẫn giữ bản chất (hành động + đích + mục đích + phương pháp cốt lõi). Gốc KHÔNG nhất thiết trùng tên một PL2 có sẵn. Không cấp mã danh mục mới. |
| M3-03 | `kernel_id` do máy chủ tính bằng `cpn_ai_kernel.kernel_id` (`HASH_VERSION = "1"`); thiếu hành động hoặc đích ⇒ từ chối. |
| M3-04 | Modifier = thuộc tính phân biệt biến thể: `loai` (5.13) + `gia_tri` nguyên văn + `don_vi` + `trich_nguon` + `anh_huong`. Mã modifier phải có trong `modifier_definition`. |
| M3-05 | Thành phần phối hợp độc lập ghi riêng ở `thanh_phan_phoi_hop`, KHÔNG làm phẳng thành modifier. |
| M3-06 | Mỗi PL2 của họ có đúng một biến thể; không gộp/xoá PL2. |
| M3-07 | **Kiểm tái dựng:** từ gốc + modifier + thành phần phối hợp, dựng lại đặc điểm lâm sàng cốt lõi (hành động, đích, mục đích, phương pháp, các thuộc tính có trong tên) rồi so với M0 và tên PL2: đủ ⇒ `PASS`; thiếu/thừa/đổi một đặc điểm cốt lõi ⇒ `FAIL` + cờ `RECONSTRUCTION_FAIL`; không đủ căn cứ ⇒ `UNCERTAIN`. Không đòi trùng chữ. Phép so tên hiện có (`KHOP`/`KHONG_KHOP`, giữ hoa/thường và dấu) giữ làm chỉ số phụ. |
| M3-08 | Khoảng giá trị giữ nguyên ranh giới nguồn; khoảng hở ⇒ `KHOANG_HO`. |
| M3-09 | Modifier có thể đổi nút ⇒ `anh_huong=CHANGES_NODE` + `M1_REVIEW_FLAG`; đổi hạt nhân ⇒ `M2_REVIEW_FLAG`. Không tự sửa M1/M2. |
| M3-10 | `phan_tach` và `co_thanh_phan_gop` lệch ⇒ hiện cả hai (`GHEP_LECH`), không chọn bừa (ADR-09). |

**Ca thử:**

| Ca | ĐÚNG | SAI |
|---|---|---|
| 6.64–6.67 | Gốc «cắt lọc vết loét, hoại tử chi dưới»; modifier `LM_DIEN_TICH` «dưới 50»/«51-100»/«101-200»/«201-400» `cm2`; `LM_BOI_CANH` «do đái tháo đường»; `KHOANG_HO` ở 50 cm2 và trên 400 | Modifier «0–50», «51–100»… (tự lấp) |
| 6.123–6.125 | Gốc «cắt tuyến giáp» + `LM_PHAN_CO_QUAN` («1 thùy»/«toàn bộ») + `LM_DUONG_TIEP_CAN` «nội soi»; `thanh_phan_phoi_hop` = nạo vét hạch + `LM_BEN` «1 bên»/«2 bên» | Bỏ nạo vét hạch ⇒ tái dựng thiếu ⇒ phải `FAIL` |
| 2.254/2.337/2.338 | Gốc IVUS; `LM_VI_TRI` «động mạch vành»/«ngoại biên»/«thận» | Ba gốc |
| 2.239/2.241/2.242 | 2.241 và 2.242 khác ở thành phần «nong» (thành phần phối hợp hoặc khác họ — chuyên gia); 2.239 = 2.242 + `LM_CONG_NGHE` «cánh tay robot» | Robot thành thành phần phối hợp |

