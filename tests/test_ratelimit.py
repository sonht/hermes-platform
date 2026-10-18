import unittest

from website.ratelimit import RateLimiter


class Clock:
    def __init__(self):
        self.t = 0.0
        self.day = "2026-10-18"

    def __call__(self):
        return self.t


class RateLimiterTests(unittest.TestCase):
    def setUp(self):
        self.c = Clock()
        self.rl = RateLimiter(per_session=2, per_app=3, daily_per_app=5,
                              clock=self.c, today=lambda: self.c.day)

    def test_session_limit_is_independent_per_session(self):
        self.assertIsNone(self.rl.allow("dm", "a"))
        self.assertIsNone(self.rl.allow("dm", "a"))
        self.assertEqual(self.rl.allow("dm", "a"), "session")
        self.assertIsNone(self.rl.allow("dm", "b"))

    def test_app_limit_is_shared_across_sessions(self):
        for s in ("a", "b", "c"):
            self.assertIsNone(self.rl.allow("dm", s))
        self.assertEqual(self.rl.allow("dm", "d"), "app")
        self.assertIsNone(self.rl.allow("other", "a"))

    def test_window_slides_after_60s(self):
        self.rl.allow("dm", "a")
        self.rl.allow("dm", "a")
        self.c.t = 61
        self.assertIsNone(self.rl.allow("dm", "a"))

    def test_rejected_requests_do_not_consume_quota(self):
        self.rl.allow("dm", "a")
        self.rl.allow("dm", "a")
        for _ in range(10):
            self.assertEqual(self.rl.allow("dm", "a"), "session")
        self.c.t = 61
        self.assertIsNone(self.rl.allow("dm", "a"))

    def test_daily_cap_resets_next_day(self):
        for i in range(5):
            self.c.t = i * 100.0
            self.assertIsNone(self.rl.allow("dm", f"s{i}"))
        self.c.t = 600.0
        self.assertEqual(self.rl.allow("dm", "z"), "daily")
        self.c.day = "2026-10-19"
        self.assertIsNone(self.rl.allow("dm", "z"))

    def test_rejected_requests_do_not_create_session_entries(self):
        rl = RateLimiter(per_session=2, per_app=1000, daily_per_app=2,
                         clock=self.c, today=lambda: self.c.day)
        rl.allow("dm", "s0")
        rl.allow("dm", "s1")
        before = len(rl._session)
        for i in range(50):
            self.assertEqual(rl.allow("dm", f"fresh{i}"), "daily")
        self.assertEqual(len(rl._session), before)

        app_rl = RateLimiter(per_session=2, per_app=3, daily_per_app=1000,
                             clock=self.c, today=lambda: self.c.day)
        for s in ("a", "b", "c"):
            app_rl.allow("dm", s)
        before = len(app_rl._session)
        for i in range(50):
            self.assertEqual(app_rl.allow("dm", f"fresh{i}"), "app")
        self.assertEqual(len(app_rl._session), before)

    def test_stale_empty_session_keys_are_swept(self):
        rl = RateLimiter(per_session=5, per_app=2000, daily_per_app=10000,
                         clock=self.c, today=lambda: self.c.day)
        for i in range(1100):
            self.assertIsNone(rl.allow("dm", f"s{i}"))
        self.assertEqual(len(rl._session), 1100)
        self.c.t = 61
        self.assertIsNone(rl.allow("dm", "new"))
        self.assertEqual(len(rl._session), 1)

    def test_app_rejection_does_not_consume_session_quota(self):
        rl = RateLimiter(per_session=2, per_app=3, daily_per_app=1000,
                         clock=self.c, today=lambda: self.c.day)
        rl.allow("dm", "b")
        rl.allow("dm", "c")
        rl.allow("dm", "d")
        self.assertEqual(rl.allow("dm", "a"), "app")
        self.c.t = 61
        self.assertIsNone(rl.allow("dm", "a"))
        self.assertIsNone(rl.allow("dm", "a"))
        self.assertEqual(rl.allow("dm", "a"), "session")


if __name__ == "__main__":
    unittest.main()
