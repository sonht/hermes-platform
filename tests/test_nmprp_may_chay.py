import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import unittest.mock

from support import nmprp_may_chay as mc
from support import nmprp_shadow as sh
from support.nmprp_client import NmprpError
from tests.test_nmprp_shadow import KHUNG, runner_tra, tot

PL2 = [{"code": "6.1", "name": "Cat tuyen giap toan phan"}, {"code": "6.2", "name": "Cat thuong than"},
       {"code": "6.3", "name": "Cat tuyen giap ban phan"}]
TUYEN_GIAP = "Surgery > Endocrine > Thyroid"
TRICH = ["Cat tuyen giap"]


def luot(**kw):
    d = {"luot_id": "HL_aaaaaaaaaaaa", "chuong": "6", "me": 2, "mo_hinh": "", "suy_luan": "", "tran_token": 300000,
         "goi_moi_dot": 5, "han_goi": 5, "tien_do": {}, "ds_pl2": PL2, "pl2_da_xong": []}
    d.update(kw)
    return d


class FakeNmprp:
    """Records every call of the queue protocol. `dung` = list of (reply) returned by successive tien-do calls."""

    def __init__(self, ai=True, dung_o_lan=None, ly_do="HUY"):
        self.ai, self.goi, self.dung_o_lan, self.ly_do, self.n_tien_do = ai, [], dung_o_lan, ly_do, 0

    def ai_cong_tac_bat(self, chiu_loi_mang=False):
        self.chiu_loi_mang = chiu_loi_mang
        if isinstance(self.ai, Exception):
            if chiu_loi_mang:
                raise self.ai
            return False
        return self.ai

    def khung(self):
        return KHUNG

    def _ghi(self, ten, *a):
        self.goi.append((ten,) + a)

    def may_tien_do(self, luot_id, buoc=None, tien_do=None, thong_diep=None):
        self.n_tien_do += 1
        self._ghi("tien_do", buoc or {}, tien_do or {})
        if self.dung_o_lan == self.n_tien_do:
            return {"ok": True, "dung": True, "ly_do_dung": self.ly_do}
        return {"ok": True, "dung": False, "ly_do_dung": ""}

    def may_goi_y(self, luot_id, items):
        self._ghi("goi_y", items)
        return {"ok": True}

    def may_ket_qua(self, luot_id, pl2):
        self._ghi("ket_qua", pl2)
        return {"ok": True}

    def may_ket_thuc(self, luot_id, trang_thai, thong_diep=""):
        self._ghi("ket_thuc", trang_thai, thong_diep)
        return {"ok": True}

    def cuoi(self):
        return [g for g in self.goi if g[0] == "ket_thuc"][-1][1:]

    def loai(self, ten):
        return [g for g in self.goi if g[0] == ten]


def cau_hinh(**kw):
    return mc.CauHinh(**kw)


def tra_loi(*ma):
    return {"ket_qua": [tot(m, TUYEN_GIAP, TRICH) for m in ma]}


def runner_van_xuoi(van_ban):
    """Fake `docker exec`: mo hinh tra loi bang van xuoi (khong co JSON), nhu khi no dung o «buoc 0» xin terminal."""
    goi = []

    def run(argv):
        goi.append(argv)
        if argv[-2] == "-z":
            return 0, van_ban
        return 0, json.dumps({"total_tokens": 7000, "api_calls": 2})
    run.goi = goi
    return run


class TestKhongTraJson(unittest.TestCase):
    def test_tra_loi_van_xuoi_ghi_dung_ly_do_chu_khong_phai_cau_chung(self):
        c = FakeNmprp()
        run = runner_van_xuoi("Toi chua kiem tra duoc cong tac AI cua NMPRP (buoc 0) vi khong co terminal. Toi dung o day.")
        self.assertEqual(mc.xu_ly_luot(c, luot(ds_pl2=PL2[:2], me=2), cau_hinh(), run), "XONG")
        kq = c.loai("ket_qua")[0][1]
        self.assertEqual([r["muc"] for r in kq], ["KHONG_DAP_UNG", "KHONG_DAP_UNG"])
        for r in kq:
            self.assertIn("khong tra JSON", r["ly_do"])
            self.assertIn("buoc 0", r["ly_do"])                                         # tra loi that cua mo hinh, de nguoi duyet thay
            self.assertNotIn("mo hinh khong tra loi cho PL2 nay", r["ly_do"])

    def test_co_json_nhung_thieu_pl2_van_giu_cau_chung_khong_bia_ly_do_van_xuoi(self):
        c, run = FakeNmprp(), runner_tra(tra_loi("6.1"))
        mc.xu_ly_luot(c, luot(ds_pl2=PL2[:2], me=2), cau_hinh(), run)
        kq = {r["pl2_code"]: r for r in c.loai("ket_qua")[0][1]}
        self.assertEqual(kq["6.2"]["muc"], "KHONG_DAP_UNG")
        self.assertEqual(kq["6.2"]["ly_do"], "mo hinh khong tra loi cho PL2 nay")        # co JSON => khong phai van xuoi
        self.assertNotEqual(kq["6.1"]["muc"], "KHONG_DAP_UNG")

    def test_mau_van_xuoi_co_chuoi_giong_ma_cpt_bi_bo(self):
        c = FakeNmprp()
        mc.xu_ly_luot(c, luot(ds_pl2=PL2[:1], me=1), cau_hinh(), runner_van_xuoi("Toi khong the. Ma 99213 la gi?"))
        r = c.loai("ket_qua")[0][1][0]
        self.assertNotIn("99213", r["ly_do"])
        self.assertIn("khong tra JSON", r["ly_do"])


