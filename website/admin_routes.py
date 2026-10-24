"""Admin dashboard, FAQ studio and opt-in feedback routes (mixed into the website Handler).

The public chat contract lives in server.py and is not touched here: these routes never
answer from source code and never call Hermes.
"""
import json
import os
from urllib.parse import parse_qs, urlsplit

from support.dashboard_auth import COOKIE as ADMIN_COOKIE, login as admin_login, valid as admin_valid
from support.faq_candidates import candidates as faq_candidates
from support.faq_studio import list_articles, save_draft, set_publication
from support.intelligence import record as record_feedback, recent as feedback_recent
from support.intelligence import set_status as feedback_set_status, summary as feedback_summary

ADMIN_POST = ("/api/admin/login", "/api/admin/faq/draft", "/api/admin/faq/publish", "/api/admin/report/status")


class AdminRoutes:
    """Needs the host class to provide send_json(), headers, rfile, wfile, client_address."""

    def _admin_db(self):
        """Admin session + configured DB, else answer 401/503 and return None."""
        if not admin_valid(self.headers.get("Cookie", "")):
            self.send_json(401, {"error": "Cần đăng nhập quản trị."})
            return None
        db = os.environ.get("HERMES_FEEDBACK_DB", "")
        if not db:
            self.send_json(503, {"error": "Chưa cấu hình dữ liệu."})
            return None
        return db

    def admin_get(self, path):
        """Handle an admin/FAQ GET. Returns True when the request was answered."""
        if path == "/api/admin/session":
            self.send_json(200, {"authenticated": admin_valid(self.headers.get("Cookie", ""))})
            return True
        if path == "/api/public/faq":
            # Only explicitly published, app-scoped content is visible publicly.
            app = parse_qs(urlsplit(self.path).query).get("app", [""])[0]
            if app not in set(os.environ.get("HERMES_FEEDBACK_APPS", "").split(",")):
                self.send_json(400, {"error": "Ứng dụng không hợp lệ."})
                return True
            db = os.environ.get("HERMES_FEEDBACK_DB", "")
            try:
                self.send_json(200, {"rows": list_articles(db, app=app, published_only=True) if db else []})
            except OSError:
                self.send_json(503, {"error": "Chưa đọc được FAQ."})
            return True
        readers = {
            "/api/admin/summary": feedback_summary,
            "/api/admin/faq/articles": list_articles,
            "/api/admin/faq/candidates": faq_candidates,
            "/api/admin/reports": feedback_recent,
        }
        if path not in readers:
            return False
        db = self._admin_db()
        if db:
            try:
                self.send_json(200, {"rows": readers[path](db)})
            except (OSError, ValueError):
                self.send_json(503, {"error": "Không đọc được dữ liệu."})
        return True

    def _admin_json_body(self, limit):
        """Same-origin + JSON + size-bounded body for admin mutations; None after answering an error."""
        if self.headers.get("Origin", "") != "https://" + self.headers.get("Host", ""):
            self.send_json(403, {"error": "Nguồn yêu cầu không hợp lệ."})
            return None
        if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
            self.send_json(415, {"error": "Chỉ hỗ trợ JSON."})
            return None
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 1 <= length <= limit:
                raise ValueError("length")
            return json.loads(self.rfile.read(length))
        except (ValueError, TypeError, json.JSONDecodeError):
            self.send_json(400, {"error": "Yêu cầu không hợp lệ."})
            return None

    def admin_post(self, path):
        if path == "/api/admin/login":
            return self._admin_login()
        db = self._admin_db()
        if not db:
            return
        payload = self._admin_json_body(4096 if "faq" in path else 256)
        if payload is None:
            return
        try:
            if path == "/api/admin/faq/draft":
                if payload["app"] not in set(os.environ.get("HERMES_FEEDBACK_APPS", "").split(",")):
                    raise ValueError("app")
                self.send_json(201, {"id": save_draft(db, payload["app"], payload["question"], payload["answer"])})
            elif path == "/api/admin/faq/publish":
                updated = set_publication(db, payload["id"], payload["publish"])
                self.send_json(200 if updated else 404, {"updated": updated})
            else:
                updated = feedback_set_status(db, payload["id"], payload["status"])
                self.send_json(200 if updated else 404, {"updated": updated})
        except (ValueError, TypeError, KeyError):
            self.send_json(400, {"error": "Dữ liệu không hợp lệ."})
        except OSError:
            self.send_json(503, {"error": "Không lưu được dữ liệu."})

    def _admin_login(self):
        # Origin-side safety net only; edge limits and an identity provider come before production.
        from website import server as host
        if not host.LOGIN_LIMITER.allow("admin-login", self.client_address[0]) is None:
            return self.send_json(429, {"error": "Thử lại sau."})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 1 <= length <= 512:
                raise ValueError("length")
            token = admin_login(json.loads(self.rfile.read(length)).get("password"))
        except (ValueError, TypeError, AttributeError, json.JSONDecodeError):
            return self.send_json(400, {"error": "Yêu cầu không hợp lệ."})
        except RuntimeError:
            return self.send_json(503, {"error": "Chưa cấu hình xác thực quản trị."})
        if not token:
            return self.send_json(401, {"error": "Thông tin đăng nhập không đúng."})
        self.send_json(200, {"authenticated": True}, headers={
            "Set-Cookie": f"{ADMIN_COOKIE}={token}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=3600"})

    def public_feedback(self, apps, limiter, slots):
        """Opt-in (HERMES_FEEDBACK_ENABLED=1). App must be registered, origin allowed, and rate-limited."""
        if os.environ.get("HERMES_FEEDBACK_ENABLED") != "1":
            return self.send_json(404, {"error": "Chức năng góp ý chưa được kích hoạt."})
        origin = self.headers.get("Origin")
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 1 <= length <= 2048:
                raise ValueError("length")
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict) or set(payload) != {"app", "kind", "summary"}:
                raise ValueError("shape")
            app_id = payload["app"]
            if apps.get(app_id) is None or app_id not in set(os.environ.get("HERMES_FEEDBACK_APPS", "").split(",")):
                raise ValueError("app")
        except (ValueError, TypeError, KeyError, json.JSONDecodeError):
            return self.send_json(400, {"error": "Nội dung góp ý không hợp lệ."})
        if not apps.origin_allowed(app_id, origin):
            return self.send_json(403, {"error": "Nguồn không được phép"})
        if limiter.allow(app_id, "feedback"):
            return self.send_json(429, {"error": "Quá nhiều yêu cầu. Vui lòng thử lại sau."}, origin=origin,
                                  headers={"Retry-After": "60"})
        if not slots.acquire(blocking=False):
            return self.send_json(503, {"error": "Hệ thống đang bận. Vui lòng thử lại."}, origin=origin)
        try:
            db = os.environ.get("HERMES_FEEDBACK_DB", "")
            if not db:
                raise RuntimeError("storage")
            record_feedback(db, app_id, payload["kind"], payload["summary"])
        except (ValueError, TypeError, KeyError):
            return self.send_json(400, {"error": "Nội dung góp ý không hợp lệ."}, origin=origin)
        except (OSError, RuntimeError):
            return self.send_json(503, {"error": "Chưa thể tiếp nhận góp ý. Vui lòng thử lại sau."}, origin=origin)
        finally:
            slots.release()
        self.send_json(202, {"message": "Đã tiếp nhận góp ý để xem xét. Cảm ơn anh/chị."}, origin=origin)
