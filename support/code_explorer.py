"""Read-only, bounded source explorer for NMPRP support journeys."""
from pathlib import Path
import re

ALLOWED = ("frontend/src/", "backend/app/api/")
EXTENSIONS = {".jsx", ".js", ".ts", ".tsx", ".py"}
MAX_BYTES = 150_000
PATTERNS = {
    "login": re.compile(r"login|đăng nhập|dang.nhap|GoogleLogin|/auth/google", re.I),
    "register": re.compile(r"đăng ký|dang.ky|registration|DangKy|kích hoạt", re.I),
}

def explore(root: str | Path, topic: str, max_files: int = 30) -> list[dict]:
    """Return source citations, never credentials or arbitrary repository files."""
    if topic not in PATTERNS:
        raise ValueError("Unsupported journey")
    base = Path(root).resolve(strict=True)
    if not 1 <= max_files <= 100:
        raise ValueError("Invalid file limit")
    findings = []
    for prefix in ALLOWED:
        folder = base / prefix
        if not folder.is_dir():
            continue
        for file in sorted(folder.rglob("*")):
            if len(findings) >= max_files:
                return findings
            if file.is_symlink() or not file.is_file() or file.suffix not in EXTENSIONS:
                continue
            resolved = file.resolve()
            if not resolved.is_relative_to(base) or file.stat().st_size > MAX_BYTES:
                continue
            for line_no, line in enumerate(file.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if PATTERNS[topic].search(line):
                    if re.search(r"secret|password_hash|private.key|api.key|token\s*=", line, re.I):
                        continue
                    findings.append({"path": file.relative_to(base).as_posix(), "line": line_no,
                                     "excerpt": line.strip()[:220]})
                    break
    return findings
