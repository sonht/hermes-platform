import re
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path

from website.server import Handler

WIDGET = Path(__file__).resolve().parents[1] / "website" / "widget.js"


class WidgetTests(unittest.TestCase):
    def test_served_as_javascript(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        try:
            conn = HTTPConnection("127.0.0.1", server.server_port, timeout=3)
            conn.request("GET", "/widget.js")
            r = conn.getresponse()
            body = r.read().decode("utf-8")
            self.assertEqual(r.status, 200)
            self.assertIn("javascript", r.getheader("Content-Type"))
            self.assertIn("attachShadow", body)
        finally:
            server.shutdown()
            server.server_close()
            t.join(timeout=3)

    def test_static_safety_rules(self):
        src = WIDGET.read_text(encoding="utf-8")
        self.assertNotIn("innerHTML", src)          # answers are inserted as text only
        self.assertNotIn("eval(", src)
        self.assertNotIn("document.write", src)
        self.assertNotIn("localStorage", src)       # session id lives in sessionStorage only
        self.assertFalse(re.search(r"(password|otp|token)\s*[:=]", src, re.I))

    def test_requires_data_app_and_uses_script_origin(self):
        src = WIDGET.read_text(encoding="utf-8")
        self.assertIn("data-app", src)
        self.assertIn("/api/public/chat", src)
        self.assertIn("new URL(script.src).origin", src)

    def test_messages_do_not_guess_cause(self):
        src = WIDGET.read_text(encoding="utf-8")
        self.assertNotIn("Bạn gửi hơi nhanh", src)
        self.assertNotIn("Không kết nối được", src)


if __name__ == "__main__":
    unittest.main()
