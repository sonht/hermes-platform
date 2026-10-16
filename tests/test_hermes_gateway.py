import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from support.hermes_gateway import ask_hermes

class GatewayTests(unittest.TestCase):
    @patch("support.hermes_gateway.subprocess.run")
    def test_docker_command_is_fixed_and_bounded(self, run):
        run.return_value = SimpleNamespace(returncode=0, stdout="Hướng dẫn", stderr="")
        with patch.dict(os.environ, {"HERMES_AGENT_ENABLED": "1", "HERMES_GATEWAY_MODE": "docker"}):
            self.assertEqual(ask_hermes("Đăng nhập", [{"path":"frontend/src/AuthAdmin.jsx", "line":1, "excerpt":"GoogleLogin"}]), "Hướng dẫn")
        args, kwargs = run.call_args
        self.assertEqual(args[0][:7], ["docker", "exec", "-i", "-u", "10000", "hermes-platform-agent", "hermes", "-m"])
        self.assertEqual(kwargs["timeout"], 45)
        self.assertFalse(kwargs["check"])

    def test_unknown_mode_fails_closed(self):
        with patch.dict(os.environ, {"HERMES_AGENT_ENABLED": "1", "HERMES_GATEWAY_MODE": "remote"}):
            with self.assertRaises(RuntimeError):
                ask_hermes("Đăng nhập", [])

if __name__ == "__main__":
    unittest.main()
