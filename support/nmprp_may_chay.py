"""Run runner ("may chay") of the NMPRP mapping profile — the other half of the «Hermes Agent» tab in NMPRP.

NMPRP never calls out to Hermes. The admin creates a RUN in the NMPRP tab (chapter, number of PL2, model, token ceiling,
number of model calls per round); this runner, on the HOST (Rocky), polls NMPRP: it says it is alive (`chao`), asks for work
(`nhan`), reports each step (`tien-do`), sends the suggestions and per-PL2 results, and closes the round (`ket-thuc`).
Contract: docs/NMPRP_HERMES_MAY_CHAY.md (mirror of NMPRP docs/hermes-agent/DIEU_PHOI_LUOT.md).

Why on the host, like `nmprp_shadow`: the NMPRP service password must never enter the Hermes container (its volume is backed up).

What it reuses from `nmprp_shadow`, unchanged: prompt building, the validation of every answer (node must exist in the frame,
verbatim quotes, no CPT-like strings, max 3 per PL2) and the `docker exec ... hermes -z` call. It adds only the queue protocol.

Safety rules:
- Every suggestion it sends is UNREVIEWED; nothing here can write a mapping (the client allowlist has no such path).
- Model and reasoning level of a run are checked against lists THIS runner declares (env), not against what NMPRP says.
- Budgets are checked BEFORE each model call: a call that would cross the ceiling is not made, the run pauses.
- A network error never kills a run: the run stays DANG_CHAY and the restarted runner resumes it (NMPRP returns the run of
  the same runner). An unexpected error closes the run as LOI with the error class only.
- `bang_chung` (quotes) goes to NMPRP inside the suggestions only; it is never printed.
- A stop file (env HERMES_RUNNER_DUNG, default /home/rocky/hermes-shadow-out/DUNG) makes the runner stop taking work and stop
  saying hello. `hermes pause` stays the emergency stop for everything else.
- Exactly ONE runner at a time: `main` takes an exclusive, non-blocking `flock(2)` on a lock file (env HERMES_RUNNER_LOCK,
  default /home/rocky/hermes-shadow-out/may-chay.lock) held on an fd kept open for the life of the process — no stale PID
  file to clean up, the OS releases the lock the instant the process dies for any reason. A second runner sees the lock
  taken, prints a message naming the PID of the holder (best effort) and exits with MA_THOAT_DA_CO_MAY_CHAY WITHOUT polling
  NMPRP even once (this is what the 19/10/2026 incident needed: two runners of the same name both resumed the same
  DANG_CHAY run and paid for the model twice).

Python 3.9 compatible on purpose (Rocky host).

Run (see the doc):  set -a; . deploy/rocky/nmprp-service.env; set +a; python3 -m support.nmprp_may_chay
"""
from __future__ import annotations

import argparse
import fcntl
import os
import re
import sys
import threading
import time
from datetime import datetime, timezone

from support import nmprp_shadow as sh
from support.nmprp_client import NmprpClient, NmprpError

PHIEN_BAN = "nmprp-may-chay@0.1"
PHIEN_BAN_GOI_Y = "nmprp-retrieval-assist@may-0.1"          # <= 40 characters (NMPRP limit)
MO_HINH_AN_TOAN = re.compile(r"^[A-Za-z0-9._:/@-]{1,100}$")
SUY_LUAN_MAC_DINH = ("low", "medium", "high")
MUC_SUY_LUAN_MAC_DINH = "low"                                # what `goi_hermes` uses when a run chose no level
SUY_LUAN_HERMES = ("none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra")
NHIP_CHAO_GIAY = 60                                          # NMPRP treats a runner as "on duty" for 180 s after its last hello
NHIP_HOI_VIEC_GIAY = 30
DUNG_MAC_DINH = "/home/rocky/hermes-shadow-out/DUNG"
KHOA_MAC_DINH = "/home/rocky/hermes-shadow-out/may-chay.lock"       # canh tep dung mem, env HERMES_RUNNER_LOCK doi duoc
MA_THOAT_DA_CO_MAY_CHAY = 3                                          # rieng cho systemd RestartPreventExitStatus=
MA_THOAT_LOI_KHOA = 4                                                 # khong tao/mo duoc tep khoa (vd duong hong, quyen)
BUOC_DAU_VAO = ("DOC", "CHUAN_BI", "SUY_LUAN", "KIEM_DINH", "GUI")


def ghi_nhat_ky(msg: str) -> None:
    print("%s %s" % (datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), msg), flush=True)


