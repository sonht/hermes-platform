import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "hermes" / "profiles" / "nmprp-mapping"
DOCS = REPO / "docs"
LIMIT_MEMORY, LIMIT_USER = 2200, 1375


def read(p):
    return (ROOT / p).read_text(encoding="utf-8")


class ProfileFilesTest(unittest.TestCase):
    def test_memory_seeds_fit_hermes_limits(self):
        self.assertLessEqual(len(read("memories/MEMORY.md")), LIMIT_MEMORY)
        self.assertLessEqual(len(read("memories/USER.md")), LIMIT_USER)
        for f in ("memories/MEMORY.md", "memories/USER.md"):
            self.assertGreaterEqual(len(read(f).split("\n§\n")), 3, f)      # entries separated by §

    def test_skills_have_frontmatter_matching_directory(self):
        dirs = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
        self.assertGreaterEqual(len(dirs), 4)
        for d in dirs:
            txt = (d / "SKILL.md").read_text(encoding="utf-8")
            m = re.match(r"^---\nname: ([a-z0-9-]+)\ndescription: (.+)\n---\n", txt)
            self.assertTrue(m, d.name)
            self.assertEqual(m.group(1), d.name)
            for sec in ("## When to Use", "## Procedure", "## Pitfalls", "## Verification"):
                self.assertIn(sec, txt, f"{d.name}: {sec}")

    def test_no_secrets_and_no_cpt_codes(self):
        bad = re.compile(r"(sk-[A-Za-z0-9]{10,}|Bearer\s+[A-Za-z0-9_\-]{20,}|password\s*[:=]\s*\S+|\b\d{5}\b\s*-\s*\d{5}\b)", re.I)
        for p in ROOT.rglob("*"):
            if p.is_file():
                self.assertIsNone(bad.search(p.read_text(encoding="utf-8")), str(p))

    def test_archive_has_no_secrets(self):
        bad = re.compile(r"(sk-[A-Za-z0-9]{10,}|Bearer\s+[A-Za-z0-9_\-]{20,}|password\s*[:=]\s*\S+|\b\d{5}\b\s*-\s*\d{5}\b)", re.I)
        files = [p for p in (DOCS / "lich-su").rglob("*") if p.is_file()]
        self.assertTrue(files)
        for p in files:
            self.assertIsNone(bad.search(p.read_text(encoding="utf-8")), str(p))
        self.assertFalse(any("lich-su" in p.parts for p in ROOT.rglob("*")))

    def _live_docs(self):
        return [p for p in ROOT.rglob("*.md")] + [DOCS / "NMPRP_HERMES_BRAIN_DUMP.md", DOCS / "NMPRP_HERMES_KIEN_TRUC.md"]

    def test_live_docs_use_only_pl1_and_pl2(self):
        allowed = re.compile(r"kind=pl3|PL3-PROC-", re.I)
        for p in self._live_docs():
            txt = allowed.sub("", p.read_text(encoding="utf-8"))
            self.assertIsNone(re.search(r"pl3", txt, re.I), str(p))

    def test_pl1_is_never_called_price_or_history(self):
        for p in self._live_docs():
            txt = p.read_text(encoding="utf-8")
            self.assertNotIn("lịch sử/giá", txt, str(p))
            self.assertNotIn("liên hệ lịch sử", txt, str(p))
        a = read("AGENTS.md")
        self.assertIn("01/01/2028", a)
        self.assertIn("không phải danh mục giá", a)

    def test_ha_status_labels_live_in_agents_and_stay_out_of_nmprp_fields(self):
        a = read("AGENTS.md")
        for s in ("HIGH_CONFIDENCE_PROPOSAL", "REVIEW_RECOMMENDED", "EXPERT_REQUIRED", "UNRESOLVED",
                  "NO_SAFE_MATCH", "PENDING_EXPERT_REVIEW", "DISPUTED", "RULE_CANDIDATE"):
            self.assertIn(s, a)
        self.assertIn("KHÔNG ghi vào trường trạng thái của NMPRP", a)
        for s2 in ("EXPERT_FEEDBACK", "VERIFIED_KNOWLEDGE", "GOLD_STANDARD"):
            self.assertIn(s2, a)
        self.assertIn("CHO_XEM", a)

    def test_brain_dump_has_32_answers_and_owner_gate(self):
        txt = (DOCS / "NMPRP_HERMES_BRAIN_DUMP.md").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"^###\s+(?:\d+\.|★)?", txt, re.M)), 32)
        self.assertIn("chờ chủ dự án duyệt", txt)

    def test_soul_keeps_the_hard_rules(self):
        soul = read("SOUL.md")
        for needle in ("CHỈ ĐỀ XUẤT", "CHUỖI", "mã CPT", "Công tắc AI"):
            self.assertIn(needle, soul)

    def test_agents_md_names_forbidden_paths(self):
        a = read("AGENTS.md")
        self.assertIn("ma-cpt", a)
        self.assertIn("kind=cpt", a)
        self.assertIn("POST /admin/hermes/goi-y", a)


if __name__ == "__main__":
    unittest.main()
