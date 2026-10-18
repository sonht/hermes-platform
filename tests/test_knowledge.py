import json
import tempfile
import unittest
from pathlib import Path

from support.knowledge import NO_ANSWER, find_entry, load_entries, render_answer


def entry(**kw):
    base = {"id": "login", "intent": "login", "title": "Đăng nhập",
            "keywords": ["đăng nhập", "login"], "steps": ["Mở trang", "Chọn Google"],
            "failure_modes": ["Chưa được cấp quyền"], "source_paths": ["frontend/src/AuthAdmin.jsx"],
            "source_commit": "cdc6e7c1", "verification_status": "chua-xac-minh"}
    base.update(kw)
    return base


class KnowledgeTests(unittest.TestCase):
    def write(self, tmp, name, obj):
        (Path(tmp) / name).write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")

    def test_load_valid_and_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.write(tmp, "a.json", entry())
            self.assertEqual(load_entries(tmp)[0]["id"], "login")
            self.write(tmp, "b.json", entry(id="bad", steps=[]))
            with self.assertRaises(ValueError):
                load_entries(tmp)

    def test_approved_requires_commit_hex(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.write(tmp, "a.json", entry(verification_status="da-duyet", source_commit=""))
            with self.assertRaises(ValueError):
                load_entries(tmp)

    def test_unknown_status_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.write(tmp, "a.json", entry(verification_status="tam-duoc"))
            with self.assertRaises(ValueError):
                load_entries(tmp)

    def test_find_is_accent_and_case_insensitive(self):
        entries = [entry(), entry(id="register", intent="register", keywords=["đăng ký", "tạo tài khoản"])]
        self.assertEqual(find_entry(entries, "DANG NHAP the nao")["id"], "login")
        self.assertEqual(find_entry(entries, "Tôi muốn tạo tài khoản")["id"], "register")

    def test_find_none_and_tie(self):
        entries = [entry(), entry(id="register", intent="register", keywords=["đăng ký"])]
        self.assertIsNone(find_entry(entries, "xin chào"))
        self.assertIsNone(find_entry(entries, "đăng nhập và đăng ký"))

    def test_render_unverified_has_notice_and_no_file_paths(self):
        text = render_answer(entry())
        self.assertIn("1. Mở trang", text)
        self.assertIn("chưa được xác minh", text)
        self.assertIn("NMPRP @cdc6e7c", text)
        self.assertNotIn("AuthAdmin.jsx", text)

    def test_render_verified_has_no_notice(self):
        text = render_answer(entry(verification_status="da-duyet"))
        self.assertNotIn("chưa được xác minh", text)

    def test_missing_directory_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                load_entries(Path(tmp) / "khong-co")

    def test_non_object_entry_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.write(tmp, "a.json", [])
            with self.assertRaises(ValueError):
                load_entries(tmp)

    def test_non_string_source_commit_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.write(tmp, "a.json", entry(source_commit=123))
            with self.assertRaises(ValueError):
                load_entries(tmp)

    def test_no_answer_asks_for_error_text_without_secrets(self):
        self.assertIn("mật khẩu", NO_ANSWER)


if __name__ == "__main__":
    unittest.main()
