"""Client for the NMPRP (dm.kcb.vn) API, for Hermes pilot jobs: reads (incl. reviewer feedback) plus narrow writes.

Design rules (see docs/NMPRP_HERMES_API_ACCESS.md):
- Only GET requests after login, plus POST to exactly /admin/hermes/goi-y and /admin/hermes/su-kien
  (unreviewed suggestions into NMPRP's own tables), the six queue endpoints of the run runner
  (/admin/hermes/may/chao, /may/nhan and /may/luot/<HL_id>/{tien-do,goi-y,ket-qua,ket-thuc}; see
  docs/NMPRP_HERMES_MAY_CHAY.md) and /admin/auth/login. Nothing else can be written.
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
    # run queue (runner only): NMPRP never calls out, the runner polls these. The run id is HL_ + 12 hex digits (as NMPRP issues them), nothing else.
    re.compile(r"^/admin/hermes/may/chao$"),
    re.compile(r"^/admin/hermes/may/nhan$"),
    re.compile(r"^/admin/hermes/may/luot/HL_[0-9a-f]{12}/(tien-do|goi-y|ket-qua|ket-thuc)$"),
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
    # Reviewer feedback on Hermes' own suggestions (read-only, no reviewer names). `/admin/hermes/goi-y` (GET), `/tom-tat`
    # and `/su-kien` (GET) are admin-only tab endpoints and deliberately NOT here.
    (re.compile(r"^/admin/hermes/phan-hoi$"), None),
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

    def ai_cong_tac_bat(self, chiu_loi_mang: bool = False) -> bool:
        """NMPRP's global AI switch. FAIL-CLOSED: any error, missing field or non-True value means OFF.

        The switch only stops model calls made INSIDE NMPRP; Hermes calls its model itself, so the pilot job
        MUST call this first and stop when it is False.

        `chiu_loi_mang=True` (the run runner): a transport/HTTP failure is RAISED instead of turned into OFF, so a brief
        outage is retried by the caller rather than read as "the switch is off". A missing field or a non-True value is
        still OFF."""
        try:
            return self.get("/admin/ai/status").get("cong_tac") is True
        except NmprpError:
            if chiu_loi_mang:
                raise
            return False

    def phan_hoi(self, sau="", limit=200):
        """One page of reviewer feedback, OLD -> NEW. `sau` is the `tiep` cursor of the previous page ("" = from the start)."""
        return self.get("/admin/hermes/phan-hoi", sau=sau, limit=limit)

    def phan_hoi_moi(self, sau="", limit=200, toi_da_trang=50):
        """Read ALL feedback after cursor `sau`. Returns (rows, new_cursor); the caller stores new_cursor for the next run.

        The server returns only STABLE feedback (a few seconds old), so new rows may arrive a few seconds late; that is intended. Rows are de-duplicated by goi_y_id. Stops when a page is empty, has no new row (a server that ignores the cursor would
        otherwise repeat the same page forever) or after `toi_da_trang` pages. Feedback is a PROPOSAL signal (EXPERT_FEEDBACK),
        never a gold label; do not turn it into memory or rules from a single row."""
        rows, thay = [], set()
        for _ in range(max(1, int(toi_da_trang))):
            d = self.phan_hoi(sau=sau, limit=limit)
            trang = d.get("phan_hoi") if isinstance(d, dict) else None
            if not trang:
                break
            moi = [r for r in trang if r.get("goi_y_id") not in thay]
            if not moi:
                break
            for r in moi:
                thay.add(r.get("goi_y_id"))
            rows.extend(moi)
            sau = d.get("tiep") or sau
        return rows, sau

    def post_goi_y(self, items):
        """Send a batch (<=200) of UNREVIEWED suggestions; the server forces source and status."""
        return self.post("/admin/hermes/goi-y", {"items": items})

    def post_su_kien(self, loai, chi_tiet=""):
        return self.post("/admin/hermes/su-kien", {"loai": loai, "chi_tiet": chi_tiet})

    # Run queue (used by support.nmprp_may_chay) ---------------------------------------------------
    def may_chao(self, phien_ban, mo_hinh, suy_luan):
        return self.post("/admin/hermes/may/chao", {"phien_ban": phien_ban, "mo_hinh": list(mo_hinh), "suy_luan": list(suy_luan)})

    def may_nhan(self):
        return self.post("/admin/hermes/may/nhan", {})

    def may_tien_do(self, luot_id, buoc=None, tien_do=None, thong_diep=None):
        body = {"buoc": buoc or {}, "tien_do": tien_do or {}}
        if thong_diep is not None:
            body["thong_diep"] = thong_diep
        return self.post("/admin/hermes/may/luot/%s/tien-do" % luot_id, body)

    def may_goi_y(self, luot_id, items):
        return self.post("/admin/hermes/may/luot/%s/goi-y" % luot_id, {"items": items})

    def may_ket_qua(self, luot_id, pl2):
        return self.post("/admin/hermes/may/luot/%s/ket-qua" % luot_id, {"pl2": pl2})

    def may_ket_thuc(self, luot_id, trang_thai, thong_diep=""):
        return self.post("/admin/hermes/may/luot/%s/ket-thuc" % luot_id, {"trang_thai": trang_thai, "thong_diep": thong_diep})