class CauHinh:
    """What THIS runner allows. Models are never hard-coded: the operator lists them (empty = the profile's default only)."""

    def __init__(self, mo_hinh=(), suy_luan=SUY_LUAN_MAC_DINH, tep_dung=DUNG_MAC_DINH, tep_khoa=KHOA_MAC_DINH,
                 container=sh.CONTAINER, profile=sh.PROFILE, ky_nang=sh.SKILL):
        self.mo_hinh = tuple(m for m in mo_hinh if MO_HINH_AN_TOAN.match(m))
        self.suy_luan = tuple(x for x in suy_luan if x in SUY_LUAN_HERMES)
        self.tep_dung = tep_dung
        self.tep_khoa = tep_khoa
        self.container, self.profile, self.ky_nang = container, profile, ky_nang

    @classmethod
    def tu_moi_truong(cls, env=None):
        e = os.environ if env is None else env
        ds = lambda k, mac: tuple(x.strip() for x in e.get(k, mac).split(",") if x.strip())      # noqa: E731
        return cls(ds("HERMES_RUNNER_MODELS", ""), ds("HERMES_RUNNER_REASONING", ",".join(SUY_LUAN_MAC_DINH)),
                   e.get("HERMES_RUNNER_DUNG", DUNG_MAC_DINH), e.get("HERMES_RUNNER_LOCK", KHOA_MAC_DINH))


# --- single-instance lock ---------------------------------------------------------------------------------------

def khoa_mot_lan(duong: str):
    """Try an exclusive, non-blocking `flock(2)` on `duong`. The lock lives on the returned open file's fd for as long
    as the caller keeps it referenced (and open) — the OS drops it the instant the fd closes, including on process
    death of any kind (crash, kill -9, power loss), so there is never a stale PID file to clean up by hand. Returns the
    open file object on success, or None when some OTHER open file description already holds the lock (two separate
    `open()` calls on the same path get separate file descriptions even inside the very same process, which is what
    lets the test suite prove rejection with two real fds without needing a subprocess)."""
    thu_muc = os.path.dirname(duong)
    if thu_muc:
        os.makedirs(thu_muc, exist_ok=True)
    f = open(duong, "a+")
    try:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        f.close()
        return None
    try:
        f.seek(0)
        f.truncate()
        f.write(str(os.getpid()))
        f.flush()
    except OSError:                                               # noqa: BLE001 — holding the lock matters, not this hint
        pass
    return f


def doc_pid_khoa(duong: str) -> str:
    """Best-effort read of the PID the current holder wrote, for the message printed when the lock is already taken."""
    try:
        with open(duong) as f:
            return f.read().strip()
    except OSError:
        return ""


class DungLuot(Exception):
    """Internal: stop the current run with a given final state."""

    def __init__(self, trang_thai, thong_diep):
        Exception.__init__(self, thong_diep)
        self.trang_thai, self.thong_diep = trang_thai, thong_diep


# --- one run ---------------------------------------------------------------------------------------------------

def _chia_lo(pl2: list, me: int) -> list:
    return [pl2[i:i + me] for i in range(0, len(pl2), me)]


def _bo_hop_dong(bo: list) -> list:
    """Server accepts rejected-item entries only as strings or objects holding just branch_key / ly_do (strings)."""
    ra = []
    for b in bo[:20]:
        if isinstance(b, dict):
            ra.append({"branch_key": str(b.get("branch_key", ""))[:500], "ly_do": str(b.get("ly_do_bo", ""))[:200]})
    return ra


def xu_ly_luot(client, luot: dict, cau_hinh: CauHinh, runner=None) -> str:
    """Process one run until it ends or must pause. Returns the final state sent to NMPRP. Network errors propagate."""
    luot_id = luot["luot_id"]
    try:
        return _chay_luot(client, luot, cau_hinh, runner)
    except DungLuot as d:
        client.may_ket_thuc(luot_id, d.trang_thai, d.thong_diep)
        ghi_nhat_ky("luot %s -> %s: %s" % (luot_id, d.trang_thai, d.thong_diep))
        return d.trang_thai
    except NmprpError:
        raise                                                    # transient: the run stays DANG_CHAY, resumed later
    except sh.ShadowStop as e:
        client.may_ket_thuc(luot_id, "LOI", "Hermes: %s" % str(e)[:300])
        return "LOI"
    except Exception as e:                                       # noqa: BLE001 — class only, never a message that may carry text
        client.may_ket_thuc(luot_id, "LOI", "Loi may chay: %s" % type(e).__name__)
        ghi_nhat_ky("luot %s LOI %s" % (luot_id, type(e).__name__))
        return "LOI"


