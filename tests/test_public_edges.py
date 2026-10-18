import json
import tempfile
import threading
import unicodedata
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path

import website.server as server_module
from support.knowledge import find_entry, load_entries
from tests.test_knowledge import entry
from website.ratelimit import RateLimiter
from website.registry import AppRegistry
from website.server import Handler

DM = "https://dm.kcb.vn"
OTHER = "https://other.example"
PUBLIC = "/api/public/chat"
ROOT = Path(__file__).resolve().parents[1]


class PublicEdgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        kb = Path(self.tmp.name) / "kb"
        kb.mkdir()
        (kb / "login.json").write_text(json.dumps(entry(), ensure_ascii=False), encoding="utf-8")
        self.kb = kb
        self._apps, self._limiter = server_module.APPS, server_module.LIMITER
        server_module.LIMITER = RateLimiter()
        server_module.APPS = AppRegistry({
            "dm": {"name": "dm", "origins": [DM], "knowledge": str(kb)},
            "other": {"name": "other", "origins": [OTHER], "knowledge": str(kb)}})
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        server_module.APPS, server_module.LIMITER = self._apps, self._limiter
        self.tmp.cleanup()

    def post(self, raw, headers=None):
        conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        conn.request("POST", PUBLIC, raw if isinstance(raw, bytes) else json.dumps(raw, ensure_ascii=False).encode(),
                     {"Content-Type": "application/json", **(headers or {})})
        r = conn.getresponse()
        data = r.read()
        out = (r.status, dict(r.getheaders()), data)
        conn.close()
        return out

    def test_origin_of_other_app_cannot_use_dm_403_no_cors(self):
        status, h, _ = self.post({"app": "dm", "message": "đăng nhập"}, {"Origin": OTHER})
        self.assertEqual(status, 403)
        self.assertNotIn("Access-Control-Allow-Origin", h)

    def test_each_app_accepts_its_own_origin_with_matching_cors(self):
        for app, origin in (("dm", DM), ("other", OTHER)):
            status, h, _ = self.post({"app": app, "message": "đăng nhập"}, {"Origin": origin})
            self.assertEqual((status, h["Access-Control-Allow-Origin"]), (200, origin))

    def test_origin_case_and_trailing_slash_are_not_allowed(self):
        for origin in ("https://DM.kcb.vn", DM + "/", "http://dm.kcb.vn"):
            status, h, _ = self.post({"app": "dm", "message": "đăng nhập"}, {"Origin": origin})
            self.assertEqual(status, 403, origin)
            self.assertNotIn("Access-Control-Allow-Origin", h)

    def test_malformed_bodies_are_400_not_dropped(self):
        for raw in (b"not json", b"[]", b"null", b'"x"', b'{"message": 5}', b'{"message": "   "}',
                    b'{"message": null}', b'\xff\xfe'):
            self.assertEqual(self.post(raw)[0], 400, raw)

    def test_non_string_app_and_session_do_not_crash(self):
        status, _, _ = self.post({"app": ["dm"], "message": "đăng nhập"})
        self.assertEqual(status, 400)
        status, _, _ = self.post({"app": {"x": 1}, "message": "đăng nhập"})
        self.assertEqual(status, 400)
        for session in (123, ["a"], None, "a" * 65, "", "a b", "é"):
            server_module.LIMITER = RateLimiter()  # invalid ids share the "anon" bucket
            self.assertEqual(self.post({"message": "đăng nhập", "session": session})[0], 200, session)

    def test_non_numeric_content_length_is_400(self):
        conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        conn.putrequest("POST", PUBLIC)
        conn.putheader("Content-Length", "abc")
        conn.endheaders()
        r = conn.getresponse()
        r.read()
        conn.close()
        self.assertEqual(r.status, 400)

    def test_corrupt_knowledge_file_is_503_with_fixed_message(self):
        (self.kb / "bad.json").write_text("{not json", encoding="utf-8")
        status, _, raw = self.post({"message": "đăng nhập"})
        self.assertEqual(status, 503)
        self.assertEqual(json.loads(raw)["error"], "Kho hướng dẫn chưa sẵn sàng.")
        self.assertNotIn(self.tmp.name.encode(), raw)

    def test_message_exactly_2000_ok_and_2001_rejected(self):
        self.assertEqual(self.post({"message": "a" * 2000})[0], 200)
        self.assertEqual(self.post({"message": "a" * 2001})[0], 400)

    def test_decomposed_unicode_and_extra_spaces_match(self):
        entries = load_entries(self.kb)
        nfd = unicodedata.normalize("NFD", "Hướng dẫn đăng nhập")
        self.assertNotEqual(nfd, "Hướng dẫn đăng nhập")
        self.assertEqual(find_entry(entries, nfd)["intent"], "login")
        self.assertEqual(find_entry(entries, "đăng    nhập\t\nvào")["intent"], "login")
        self.assertEqual(find_entry(entries, "ĐĂNG NHẬP")["intent"], "login")

    def test_shipped_knowledge_login_and_register_have_distinct_answers(self):
        entries = load_entries(ROOT / "knowledge/dm")
        self.assertEqual(sorted(e["id"] for e in entries), ["login", "register"])
        self.assertTrue(all(e["verification_status"] == "chua-xac-minh" for e in entries))
        self.assertEqual(find_entry(entries, "Đăng nhập")["intent"], "login")
        self.assertEqual(find_entry(entries, "Đăng ký")["intent"], "register")


if __name__ == "__main__":
    unittest.main()
