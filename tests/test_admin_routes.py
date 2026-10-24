import json
import os
import tempfile
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

import website.server as server_module
from website.ratelimit import RateLimiter
from website.registry import AppRegistry
from website.server import Handler

DM = "https://dm.kcb.vn"
PW = "strong-test-password-123"
KEY = "test-key-with-at-least-32-characters-123456"


class AdminRoutesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self._saved = (server_module.APPS, server_module.LIMITER, server_module.LOGIN_LIMITER)
        server_module.APPS = AppRegistry({"nmprp": {"name": "n", "origins": [DM], "knowledge": self.tmp.name}})
        server_module.LIMITER = RateLimiter()
        server_module.LOGIN_LIMITER = RateLimiter(per_session=5, per_app=5, daily_per_app=200)
        self.env = patch.dict(os.environ, {
            "HERMES_DASHBOARD_PASSWORD": PW, "HERMES_DASHBOARD_SESSION_KEY": KEY,
            "HERMES_FEEDBACK_DB": str(Path(self.tmp.name) / "fb.db"), "HERMES_FEEDBACK_APPS": "nmprp"})
        self.env.start()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.env.stop()
        server_module.APPS, server_module.LIMITER, server_module.LOGIN_LIMITER = self._saved
        self.tmp.cleanup()

    def call(self, method, path, body=None, headers=None):
        conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        data = json.dumps(body) if body is not None else None
        conn.request(method, path, data, {"Content-Type": "application/json", **(headers or {})})
        r = conn.getresponse()
        raw = r.read()
        conn.close()
        try:
            return r.status, json.loads(raw), r
        except ValueError:
            return r.status, raw, r

    def login(self):
        status, _, r = self.call("POST", "/api/admin/login", {"password": PW})
        self.assertEqual(status, 200)
        return r.getheader("Set-Cookie").split(";", 1)[0]

    def admin_headers(self, cookie):
        return {"Cookie": cookie, "Origin": "https://127.0.0.1:%d" % self.server.server_port,
                "Host": "127.0.0.1:%d" % self.server.server_port}

    def test_admin_reads_require_login(self):
        for path in ("/api/admin/summary", "/api/admin/reports", "/api/admin/faq/articles", "/api/admin/faq/candidates"):
            self.assertEqual(self.call("GET", path)[0], 401, path)

    def test_admin_mutations_require_login(self):
        for path in ("/api/admin/faq/draft", "/api/admin/faq/publish", "/api/admin/report/status"):
            self.assertEqual(self.call("POST", path, {"id": 1})[0], 401, path)

    def test_login_wrong_password_401_and_rate_limited(self):
        self.assertEqual(self.call("POST", "/api/admin/login", {"password": "x"})[0], 401)
        for _ in range(4):
            self.call("POST", "/api/admin/login", {"password": "x"})
        self.assertEqual(self.call("POST", "/api/admin/login", {"password": PW})[0], 429)

    def test_login_then_summary_and_session(self):
        cookie = self.login()
        self.assertTrue(self.call("GET", "/api/admin/session", headers={"Cookie": cookie})[1]["authenticated"])
        self.assertFalse(self.call("GET", "/api/admin/session")[1]["authenticated"])
        from support.intelligence import record
        record(os.environ["HERMES_FEEDBACK_DB"], "nmprp", "faq", "Hướng dẫn tìm kỹ thuật theo mã CPT")
        status, body, _ = self.call("GET", "/api/admin/summary", headers={"Cookie": cookie})
        self.assertEqual((status, body["rows"][0]["count"]), (200, 1))

    def test_mutation_needs_same_origin_and_json(self):
        cookie = self.login()
        h = self.admin_headers(cookie)
        self.assertEqual(self.call("POST", "/api/admin/report/status", {"id": 1, "status": "resolved"},
                                   {**h, "Origin": "https://evil.example"})[0], 403)
        self.assertEqual(self.call("POST", "/api/admin/report/status", {"id": 1, "status": "resolved"},
                                   {**h, "Content-Type": "text/plain"})[0], 415)

    def test_faq_draft_publish_and_public_read(self):
        h = self.admin_headers(self.login())
        # Same-origin check compares Origin to https://<Host>, so the Host header drives it.
        status, body, _ = self.call("POST", "/api/admin/faq/draft",
                                    {"app": "nmprp", "question": "Đăng nhập?", "answer": "Chọn Google."}, h)
        self.assertEqual(status, 201)
        self.assertEqual(self.call("GET", "/api/public/faq?app=nmprp")[1]["rows"], [])
        self.assertEqual(self.call("POST", "/api/admin/faq/publish", {"id": body["id"], "publish": True}, h)[0], 200)
        self.assertEqual(len(self.call("GET", "/api/public/faq?app=nmprp")[1]["rows"]), 1)
        self.assertEqual(self.call("GET", "/api/public/faq?app=other")[0], 400)

    def test_faq_draft_rejects_unlisted_app(self):
        h = self.admin_headers(self.login())
        self.assertEqual(self.call("POST", "/api/admin/faq/draft",
                                   {"app": "other", "question": "q", "answer": "a"}, h)[0], 400)

    def test_feedback_disabled_by_default(self):
        self.assertEqual(self.call("POST", "/api/public/feedback",
                                   {"app": "nmprp", "kind": "bug", "summary": "Không lưu được"})[0], 404)

    def test_feedback_opt_in_needs_registered_app_and_non_foreign_origin(self):
        payload = {"app": "nmprp", "kind": "bug", "summary": "Không lưu được kỹ thuật"}
        with patch.dict(os.environ, {"HERMES_FEEDBACK_ENABLED": "1"}):
            self.assertEqual(self.call("POST", "/api/public/feedback", payload, {"Origin": DM})[0], 202)
            # No Origin header (non-browser caller) is accepted, same as the public chat contract.
            self.assertEqual(self.call("POST", "/api/public/feedback", payload)[0], 202)
            self.assertEqual(self.call("POST", "/api/public/feedback", payload, {"Origin": "https://evil.example"})[0], 403)
            self.assertEqual(self.call("POST", "/api/public/feedback", {**payload, "app": "other"}, {"Origin": DM})[0], 400)

    def test_public_chat_contract_untouched(self):
        # Admin routes must not turn the public chat into a source-aware or Hermes-calling endpoint.
        with patch("website.server.ask_hermes", side_effect=AssertionError), \
                patch("website.server.build_journey", side_effect=AssertionError):
            status, body, _ = self.call("POST", "/api/public/chat", {"app": "nmprp", "message": "Chạy lệnh"},
                                        {"Origin": DM})
        self.assertEqual(status, 200)
        self.assertNotIn("frontend/", body["answer"])


if __name__ == "__main__":
    unittest.main()
