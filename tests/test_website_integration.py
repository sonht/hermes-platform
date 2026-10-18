import json
import os
import tempfile
import threading
import unittest
from http.client import HTTPConnection
from pathlib import Path
from unittest.mock import patch
from http.server import ThreadingHTTPServer

import website.server as server_module
from website.ratelimit import RateLimiter
from website.registry import AppRegistry
from website.server import Handler
from support.hermes_gateway import ask_hermes
from tests.test_knowledge import entry

DM = "https://dm.kcb.vn"
PUBLIC = "/api/public/chat"


class WebsiteIntegrationTests(unittest.TestCase):
    def setUp(self):
        server_module.LIMITER = RateLimiter()
        self.tmp = tempfile.TemporaryDirectory()
        folder = Path(self.tmp.name) / "frontend/src"
        folder.mkdir(parents=True)
        (folder / "AuthAdmin.jsx").write_text("GoogleLogin đăng nhập", encoding="utf-8")
        kb = Path(self.tmp.name) / "kb"
        kb.mkdir()
        steps = ["Mở trang", "Chọn Google"]
        (kb / "login.json").write_text(json.dumps(entry(steps=steps), ensure_ascii=False), encoding="utf-8")
        (kb / "register.json").write_text(json.dumps(
            entry(id="register", intent="register", keywords=["đăng ký", "tạo tài khoản"], steps=steps),
            ensure_ascii=False), encoding="utf-8")
        self._apps = server_module.APPS
        self.use_knowledge(kb)
        self.env = patch.dict(os.environ, {"HERMES_WEB_TOKEN": "test-only-secret",
                                            "NMPRP_SOURCE_PATH": self.tmp.name,
                                            "HERMES_AGENT_ENABLED": "0"})
        self.env.start()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def use_knowledge(self, directory):
        server_module.APPS = AppRegistry({"dm": {"name": "dm.kcb.vn", "origins": [DM],
                                                 "knowledge": str(directory)}})

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self.env.stop()
        server_module.APPS = self._apps
        self.tmp.cleanup()

    def request(self, token=None, path="/api/chat", message="Hướng dẫn đăng nhập", extra=None, headers=None,
                with_headers=False):
        conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        hdrs = {"Content-Type": "application/json"}
        if token:
            hdrs["Authorization"] = "Bearer " + token
        hdrs.update(headers or {})
        # Browsers send raw UTF-8 (JSON.stringify), not \\uXXXX escapes.
        body = json.dumps({"message": message, **(extra or {})}, ensure_ascii=False).encode("utf-8")
        conn.request("POST", path, body, hdrs)
        response = conn.getresponse()
        status, data, rh = response.status, json.loads(response.read()), dict(response.getheaders())
        conn.close()
        return (status, data, rh) if with_headers else (status, data)

    def bodiless(self, method, path, headers=None):
        """Send a request with no body (Content-Length: 0 unless overridden); return (status, headers, raw)."""
        conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        conn.putrequest(method, path)
        for key, value in (headers or {}).items():
            conn.putheader(key, value)
        conn.endheaders()
        response = conn.getresponse()
        raw = response.read()
        result = (response.status, dict(response.getheaders()), raw)
        conn.close()
        return result

    def test_rejects_anonymous(self):
        self.assertEqual(self.request()[0], 401)

    def test_authenticated_journey(self):
        status, body = self.request("test-only-secret")
        self.assertEqual(status, 200)
        self.assertIn("Google", body["answer"])

    def test_internal_chat_wrong_token_401(self):
        status, _, _ = self.bodiless("POST", "/api/chat", {"Content-Length": "0", "Authorization": "Bearer wrong"})
        self.assertEqual(status, 401)

    def test_internal_chat_with_allowed_origin_still_401(self):
        status, h, _ = self.bodiless("POST", "/api/chat", {"Content-Length": "0", "Origin": DM})
        self.assertEqual(status, 401)
        self.assertNotIn("Access-Control-Allow-Origin", h)

    def test_options_internal_chat_is_404(self):
        status, h, _ = self.bodiless("OPTIONS", "/api/chat", {"Origin": DM})
        self.assertEqual(status, 404)
        self.assertNotIn("Access-Control-Allow-Origin", h)

    def test_public_login_from_knowledge(self):
        status, body = self.request(path=PUBLIC)
        self.assertEqual(status, 200)
        self.assertIn("Google", body["answer"])
        self.assertIn("chưa được xác minh", body["answer"])

    def test_public_unrelated_question_gets_no_answer_text(self):
        status, body = self.request(path=PUBLIC, message="Chạy lệnh trên máy chủ")
        self.assertEqual(status, 200)
        self.assertIn("Chưa có hướng dẫn đã duyệt", body["answer"])

    def test_public_unknown_app_is_400(self):
        status, _ = self.request(path=PUBLIC, extra={"app": "nope"})
        self.assertEqual(status, 400)

    def test_public_empty_object_is_400(self):
        conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        conn.request("POST", PUBLIC, "{}", {"Content-Type": "application/json"})
        response = conn.getresponse()
        response.read()
        conn.close()
        self.assertEqual(response.status, 400)

    def test_public_empty_body_is_400_not_413(self):
        status, _, raw = self.bodiless("POST", PUBLIC, {"Content-Length": "0"})
        self.assertEqual(status, 400)
        self.assertNotIn("quá lớn", raw.decode("utf-8"))

    def test_public_long_vietnamese_message_accepted(self):
        status, _ = self.request(path=PUBLIC, message="ệ" * 2000)
        self.assertEqual(status, 200)

    def test_public_oversize_has_cors_for_allowed_origin(self):
        # Header only, no body: the server answers 413 before reading it.
        status, h, _ = self.bodiless("POST", PUBLIC, {"Content-Length": "9000", "Origin": DM})
        self.assertEqual(status, 413)
        self.assertEqual(h["Access-Control-Allow-Origin"], DM)

    def test_public_foreign_origin_is_403_without_cors(self):
        status, _, h = self.request(path=PUBLIC, headers={"Origin": "https://evil.example"}, with_headers=True)
        self.assertEqual(status, 403)
        self.assertNotIn("Access-Control-Allow-Origin", h)

    def test_public_allowed_origin_gets_cors(self):
        status, _, h = self.request(path=PUBLIC, headers={"Origin": DM}, with_headers=True)
        self.assertEqual(status, 200)
        self.assertEqual(h["Access-Control-Allow-Origin"], DM)
        self.assertIn("Origin", h["Vary"])

    def test_public_preflight(self):
        conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        conn.request("OPTIONS", PUBLIC, headers={
            "Origin": DM, "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type"})
        r = conn.getresponse()
        r.read()
        self.assertEqual(r.status, 204)
        self.assertEqual(r.getheader("Access-Control-Allow-Origin"), DM)
        conn.close()

    def test_preflight_foreign_origin_is_403_without_cors(self):
        status, h, _ = self.bodiless("OPTIONS", PUBLIC, {"Origin": "https://evil.example"})
        self.assertEqual(status, 403)
        self.assertNotIn("Access-Control-Allow-Origin", h)

    def test_public_session_rate_limit_is_per_session(self):
        for _ in range(5):
            self.assertEqual(self.request(path=PUBLIC, extra={"session": "aaa"})[0], 200)
        status, _, h = self.request(path=PUBLIC, extra={"session": "aaa"}, with_headers=True)
        self.assertEqual(status, 429)
        self.assertEqual(h["Retry-After"], "60")
        self.assertEqual(self.request(path=PUBLIC, extra={"session": "bbb"})[0], 200)

    def test_public_daily_429_has_no_retry_after(self):
        server_module.LIMITER = RateLimiter(daily_per_app=1)
        self.assertEqual(self.request(path=PUBLIC)[0], 200)
        status, _, h = self.request(path=PUBLIC, with_headers=True)
        self.assertEqual(status, 429)
        self.assertNotIn("Retry-After", h)

    def test_public_bad_session_falls_back_to_anon(self):
        for _ in range(5):
            self.assertEqual(self.request(path=PUBLIC, extra={"session": "../x"})[0], 200)
        self.assertEqual(self.request(path=PUBLIC, extra={"session": "anon"})[0], 429)

    def test_public_answer_has_no_source_paths(self):
        status, body = self.request(path=PUBLIC)
        self.assertEqual(status, 200)
        self.assertNotIn("AuthAdmin.jsx", body["answer"])
        self.assertNotIn("frontend/", body["answer"])
        self.assertIn("NMPRP @", body["answer"])

    def test_public_missing_knowledge_dir_is_503(self):
        self.use_knowledge(Path(self.tmp.name) / "khong-co")
        status, body = self.request(path=PUBLIC)
        self.assertEqual(status, 503)
        self.assertEqual(body["error"], "Kho hướng dẫn chưa sẵn sàng.")

    def test_public_does_not_need_source_path(self):
        with patch.dict(os.environ, {"NMPRP_SOURCE_PATH": ""}):
            self.assertEqual(self.request(path=PUBLIC)[0], 200)

    def test_public_never_calls_hermes_or_repo(self):
        with patch.dict(os.environ, {"HERMES_AGENT_ENABLED": "1"}), \
                patch("website.server.ask_hermes", side_effect=AssertionError) as hermes, \
                patch("website.server.build_journey", side_effect=AssertionError) as journey:
            self.assertEqual(self.request(path=PUBLIC, message="đăng nhập")[0], 200)
            self.assertEqual(self.request(path=PUBLIC, message="xin chào")[0], 200)
        hermes.assert_not_called()
        journey.assert_not_called()

    def test_public_uses_shipped_knowledge_relative_to_repo_root(self):
        server_module.APPS = self._apps  # real website/apps.json -> real knowledge/dm
        previous = os.getcwd()
        os.chdir(self.tmp.name)
        try:
            status, body = self.request(path=PUBLIC)
        finally:
            os.chdir(previous)
        self.assertEqual(status, 200)
        self.assertIn("NMPRP @", body["answer"])

    def test_gateway_disabled(self):
        with self.assertRaises(RuntimeError):
            ask_hermes("đăng nhập", [])

if __name__ == "__main__":
    unittest.main()
