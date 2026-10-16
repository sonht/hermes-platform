"""Local MVP server: static website and conservative NMPRP support endpoint.

No direct Hermes LLM connection yet; never expose an unauthenticated agent.
"""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import hmac
import os
import sys
import time
import threading
from collections import defaultdict, deque

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from support.user_journey_builder import build_journey
from support.hermes_gateway import ask_hermes
from support.code_aware import public_answer

_public_lock = threading.Lock()
_public_requests = defaultdict(deque)
_public_slots = threading.BoundedSemaphore(2)

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/"):
            self.send_error(404)
            return
        return super().do_GET()

    def do_POST(self):
        if self.path not in ("/api/chat", "/api/public/chat"):
            self.send_error(404)
            return
        public = self.path == "/api/public/chat"
        if public:
            # The website is proxied only by local Caddy. Ignore untrusted X-Forwarded-For.
            peer = self.client_address[0]
            now = time.monotonic()
            with _public_lock:
                times = _public_requests[peer]
                while times and now - times[0] > 60:
                    times.popleft()
                if len(times) >= 5:
                    self.send_json(429, {"error": "Quá nhiều yêu cầu. Vui lòng thử lại sau."})
                    return
                times.append(now)
            if not _public_slots.acquire(blocking=False):
                self.send_json(503, {"error": "Hệ thống đang bận. Vui lòng thử lại."})
                return
            try:
                return self.handle_chat(public=True)
            finally:
                _public_slots.release()
        return self.handle_chat(public=False)

    def send_json(self, status, obj):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def handle_chat(self, public=False):
        configured = os.environ.get("HERMES_WEB_TOKEN", "")
        provided = self.headers.get("Authorization", "")
        if not public and (not configured or not hmac.compare_digest(provided, "Bearer " + configured)):
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(b'{"error":"Unauthorized"}')
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(400)
            return
        if length < 1 or length > 4096:
            self.send_error(413)
            return
        try:
            payload = json.loads(self.rfile.read(length))
            question = payload["message"]
            if not isinstance(question, str) or not 1 <= len(question.strip()) <= 2000:
                raise ValueError("invalid message")
            topic = "register" if any(word in question.lower() for word in ("đăng ký", "tạo tài khoản", "dang ky")) else "login" if any(word in question.lower() for word in ("đăng nhập", "login", "dang nhap")) else None
            repo = os.environ.get("NMPRP_SOURCE_PATH")
            if public and not topic:
                answer = public_answer(repo, question) if repo else "Chưa cấu hình mã nguồn hỗ trợ."
            elif not topic or not repo:
                answer = "Hiện chỉ hỗ trợ hướng dẫn đăng nhập/đăng ký dm.kcb.vn; cần cấu hình NMPRP_SOURCE_PATH để đọc mã nguồn."
            else:
                result = build_journey(repo, topic)
                answer = (ask_hermes(question, result["evidence"]) if not public and os.environ.get("HERMES_AGENT_ENABLED") == "1" else "\n".join(f"{i}. {step}" for i, step in enumerate(result["steps"], 1)) + "\n\nBản nháp cần xác minh với giao diện hiện hành.") if result["steps"] else "Chưa đủ bằng chứng mã nguồn để tạo hướng dẫn."
            data = json.dumps({"answer": answer}, ensure_ascii=False).encode()
            self.send_response(200)
        except RuntimeError:
            data = json.dumps({"error": "Hermes chưa sẵn sàng; vui lòng thử lại sau."}, ensure_ascii=False).encode()
            self.send_response(503)
        except (ValueError, KeyError, json.JSONDecodeError):
            data = json.dumps({"error": "Yêu cầu không hợp lệ"}).encode()
            self.send_response(400)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

if __name__ == "__main__":
    if not os.environ.get("HERMES_WEB_TOKEN"):
        raise SystemExit("Set HERMES_WEB_TOKEN before starting website")
    ThreadingHTTPServer(("127.0.0.1", int(os.environ.get("HERMES_WEB_PORT", "8099"))), Handler).serve_forever()
