import tempfile
import unittest
from pathlib import Path
from support.intelligence import record
from support.faq_candidates import candidates

class FAQCandidatesTests(unittest.TestCase):
    def test_repeat_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=str(Path(tmp)/"feedback.db")
            record(db,"nmprp","faq","Làm thế nào đăng nhập?")
            record(db,"nmprp","faq","  làm THẾ nào đăng nhập  ")
            record(db,"nmprp","faq","Cách tìm mã CPT?")
            record(db,"icd10","faq","Làm thế nào đăng nhập?")
            rows=candidates(db)
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0]["count"],2)
            self.assertEqual(rows[0]["app"],"nmprp")
            with self.assertRaises(ValueError):
                candidates(db,minimum=1)