def _kiem_cho_phep(luot: dict, cfg: CauHinh):
    mh, sl = luot.get("mo_hinh") or "", luot.get("suy_luan") or MUC_SUY_LUAN_MAC_DINH
    if mh and (mh not in cfg.mo_hinh or not MO_HINH_AN_TOAN.match(mh)):
        raise DungLuot("LOI", "Mo hinh khong nam trong danh sach may chay cho phep")
    if sl not in cfg.suy_luan:                       # the EFFECTIVE level: an empty choice runs as MUC_SUY_LUAN_MAC_DINH
        raise DungLuot("LOI", "Muc suy luan %s khong nam trong danh sach may chay cho phep" % sl)


def _theo_phan_hoi(rep: dict, con_lo: bool):
    """Honour the server's stop order, but never pause when nothing is left to do (the run then simply finishes)."""
    if not isinstance(rep, dict) or not rep.get("dung"):
        return
    ly = rep.get("ly_do_dung") or ""
    if ly == "HUY":
        raise DungLuot("DA_HUY", "Admin huy luot")
    if con_lo:
        raise DungLuot("TAM_DUNG", {"HET_GOI": "Het so loi goi cua dot", "HET_TOKEN": "Cham tran token"}.get(ly, "May chu yeu cau dung"))


def _ghi_ly_do_khong_json(kq: dict, out: str) -> None:
    """The model answered in prose (no JSON object at all). `kiem_ket_qua` marks every PL2 of the batch KHONG_DAP_UNG with a
    generic reason; say what the model actually did, so a reviewer can tell «refused / asked for a tool» from «omitted this PL2».
    Only a short single-line snippet, and nothing that looks like a CPT code (the server rule is the same)."""
    mau = " ".join((out or "").split())[:300]
    if sh.CPT_LIKE.search(mau):
        mau = ""
    ly_do = "mo hinh khong tra JSON (tra loi bang van xuoi)" + (": " + mau if mau else "")
    for r in kq.values():
        if r["muc"] == "KHONG_DAP_UNG":
            r["ly_do"] = ly_do


