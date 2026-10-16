import tempfile
import unittest
from pathlib import Path
from support.intelligence import record, summary, retention, sanitize


class IntelligenceTests(unittest.TestCase):
    def test_record_aggregate_and_redact(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "support.sqlite3")
            record(db, "nmprp", "bug", "Bấm lưu kỹ thuật bị lỗi. Email: person@example.com token=secret123")
            record(db, "nmprp", "feature", "Đề nghị có chức năng nhập Excel hàng loạt")
            self.assertEqual(summary(db, "nmprp"), [
                {"app": "nmprp", "kind": "bug", "count": 1},
                {"app": "nmprp", "kind": "feature", "count": 1},
            ])
            import sqlite3
            with sqlite3.connect(db) as con:
                stored = con.execute("SELECT summary FROM feedback WHERE kind='bug'").fetchone()[0]
            self.assertNotIn("person@example.com", stored)
            self.assertNotIn("secret123", stored)
            self.assertEqual(retention(db, 30), 0)

    def test_invalid_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "feedback.db")
            with self.assertRaises(ValueError):
                record(db, "../../etc", "bug", "Something went wrong")
            with self.assertRaises(ValueError):
                record(db, "nmprp", "unknown", "Something went wrong")
            with self.assertRaises(ValueError):
                summary(db, days=0)
            self.assertIn("[credential]", sanitize("token=abc123"))
