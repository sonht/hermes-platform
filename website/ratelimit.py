"""Rate limits that do not depend on client IP (all traffic arrives from 127.0.0.1 via Caddy)."""
import threading
import time
from collections import defaultdict, deque

_WINDOW = 60.0


class RateLimiter:
    def __init__(self, per_session=5, per_app=20, daily_per_app=500,
                 clock=time.monotonic, today=lambda: time.strftime("%Y-%m-%d")):
        self.per_session, self.per_app, self.daily_per_app = per_session, per_app, daily_per_app
        self._clock, self._today = clock, today
        self._lock = threading.Lock()
        self._session = defaultdict(deque)
        self._app = defaultdict(deque)
        self._daily = {}

    @staticmethod
    def _trim(q, now):
        while q and now - q[0] > _WINDOW:
            q.popleft()

    def allow(self, app_id, session):
        with self._lock:
            now, day = self._clock(), self._today()
            day_key, count = self._daily.get(app_id, (day, 0))
            if day_key != day:
                day_key, count = day, 0
            sq, aq = self._session[(app_id, session)], self._app[app_id]
            self._trim(sq, now)
            self._trim(aq, now)
            if count >= self.daily_per_app:
                return "daily"
            if len(aq) >= self.per_app:
                return "app"
            if len(sq) >= self.per_session:
                return "session"
            sq.append(now)
            aq.append(now)
            self._daily[app_id] = (day_key, count + 1)
            return None
