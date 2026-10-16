import os
import unittest
from unittest.mock import patch

from support.public_inference import answer


class PublicInferenceTests(unittest.TestCase):
    def test_disabled(self):
        with patch.dict(os.environ, {"HERMES_PUBLIC_AI_ENABLED": "0"}):
            with self.assertRaises(RuntimeError):
                answer("Đăng ký kỹ thuật", [{"path": "frontend/src/Test.jsx", "line": 1}])

    def test_reject_insecure_url(self):
        with patch.dict(os.environ, {
            "HERMES_PUBLIC_AI_ENABLED": "1",
            "HERMES_PUBLIC_AI_KEY": "test",
            "HERMES_PUBLIC_AI_MODEL": "test",
            "HERMES_PUBLIC_AI_URL": "http://127.0.0.1:1234/chat",
        }):
            with self.assertRaises(RuntimeError):
                answer("Đăng ký kỹ thuật", [{"path": "frontend/src/Test.jsx", "line": 1}])

    def test_no_evidence_no_network(self):
        with patch.dict(os.environ, {
            "HERMES_PUBLIC_AI_ENABLED": "1",
            "HERMES_PUBLIC_AI_KEY": "test",
            "HERMES_PUBLIC_AI_MODEL": "test",
            "HERMES_PUBLIC_AI_URL": "https://example.org/v1/chat/completions",
        }):
            with patch("support.public_inference.request.urlopen") as network:
                result = answer("Đăng ký kỹ thuật", [])
                self.assertIn("Chưa có đủ bằng chứng", result)
                network.assert_not_called()


if __name__ == "__main__":
    unittest.main()
