"""Local MVP server: static website and conservative NMPRP support endpoint.

No direct Hermes LLM connection yet; never expose an unauthenticated agent.
"""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from support.user_journey_builder import build_journey
from support.hermes_gateway import ask_hermes

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_POST(self):
        if self.path != "/api/chat":
            self.send_error(404)
            return
        if int(self.headers.get("Content-Length", "0") or "0") > 4096:
            self.send_error(413)
            return
        try:
            payload = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
            question = payload["message"]
            if not isinstance(question, str) or not 1 <= len(question.strip()) <= 2000:
                raise ValueError("invalid message")
            topic = "register" if any(word in question.lower() for word in ("đăng ký", "tạo tài khoản", "dang ky")) else "login" if any(word in question.lower() for word in ("đăng nhập", "login", "dang nhap")) else None
            repo = os.environ.get("NMPRP_SOURCE_PATH")
            if not topic or not repo:
                answer = "Hiện chỉ hỗ trợ hướng dẫn đăng nhập/đăng ký dm.kcb.vn; cần cấu hình NMPRP_SOURCE_PATH để đọc mã nguồn."
            else:
                result = build_journey(repo, topic)
                answer = (ask_hermes(question, result["evidence"]) if os.environ.get("HERMES_AGENT_ENABLED") == "1" else "\n".join(f"{i}. {step}" for i, step in enumerate(result["steps"], 1)) + "\n\nBản nháp cần xác minh với giao diện hiện hành.") if result["steps"] else "Chưa đủ bằng chứng mã nguồn để tạo hướng dẫn."
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
    ThreadingHTTPServer(("127.0.0.1", int(os.environ.get("HERMES_WEB_PORT", "8099"))), Handler).serve_forever()
