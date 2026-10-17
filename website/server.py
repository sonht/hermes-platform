"""Local MVP server: static website and conservative NMPRP support endpoint.

No direct Hermes LLM connection yet; never expose an unauthenticated agent.
"""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
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
from support.code_aware import public_answer, retrieve
from support.public_inference import answer as public_ai_answer
from support.intelligence import record as record_feedback, summary as feedback_summary, recent as feedback_recent, set_status as feedback_set_status
from support.dashboard_auth import login as admin_login, valid as admin_valid, COOKIE as ADMIN_COOKIE

_public_lock = threading.Lock()
_public_requests = defaultdict(deque)
_public_slots = threading.BoundedSemaphore(2)

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path in ("/chat", "/chat/"):
            self.path = "/index.html"
        elif path in ("/dashboard", "/dashboard/"):
            self.path = "/dashboard.html"
        elif path in ("/web", "/web/"):
            self.path = "/web.html"
        elif path in ("/", ""):
            self.path = "/home.html"
        if path == "/api/admin/summary":
            if not admin_valid(self.headers.get("Cookie", "")):
                self.send_json(401, {"error": "Cần đăng nhập quản trị."})
                return
            db = os.environ.get("HERMES_FEEDBACK_DB", "")
            if not db:
                self.send_json(503, {"error": "Chưa cấu hình dữ liệu."})
                return
            try:
                self.send_json(200, {"rows": feedback_summary(db)})
            except OSError:
                self.send_json(503, {"error": "Không đọc được dữ liệu."})
            return
        if path == "/api/admin/reports":
            if not admin_valid(self.headers.get("Cookie", "")):
                self.send_json(401, {"error": "Cần đăng nhập quản trị."})
                return
            db = os.environ.get("HERMES_FEEDBACK_DB", "")
            if not db:
                self.send_json(503, {"error": "Chưa cấu hình dữ liệu."})
                return
            try:
                self.send_json(200, {"rows": feedback_recent(db)})
            except (OSError, ValueError):
                self.send_json(503, {"error": "Không đọc được dữ liệu."})
            return
        if path == "/api/admin/session":
            self.send_json(200, {"authenticated": admin_valid(self.headers.get("Cookie", ""))})
            return
        if self.path.startswith("/api/"):
            self.send_error(404)
            return
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/admin/report/status":
            return self.handle_report_status()
        if self.path == "/api/admin/login":
            return self.handle_admin_login()
        if self.path not in ("/api/chat", "/api/public/chat", "/api/public/feedback"):
            self.send_error(404)
            return
        public = self.path in ("/api/public/chat", "/api/public/feedback")
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
                return self.handle_feedback() if self.path == "/api/public/feedback" else self.handle_chat(public=True)
            finally:
                _public_slots.release()
        return self.handle_chat(public=False)

    def handle_report_status(self):
        if not admin_valid(self.headers.get("Cookie", "")):
            self.send_json(401, {"error": "Cần đăng nhập quản trị."})
            return
        # JSON + SameSite=Strict + exact same-origin browser check for mutation.
        origin = self.headers.get("Origin", "")
        host = self.headers.get("Host", "")
        if origin != "https://" + host:
            self.send_json(403, {"error": "Nguồn yêu cầu không hợp lệ."})
            return
        if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
            self.send_json(415, {"error": "Chỉ hỗ trợ JSON."})
            return
        db = os.environ.get("HERMES_FEEDBACK_DB", "")
        if not db:
            self.send_json(503, {"error": "Chưa cấu hình dữ liệu."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 1 <= length <= 256:
                raise ValueError("Invalid length")
            payload = json.loads(self.rfile.read(length))
            updated = feedback_set_status(db, payload["id"], payload["status"])
            self.send_json(200 if updated else 404, {"updated": updated})
        except (ValueError, TypeError, KeyError, json.JSONDecodeError):
            self.send_json(400, {"error": "Dữ liệu không hợp lệ."})
        except OSError:
            self.send_json(503, {"error": "Không cập nhật được dữ liệu."})

    def handle_admin_login(self):
        # Login rate limiting at origin is a temporary safety net; edge limits
        # and an identity provider are required before production rollout.
        peer = self.client_address[0]
        now = time.monotonic()
        with _public_lock:
            times = _public_requests["admin-login:" + peer]
            while times and now - times[0] > 300:
                times.popleft()
            if len(times) >= 5:
                self.send_json(429, {"error": "Thử lại sau."})
                return
            times.append(now)
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 1 <= length <= 512:
                raise ValueError("Invalid length")
            payload = json.loads(self.rfile.read(length))
            token = admin_login(payload.get("password"))
            if not token:
                self.send_json(401, {"error": "Thông tin đăng nhập không đúng."})
                return
            data = json.dumps({"authenticated": True}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Set-Cookie", f"{ADMIN_COOKIE}={token}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=3600")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(data)
        except (ValueError, TypeError, AttributeError, json.JSONDecodeError):
            self.send_json(400, {"error": "Yêu cầu không hợp lệ."})
        except RuntimeError:
            self.send_json(503, {"error": "Chưa cấu hình xác thực quản trị."})

    def handle_feedback(self):
        # Opt-in staging endpoint; public feedback is disabled until edge anti-abuse
        # and privacy controls are reviewed and enabled by the operator.
        if os.environ.get("HERMES_FEEDBACK_ENABLED") != "1":
            self.send_json(404, {"error": "Chức năng góp ý chưa được kích hoạt."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 1 <= length <= 2048:
                raise ValueError("Invalid length")
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict) or set(payload) != {"app", "kind", "summary"}:
                raise ValueError("Invalid payload")
            # An application allowlist is mandatory. Browser-supplied app ID
            # is a routing label, never an authorization credential.
            allowed = set(os.environ.get("HERMES_FEEDBACK_APPS", "").split(","))
            if payload["app"] not in allowed:
                raise ValueError("Unknown application")
            db = os.environ.get("HERMES_FEEDBACK_DB", "")
            if not db:
                raise RuntimeError("Feedback storage not configured")
            record_feedback(db, payload["app"], payload["kind"], payload["summary"])
            self.send_json(202, {"message": "Đã tiếp nhận góp ý để xem xét. Cảm ơn anh/chị."})
        except (ValueError, TypeError, KeyError, json.JSONDecodeError):
            self.send_json(400, {"error": "Nội dung góp ý không hợp lệ."})
        except (OSError, RuntimeError):
            self.send_json(503, {"error": "Chưa thể tiếp nhận góp ý. Vui lòng thử lại sau."})

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
                answer = (public_ai_answer(question, retrieve(repo, question)) if os.environ.get("HERMES_PUBLIC_AI_ENABLED") == "1" else public_answer(repo, question)) if repo else "Chưa cấu hình mã nguồn hỗ trợ."
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