class TestChayLuot(unittest.TestCase):
    def test_chay_het_ba_pl2_hai_lan_goi_va_gui_goi_y_dung_hop_dong(self):
        c, run = FakeNmprp(), runner_tra(tra_loi("6.1", "6.2"))
        kq = mc.xu_ly_luot(c, luot(), cau_hinh(), run)
        self.assertEqual(kq, "XONG")
        self.assertEqual(len(run.goi) // 2, 2)                                   # hai lời gọi mô hình (mỗi lời hai lệnh docker)
        ket_qua = c.loai("ket_qua")
        self.assertEqual([r["pl2_code"] for r in ket_qua[0][1]], ["6.1", "6.2"])   # mã TEXT, đúng thứ tự
        self.assertEqual([r["pl2_code"] for r in ket_qua[1][1]], ["6.3"])
        gy = c.loai("goi_y")[0][1]
        self.assertEqual({g["pl2_code"] for g in gy}, {"6.1", "6.2"})
        self.assertTrue(all(g["phien_ban"] == mc.PHIEN_BAN_GOI_Y and len(g["phien_ban"]) <= 40 for g in gy))
        self.assertTrue(all("run_id" not in g for g in gy))                       # run_id do máy chủ ép, runner không gửi
        self.assertEqual(c.cuoi()[0], "XONG")

    def test_bo_gui_dung_hinh_dang_may_chu_chap_nhan(self):
        # nút không tồn tại ⇒ bị loại, lý do loại phải đi dưới dạng {branch_key, ly_do} chứ không kèm khoá chẩn đoán
        run = runner_tra({"ket_qua": [tot("6.1", "Khong co nut nay", TRICH)]})
        c = FakeNmprp()
        mc.xu_ly_luot(c, luot(ds_pl2=PL2[:1]), cau_hinh(), run)
        bo = c.loai("ket_qua")[0][1][0]["bo"]
        self.assertTrue(bo)
        for b in bo:
            self.assertEqual(set(b), {"branch_key", "ly_do"})
            self.assertIsInstance(b["ly_do"], str)

    def test_het_so_loi_goi_cua_dot_thi_tam_dung_khong_goi_them(self):
        c, run = FakeNmprp(), runner_tra(tra_loi("6.1", "6.2"))
        kq = mc.xu_ly_luot(c, luot(han_goi=1), cau_hinh(), run)
        self.assertEqual(kq, "TAM_DUNG")
        self.assertEqual(len(run.goi) // 2, 1)
        self.assertEqual([r["pl2_code"] for r in c.loai("ket_qua")[0][1]], ["6.1", "6.2"])   # phần đã làm được ghi trọn

    def test_han_goi_bang_khong_la_khong_gioi_han(self):
        c, run = FakeNmprp(), runner_tra(tra_loi("6.1", "6.2"))
        self.assertEqual(mc.xu_ly_luot(c, luot(han_goi=0), cau_hinh(), run), "XONG")

    def test_tran_token_chan_truoc_khi_goi_mo_hinh(self):
        c, run = FakeNmprp(), runner_tra(tra_loi("6.1"))
        kq = mc.xu_ly_luot(c, luot(tran_token=1000), cau_hinh(), run)
        self.assertEqual(kq, "TAM_DUNG")
        self.assertEqual(run.goi, [])                                             # chưa gọi mô hình lần nào
        self.assertEqual(c.loai("ket_qua"), [])

    def test_bo_cua_moi_lan_dung_tich_luy_tu_gia_tri_nen(self):
        c, run = FakeNmprp(), runner_tra(tra_loi("6.3"), usage={"total_tokens": 5000})
        mc.xu_ly_luot(c, luot(ds_pl2=PL2, pl2_da_xong=["6.1", "6.2"],
                              tien_do={"lan_goi": 4, "token_da_dung": 40000, "pl2_xong": 2, "lo_xong": 1}),
                      cau_hinh(), run)
        cuoi = [g[2] for g in c.loai("tien_do") if "lan_goi" in g[2] and "pl2_xong" in g[2]][-1]
        self.assertEqual((cuoi["lan_goi"], cuoi["token_da_dung"], cuoi["pl2_xong"], cuoi["lo_xong"]), (5, 45000, 3, 2))
        self.assertEqual(len(run.goi) // 2, 1)                                    # chỉ làm PL2 còn lại
        self.assertEqual([r["pl2_code"] for r in c.loai("ket_qua")[0][1]], ["6.3"])

    def test_may_chu_ra_lenh_huy_thi_ket_thuc_da_huy(self):
        c, run = FakeNmprp(dung_o_lan=2, ly_do="HUY"), runner_tra(tra_loi("6.1", "6.2"))
        self.assertEqual(mc.xu_ly_luot(c, luot(), cau_hinh(), run), "DA_HUY")
        self.assertEqual(run.goi, [])

    def test_lenh_dung_het_goi_o_lo_cuoi_van_la_xong(self):
        # sau lô CUỐI máy chủ báo HET_GOI (lan_goi == han_goi): hết việc nên XONG, không TAM_DUNG
        c, run = FakeNmprp(), runner_tra(tra_loi("6.1"))
        c.may_tien_do = lambda *a, **k: {"ok": True, "dung": True, "ly_do_dung": "HET_GOI"} if a[2:3] and "lo_xong" in (a[2] if len(a) > 2 else k.get("tien_do", {})) else {"ok": True, "dung": False}
        self.assertEqual(mc.xu_ly_luot(c, luot(ds_pl2=PL2[:1], han_goi=1), cau_hinh(), run), "XONG")

    def test_huy_den_trong_luc_goi_mo_hinh_thi_khong_gui_gi_ve(self):
        # tien-do thứ 4 (sau lời gọi) là chỗ ĐẦU TIÊN máy thấy lệnh huỷ: không được gửi gợi ý/kết quả của lô đó
        c, run = FakeNmprp(dung_o_lan=4, ly_do="HUY"), runner_tra(tra_loi("6.1", "6.2"))
        self.assertEqual(mc.xu_ly_luot(c, luot(), cau_hinh(), run), "DA_HUY")
        self.assertEqual(len(run.goi) // 2, 1)
        self.assertEqual(c.loai("goi_y"), [])
        self.assertEqual(c.loai("ket_qua"), [])

    def test_het_goi_hay_het_token_sau_loi_goi_van_gui_ket_qua_da_tra_tien(self):
        # HET_GOI do chính lời gọi vừa xong gây ra: kết quả đã trả tiền phải được gửi, rồi mới tạm dừng ở lô kế
        class DungTu4(FakeNmprp):                                                       # máy chủ nhắc dừng từ báo cáo thứ 4 trở đi
            def may_tien_do(self, *a, **k):
                r = FakeNmprp.may_tien_do(self, *a, **k)
                return {"ok": True, "dung": True, "ly_do_dung": self.ly_do} if self.n_tien_do >= 4 else r
        for ly in ("HET_GOI", "HET_TOKEN"):
            c, run = DungTu4(ly_do=ly), runner_tra(tra_loi("6.1", "6.2"))
            self.assertEqual(mc.xu_ly_luot(c, luot(), cau_hinh(), run), "TAM_DUNG", ly)
            self.assertEqual([r["pl2_code"] for r in c.loai("ket_qua")[0][1]], ["6.1", "6.2"], ly)
            self.assertEqual(len(run.goi) // 2, 1)

    def test_loi_goi_duoc_ghi_nhan_truoc_khi_goi_mo_hinh(self):
        # máy chết sau khi Hermes trả lời mà chưa báo được: lần gọi phải đã được tính từ TRƯỚC, kẻo khởi động lại gọi (và trả tiền) lần nữa
        class Chet(FakeNmprp):
            def may_tien_do(self, luot_id, buoc=None, tien_do=None, thong_diep=None):
                if buoc and "KIEM_DINH" in buoc:
                    raise NmprpError("POST /admin/hermes/may/luot/HL_x/tien-do: HTTP 502")
                return FakeNmprp.may_tien_do(self, luot_id, buoc, tien_do, thong_diep)
        c = Chet()
        with self.assertRaises(NmprpError):
            mc.xu_ly_luot(c, luot(tien_do={"lan_goi": 2}, han_goi=3), cau_hinh(), runner_tra(tra_loi("6.1", "6.2")))
        truoc_goi = [g[2] for g in c.loai("tien_do") if "SUY_LUAN" in g[1] and g[1]["SUY_LUAN"]["tt"] == "DANG"]
        self.assertEqual(truoc_goi[0]["lan_goi"], 3)                                # đã đặt chỗ lần gọi thứ 3 trước khi gọi
        # lần khởi động lại: nhận lại lượt với lan_goi=3, han_goi=3 ⇒ không được gọi thêm
        run2 = runner_tra(tra_loi("6.1", "6.2"))
        self.assertEqual(mc.xu_ly_luot(FakeNmprp(), luot(tien_do={"lan_goi": 3}, han_goi=3), cau_hinh(), run2), "TAM_DUNG")
        self.assertEqual(run2.goi, [])

    def test_muc_suy_luan_mac_dinh_cung_phai_nam_trong_danh_sach(self):
        c, run = FakeNmprp(), runner_tra(tra_loi("6.1", "6.2"))
        # lượt không chọn mức ⇒ chạy ở "low"; máy chỉ cho "high" ⇒ phải từ chối, không lặng lẽ chạy "low"
        self.assertEqual(mc.xu_ly_luot(c, luot(suy_luan=""), cau_hinh(suy_luan=("high",)), run), "LOI")
        self.assertEqual(run.goi, [])
        run2 = runner_tra(tra_loi("6.1", "6.2"))
        self.assertEqual(mc.xu_ly_luot(FakeNmprp(), luot(suy_luan=""), cau_hinh(suy_luan=("low", "high")), run2), "XONG")
        self.assertEqual(run2.goi[0][run2.goi[0].index("--reasoning") + 1], "low")

    def test_cong_tac_ai_loi_mang_thi_thu_lai_khong_tam_dung(self):
        c = FakeNmprp(ai=NmprpError("GET /admin/ai/status: HTTP 502"))
        with self.assertRaises(NmprpError):
            mc.xu_ly_luot(c, luot(), cau_hinh(), runner_tra(tra_loi("6.1")))
        self.assertEqual(c.loai("ket_thuc"), [])                                      # lượt vẫn DANG_CHAY
        self.assertTrue(c.chiu_loi_mang)

    def test_mo_hinh_ngoai_danh_sach_bi_tu_choi_truoc_khi_goi(self):
        c, run = FakeNmprp(), runner_tra(tra_loi("6.1"))
        kq = mc.xu_ly_luot(c, luot(mo_hinh="model-la"), cau_hinh(mo_hinh=("model-a",)), run)
        self.assertEqual(kq, "LOI")
        self.assertEqual(run.goi, [])
        self.assertEqual(mc.xu_ly_luot(FakeNmprp(), luot(suy_luan="ultra"), cau_hinh(), runner_tra(tra_loi("6.1"))), "LOI")

    def test_mo_hinh_hop_le_di_vao_lenh_hermes_dang_danh_sach_khong_qua_shell(self):
        c, run = FakeNmprp(), runner_tra(tra_loi("6.1"))
        mc.xu_ly_luot(c, luot(ds_pl2=PL2[:1], mo_hinh="model-a", suy_luan="high"), cau_hinh(mo_hinh=("model-a",)), run)
        argv = run.goi[0]
        self.assertEqual(argv[argv.index("-m") + 1], "model-a")
        self.assertEqual(argv[argv.index("--reasoning") + 1], "high")

    def test_mo_hinh_co_ky_tu_la_khong_vao_danh_sach_cho_phep(self):
        self.assertEqual(cau_hinh(mo_hinh=("a; rm -rf /", "ok-1", "x y")).mo_hinh, ("ok-1",))

    def test_cong_tac_ai_tat_thi_tam_dung_khong_goi(self):
        c, run = FakeNmprp(ai=False), runner_tra(tra_loi("6.1"))
        self.assertEqual(mc.xu_ly_luot(c, luot(), cau_hinh(), run), "TAM_DUNG")
        self.assertEqual(run.goi, [])

    def test_hermes_loi_ma_thoat_thi_luot_loi(self):
        c, run = FakeNmprp(), runner_tra({}, rc=3)
        self.assertEqual(mc.xu_ly_luot(c, luot(), cau_hinh(), run), "LOI")

    def test_loi_mang_khong_ket_thuc_luot(self):
        class Rot(FakeNmprp):
            def may_goi_y(self, *a):
                raise NmprpError("POST /admin/hermes/may/luot/HL_x/goi-y: HTTP 502")
        c = Rot()
        with self.assertRaises(NmprpError):
            mc.xu_ly_luot(c, luot(), cau_hinh(), runner_tra(tra_loi("6.1", "6.2")))
        self.assertEqual(c.loai("ket_thuc"), [])                                   # luot van DANG_CHAY, may khoi dong lai se tiep tuc

    def test_loi_la_chi_gui_ten_lop_khong_gui_noi_dung(self):
        c = FakeNmprp()
        c.khung = lambda: (_ for _ in ()).throw(KeyError("mat-khau-bi-mat"))
        self.assertEqual(mc.xu_ly_luot(c, luot(), cau_hinh(), runner_tra({})), "LOI")
        self.assertNotIn("mat-khau", json.dumps(c.loai("ket_thuc")))

    def test_prompt_qua_lon_thi_chia_doi_lo(self):
        goc = sh.MAX_PROMPT_BYTES
        sh.MAX_PROMPT_BYTES = len(sh.dung_prompt(PL2[:1], sh.thu_nut_tan(KHUNG)).encode()) + 5
        try:
            c, run = FakeNmprp(), runner_tra(tra_loi("6.1"))
            mc.xu_ly_luot(c, luot(me=3), cau_hinh(), run)
            self.assertEqual(len(run.goi) // 2, 3)                                   # 3 PL2 → từng PL2 một
        finally:
            sh.MAX_PROMPT_BYTES = goc


class ServerThat(FakeNmprp):
    """Answers `dung` the way NMPRP's `cap_nhat` does: HET_GOI as soon as the REPORTED lan_goi reaches han_goi (han_goi > 0), HET_TOKEN
    when the reported token_da_dung reaches the ceiling. A fake that only returns `dung` at a chosen call number hid the bug where
    reserving the last allowed call paused the run before the call was made."""

    def __init__(self, han_goi, tran=10 ** 9, **kw):
        FakeNmprp.__init__(self, **kw)
        self.han, self.tran, self.lan, self.tok = han_goi, tran, 0, 0

    def may_tien_do(self, luot_id, buoc=None, tien_do=None, thong_diep=None):
        FakeNmprp.may_tien_do(self, luot_id, buoc, tien_do, thong_diep)
        td = tien_do or {}
        self.lan, self.tok = max(self.lan, td.get("lan_goi", 0)), max(self.tok, td.get("token_da_dung", 0))
        if self.han and self.lan >= self.han:
            return {"ok": True, "dung": True, "ly_do_dung": "HET_GOI"}
        if self.tok >= self.tran:
            return {"ok": True, "dung": True, "ly_do_dung": "HET_TOKEN"}
        return {"ok": True, "dung": False, "ly_do_dung": ""}


class TestMaySachVoiMayChuThat(unittest.TestCase):
    def test_han_goi_bang_mot_van_goi_dung_mot_lan(self):
        # lỗi thật 18/10/2026: lượt han_goi=1 tạm dừng sau 2 giây mà CHƯA gọi Hermes lần nào
        c, run = ServerThat(han_goi=1), runner_tra(tra_loi("6.1"))
        self.assertEqual(mc.xu_ly_luot(c, luot(han_goi=1, ds_pl2=PL2[:1]), cau_hinh(), run), "XONG")
        self.assertEqual(len(run.goi) // 2, 1)
        self.assertEqual([r["pl2_code"] for r in c.loai("ket_qua")[0][1]], ["6.1"])

    def test_han_goi_n_goi_dung_n_lan_roi_tam_dung(self):
        c, run = ServerThat(han_goi=2), runner_tra(tra_loi("6.1", "6.2", "6.3"))
        self.assertEqual(mc.xu_ly_luot(c, luot(han_goi=2, me=1), cau_hinh(), run), "TAM_DUNG")
        self.assertEqual(len(run.goi) // 2, 2)                                      # đúng hai lời gọi, không phải một
        self.assertEqual([r["pl2_code"] for r in c.loai("ket_qua")[1][1]], ["6.2"])

    def test_het_goi_khong_chan_loi_goi_da_dat_cho_nhung_huy_van_chan(self):
        c, run = ServerThat(han_goi=1), runner_tra(tra_loi("6.1"))
        c.may_tien_do_goc = c.may_tien_do
        c.may_tien_do = lambda *a, **k: {"ok": True, "dung": True, "ly_do_dung": "HUY"} if (a[1:2] and "SUY_LUAN" in (a[1] or {}) and a[1]["SUY_LUAN"]["tt"] == "DANG") else c.may_tien_do_goc(*a, **k)
        self.assertEqual(mc.xu_ly_luot(c, luot(han_goi=1, ds_pl2=PL2[:1]), cau_hinh(), run), "DA_HUY")
        self.assertEqual(run.goi, [])


class TestVong(unittest.TestCase):
    def test_tep_dung_thi_khong_nhan_viec_va_khong_chao(self):
        with tempfile.NamedTemporaryFile() as f:
            class C:
                goi = []
                def may_chao(self, *a): C.goi.append("chao")
                def may_nhan(self): C.goi.append("nhan")
            self.assertEqual(mc.mot_vong(C(), cau_hinh(tep_dung=f.name)), "DUNG")
            self.assertEqual(C.goi, [])

    def test_khong_viec_thi_chi_chao_va_hoi(self):
        class C:
            goi = []
            def may_chao(self, *a): C.goi.append(("chao", a[1:]))
            def may_nhan(self): C.goi.append("nhan"); return {"ok": True, "luot": None}
        r = mc.mot_vong(C(), cau_hinh(mo_hinh=("m",), tep_dung="/khong/co/tep"))
        self.assertEqual(r, "KHONG_VIEC")
        # khai đúng danh sách của chính máy; công tắc khai profile TẮT (mặc định khi dựng CauHinh trực tiếp) ⇒ None = thân cũ
        self.assertEqual(C.goi[0], ("chao", (("m",), ("low", "medium", "high"), None)))

    def test_chay_mai_loi_mang_thi_cho_roi_thu_lai(self):
        lan = []

        class C:
            def may_chao(self, *a): lan.append("chao")
            def may_nhan(self):
                lan.append("nhan")
                if lan.count("nhan") == 1:
                    raise NmprpError("POST /admin/hermes/may/nhan: HTTP 502")
                return {"ok": True, "luot": None}
        ngu = []
        mc.chay_mai(C, cau_hinh(tep_dung="/khong/co/tep"), nhip=1, ngu=ngu.append, nhip_tim=False, so_vong=2)
        self.assertEqual(ngu, [2, 1])                                              # lỗi ⇒ chờ gấp đôi, rồi vòng sau bình thường

    def test_mot_lan_loi_mang_thi_that_bai_khong_thoat_ma_0(self):
        class C:
            def may_chao(self, *a): raise NmprpError("POST /admin/hermes/may/chao: HTTP 502")
        with self.assertRaises(NmprpError):
            mc.chay_mai(C, cau_hinh(tep_dung="/khong/co/tep"), nhip=1, ngu=lambda s: None, nhip_tim=False, so_vong=1, mot_lan=True)
        with tempfile.TemporaryDirectory() as td:
            cfg = cau_hinh(tep_dung="/khong/co/tep", tep_khoa=os.path.join(td, "may-chay.lock"))
            with unittest.mock.patch.object(mc, "CauHinh") as ch, unittest.mock.patch.object(mc, "NmprpClient", C):
                ch.tu_moi_truong.return_value = cfg
                self.assertEqual(mc.main(["--mot-lan"]), 2)

    def test_cau_hinh_tu_moi_truong(self):
        c = mc.CauHinh.tu_moi_truong({"HERMES_RUNNER_MODELS": "a, b ,", "HERMES_RUNNER_REASONING": "low,bogus,high",
                                      "HERMES_RUNNER_DUNG": "/x"})
        self.assertEqual((c.mo_hinh, c.suy_luan, c.tep_dung), (("a", "b"), ("low", "high"), "/x"))
        self.assertEqual(mc.CauHinh.tu_moi_truong({}).mo_hinh, ())                  # không ghi cứng tên mô hình nào


class TestKhoaMotLan(unittest.TestCase):
    """Kiem nguoc thuc: lay khoa bang MOT fd thuc, thu lay lan hai bang fd KHAC (hoac tien trinh con thuc) phai bi
    tu choi; khoa phai nha khi tien trinh/fd giu thoat."""

    def test_fd_thu_hai_bi_tu_choi_khi_fd_dau_con_giu(self):
        with tempfile.TemporaryDirectory() as td:
            duong = os.path.join(td, "con/sau/may-chay.lock")                     # thu muc chua co, phai tu tao
            giu = mc.khoa_mot_lan(duong)
            self.assertIsNotNone(giu)
            try:
                self.assertIsNone(mc.khoa_mot_lan(duong))                          # fd thu hai, VAN trong tien trinh nay
            finally:
                giu.close()
            self.assertIsNotNone(mc.khoa_mot_lan(duong))                           # fd dau da dong -> nha khoa

    def test_pid_ghi_vao_tep_khoa_doc_lai_duoc(self):
        with tempfile.TemporaryDirectory() as td:
            duong = os.path.join(td, "may-chay.lock")
            giu = mc.khoa_mot_lan(duong)
            try:
                self.assertEqual(mc.doc_pid_khoa(duong), str(os.getpid()))
            finally:
                giu.close()

    def test_doc_pid_tep_khong_co_khong_loi(self):
        self.assertEqual(mc.doc_pid_khoa("/khong/co/duong/nay.lock"), "")

    def test_tien_trinh_con_thuc_giu_khoa_thi_tien_trinh_chinh_bi_tu_choi_roi_duoc_khi_con_thoat(self):
        # kiem ngược THẬT bằng MỘT tiến trình con độc lập (không chỉ fd thứ hai trong tiến trình này)
        with tempfile.TemporaryDirectory() as td:
            duong = os.path.join(td, "may-chay.lock")
            kich_ban = (
                "import fcntl, os, sys, time\n"
                "f = open(%r, 'a+')\n" % duong +
                "fcntl.flock(f.fileno(), fcntl.LOCK_EX)\n"
                "sys.stdout.write('da-giu\\n'); sys.stdout.flush()\n"
                "time.sleep(2.0)\n"
            )
            con = subprocess.Popen([sys.executable, "-c", kich_ban], stdout=subprocess.PIPE, text=True)
            try:
                dong_dau = con.stdout.readline()
                self.assertEqual(dong_dau.strip(), "da-giu")
                self.assertIsNone(mc.khoa_mot_lan(duong))                           # bi giu boi TIEN TRINH KHAC that
                con.wait(timeout=5)
                for _ in range(50):                                                # cho fd cua tien trinh con thuc dong het
                    giu = mc.khoa_mot_lan(duong)
                    if giu is not None:
                        break
                    time.sleep(0.1)
                self.assertIsNotNone(giu, "khoa phai nha khi tien trinh giu da thoat")
                giu.close()
            finally:
                if con.poll() is None:
                    con.kill()
                    con.wait()

    def test_cau_hinh_tu_moi_truong_doc_duong_khoa_tu_bien_moi_truong(self):
        c = mc.CauHinh.tu_moi_truong({"HERMES_RUNNER_LOCK": "/tmp/x/khac.lock"})
        self.assertEqual(c.tep_khoa, "/tmp/x/khac.lock")
        self.assertEqual(mc.CauHinh.tu_moi_truong({}).tep_khoa, mc.KHOA_MAC_DINH)   # mac dinh canh tep dung mem

    def test_main_tu_choi_voi_ma_thoat_rieng_khong_hoi_nmprp_khi_khoa_da_bi_giu(self):
        class ChuaDuocGoi:
            def may_chao(self, *a):
                raise AssertionError("main khong duoc hoi NMPRP khi khoa da bi giu")
        with tempfile.TemporaryDirectory() as td:
            duong = os.path.join(td, "may-chay.lock")
            giu = mc.khoa_mot_lan(duong)
            try:
                cfg = cau_hinh(tep_dung="/khong/co/tep", tep_khoa=duong)
                with unittest.mock.patch.object(mc, "CauHinh") as ch, unittest.mock.patch.object(mc, "NmprpClient", ChuaDuocGoi):
                    ch.tu_moi_truong.return_value = cfg
                    self.assertEqual(mc.main([]), mc.MA_THOAT_DA_CO_MAY_CHAY)
            finally:
                giu.close()

    def test_main_khong_bi_khoa_thi_chay_binh_thuong_va_dong_khoa_khi_thoat(self):
        with tempfile.TemporaryDirectory() as td:
            duong = os.path.join(td, "may-chay.lock")

            class C:
                def may_chao(self, *a): raise NmprpError("POST /admin/hermes/may/chao: HTTP 502")
            cfg = cau_hinh(tep_dung="/khong/co/tep", tep_khoa=duong)
            with unittest.mock.patch.object(mc, "CauHinh") as ch, unittest.mock.patch.object(mc, "NmprpClient", C):
                ch.tu_moi_truong.return_value = cfg
                self.assertEqual(mc.main(["--mot-lan"]), 2)
            lai = mc.khoa_mot_lan(duong)                                            # khoa da duoc tra khi main thoat
            self.assertIsNotNone(lai, "main phai nha khoa truoc khi tra ve")
            lai.close()

    def test_mot_lan_cung_ton_trong_khoa_qua_argv(self):
        # yeu cau rieng: --mot-lan khong duoc la ngoai le cua khoa (khac test tren dung argv=[])
        class ChuaDuocGoi:
            def may_chao(self, *a):
                raise AssertionError("--mot-lan van khong duoc hoi NMPRP khi khoa da bi giu")
        with tempfile.TemporaryDirectory() as td:
            duong = os.path.join(td, "may-chay.lock")
            giu = mc.khoa_mot_lan(duong)
            try:
                cfg = cau_hinh(tep_dung="/khong/co/tep", tep_khoa=duong)
                with unittest.mock.patch.object(mc, "CauHinh") as ch, unittest.mock.patch.object(mc, "NmprpClient", ChuaDuocGoi):
                    ch.tu_moi_truong.return_value = cfg
                    self.assertEqual(mc.main(["--mot-lan"]), mc.MA_THOAT_DA_CO_MAY_CHAY)
            finally:
                giu.close()


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _env_hai_tien_trinh(td, **extra):
    """Bien moi truong AN TOAN cho subprocess thuc: tep khoa/dung o trong `td` (KHONG BAO GIO dung mac dinh
    /home/rocky/... trong bai kiem), va NMPRP gia (URL khong goi mang thuc, tu choi ket noi ngay)."""
    env = dict(os.environ)
    env.update({
        "HERMES_RUNNER_LOCK": os.path.join(td, "may-chay.lock"),
        "HERMES_RUNNER_DUNG": os.path.join(td, "KHONG_CO_TEP_DUNG"),
        "NMPRP_BASE_URL": "http://127.0.0.1:1",            # port 1: tu choi ket noi ngay, khong cham mang thuc
        "NMPRP_SERVICE_USER": "x",
        "NMPRP_SERVICE_PASSWORD": "y",
    })
    env.update(extra)
    return env


def _cho_tien_trinh_giu_khoa(proc, han_giay=10):
    """Doc stdout cua tien trinh cho toi khi thay dong log xac nhan NO DA QUA buoc khoa va dang chay (khong
    phai doan bi tu choi) - tranh dua (race) giua lam test va thoi diem tien trinh thuc giu duoc flock.

    Doc trong LUONG PHU: `readline()` cua `subprocess.PIPE` la goi CHAN (blocking) - neu tien trinh con treo
    MA KHONG in gi them (vd mot loi hang truoc dong log mong doi), ban than `readline()` khong co han gio rieng
    nen vong lap `while time.time() < han` khong bao gio duoc kiem tra lai; ca bai kiem se treo vo han du da
    co `han_giay`. Luong phu chi lam viec doc, dua tung dong vao queue; luong chinh cho co han bang
    `queue.get(timeout=...)` nen LUON thoat dung han du tien trinh con im lang hoan toan."""
    import queue as _queue

    hang = _queue.Queue()

    def _doc():
        try:
            for dong in iter(proc.stdout.readline, ""):
                hang.put(dong)
                if not dong:
                    break
        except (ValueError, OSError):
            pass

    luong = threading.Thread(target=_doc, daemon=True)
    luong.start()
    han = time.time() + han_giay
    while time.time() < han:
        try:
            dong = hang.get(timeout=max(0.05, han - time.time()))
        except _queue.Empty:
            break
        if not dong:
            if proc.poll() is not None:
                break
            continue
        if "tep khoa=" in dong:                           # dung dong log NGAY SAU khi khoa_mot_lan() thanh cong
            return dong
    return None


class TestKhoaThucTeHaiTienTrinh(unittest.TestCase):
    """KIEM NGUOC THAT bang hai tien trinh `python3 -m support.nmprp_may_chay` doc lap (khong mock subprocess),
    dung NMPRP gia (URL tu choi ket noi) de khong cham mang thuc nao."""

    def _tien_trinh_dau(self, td):
        duong_khoa = os.path.join(td, "may-chay.lock")                 # phai khop _env_hai_tien_trinh
        p = subprocess.Popen([sys.executable, "-m", "support.nmprp_may_chay", "--nhip", "1"],
                              cwd=REPO_ROOT, env=_env_hai_tien_trinh(td), stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True)
        dong = _cho_tien_trinh_giu_khoa(p)
        self.assertIsNotNone(dong, "tien trinh dau phai bao da qua khoa va dang chay")
        self.assertIsNone(p.poll(), "tien trinh dau phai con song luc nay")
        # bat dot bien doc sai ten bien moi truong (HERMES_RUNNER_LOCK): neu may chay doc nham bien khac, no roi
        # ve KHOA_MAC_DINH that (/home/rocky/...) thay vi duong trong `td` - dong log phai neu dung duong trong `td`
        self.assertIn(duong_khoa, dong, "dong log 'tep khoa=' phai neu dung duong khoa trong thu muc tam (td)")
        self.assertNotIn("/home/rocky/hermes-shadow-out/may-chay.lock", dong,
                          "khong duoc roi ve duong khoa mac dinh thuc - nghia la bien moi truong bi doc sai ten")
        return p

    def _dung(self, p):
        if p.poll() is None:
            p.kill()
            p.wait(timeout=5)

    def test_ban_thu_hai_thoat_ma_3_kem_pid_ban_dau_van_giu_khoa(self):
        with tempfile.TemporaryDirectory() as td:
            dau = self._tien_trinh_dau(td)
            try:
                hai = subprocess.run([sys.executable, "-m", "support.nmprp_may_chay", "--mot-lan"],
                                      cwd=REPO_ROOT, env=_env_hai_tien_trinh(td), capture_output=True,
                                      text=True, timeout=10)
                self.assertEqual(hai.returncode, mc.MA_THOAT_DA_CO_MAY_CHAY)
                self.assertIn("da co may chay khac dang chay", hai.stdout)
                self.assertIn(str(dau.pid), hai.stdout, "thong bao phai neu dung PID cua ban dang giu khoa")
                self.assertIsNone(dau.poll(), "ban dau phai VAN con giu khoa, khong bi anh huong boi ban thu hai")
            finally:
                self._dung(dau)

    def test_khoa_tu_nha_khi_tien_trinh_giu_bi_kill_9_khong_ket_pid_cu(self):
        with tempfile.TemporaryDirectory() as td:
            dau = self._tien_trinh_dau(td)
            dau.kill()                                    # SIGKILL = kill -9, tien trinh KHONG the tu don (khong try/except nao chay)
            dau.wait(timeout=5)
            self.assertIsNotNone(dau.poll())
            # khoa phai nha NGAY (muc OS, khong phu thuoc code don dep) - mot ban moi phai qua duoc buoc khoa
            # (loi mang NMPRP sau do la mong doi, khong phai ma 3 "da co may chay khac")
            hai = subprocess.run([sys.executable, "-m", "support.nmprp_may_chay", "--mot-lan"],
                                  cwd=REPO_ROOT, env=_env_hai_tien_trinh(td), capture_output=True,
                                  text=True, timeout=10)
            self.assertNotEqual(hai.returncode, mc.MA_THOAT_DA_CO_MAY_CHAY,
                                 "khoa phai duoc nha khi tien trinh giu bi kill -9, khong ket lai may chay cu")
            self.assertNotIn("da co may chay khac dang chay", hai.stdout)

    def test_mot_lan_thuc_qua_module_cung_bi_tu_choi_khi_dang_bi_khoa(self):
        # --mot-lan (khong phai vong lap chinh) cua MOT TIEN TRINH THAT cung phai bi tu choi dung cach
        with tempfile.TemporaryDirectory() as td:
            dau = self._tien_trinh_dau(td)
            try:
                hai = subprocess.run([sys.executable, "-m", "support.nmprp_may_chay", "--mot-lan"],
                                      cwd=REPO_ROOT, env=_env_hai_tien_trinh(td), capture_output=True,
                                      text=True, timeout=10)
                self.assertEqual(hai.returncode, mc.MA_THOAT_DA_CO_MAY_CHAY)
            finally:
                self._dung(dau)


class TestThuMucKhoaHong(unittest.TestCase):
    """Yeu cau: thu muc/tep khoa khong tao/mo duoc (vd mot thanh phan duong dan la TEP, khong phai thu muc) thi
    bao loi RO RANG va thoat voi ma hop ly - KHONG traceback tran, KHONG chay ma khong co khoa."""

    def _duong_hong(self, td):
        # mot thanh phan giua duong dan la TEP thuong (khong phai thu muc) -> os.makedirs khong the tao con duoi no,
        # loi nay xay ra ca khi chay bang root (khac loi quyen thu muc, thu khong gia lap duoc trong sandbox nay)
        notadir = os.path.join(td, "day_la_tep_khong_phai_thu_muc")
        open(notadir, "w").close()
        return os.path.join(notadir, "con", "may-chay.lock")

    def test_khoa_mot_lan_nem_oserror_ro_rang_khong_am_tham_tra_none(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(OSError):
                mc.khoa_mot_lan(self._duong_hong(td))

    def test_main_tra_ma_rieng_khong_phai_0_2_3_khong_nem_loi_ra_ngoai(self):
        with tempfile.TemporaryDirectory() as td:
            cfg = cau_hinh(tep_dung="/khong/co/tep", tep_khoa=self._duong_hong(td))

            class ChuaDuocGoi:
                def may_chao(self, *a):
                    raise AssertionError("khong duoc chay toi NMPRP khi chua co khoa")
            with unittest.mock.patch.object(mc, "CauHinh") as ch, unittest.mock.patch.object(mc, "NmprpClient", ChuaDuocGoi):
                ch.tu_moi_truong.return_value = cfg
                ma = mc.main([])                            # KHONG duoc nem ra ngoai (khong traceback tran)
            self.assertNotIn(ma, (0, 2, 3), "ma thoat cua loi-khoa-hong khong duoc trung ma khac trong main()")

    def test_tien_trinh_thuc_bao_loi_ro_khong_traceback_tran_khong_chay(self):
        with tempfile.TemporaryDirectory() as td:
            env = _env_hai_tien_trinh(td, HERMES_RUNNER_LOCK=self._duong_hong(td))
            p = subprocess.run([sys.executable, "-m", "support.nmprp_may_chay", "--mot-lan"],
                                cwd=REPO_ROOT, env=env, capture_output=True, text=True, timeout=10)
            toan_bo = p.stdout + p.stderr
            self.assertNotIn("Traceback (most recent call last)", toan_bo)
            self.assertNotEqual(p.returncode, 0, "khong duoc bao thanh cong khi khong khoa duoc")
            self.assertNotIn(p.returncode, (2, 3))
            self.assertNotIn("tep khoa=", toan_bo, "khong duoc chay (qua buoc khoa) khi khong tao/mo duoc tep khoa")


class TestTepMauDichVuSystemd(unittest.TestCase):
    """Yeu cau: ExecStart dung module may chay, RestartPreventExitStatus=3 co mat, va ma 3 khong trung bat ky
    ma thoat KHAC ma main() co the tra ve - de dich vu KHONG lap lai mai khi gap dung ma "da co may chay khac",
    nhung VAN lap lai binh thuong voi moi ma loi khac."""

    def _noi_dung(self):
        duong = os.path.join(REPO_ROOT, "deploy", "rocky", "hermes-nmprp-may-chay.service.example")
        with open(duong, encoding="utf-8") as f:
            return f.read()

    def test_execstart_goi_dung_module_may_chay(self):
        tx = self._noi_dung()
        self.assertIn("ExecStart=", tx)
        m = re.search(r"^ExecStart=(.+)$", tx, re.M)
        self.assertIsNotNone(m)
        # khop CHINH XAC ten module (khong phai chi substring - "nmprp_may_chay_khac" cung chua chuoi nay)
        mo = re.search(r"python3\s+-m\s+(\S+)", m.group(1))
        self.assertIsNotNone(mo, "phai goi python3 -m <module>")
        self.assertEqual(mo.group(1).rstrip("'\""), "support.nmprp_may_chay")
        self.assertIn("exec ", m.group(1), "phai exec python3 de systemd theo dung PID (khong qua bash con)")

    def test_restart_prevent_exit_status_3_co_mat(self):
        tx = self._noi_dung()
        self.assertRegex(tx, re.compile(r"^RestartPreventExitStatus=3\s*$", re.M), "phai co dung dong nay trong [Service]")
        dong_chi_thi = [d for d in tx.splitlines() if d.startswith("RestartPreventExitStatus=")]
        self.assertEqual(len(dong_chi_thi), 1, "chi dung MOT dong chi thi thuc su (comment giai thich khong tinh)")

    def test_ma_3_khong_trung_ma_thoat_khac_trong_main(self):
        # cac ma thoat THAT main() co the tra ve, lay tu hang so (khong doan bang doc van ban nguon vi 3/4 duoc
        # tra ve qua ten hang so MA_THOAT_..., khong phai so nguyen tran trong code)
        self.assertEqual(mc.MA_THOAT_DA_CO_MAY_CHAY, 3, "tep mau dich vu ghim cung so 3, doi hang so thi phai doi ca tep mau")
        ma_khac = {0, 2, mc.MA_THOAT_LOI_KHOA}                        # 0=xong/KeyboardInterrupt, 2=loi mang NMPRP
        self.assertNotIn(mc.MA_THOAT_DA_CO_MAY_CHAY, ma_khac, "ma 'da co may chay khac' khong duoc trung ma thoat nao khac")
        self.assertEqual(len({0, 2, mc.MA_THOAT_DA_CO_MAY_CHAY, mc.MA_THOAT_LOI_KHOA}), 4, "bon ma thoat phai doi mot rieng")


class TestMaNguon(unittest.TestCase):
    def test_khong_co_duong_ghi_nguy_hiem(self):
        with open(mc.__file__, encoding="utf-8") as f:
            src = f.read()
        for ten in ("--yolo", "shell=True", "os.system", "post_goi_y(", "/admin/hermes/goi-y", "/duyet"):
            self.assertNotIn(ten, src)


SHA_A = "a" * 64
SHA_B = "B" * 64


class TestKhaiProfile(unittest.TestCase):
    """Máy chạy khai tệp profile khi chào (NMPRP CAU_HINH_PROFILE.md §1). Không bao giờ làm hỏng lời chào."""

    def test_doc_dong_sha_chi_giu_ten_nmprp_nhan_sap_xep_khu_trung(self):
        out = "\n".join([
            "%s  SOUL.md" % SHA_B,
            "%s  ./skills/nmprp-qa-governance/SKILL.md" % SHA_A,
            "%s  AGENTS.md" % SHA_A,
            "%s  SOUL.md" % SHA_A,                                  # trùng tên ⇒ giữ dòng đầu
            "%s  ../ngoai.md" % SHA_A,                              # ".." ⇒ bỏ
            "%s  co khoang trang.md" % SHA_A,                       # ký tự NMPRP không nhận ⇒ bỏ
            "sha256sum: memories/USER.md: No such file or directory",
            "rac",
        ])
        ds = mc.doc_dong_sha(out)
        self.assertEqual([d["ten"] for d in ds], ["AGENTS.md", "SOUL.md", "skills/nmprp-qa-governance/SKILL.md"])
        self.assertEqual(ds[1]["sha256"], "b" * 64)                  # chữ thường như NMPRP lưu
        for d in ds:
            self.assertEqual(set(d), {"ten", "sha256"})

    def test_doc_dong_sha_cat_toi_da_20(self):
        out = "\n".join("%s  skills/s%02d/SKILL.md" % (SHA_A, i) for i in range(30))
        self.assertEqual(len(mc.doc_dong_sha(out)), mc.TOI_DA_TEP_PROFILE)

    def test_khai_profile_goi_docker_exec_dung_nguoi_dung_va_thu_muc(self):
        seen = []

        def runner(argv):
            seen.append(argv)
            return 0, "%s  SOUL.md\n" % SHA_A
        ds = mc.khai_profile(cau_hinh(khai_profile=True, container="c1", profile="nmprp-mapping"), runner=runner)
        self.assertEqual(ds, [{"ten": "SOUL.md", "sha256": SHA_A}])
        self.assertEqual(seen[0][:6], ["docker", "exec", "-u", "hermes", "c1", "sh"])
        self.assertIn("/opt/data/profiles/nmprp-mapping", seen[0][-1])
        self.assertIn("skills/*/SKILL.md", seen[0][-1])

    def test_khai_profile_loi_thi_tra_rong_khong_nem(self):
        def hong(argv):
            raise FileNotFoundError("docker")
        self.assertEqual(mc.khai_profile(cau_hinh(khai_profile=True), runner=hong), [])

    def test_khai_profile_tat_thi_none_va_khong_goi_docker(self):
        def cam(argv):
            raise AssertionError("khong duoc goi docker khi cong tac tat")
        self.assertIsNone(mc.khai_profile(cau_hinh(khai_profile=False), runner=cam))

    def test_moi_truong_mac_dinh_bat_va_tat_bang_0(self):
        self.assertTrue(mc.CauHinh.tu_moi_truong({}).khai_profile)
        self.assertFalse(mc.CauHinh.tu_moi_truong({"HERMES_RUNNER_KHAI_PROFILE": "0"}).khai_profile)

    def test_mot_vong_gui_profile_tep_trong_loi_chao(self):
        class C:
            goi = []
            def may_chao(self, *a): C.goi.append(a)
            def may_nhan(self): return {"ok": True, "luot": None}
        with unittest.mock.patch.object(mc, "_chay_ngan", lambda argv: (0, "%s  AGENTS.md\n" % SHA_A)):
            mc.mot_vong(C(), cau_hinh(khai_profile=True, tep_dung="/khong/co/tep"))
        self.assertEqual(C.goi[0][3], [{"ten": "AGENTS.md", "sha256": SHA_A}])


if __name__ == "__main__":
    unittest.main()
