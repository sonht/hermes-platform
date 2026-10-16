import tempfile
import unittest
from pathlib import Path
from support.code_explorer import explore
from support.user_journey_builder import build_journey

class JourneyTests(unittest.TestCase):
    def test_evidence_and_draft(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d) / "frontend/src"
            folder.mkdir(parents=True)
            (folder / "AuthAdmin.jsx").write_text("function GoogleLogin() { /* đăng nhập */ }")
            result = build_journey(d, "login")
            self.assertEqual(result["status"], "draft_needs_review")
            self.assertEqual(result["evidence"][0]["path"], "frontend/src/AuthAdmin.jsx")
            self.assertTrue(result["review_required"])

    def test_no_evidence_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(build_journey(d, "register")["steps"], [])

    def test_reject_unsupported_topic(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                explore(d, "secrets")

if __name__ == "__main__":
    unittest.main()
