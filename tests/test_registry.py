import json
import tempfile
import unittest
from pathlib import Path

from website.registry import AppRegistry

APPS = {"dm": {"name": "dm.kcb.vn", "origins": ["https://dm.kcb.vn"], "knowledge": "knowledge/dm"}}


class RegistryTests(unittest.TestCase):
    def test_get_known_and_unknown(self):
        reg = AppRegistry(APPS)
        self.assertEqual(reg.get("dm")["name"], "dm.kcb.vn")
        self.assertIsNone(reg.get("nope"))
        self.assertIsNone(reg.get("../etc"))

    def test_origin_rules(self):
        reg = AppRegistry(APPS)
        self.assertTrue(reg.origin_allowed("dm", "https://dm.kcb.vn"))
        self.assertFalse(reg.origin_allowed("dm", "https://evil.example"))
        self.assertFalse(reg.origin_allowed("dm", "https://dm.kcb.vn.evil.example"))
        self.assertTrue(reg.origin_allowed("dm", None))
        self.assertFalse(reg.origin_allowed("nope", "https://dm.kcb.vn"))

    def test_load_rejects_bad_key_and_origin(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "apps.json"
            p.write_text(json.dumps({"Bad Key": APPS["dm"]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                AppRegistry.load(p)
            p.write_text(json.dumps({"dm": {**APPS["dm"], "origins": ["*"]}}), encoding="utf-8")
            with self.assertRaises(ValueError):
                AppRegistry.load(p)

    def test_shipped_apps_json_is_valid(self):
        reg = AppRegistry.load(Path(__file__).resolve().parents[1] / "website" / "apps.json")
        self.assertIn("https://dm.kcb.vn", reg.get("dm")["origins"])


if __name__ == "__main__":
    unittest.main()
