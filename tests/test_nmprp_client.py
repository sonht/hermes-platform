import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from support.nmprp_client import NmprpClient, NmprpError, check_allowed, strip_cpt

SEEN = []
STATE = {"expire_once": False}


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
        SEEN.append(("POST", self.path))
        if self.path == "/admin/auth/login" and body.get("password") == "pw":
            self._send(200, {"ok": True, "token": "tok%d" % len(SEEN)})
        else:
            self._send(401, {"detail": "no"})

    def do_GET(self):
        SEEN.append(("GET", self.path, self.headers.get("Authorization")))
        if STATE["expire_once"]:
            STATE["expire_once"] = False
            return self._send(401, {"detail": "expired"})
        if not (self.headers.get("Authorization") or "").startswith("Bearer tok"):
            return self._send(401, {"detail": "no"})
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

    def test_missing_config(self):
        with self.assertRaises(NmprpError):
            NmprpClient("", "", "")

    def test_strip_cpt_nested(self):
        self.assertEqual(strip_cpt({"a": [{"ma_cpt": "1", "b": 2}], "dai_ma": "x"}), {"a": [{"b": 2}]})


if __name__ == "__main__":
    unittest.main()
