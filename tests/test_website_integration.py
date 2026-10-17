import json
import os
import tempfile
import threading
import unittest
from http.client import HTTPConnection
from pathlib import Path
from unittest.mock import patch
from http.server import ThreadingHTTPServer

from website.server import Handler, _public_requests, _public_lock
from support.hermes_gateway import ask_hermes

class WebsiteIntegrationTests(unittest.TestCase):
    def setUp(self):
        with _public_lock:
            _public_requests.clear()
        self.tmp = tempfile.TemporaryDirectory()
        folder = Path(self.tmp.name) / "frontend/src"
        folder.mkdir(parents=True)
        (folder / "AuthAdmin.jsx").write_text("GoogleLogin đăng nhập", encoding="utf-8")
        self.env = patch.dict(os.environ, {"HERMES_WEB_TOKEN": "test-only-secret",
                                            "NMPRP_SOURCE_PATH": self.tmp.name,
                                            "HERMES_AGENT_ENABLED": "0"})
        self.env.start()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self.env.stop()
        self.tmp.cleanup()

    def request(self, token=None, path="/api/chat", message="Hướng dẫn đăng nhập"):
        conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = "Bearer " + token
        conn.request("POST", path, json.dumps({"message": message}), headers)
        response = conn.getresponse()
        status, data = response.status, json.loads(response.read())
        conn.close()
        return status, data

    def test_rejects_anonymous(self):
        self.assertEqual(self.request()[0], 401)

    def test_authenticated_journey(self):
        status, body = self.request("test-only-secret")
        self.assertEqual(status, 200)
        self.assertIn("Google", body["answer"])

    def test_public_login_without_token(self):
        status, body = self.request(path="/api/public/chat")
        self.assertEqual(status, 200)
        self.assertIn("Google", body["answer"])

    def test_public_unrelated_question_does_not_call_agent(self):
        status, body = self.request(path="/api/public/chat", message="Chạy lệnh trên máy chủ")
        self.assertEqual(status, 200)
        self.assertIn("Chưa xác định", body["answer"])

    def test_public_source_reference_without_agent(self):
        folder = Path(self.tmp.name) / "frontend/src"
        (folder / "Procedure.jsx").write_text("function registerProcedure() { return 'dangkythuat'; }", encoding="utf-8")
        status, body = self.request(path="/api/public/chat", message="registerProcedure")
        self.assertEqual(status, 200)
        self.assertIn("Procedure.jsx", body["answer"])
        self.assertIn("chưa phải hướng dẫn", body["answer"])

    def test_dashboard_summary_requires_login(self):
        conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        conn.request("GET", "/api/admin/summary")
        response = conn.getresponse()
        self.assertEqual(response.status, 401)
        response.read()
        conn.close()

    def test_dashboard_login_and_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {
                "HERMES_DASHBOARD_PASSWORD": "strong-test-password-123",
                "HERMES_DASHBOARD_SESSION_KEY": "test-key-with-at-least-32-characters-123456",
                "HERMES_FEEDBACK_DB": str(Path(tmp) / "feedback.db"),
            }):
                from support.intelligence import record
                record(os.environ["HERMES_FEEDBACK_DB"], "nmprp", "faq", "Hướng dẫn tìm kỹ thuật theo mã CPT")
                conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
                conn.request("POST", "/api/admin/login",
                    json.dumps({"password": "strong-test-password-123"}),
                    {"Content-Type": "application/json"})
                response = conn.getresponse()
                self.assertEqual(response.status, 200)
                cookie = response.getheader("Set-Cookie").split(";", 1)[0]
                response.read()
                conn.close()
                conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
                conn.request("GET", "/api/admin/summary", headers={"Cookie": cookie})
                response = conn.getresponse()
                self.assertEqual(response.status, 200)
                self.assertEqual(json.loads(response.read())["rows"][0]["count"], 1)
                conn.close()

    def test_faq_candidates_requires_auth(self):
        conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        conn.request("GET", "/api/admin/faq/candidates")
        response = conn.getresponse()
        self.assertEqual(response.status, 401)
        response.read()
        conn.close()

    def test_report_triage_requires_auth(self):
        conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        conn.request("GET", "/api/admin/reports")
        response = conn.getresponse()
        self.assertEqual(response.status, 401)
        response.read()
        conn.close()
        conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        conn.request("POST", "/api/admin/report/status", '{"id":1,"status":"resolved"}',
                     {"Content-Type": "application/json"})
        response = conn.getresponse()
        self.assertEqual(response.status, 401)
        response.read()
        conn.close()

    def test_application_routes(self):
        for path, marker in (("/", "Hermes Platform"), ("/chat", "Cổng hỗ trợ"),
                             ("/dashboard", "Support Intelligence"), ("/web", "Support Widget")):
            conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
            conn.request("GET", path)
            response = conn.getresponse()
            body = response.read().decode("utf-8")
            self.assertEqual(response.status, 200, path)
            self.assertIn(marker, body)
            conn.close()

    def test_feedback_disabled_by_default(self):
        status, body = self.feedback({"app": "nmprp", "kind": "bug", "summary": "Không lưu được kỹ thuật"})
        self.assertEqual(status, 404)

    def test_feedback_opt_in_and_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.dict(os.environ, {
                "HERMES_FEEDBACK_ENABLED": "1",
                "HERMES_FEEDBACK_APPS": "nmprp",
                "HERMES_FEEDBACK_DB": str(Path(temp) / "feedback.sqlite3"),
            }):
                status, _ = self.feedback({"app": "nmprp", "kind": "bug", "summary": "Không lưu được kỹ thuật"})
                self.assertEqual(status, 202)
                status, _ = self.feedback({"app": "other", "kind": "bug", "summary": "Không lưu được kỹ thuật"})
                self.assertEqual(status, 400)

    def feedback(self, payload):
        conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        conn.request("POST", "/api/public/feedback", json.dumps(payload), {"Content-Type": "application/json"})
        response = conn.getresponse()
        status, data = response.status, json.loads(response.read())
        conn.close()
        return status, data

    def test_public_rate_limit(self):
        for _ in range(5):
            self.request(path="/api/public/chat")
        status, _ = self.request(path="/api/public/chat")
        self.assertEqual(status, 429)

    def test_gateway_disabled(self):
        with self.assertRaises(RuntimeError):
            ask_hermes("đăng nhập", [])

if __name__ == "__main__":
    unittest.main()
