import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_knowledge import TOPIC_KEYWORDS, build_entry, write_entry
from support.knowledge import load_entries


def fake_repo(tmp):
    folder = Path(tmp) / "frontend/src"
    folder.mkdir(parents=True)
    (folder / "AuthAdmin.jsx").write_text("GoogleLogin đăng nhập", encoding="utf-8")


class BuildKnowledgeTests(unittest.TestCase):
    def test_entry_is_draft_with_sources_and_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_repo(tmp)
            e = build_entry(tmp, "login", "cdc6e7c1")
            self.assertEqual(e["verification_status"], "chua-xac-minh")
            self.assertEqual(e["source_commit"], "cdc6e7c1")
            self.assertIn("frontend/src/AuthAdmin.jsx", e["source_paths"])
            self.assertEqual(e["keywords"], TOPIC_KEYWORDS["login"])

    def test_no_evidence_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(build_entry(tmp, "login", "cdc6e7c1"))

    def test_write_refuses_to_overwrite_approved(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_repo(tmp)
            out = Path(tmp) / "out" / "login.json"
            write_entry(out, build_entry(tmp, "login", "cdc6e7c1"))
            self.assertEqual(load_entries(out.parent)[0]["id"], "login")
            data = json.loads(out.read_text(encoding="utf-8"))
            data["verification_status"] = "da-duyet"
            out.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(SystemExit):
                write_entry(out, build_entry(tmp, "login", "cdc6e7c1"))


if __name__ == "__main__":
    unittest.main()
