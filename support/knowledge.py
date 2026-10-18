"""Reviewed knowledge entries for the support widget: load, validate, match, render."""
import json
import re
import unicodedata
from pathlib import Path

STATUSES = {"da-duyet", "chua-xac-minh"}
REQUIRED = ("id", "intent", "title", "keywords", "steps", "failure_modes",
            "source_paths", "source_commit", "verification_status")
NO_ANSWER = ("Chưa có hướng dẫn đã duyệt phù hợp cho câu hỏi này. Anh/chị vui lòng hỏi riêng về "
             "đăng nhập hoặc đăng ký, hoặc gửi nội dung thông báo lỗi cho bộ phận hỗ trợ "
             "(không gửi mật khẩu, mã OTP hay token).")


def _fold(text):
    text = unicodedata.normalize("NFD", text.replace("đ", "d").replace("Đ", "D"))
    return " ".join("".join(c for c in text if not unicodedata.combining(c)).casefold().split())


def _validate(obj, source):
    if not isinstance(obj, dict):
        raise ValueError(f"{source}: entry must be a JSON object")
    for key in REQUIRED:
        if key not in obj:
            raise ValueError(f"{source}: missing {key}")
    if obj["verification_status"] not in STATUSES:
        raise ValueError(f"{source}: bad verification_status")
    for key in ("keywords", "steps"):
        if not isinstance(obj[key], list) or not obj[key] or not all(isinstance(x, str) and x for x in obj[key]):
            raise ValueError(f"{source}: {key} must be a non-empty list of strings")
    for key in ("failure_modes", "source_paths"):
        if not isinstance(obj[key], list) or not all(isinstance(x, str) for x in obj[key]):
            raise ValueError(f"{source}: {key} must be a list of strings")
    commit = obj["source_commit"]
    if not isinstance(commit, str):
        raise ValueError(f"{source}: source_commit must be a string")
    if obj["verification_status"] == "da-duyet" and not re.fullmatch(r"[0-9a-f]{7,40}", commit):
        raise ValueError(f"{source}: approved entry needs a hex source_commit")
    return obj


def load_entries(directory):
    if not Path(directory).is_dir():
        raise FileNotFoundError(f"knowledge directory not found: {directory}")
    entries = []
    for path in sorted(Path(directory).glob("*.json")):
        entries.append(_validate(json.loads(path.read_text(encoding="utf-8")), path.name))
    return entries


def find_entry(entries, question):
    folded = _fold(question)
    scored = [(sum(1 for k in e["keywords"] if _fold(k) in folded), e) for e in entries]
    best = max((s for s, _ in scored), default=0)
    if best == 0:
        return None
    top = [e for s, e in scored if s == best]
    return top[0] if len(top) == 1 else None


def render_answer(entry):
    lines = [f"{i}. {step}" for i, step in enumerate(entry["steps"], 1)]
    if entry["failure_modes"]:
        lines += ["", "Nếu gặp sự cố:"] + [f"- {m}" for m in entry["failure_modes"]]
    if entry["verification_status"] != "da-duyet":
        lines += ["", "Lưu ý: hướng dẫn này chưa được xác minh với giao diện hiện hành."]
    if entry["source_commit"]:
        lines += ["", f"Nguồn: NMPRP @{entry['source_commit'][:7]}"]
    return "\n".join(lines)
