"""Generate a DRAFT knowledge entry from the NMPRP repo. A human must review before approval."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from support.user_journey_builder import build_journey

TOPIC_KEYWORDS = {
    "login": ["đăng nhập", "login", "google"],
    "register": ["đăng ký", "tạo tài khoản"],
}
TITLES = {"login": "Đăng nhập dm.kcb.vn", "register": "Đăng ký tài khoản dm.kcb.vn"}
FAILURES = {
    "login": ["Chưa được cấp quyền hoặc tài khoản chưa kích hoạt: làm theo thông báo trên màn hình hoặc liên hệ bộ phận hỗ trợ."],
    "register": ["Hồ sơ đang chờ xét duyệt: chưa truy cập được chức năng có phân quyền cho đến khi được kích hoạt."],
}


def build_entry(root, topic, commit):
    journey = build_journey(root, topic)
    if not journey["steps"]:
        return None
    return {"id": topic, "intent": topic, "title": TITLES[topic],
            "keywords": TOPIC_KEYWORDS[topic], "steps": journey["steps"],
            "failure_modes": FAILURES[topic],
            "source_paths": sorted({e["path"] for e in journey["evidence"]}),
            "source_commit": commit, "verification_status": "chua-xac-minh"}


def write_entry(out, entry):
    out = Path(out)
    if entry is None:
        raise SystemExit("Không đủ bằng chứng mã nguồn; không ghi tệp.")
    if out.exists() and json.loads(out.read_text(encoding="utf-8")).get("verification_status") == "da-duyet":
        raise SystemExit(f"{out} đã được duyệt; không ghi đè. Sửa tay hoặc xoá có chủ ý.")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(entry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--topic", required=True, choices=sorted(TOPIC_KEYWORDS))
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    commit = subprocess.run(["git", "-C", args.repo, "rev-parse", "HEAD"], capture_output=True,
                            text=True, check=True).stdout.strip()
    write_entry(args.out, build_entry(args.repo, args.topic, commit))
    print(f"wrote {args.out} @ {commit[:7]} (chua-xac-minh)")


if __name__ == "__main__":
    main()
