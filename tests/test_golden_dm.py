import json
import unittest
from pathlib import Path

from support.knowledge import find_entry, load_entries

ROOT = Path(__file__).resolve().parents[1]


class GoldenDmTests(unittest.TestCase):
    def test_at_least_20_cases_route_as_expected(self):
        cases = json.loads((ROOT / "tests/golden/dm_login.json").read_text(encoding="utf-8"))["cases"]
        self.assertGreaterEqual(len(cases), 20)
        entries = load_entries(ROOT / "knowledge/dm")
        for c in cases:
            got = find_entry(entries, c["q"])
            self.assertEqual(got["intent"] if got else None, c["intent"], c["q"])


if __name__ == "__main__":
    unittest.main()
