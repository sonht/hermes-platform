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