def _chay_luot(client, luot: dict, cfg: CauHinh, runner):
    luot_id = luot["luot_id"]
    _kiem_cho_phep(luot, cfg)
    if not client.ai_cong_tac_bat(chiu_loi_mang=True):          # an outage raises (retried), only an explicit OFF pauses
        raise DungLuot("TAM_DUNG", "Cong tac AI cua NMPRP dang TAT: bat lai roi bam Chay tiep")
    base = luot.get("tien_do") or {}
    lan_goi = int(base.get("lan_goi") or 0)
    token = int(base.get("token_da_dung") or 0)
    pl2_xong = int(base.get("pl2_xong") or 0)
    so_goi_y, so_nhan, so_bo = (int(base.get(k) or 0) for k in ("so_goi_y", "so_nhan", "so_bo"))
    lo_xong = int(base.get("lo_xong") or 0)
    han_goi, tran = int(luot.get("han_goi") or 0), int(luot.get("tran_token") or 0)
    me = max(1, int(luot.get("me") or 5))

    rep = client.may_tien_do(luot_id, {"DOC": {"tt": "DANG", "ghi_chu": "khung cay + danh sach PL2"}})
    nut = sh.thu_nut_tan(client.khung())
    if not nut:
        raise DungLuot("LOI", "Khong doc duoc nut tan nao tu khung cay CPT")
    da_xong = set(luot.get("pl2_da_xong") or [])
    cho = [{"code": p["code"], "name": p["name"]} for p in (luot.get("ds_pl2") or []) if p["code"] not in da_xong]
    rep = client.may_tien_do(luot_id, {"DOC": {"tt": "XONG", "ghi_chu": "%d nut tan, %d PL2 con lai" % (len(nut), len(cho))}},
                             {"so_pl2": len(luot.get("ds_pl2") or [])})
    hang = _chia_lo(cho, me)
    _theo_phan_hoi(rep, bool(hang))

    while hang:
        lo = hang.pop(0)
        prompt = sh.dung_prompt(lo, nut)
        if len(prompt.encode("utf-8")) > sh.MAX_PROMPT_BYTES:
            if len(lo) == 1:
                raise DungLuot("LOI", "Mot PL2 van lam cau hoi vuot %d byte" % sh.MAX_PROMPT_BYTES)
            giua = len(lo) // 2
            hang[:0] = [lo[:giua], lo[giua:]]                    # split the batch, retry before any call is made
            continue
        if han_goi and lan_goi >= han_goi:
            raise DungLuot("TAM_DUNG", "Het so loi goi cua dot")
        if tran and token + sh.uoc_token(prompt) > tran:
            raise DungLuot("TAM_DUNG", "Uoc tinh vuot tran token: nang tran roi bam Chay tiep")
        # Reserve the call BEFORE it is made: if the runner dies after Hermes answered, the restarted runner sees this call
        # already counted and cannot make more paid calls than `han_goi` allows (tokens are reported after the call).
        lan_goi += 1
        rep = client.may_tien_do(luot_id, {"CHUAN_BI": {"tt": "XONG", "ghi_chu": "~%d token" % sh.uoc_token(prompt)},
                                           "SUY_LUAN": {"tt": "DANG", "ghi_chu": "PL2 %s..%s" % (lo[0]["code"], lo[-1]["code"])}},
                                 {"token_uoc_lo": sh.uoc_token(prompt), "lan_goi": lan_goi})
        # Only a cancel may stop us HERE. The server answers HET_GOI as soon as the reported count reaches `han_goi`, which is
        # exactly what reserving the LAST allowed call does: pausing on it would leave that call unmade (a run with han_goi=1
        # never called Hermes). The budget was already checked locally BEFORE the reservation.
        if isinstance(rep, dict) and rep.get("dung") and rep.get("ly_do_dung") == "HUY":
            raise DungLuot("DA_HUY", "Admin huy luot")
        out, usage = sh.goi_hermes(prompt, "may-%s-%d.json" % (luot_id, lan_goi), cfg.container, cfg.profile, cfg.ky_nang,
                                   runner, luot.get("mo_hinh") or "", luot.get("suy_luan") or MUC_SUY_LUAN_MAC_DINH)
        token += int(usage.get("total_tokens") or sh.uoc_token(prompt))
        du_lieu = sh.tach_json(out)
        kq = sh.kiem_ket_qua(du_lieu, lo, nut, PHIEN_BAN_GOI_Y)
        if du_lieu is None:
            _ghi_ly_do_khong_json(kq, out)
        rep = client.may_tien_do(luot_id, {"SUY_LUAN": {"tt": "XONG", "ghi_chu": ""}, "KIEM_DINH": {"tt": "XONG", "ghi_chu": ""},
                                           "GUI": {"tt": "DANG", "ghi_chu": ""}}, {"lan_goi": lan_goi, "token_da_dung": token})
        # An admin cancel that arrived DURING the model call is first seen here: stop before publishing anything. Only HUY stops
        # here: HET_GOI / HET_TOKEN are reached BECAUSE of the call just paid for, whose results must still be published.
        if isinstance(rep, dict) and rep.get("dung") and rep.get("ly_do_dung") == "HUY":
            raise DungLuot("DA_HUY", "Admin huy luot")
        items = [g for p in lo for g in kq[p["code"]]["chap_nhan"]]
        if items:
            client.may_goi_y(luot_id, items)
        client.may_ket_qua(luot_id, [{
            "pl2_code": p["code"], "muc": kq[p["code"]]["muc"], "ly_do": kq[p["code"]]["ly_do"],
            "so_nhan": len(kq[p["code"]]["chap_nhan"]), "so_bo": len(kq[p["code"]]["bo"]),
            "bo": _bo_hop_dong(kq[p["code"]]["bo"]), "lo": lo_xong} for p in lo])
        lo_xong += 1
        pl2_xong += len(lo)
        so_goi_y += len(items)
        so_nhan += sum(len(kq[p["code"]]["chap_nhan"]) for p in lo)
        so_bo += sum(len(kq[p["code"]]["bo"]) for p in lo)
        rep = client.may_tien_do(luot_id, {"GUI": {"tt": "XONG", "ghi_chu": "%d goi y" % len(items)}},
                                 {"lo_xong": lo_xong, "pl2_xong": pl2_xong, "so_goi_y": so_goi_y, "so_nhan": so_nhan,
                                  "so_bo": so_bo, "lan_goi": lan_goi, "token_da_dung": token})
        _theo_phan_hoi(rep, bool(hang))
    client.may_ket_thuc(luot_id, "XONG", "%d PL2, %d lan goi, %d token" % (pl2_xong, lan_goi, token))
    ghi_nhat_ky("luot %s XONG" % luot_id)
    return "XONG"


