import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "hermes" / "profiles" / "nmprp-mapping"
DRAFTS = REPO / "hermes" / "drafts"
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
        self.assertGreaterEqual(len(dirs), 2)
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

    def test_drafts_have_no_secrets_and_are_not_in_the_installable_profile(self):
        bad = re.compile(r"(sk-[A-Za-z0-9]{10,}|Bearer\s+[A-Za-z0-9_\-]{20,}|password\s*[:=]\s*\S+|\b\d{5}\b\s*-\s*\d{5}\b)", re.I)
        files = [p for p in DRAFTS.rglob("*") if p.is_file()]
        self.assertTrue(files)
        for p in files:
            self.assertIsNone(bad.search(p.read_text(encoding="utf-8")), str(p))
        self.assertFalse(any("drafts" in p.parts for p in ROOT.rglob("*")))        # bản nháp không nằm trong profile sẽ cài

    def test_reconciliation_keeps_the_pl3_warning(self):
        doc = (REPO / "docs" / "NMPRP_HA_PROFILES_V1_RECONCILIATION.md").read_text(encoding="utf-8")
        self.assertIn("PL3 là tên cũ của PL2", doc)
        self.assertIn("AWAITING OWNER APPROVAL", doc)
        wrong = (DRAFTS / "Hermes_HA_Profiles_v1" / "profiles" / "nmprp" / "SOUL.md").read_text(encoding="utf-8")
        self.assertNotIn("PL3 thuộc kiến trúc rộng hơn", wrong)  # đã sửa theo chủ dự án
        self.assertIn("PL3 là TÊN CŨ của PL2", wrong)

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
