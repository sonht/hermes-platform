import json
import os
import tempfile
import unittest

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

    def ai_cong_tac_bat(self):
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
        self.assertEqual(C.goi[0], ("chao", (("m",), ("low", "medium", "high"))))   # khai đúng danh sách của chính máy

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

    def test_cau_hinh_tu_moi_truong(self):
        c = mc.CauHinh.tu_moi_truong({"HERMES_RUNNER_MODELS": "a, b ,", "HERMES_RUNNER_REASONING": "low,bogus,high",
                                      "HERMES_RUNNER_DUNG": "/x"})
        self.assertEqual((c.mo_hinh, c.suy_luan, c.tep_dung), (("a", "b"), ("low", "high"), "/x"))
        self.assertEqual(mc.CauHinh.tu_moi_truong({}).mo_hinh, ())                  # không ghi cứng tên mô hình nào


class TestMaNguon(unittest.TestCase):
    def test_khong_co_duong_ghi_nguy_hiem(self):
        with open(mc.__file__, encoding="utf-8") as f:
            src = f.read()
        for ten in ("--yolo", "shell=True", "os.system", "post_goi_y(", "/admin/hermes/goi-y", "/duyet"):
            self.assertNotIn(ten, src)


if __name__ == "__main__":
    unittest.main()
