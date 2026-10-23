# Kiểm thử — 24/10/2026

## Phạm vi và kết quả

Không truy cập production. Backend thật/HTTP thật/DB fixture được dùng trong contract integration; phản hồi mô hình là fixture có kiểm soát. **Không gọi LLM thật, không đo độ chính xác lâm sàng hay chứng minh runtime Rocky đã sửa.**

| Lượt kiểm | Kết quả | Bằng chứng |
|---|---|---|
| Hermes trước sửa | 216 tests, OK | `.cloud-setup/logs/hermes-tests.log` |
| Hermes sau sửa cuối | **226 tests, OK** | `hermes-complete.log`; 10 bài mới, bao gồm lỗi từng đơn vị và pending/ID không hợp lệ |
| NMPRP frontend đầy đủ | **288 files, 3.318 tests passed** | `frontend-final.log`; sau thêm polling readiness chạy lại 38 bài HermesChayLien, đạt (`ui-latest.log`) |
| Frontend build | **đạt** | `frontend-build.log`; cảnh báo chunk lớn hiện có, không bỏ kiểm build |
| Backend đầy đủ trên PostgreSQL 16 | **8.704 passed, 2 failed, 7 skipped, 5 xfailed** | `backend-final.log`, 749,85 giây. Hai lỗi là fixture/danh sách route cần cập nhật cho hành vi mới, không bỏ cổng để xanh |
| Chạy lại sau sửa hai test | **68 passed** | `backend-corrections-final.log`: toàn bộ hai tệp lỗi + hai tệp M1 golden + readiness. Không chạy lại toàn bộ 12 phút sau khi chỉ sửa fixture/expected route set |
| Backend nhóm readiness/M0/M23/allowlist/chạy liền | **119 passed** | `backend-targeted3.log` |
| HTTP quyền hai route mới | **6 passed** | `security-new.log`: 401/403, đúng máy/đúng lượt, switch off, chỉ dictionary đã duyệt |
| Tích hợp chéo repository | **5 passed** | `cross-repo-replay.log`, `cross-repo-isolation.log`; bổ sung typed modifier và mất mạng GĐ2/replay M3 |
| Migration trên DB local trống | **đạt tới 0088_hermes_m2_kiem_dinh_lai** | `migrations.log`, `app-migrations.log`, kiểm `alembic_version` thật; bản vá không thêm migration |
| Cài/khởi động lặp lại | **đạt** | `install-verified.log`, `start-verified.log`; thử stop/restart backend mình đã tạo; pip check đạt |
| Local NMPRP functional | **đạt** | 22 CSV nạp, 11 index không rỗng; 4 truy vấn bắt buộc HTTP 200, có candidates, mã TEXT; `evidence/local-search-smoke.json` |
| Local Hermes support | **đạt** | `/` và widget 200; public login answer 200; Origin lạ 403, body rỗng 400, internal không token 401 |
| Live Hermes image/LLM/Rocky | **BLOCKED, chưa chạy** | Docker layer extraction: `no space left on device`; chưa có quyền Rocky/credential staging/provider |

Bảy skipped của bộ backend cần bộ REF tại đường mà chính các test legacy kiểm; full suite chạy theo chế độ CI không gắn `/data`. Không gọi đó là passed. App smoke dùng CSV thật trong repo, tách riêng với DB test. Năm xfailed là kết quả kỳ vọng sẵn có, không đổi marker. Các cảnh báo Starlette/SQLAlchemy và socket ResourceWarning hiện có được giữ nguyên, không tắt assertion.

Lượt khảo sát backend đầu tiên trùng thời gian đọc/sửa nguồn, khiến các bài `inspect.getsource` có line cache lệch và 8 lỗi; **không dùng lượt ấy làm baseline đáng tin hay gọi chúng là lỗi repository**. Lượt đầy đủ ở bảng trên chạy khi mã ứng dụng ổn định; chỉ còn hai test cần cập nhật. Một test ghim route được thêm đúng route đọc mới; fixture thời gian vẫn kiểm thứ tự cũ nhưng heartbeat nằm trong TTL thực, không hạ TTL gate.

## T0–T11

