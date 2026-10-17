"""Deterministic FAQ candidate grouping; suggestions only, never auto-publish.

Use normalized exact-match grouping first. No LLM calls or unreviewed GitHub writes.
"""
from collections import defaultdict
import re
import unicodedata
from support.intelligence import recent

def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = re.sub(r"[^\w\s]", " ", value, flags=re.UNICODE)
    return " ".join(value.split())

def candidates(db_path: str, app: str | None = None, minimum: int = 2, limit: int = 200) -> list[dict]:
    if not 2 <= minimum <= 100:
        raise ValueError("Invalid minimum")
    groups = defaultdict(list)
    for row in recent(db_path, app=app, kind="faq", limit=limit):
        key = normalize(row["summary"])
        if key:
            groups[(row["app"], key)].append(row)
    result = []
    for (application, key), items in groups.items():
        if len(items) >= minimum:
            result.append({"app": application, "question": items[0]["summary"],
                           "count": len(items), "report_ids": [x["id"] for x in items],
                           "status": "candidate"})
    return sorted(result, key=lambda x: (-x["count"], x["app"], x["question"]))
