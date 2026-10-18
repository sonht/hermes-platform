import json
import threading
import urllib.parse
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from support.nmprp_client import NmprpClient, NmprpError, check_allowed, strip_cpt

SEEN = []
STATE = {"expire_once": False, "ai": {"ok": True, "cong_tac": True, "key_masked": "sk-***"}, "ai_code": 200}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        SEEN.append(("POST", self.path, self.headers.get("Authorization"), body))
        if self.path == "/admin/auth/login" and body.get("password") == "pw":
            self._send(200, {"ok": True, "token": "tok%d" % len(SEEN)})
        elif (self.path in ("/admin/hermes/goi-y", "/admin/hermes/su-kien") or self.path.startswith("/admin/hermes/may/")) and \
                (self.headers.get("Authorization") or "").startswith("Bearer tok"):
            self._send(200, {"ok": True, "da_ghi": len(body.get("items", []))})
        else:
            self._send(401, {"detail": "no"})

    def do_GET(self):
        SEEN.append(("GET", self.path, self.headers.get("Authorization")))
        if STATE["expire_once"]:
            STATE["expire_once"] = False
            return self._send(401, {"detail": "expired"})
        if not (self.headers.get("Authorization") or "").startswith("Bearer tok"):
            return self._send(401, {"detail": "no"})
        if self.path.startswith("/admin/ai/status"):
            return self._send(STATE["ai_code"], STATE["ai"])
        if self.path.startswith("/admin/hermes/phan-hoi"):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            sau, n = (q.get("sau") or [""])[0], int((q.get("limit") or ["200"])[0])
            if STATE.get("ignore_cursor"):
                sau = ""                                                  # máy chủ cũ: bỏ qua con trỏ
            rows = [r for r in STATE["fb"] if not sau or (r["luc"], r["goi_y_id"]) > tuple(sau.split("|", 1))][:n]
            return self._send(200, {"ok": True, "phan_hoi": rows,
                                    "tiep": ("%s|%s" % (rows[-1]["luc"], rows[-1]["goi_y_id"])) if rows else ""})
        self._send(200, {"ok": True, "nodes": [{"ten": "Noi soi", "dai_ma": "14000 - 14350"}]})


class ClientTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.base = "http://127.0.0.1:%d" % cls.srv.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def setUp(self):
        SEEN.clear()
        STATE["expire_once"] = False
        STATE["ignore_cursor"] = False
        STATE["fb"] = [{"goi_y_id": "HG_%02d" % i, "pl2_code": "BS_6.%d0" % i, "branch_key": "A > B", "quyet_dinh": "TU_CHOI",
                        "ly_do": "sai", "branch_key_sua": "A > C", "nhan": "EXPERT_FEEDBACK", "luc": "2026-10-17T10:00:0%d.000000Z" % i}
                       for i in range(5)]
        STATE["ai"], STATE["ai_code"] = {"ok": True, "cong_tac": True, "key_masked": "sk-***"}, 200

    def client(self, pw="pw"):
        return NmprpClient(self.base, "svc", pw)

    def test_login_then_get_strips_cpt_ranges(self):
        d = self.client().khung()
        self.assertEqual(d["nodes"], [{"ten": "Noi soi"}])          # dai_ma removed
        self.assertEqual(SEEN[0][:2], ("POST", "/admin/auth/login"))
        self.assertTrue(SEEN[1][2].startswith("Bearer tok"))

    def test_relogin_once_on_401(self):
        c = self.client()
        c.khung()
        STATE["expire_once"] = True
        c.khung()
        self.assertEqual([s[0] for s in SEEN].count("POST"), 2)

    def test_blocked_and_unlisted_paths_make_no_request(self):
        c = self.client()
        for path, q in [("/admin/cpt-tree/khung/ma-cpt", {}),
                        ("/admin/cpn-ai/runs/r1/duyet", {}),
                        ("/admin/ai/config", {}),
                        ("/review/search", {"kind": "cpt"}),
                        ("/review/map", {"kind": "cpt"}),
                        ("/review/map", {"kind": "icd9"}),
                        ("/admin/cpn-ai/runs/../x", {})]:
            with self.assertRaises(NmprpError, msg=path):
                c.get(path, **q)
        self.assertEqual(SEEN, [])

    def test_allowed_examples(self):
        for path, q in [("/admin/cpn-ai/runs/run_1/candidates", {}),
                        ("/review/search", {"kind": "pl3", "q": "6.1"}),
                        ("/review/map", {"kind": "pl1", "code": "1"})]:
            check_allowed(path, q)

    def test_errors_never_leak_secrets(self):
        with self.assertRaises(NmprpError) as cm:
            self.client(pw="wrong-secret").khung()
        self.assertNotIn("wrong-secret", str(cm.exception))
        self.assertNotIn("wrong-secret", repr(self.client()))

    def test_owner_can_enable_cpt_content_explicitly(self):
        c = NmprpClient(self.base, "svc", "pw", allow_cpt=True)
        self.assertEqual(c.khung()["nodes"][0]["dai_ma"], "14000 - 14350")   # kept when owner enables
        check_allowed("/admin/cpt-tree/khung/ma-cpt", {}, allow_cpt=True)
        check_allowed("/review/map", {"kind": "cpt"}, allow_cpt=True)
        with self.assertRaises(NmprpError):                                  # default stays strict
            check_allowed("/admin/cpt-tree/khung/ma-cpt", {})
        with self.assertRaises(NmprpError):                                  # still allowlist-only
            check_allowed("/admin/cpn-ai/runs/r1/duyet", {}, allow_cpt=True)
        self.assertFalse(self.client().allow_cpt)

    def test_post_goi_y_va_su_kien_di_dung_duong_va_co_the_dang_nhap_lai(self):
        c = self.client()
        r = c.post_goi_y([{"pl2_code": "6.100", "branch_key": "A > B", "phien_ban": "s1"}])
        self.assertEqual(r["da_ghi"], 1)
        c.post_su_kien("NHIP", "ok")
        posts = [x for x in SEEN if x[0] == "POST" and x[1].startswith("/admin/hermes/")]
        self.assertEqual([x[1] for x in posts], ["/admin/hermes/goi-y", "/admin/hermes/su-kien"])
        self.assertTrue(posts[0][2].startswith("Bearer tok"))
        self.assertEqual(posts[0][3]["items"][0]["pl2_code"], "6.100")        # mã giữ nguyên văn

    def test_post_ra_ngoai_hai_duong_hep_bi_tu_choi_truoc_khi_goi_mang(self):
        c = self.client()
        for path in ("/admin/cpn-ai/runs", "/admin/cpn-ai/candidates/c1/duyet", "/admin/ai/set", "/admin/ai/cong-tac",
                     "/admin/hermes/goi-y/../x", "/admin/hermes/duyet", "/admin/catalog/amend"):
            with self.assertRaises(NmprpError, msg=path):
                c.post(path, {})
        self.assertEqual(SEEN, [])

    def test_hang_doi_may_chay_di_dung_sau_duong_va_khong_them_duong_nao(self):
        c = self.client()
        c.may_chao("r@1", ["m"], ["low"])
        c.may_nhan()
        c.may_tien_do("HL_0123456789ab", {"DOC": {"tt": "DANG"}}, {"lan_goi": 1}, "dang chay")
        c.may_goi_y("HL_0123456789ab", [{"pl2_code": "6.10"}])
        c.may_ket_qua("HL_0123456789ab", [{"pl2_code": "6.10", "muc": "UNRESOLVED"}])
        c.may_ket_thuc("HL_0123456789ab", "XONG", "ok")
        posts = [x for x in SEEN if x[0] == "POST" and x[1].startswith("/admin/hermes/may/")]
        self.assertEqual([x[1] for x in posts], [
            "/admin/hermes/may/chao", "/admin/hermes/may/nhan", "/admin/hermes/may/luot/HL_0123456789ab/tien-do",
            "/admin/hermes/may/luot/HL_0123456789ab/goi-y", "/admin/hermes/may/luot/HL_0123456789ab/ket-qua",
            "/admin/hermes/may/luot/HL_0123456789ab/ket-thuc"])
        self.assertEqual(posts[3][3]["items"][0]["pl2_code"], "6.10")                  # mã giữ nguyên văn
        self.assertEqual(posts[2][3]["thong_diep"], "dang chay")

    def test_duong_may_la_hoac_id_khong_phai_luot_bi_tu_choi_truoc_khi_goi_mang(self):
        c = self.client()
        for path in ("/admin/hermes/may/luot/HL_0123456789ab/duyet", "/admin/hermes/may/luot/HL_0123456789ab/",
                     "/admin/hermes/may/luot/HL_0123456789ab/tien-do/../ket-thuc", "/admin/hermes/may/luot/x/tien-do", "/admin/hermes/may/luot/HL_01/tien-do",
                     "/admin/hermes/may/luot/HL_0123456789abcd/tien-do", "/admin/hermes/may/luot/HL_0123456789AB/tien-do",
                     "/admin/hermes/may/luot/HL_01/../../goi-y/tien-do", "/admin/hermes/may/luot/HL_0123456789ab/tien-do?x=1",
                     "/admin/hermes/may/chao/x", "/admin/hermes/may", "/admin/hermes/may/luot", "/admin/hermes/luot",
                     "/admin/hermes/luot/HL_0123456789ab/chay-tiep", "/admin/hermes/luot/HL_0123456789ab/huy"):
            with self.assertRaises(NmprpError, msg=path):
                c.post(path, {})
        self.assertEqual(SEEN, [])
        for path in ("/admin/hermes/may", "/admin/hermes/luot", "/admin/hermes/chuong"):   # đọc vẫn là việc của admin, không của Hermes
            with self.assertRaises(NmprpError, msg=path):
                c.get(path)

    def test_ai_cong_tac_fail_closed(self):
        c = self.client()
        self.assertTrue(c.ai_cong_tac_bat())
        for ai, code in [({"ok": True, "cong_tac": False}, 200), ({"ok": True}, 200), ({"cong_tac": "1"}, 200),
                         ({"cong_tac": 1}, 200), ({"detail": "x"}, 500), ({"detail": "x"}, 403)]:
            STATE["ai"], STATE["ai_code"] = ai, code
            self.assertFalse(self.client().ai_cong_tac_bat(), (ai, code))      # lỗi/thiếu/lạ ⇒ TẮT

    def test_phan_hoi_doc_theo_con_tro_du_trang_va_giu_ma_nguyen_van(self):
        rows, cur = self.client().phan_hoi_moi(limit=2)
        self.assertEqual([r["goi_y_id"] for r in rows], ["HG_00", "HG_01", "HG_02", "HG_03", "HG_04"])
        self.assertEqual(rows[0]["pl2_code"], "BS_6.00")                      # tiền tố BS_ và số 0 giữ nguyên
        self.assertEqual(cur, "2026-10-17T10:00:04.000000Z|HG_04")
        STATE["fb"].append(dict(STATE["fb"][0], goi_y_id="HG_05", luc="2026-10-17T10:00:09.000000Z"))
        rows2, cur2 = self.client().phan_hoi_moi(sau=cur)                     # lần chạy sau: chỉ phần MỚI
        self.assertEqual([r["goi_y_id"] for r in rows2], ["HG_05"])
        self.assertEqual(cur2, "2026-10-17T10:00:09.000000Z|HG_05")
        self.assertEqual(self.client().phan_hoi_moi(sau=cur2), ([], cur2))     # hết: giữ nguyên con trỏ
        gets = [x[1] for x in SEEN if x[0] == "GET" and "phan-hoi" in x[1]]
        self.assertTrue(all(g.startswith("/admin/hermes/phan-hoi") for g in gets) and len(gets) >= 5)

    def test_phan_hoi_may_chu_bo_qua_con_tro_thi_khong_lap_vo_han(self):
        STATE["ignore_cursor"] = True
        rows, _ = self.client().phan_hoi_moi(limit=2, toi_da_trang=50)
        self.assertEqual(len(rows), 2)                                        # trang lặp lại ⇒ dừng, không vòng lặp vô hạn
        self.assertLessEqual(len([x for x in SEEN if x[0] == "GET" and "phan-hoi" in x[1]]), 3)

    def test_duong_admin_hermes_khac_van_bi_chan_chi_phan_hoi_duoc_doc(self):
        c = self.client()
        for path in ("/admin/hermes/goi-y", "/admin/hermes/tom-tat", "/admin/hermes/su-kien", "/admin/hermes/phan-hoi/x",
                     "/admin/hermes/phan-hoi/../goi-y", "/admin/hermes/goi-y/HG_1/duyet"):
            with self.assertRaises(NmprpError, msg=path):
                c.get(path)
        for path in ("/admin/hermes/goi-y/HG_1/duyet", "/admin/hermes/phan-hoi"):     # duyệt là việc của người, không phải Hermes
            with self.assertRaises(NmprpError, msg=path):
                c.post(path, {"quyet_dinh": "DONG_Y", "ly_do": "x"})
        self.assertEqual([x for x in SEEN if x[0] == "GET" and "/admin/hermes/" in x[1]], [])

    def test_missing_config(self):
        with self.assertRaises(NmprpError):
            NmprpClient("", "", "")

    def test_strip_cpt_nested(self):
        self.assertEqual(strip_cpt({"a": [{"ma_cpt": "1", "b": 2}], "dai_ma": "x"}), {"a": [{"b": 2}]})


if __name__ == "__main__":
    unittest.main()
