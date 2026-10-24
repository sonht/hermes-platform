import os
import time
import unittest
from unittest.mock import patch
from support.dashboard_auth import login, valid

class DashboardAuthTests(unittest.TestCase):
    def test_session(self):
        with patch.dict(os.environ, {
            "HERMES_DASHBOARD_PASSWORD": "strong-test-password-123",
            "HERMES_DASHBOARD_SESSION_KEY": "test-key-with-at-least-32-characters-123456",
        }):
            self.assertIsNone(login("wrong"))
            token=login("strong-test-password-123")
            self.assertTrue(valid("hermes_admin="+token))
            self.assertFalse(valid("hermes_admin="+token+"tampered"))
            self.assertFalse(valid("hermes_admin=invalid"))
            with patch("support.dashboard_auth.time.time", return_value=time.time()+3700):
                self.assertFalse(valid("hermes_admin="+token))
