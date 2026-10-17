"""Client for the NMPRP (dm.kcb.vn) API, for Hermes pilot jobs: reads plus TWO narrow writes.

Design rules (see docs/NMPRP_HERMES_API_ACCESS.md):
- Only GET requests after login, plus POST to exactly /admin/hermes/goi-y and /admin/hermes/su-kien
  (unreviewed suggestions into NMPRP's own tables) and /admin/auth/login. Nothing else can be written.
- Path allowlist; everything else is refused BEFORE any network call.
- CPT codes are AMA-copyrighted. By DEFAULT they must never reach a model, memory or log:
  /admin/cpt-tree/khung/ma-cpt and review kind=cpt are refused, and the keys listed in
  CPT_KEYS are removed from every response (defensive; NMPRP is the source of truth).
  The project owner may take responsibility for CPT licensing and enable CPT content with
  NMPRP_ALLOW_CPT=1 (or allow_cpt=True); the default stays strict.
- Credentials come from the environment; the session token lives in memory only.
- Errors name the path and HTTP status, never a body, token or password.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

LOGIN_PATH = "/admin/auth/login"

# (regex for the path, allowed values for the `kind` query parameter or None when unused)
_ALLOWED_POST = (
    re.compile(r"^/admin/hermes/goi-y$"),
    re.compile(r"^/admin/hermes/su-kien$"),
)
_CPT_GET = (
    (re.compile(r"^/admin/cpt-tree/khung/ma-cpt$"), None),
)
_ALLOWED_CPT_KINDS = {"cpt"}
_ALLOWED_GET = (
    (re.compile(r"^/admin/cpt-tree/khung$"), None),
    (re.compile(r"^/admin/ai/status$"), None),
    (re.compile(r"^/admin/cpn-ai/runs$"), None),
    (re.compile(r"^/admin/cpn-ai/runs/[A-Za-z0-9_\-]+/(tien-do|candidates|conflicts|families|qa)$"), None),
    (re.compile(r"^/review/search$"), {"pl1", "pl3"}),
    (re.compile(r"^/review/chapters$"), {"pl1", "pl3"}),
    (re.compile(r"^/review/map$"), {"pl1"}),
)
_BLOCKED_PATH_PARTS = ("/ma-cpt",)

# Keys that carry CPT codes or code ranges; removed from every response.
CPT_KEYS = frozenset({"dai_ma", "ma_cpt", "cpt_code", "cpt_codes", "cpt_range"})


class NmprpError(RuntimeError):
    """Raised for refused requests and HTTP/auth failures (never contains secrets)."""


def strip_cpt(obj):
    """Return a copy of a JSON-like value without CPT_KEYS at any depth."""
    if isinstance(obj, dict):
        return {k: strip_cpt(v) for k, v in obj.items() if k not in CPT_KEYS}
    if isinstance(obj, list):
        return [strip_cpt(v) for v in obj]
    return obj


def check_post_allowed(path: str) -> None:
    """Raise NmprpError unless `path` is one of the two narrow write endpoints."""
    if not isinstance(path, str) or not any(rx.match(path) for rx in _ALLOWED_POST):
        raise NmprpError(f"Refused: POST not allowed: {path}")


def check_allowed(path: str, query: dict | None = None, allow_cpt: bool = False) -> None:
    """Raise NmprpError unless (path, query) is an allowed read-only request."""
    if not isinstance(path, str) or not path.startswith("/") or ".." in path or "//" in path:
        raise NmprpError("Refused: malformed path")
    if not allow_cpt and any(part in path for part in _BLOCKED_PATH_PARTS):
        raise NmprpError(f"Refused: path is blocked (CPT content): {path}")
    for rx, kinds in _ALLOWED_GET + (_CPT_GET if allow_cpt else ()):
        if rx.match(path):
            if kinds is not None:
                kind = str((query or {}).get("kind", "")).lower()
                if kind not in (kinds | (_ALLOWED_CPT_KINDS if allow_cpt else set())):
                    raise NmprpError(f"Refused: kind={kind!r} not allowed for {path}")
            return
    raise NmprpError(f"Refused: path not on the allowlist: {path}")


class NmprpClient:
    def __init__(self, base_url=None, username=None, password=None, timeout=30, opener=None,
                 allow_cpt=None):
        self.base_url = (base_url or os.environ.get("NMPRP_BASE_URL", "")).rstrip("/")
        self._username = username or os.environ.get("NMPRP_SERVICE_USER", "")
        self._password = password or os.environ.get("NMPRP_SERVICE_PASSWORD", "")
        self.timeout = timeout
        self._opener = opener or urllib.request.build_opener()
        self._token = None
        if allow_cpt is None:
            allow_cpt = os.environ.get("NMPRP_ALLOW_CPT", "") == "1"
        self.allow_cpt = bool(allow_cpt)
        if not (self.base_url and self._username and self._password):
            raise NmprpError("Missing NMPRP_BASE_URL / NMPRP_SERVICE_USER / NMPRP_SERVICE_PASSWORD")

    def __repr__(self):  # never print credentials
        return f"NmprpClient(base_url={self.base_url!r}, allow_cpt={self.allow_cpt})"

    def _open(self, req, label):
        try:
            with self._opener.open(req, timeout=self.timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise NmprpError(f"{label}: HTTP {e.code}") from None
        except (urllib.error.URLError, TimeoutError, ValueError) as e:
            raise NmprpError(f"{label}: {type(e).__name__}") from None

    def _login(self):
        body = json.dumps({"username": self._username, "password": self._password}).encode()
        req = urllib.request.Request(self.base_url + LOGIN_PATH, data=body, method="POST",
                                     headers={"Content-Type": "application/json"})
        data = self._open(req, "login")
        token = data.get("token") if isinstance(data, dict) else None
        if not token:
            raise NmprpError("login: no token in response")
        self._token = token

    def get(self, path: str, **query):
        """GET an allowlisted path; returns the parsed JSON with CPT keys stripped."""
        check_allowed(path, query, self.allow_cpt)
        qs = urllib.parse.urlencode({k: v for k, v in query.items() if v not in (None, "")})
        url = self.base_url + path + (("?" + qs) if qs else "")
        for attempt in (1, 2):
            if not self._token:
                self._login()
            req = urllib.request.Request(url, method="GET",
                                         headers={"Authorization": "Bearer " + self._token})
            try:
                data = self._open(req, f"GET {path}")
                return data if self.allow_cpt else strip_cpt(data)
            except NmprpError as e:
                if "HTTP 401" in str(e) and attempt == 1:
                    self._token = None   # session expired: log in once more
                    continue
                raise
        raise NmprpError(f"GET {path}: unauthorized")

    def post(self, path: str, body: dict):
        """POST JSON to one of the two allowlisted write paths; returns the parsed response."""
        check_post_allowed(path)
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        for attempt in (1, 2):
            if not self._token:
                self._login()
            req = urllib.request.Request(self.base_url + path, data=data, method="POST",
                                         headers={"Authorization": "Bearer " + self._token,
                                                  "Content-Type": "application/json"})
            try:
                return self._open(req, f"POST {path}")
            except NmprpError as e:
                if "HTTP 401" in str(e) and attempt == 1:
                    self._token = None
                    continue
                raise
        raise NmprpError(f"POST {path}: unauthorized")

    # Convenience readers/writers used by the pilot job -------------------------------------------
    def khung(self):
        return self.get("/admin/cpt-tree/khung")

    def candidates(self, run_id, pl2_code="", **kw):
        return self.get(f"/admin/cpn-ai/runs/{run_id}/candidates", pl2_code=pl2_code,
                        kem_ten=1, tat_ca=1, **kw)

    def search_pl2(self, q, limit=40):
        return self.get("/review/search", kind="pl3", q=q, limit=limit)   # API still names PL2 "pl3"

    def pl2_pl1_map(self, code):
        return self.get("/review/map", kind="pl1", code=code)

    def ai_cong_tac_bat(self) -> bool:
        """NMPRP's global AI switch. FAIL-CLOSED: any error, missing field or non-True value means OFF.

        The switch only stops model calls made INSIDE NMPRP; Hermes calls its model itself, so the pilot job
        MUST call this first and stop when it is False."""
        try:
            return self.get("/admin/ai/status").get("cong_tac") is True
        except NmprpError:
            return False

    def post_goi_y(self, items):
        """Send a batch (<=200) of UNREVIEWED suggestions; the server forces source and status."""
        return self.post("/admin/hermes/goi-y", {"items": items})

    def post_su_kien(self, loai, chi_tiet=""):
        return self.post("/admin/hermes/su-kien", {"loai": loai, "chi_tiet": chi_tiet})