| Test | Trạng thái | Bằng chứng / giới hạn |
|---|---|---|
| T0 | Đạt local; production BLOCKED | Nguồn cũ bỏ `kha_nang`, không dispatcher/transport. Kiểm ngược worker cũ với job M0 đi nhầm `/ket-qua` M1 và tự báo XONG; bản mới tách đường. Ảnh gốc trong ZIP, chưa ảnh production sau sửa |
| T1 | Đạt local | readiness thiếu cap → lỗi chứa máy/version/cap; dispatcher không sẵn sàng → LOI, không sản phẩm giả |
| T2 | Đạt local | UI worker chỉ PHAN_RA: chạy liền khóa, tick M0 độc lập → POST đúng `/m0/luot`; không gửi `/chay-lien`; API M0 không đòi M2/M3 |
| T3 | Đạt local | JSON/coverage/quote sai → LOI; đơn vị M0 khác tiếp tục; `.pending` không gọi lại mù; cached result dùng lại, call budget/cancel được giữ |
| T4 | Một phần, live BLOCKED | Contract HTTP lưu M0, 2 họ M2, 2 gốc M3, hồ sơ GĐ2; model là fixture. Pilot CSV Chương 6 có 129 bản thiếu S1, không phải READY |
| T5 | Đạt local | M1 v1 golden + byte checks; v2 thiếu THAM_DINH_GD2 bị khóa qua các bài hiện có; v2 adapter riêng, không đổi `_chay_luot` |
| T6 | Đạt phần local; canary nhiều máy BLOCKED | readiness không ghép model/cap hai máy; TTL 180s, restart bỏ cap, polling form 10s. Không chứng minh routing nhiều model trên Rocky |
| T7 | Đạt contract local | M2 từng node; M3 từng họ và replay đúng một họ; không route ghi M1/upstream; scope ngoài bị từ chối |
| T8 | Đạt contract local | rerun thêm 1 gốc mới, giữ 2 gốc cũ; resume M0/GĐ2 không trả tiền lại; các cổng immutable/stale/selection hiện có nằm trong full suite |
| T9 | Đạt local | codes TEXT ở validator và 4 API search. CSV thật xác minh 1.246 shunt, 1.258 dẫn lưu ngoài, 7.10 khác 7.1 |
| T10 | Một phần | journal/log có job, stage, scope hash, worker id/version, model, usage, thời gian và mã lỗi an toàn. Live usage/cost/provider chưa đo; metadata mới chưa migration vào manifest server |
| T11 | Đạt source/local | engine M1 và `_chay_luot` byte-identical; không diff dữ liệu, migrations, QG-16, profile M1 hoặc A1–A6. Không đổi cờ production |

## Sản phẩm thực đã tạo

- **Local PostgreSQL từ CSV:** 129 bản M0 của Chương 6, cả 129 `INSUFFICIENT_SOURCE`, lần hai bỏ qua 129 bản trùng, zero LLM. `evidence/chapter6-local.json`. Không sao chép S1 production và không tự gán nhãn vàng.
- **Contract fixtures (SQLite qua HTTP):** M0 một bản hợp lệ; M2 hai họ; M3 hai gốc có typed modifier được ghi, replay thêm một gốc giữ nguyên bản cũ; GĐ2 một hồ sơ và một đối chiếu. Dữ liệu fixture tồn tại trong thời gian chạy test, không coi là sản phẩm chuyên môn của Chương 6.
- **Worker journals:** test tạo checkpoint với input/skill/prompt hash, model/worker/usage; fixture state của pytest ở `/tmp/pytest-of-agent`, không chứa credential. Hợp đồng output server và checkpoint khác nhau, không giả manifest logical của toàn thiết kế đã đủ.

CSV nguồn `REF_PL2_CONSOLIDATED_PROCEDURE_REGISTRY.csv` SHA-256: `8b9754e20b8bdd752d20c3d1aa29343944b7e813932150ca2f3581d7530b3e6b`.

## Lệnh chạy lại

**Cloud — backend; DB test riêng, không phải DB app/production.**

```bash
cd /workspace/nmprp
```

```bash
PYTHONPATH=backend DATABASE_URL=postgresql+psycopg://nmprp:nmprp_dev_password@127.0.0.1:5433/nmprp_test /workspace/.cloud-setup/venv/bin/python -m pytest backend/app/tests -q -rs
```

**Cloud — frontend.**

```bash
cd /workspace/nmprp/frontend
```

```bash
npm test -- --maxWorkers=4
```

```bash
npm run build
```

**Cloud — worker và hợp đồng hai kho.**

```bash
cd /workspace/hermes-platform
```

```bash
python3 -m unittest discover -s tests -v
```

```bash
PYTHONPATH=/workspace/nmprp/backend:/workspace/hermes-platform DATABASE_URL=postgresql+psycopg://nmprp:nmprp_dev_password@127.0.0.1:5433/nmprp_test /workspace/.cloud-setup/venv/bin/python -m pytest tests/integration/test_capability_contract.py -q
```

Kiểm ngược UI: mới tick M0 độc lập→POST phải đỏ khi dùng component gốc (đã đo trong bản sao tạm ngoài checkout; `ui-inverse.log`). Kiểm ngược worker: worker gốc chỉ có M1 vi phạm assertion không ghi kết quả M1 cho M0. Không để bản đảo vá trong checkout.
