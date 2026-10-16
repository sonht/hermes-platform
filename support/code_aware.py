"""Bounded read-only source retrieval for NMPRP public support.

No code execution, credentials, arbitrary file access or model tools.
"""
from pathlib import Path
import re

ALLOWED = ("frontend/src", "backend/app/api")
EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".py"}
MAX_FILES = 1200
MAX_BYTES = 100_000
MAX_EVIDENCE = 5
SENSITIVE = re.compile(r"password|passwd|secret|api[_-]?key|private[_-]?key|authorization|bearer|token|credential|\.env|session|cookie", re.I)
WORD = re.compile(r"[^\W_]{3,}", re.UNICODE)
STOP = {"hướng", "dẫn", "cách", "làm", "thế", "nào", "tôi", "muốn", "trên", "trong", "phần", "mềm", "không", "được", "với", "cho", "biết", "dm", "kcb", "vn", "hãy", "giúp", "mình", "như", "để", "của", "một", "các", "khi", "bị"}


def retrieve(root: str, question: str) -> list[dict]:
    """Find bounded source references, returning paths and line numbers only."""
    base = Path(root).resolve(strict=True)
    terms = list(dict.fromkeys(w.lower() for w in WORD.findall(question)
                               if w.lower() not in STOP))[:10]
    if not terms:
        return []
    matches = []
    scanned = 0
    for prefix in ALLOWED:
        folder = base / prefix
        if folder.is_symlink() or not folder.is_dir():
            continue
        for file in sorted(folder.rglob("*")):
            if scanned >= MAX_FILES:
                break
            if file.is_symlink() or not file.is_file() or file.suffix not in EXTENSIONS:
                continue
            try:
                resolved = file.resolve(strict=True)
                if not resolved.is_relative_to(base) or file.stat().st_size > MAX_BYTES:
                    continue
                scanned += 1
                for lineno, line in enumerate(file.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                    if SENSITIVE.search(line):
                        continue
                    score = sum(term in line.lower() for term in terms)
                    if score:
                        matches.append((score, file.relative_to(base).as_posix(), lineno))
            except (OSError, UnicodeError):
                continue
    matches.sort(key=lambda x: (-x[0], x[1], x[2]))
    output, seen = [], set()
    for score, path, line in matches:
        if path in seen:
            continue
        seen.add(path)
        output.append({"path": path, "line": line, "score": score})
        if len(output) >= MAX_EVIDENCE:
            break
    return output


def public_answer(root: str, question: str) -> str:
    """Fail closed: source references only, no untrusted model/tool invocation."""
    evidence = retrieve(root, question)
    if not evidence:
        return ("Chưa xác định được chức năng tương ứng trong mã nguồn. "
                "Vui lòng cho biết tên chức năng, thao tác và thông báo lỗi; "
                "không gửi mật khẩu hoặc thông tin cá nhân.")
    refs = "\n".join(f"- {e['path']}:{e['line']}" for e in evidence)
    return ("Đã tìm thấy các vị trí mã nguồn có thể liên quan:\n" + refs +
            "\n\nĐây là kết quả tra cứu mã nguồn, chưa phải hướng dẫn thao tác đã xác minh. "
            "Chức năng tổng hợp hướng dẫn bằng AI sẽ được bật sau khi có dịch vụ suy luận "
            "cách ly, chỉ đọc và được kiểm thử bảo mật.")
