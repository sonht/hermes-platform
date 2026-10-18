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


if __name__ == "__main__":
    unittest.main()
