import tempfile
import unittest
from pathlib import Path
from support.faq_studio import list_articles, save_draft, set_publication

class FAQStudioTests(unittest.TestCase):
    def test_review_workflow(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=str(Path(tmp)/"faq.db")
            id=save_draft(db,"nmprp","Đăng nhập bằng Google thế nào?","Nhấn nút Google tại màn hình đăng nhập.")
            self.assertEqual(list_articles(db,"nmprp",published_only=True),[])
            self.assertEqual(len(list_articles(db,"nmprp")),1)
            self.assertTrue(set_publication(db,id,True))
            self.assertEqual(len(list_articles(db,"nmprp",published_only=True)),1)
            self.assertEqual(list_articles(db,"icd10",published_only=True),[])
            self.assertTrue(set_publication(db,id,False))
            self.assertEqual(list_articles(db,"nmprp",published_only=True),[])
            with self.assertRaises(ValueError):
                set_publication(db,id,"true")