# --- main loop -------------------------------------------------------------------------------------------------

class NhipTim(threading.Thread):
    """Says hello every NHIP_CHAO_GIAY seconds with its OWN client, so a long model call does not make the runner look off duty."""

    def __init__(self, tao_client, cau_hinh, giay=NHIP_CHAO_GIAY):
        threading.Thread.__init__(self, daemon=True)
        self._tao, self._cfg, self._giay, self._dung = tao_client, cau_hinh, giay, threading.Event()

    def run(self):
        client = None
        while not self._dung.wait(self._giay):
            if os.path.exists(self._cfg.tep_dung):
                continue
            try:
                client = client or self._tao()
                client.may_chao(PHIEN_BAN, self._cfg.mo_hinh, self._cfg.suy_luan)
            except Exception:                                    # noqa: BLE001 — a missed hello is harmless, the main loop retries
                client = None

    def dung(self):
        self._dung.set()


def mot_vong(client, cfg: CauHinh, runner=None) -> str:
    """One poll. Returns "DUNG" (stop file), "KHONG_VIEC", or the final state of the run it processed."""
    if os.path.exists(cfg.tep_dung):
        return "DUNG"
    client.may_chao(PHIEN_BAN, cfg.mo_hinh, cfg.suy_luan)
    r = client.may_nhan()
    luot = (r or {}).get("luot")
    if not luot:
        return "KHONG_VIEC"
    ghi_nhat_ky("nhan luot %s (chuong %s)" % (luot.get("luot_id"), luot.get("chuong")))
    return xu_ly_luot(client, luot, cfg, runner)


def chay_mai(tao_client, cfg: CauHinh, nhip=NHIP_HOI_VIEC_GIAY, ngu=time.sleep, nhip_tim=True, so_vong=None, mot_lan=False):
    client = tao_client()
    tim = NhipTim(tao_client, cfg) if nhip_tim else None
    if tim:
        tim.start()
    vong = 0
    try:
        while so_vong is None or vong < so_vong:
            vong += 1
            try:
                kq = mot_vong(client, cfg)
            except NmprpError as e:
                if mot_lan:
                    raise                                        # one-shot smoke test: a network failure must FAIL, not exit 0
                ghi_nhat_ky("loi mang/NMPRP: %s" % e)            # message names path + status only
                ngu(nhip * 2)
                continue
            if kq in ("DUNG", "KHONG_VIEC"):
                ngu(nhip)
    finally:
        if tim:
            tim.dung()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Run runner of the NMPRP mapping profile (polls NMPRP; never listens).")
    ap.add_argument("--mot-lan", action="store_true", help="poll once and exit (for a first manual test)")
    ap.add_argument("--nhip", type=int, default=NHIP_HOI_VIEC_GIAY, help="seconds between polls when idle")
    a = ap.parse_args(argv)
    cfg = CauHinh.tu_moi_truong()
    try:
        khoa = khoa_mot_lan(cfg.tep_khoa)
    except OSError as e:                                          # thu muc/tep khoa hong (quyen, duong khong phai thu muc...)
        ghi_nhat_ky("khong the tao hoac mo tep khoa %s: %s - KHONG chay vi khong khoa duoc" % (cfg.tep_khoa, e))
        return MA_THOAT_LOI_KHOA
    if khoa is None:                                              # --mot-lan cung di qua day: khong co ngoai le
        pid = doc_pid_khoa(cfg.tep_khoa)
        ghi_nhat_ky("da co may chay khac dang chay" + (" (PID %s)" % pid if pid else " (khong doc duoc PID)") +
                    " - tep khoa %s" % cfg.tep_khoa)
        return MA_THOAT_DA_CO_MAY_CHAY
    ghi_nhat_ky("may chay %s: mo hinh cho phep=%s suy luan=%s tep dung=%s tep khoa=%s" % (
        PHIEN_BAN, list(cfg.mo_hinh) or "(mac dinh profile)", list(cfg.suy_luan), cfg.tep_dung, cfg.tep_khoa))
    try:
        chay_mai(NmprpClient, cfg, nhip=a.nhip, nhip_tim=not a.mot_lan, so_vong=1 if a.mot_lan else None, mot_lan=a.mot_lan)
    except NmprpError as e:
        print("DUNG: %s" % e)
        return 2
    except KeyboardInterrupt:
        return 0
    finally:
        khoa.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
