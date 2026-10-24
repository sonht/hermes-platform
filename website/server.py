"""Local MVP server: static website and conservative NMPRP support endpoint.

No direct Hermes LLM connection yet; never expose an unauthenticated agent.
"""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
import json
import hmac
import os
import re
import sys
import threading

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from support.user_journey_builder import build_journey
from support.hermes_gateway import ask_hermes
from support.knowledge import NO_ANSWER, find_entry, load_entries, render_answer
from website.registry import AppRegistry
from website.ratelimit import RateLimiter
from website.admin_routes import ADMIN_POST, AdminRoutes

APPS = AppRegistry.load(os.environ.get("HERMES_APPS_FILE", ROOT / "apps.json"))
LIMITER = RateLimiter()
LOGIN_LIMITER = RateLimiter(per_session=5, per_app=5, daily_per_app=200)
_public_slots = threading.BoundedSemaphore(2)
_SESSION_OK = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
_PUBLIC_MAX_BYTES = 8192

class Handler(AdminRoutes, SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path in ("/dashboard", "/dashboard/"):
            self.path = "/dashboard.html"
        if self.admin_get(path):
            return
        if self.path.startswith("/api/"):
            self.send_error(404)
            return
        return super().do_GET()

    def _cors_origin(self):
        """Origin header if it belongs to at least one registered app, else None."""
        origin = self.headers.get("Origin")
        # Preflight has no body, so the app is unknown: accept any registered origin.
        if origin is not None and any(APPS.origin_allowed(key, origin) for key in APPS._apps):
            return origin
        return None

    def do_OPTIONS(self):
        if self.path != "/api/public/chat":
            self.send_error(404)
            return
        origin = self.headers.get("Origin")
        allowed = origin is not None and self._cors_origin() == origin
        self.send_response(204 if allowed else 403)
        if allowed:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Methods", "POST")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Max-Age", "600")
            self.send_header("Vary", "Origin")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/public/chat":
            return self.handle_public_chat()
        if self.path in ADMIN_POST:
            return self.admin_post(self.path)
        if self.path == "/api/public/feedback":
            return self.public_feedback(APPS, LIMITER, _public_slots)
        if self.path != "/api/chat":
            self.send_error(404)
            return
        return self.handle_chat(public=False)

    def send_json(self, status, obj, origin=None, headers=None):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def handle_public_chat(self):
        cors = self._cors_origin()
        origin = self.headers.get("Origin")
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return self.send_json(400, {"error": "Yêu cầu không hợp lệ"}, origin=cors)
        if length < 1:
            return self.send_json(400, {"error": "Yêu cầu không hợp lệ"}, origin=cors)
        if length > _PUBLIC_MAX_BYTES:
            return self.send_json(413, {"error": "Yêu cầu quá lớn"}, origin=cors)
        try:
            payload = json.loads(self.rfile.read(length))
            question = payload["message"]
            if not isinstance(question, str) or not 1 <= len(question.strip()) <= 2000:
                raise ValueError("invalid message")
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            return self.send_json(400, {"error": "Yêu cầu không hợp lệ"}, origin=cors)
        # `app` is only a lookup key into apps.json; it is never joined into a path.
        app_id = payload.get("app", "dm")
        app = APPS.get(app_id)
        if app is None:
            return self.send_json(400, {"error": "Ứng dụng không hợp lệ"}, origin=cors)
        if not APPS.origin_allowed(app_id, origin):
            return self.send_json(403, {"error": "Nguồn không được phép"})
        session = payload.get("session", "")
        session = session if isinstance(session, str) and _SESSION_OK.match(session) else "anon"
        reason = LIMITER.allow(app_id, session)
        if reason:
            headers = {"Retry-After": "60"} if reason in ("session", "app") else None
            return self.send_json(429, {"error": "Quá nhiều yêu cầu. Vui lòng thử lại sau."},
                                  origin=cors, headers=headers)
        if not _public_slots.acquire(blocking=False):
            return self.send_json(503, {"error": "Hệ thống đang bận. Vui lòng thử lại."}, origin=cors)
        try:
            entries = load_entries(ROOT.parent / app["knowledge"])
            entry = find_entry(entries, question)
            answer = render_answer(entry) if entry else NO_ANSWER
        except (OSError, ValueError) as exc:
            self.log_error("knowledge load failed: %s", type(exc).__name__)
            return self.send_json(503, {"error": "Kho hướng dẫn chưa sẵn sàng."}, origin=cors)
        finally:
            _public_slots.release()
        return self.send_json(200, {"answer": answer}, origin=cors)

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
                answer = "Hiện chatbot công khai chỉ hướng dẫn đăng nhập hoặc đăng ký tài khoản dm.kcb.vn. Anh/chị vui lòng hỏi về một trong hai nội dung này."
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
