"""Rate limits that do not depend on client IP (all traffic arrives from 127.0.0.1 via Caddy)."""
import threading
import time
from collections import defaultdict, deque

_WINDOW = 60.0
_SWEEP_AT = 1024


class RateLimiter:
    def __init__(self, per_session=5, per_app=20, daily_per_app=500,
                 clock=time.monotonic, today=lambda: time.strftime("%Y-%m-%d")):
        self.per_session, self.per_app, self.daily_per_app = per_session, per_app, daily_per_app
        self._clock, self._today = clock, today
        self._lock = threading.Lock()
        self._session = {}
        self._app = {}
        self._daily = {}

    @staticmethod
    def _trim(q, now):
        while q and now - q[0] > _WINDOW:
            q.popleft()

    @staticmethod
    def _keep(bucket, key, q):
        # Store only non-empty deques so client-supplied keys never linger.
        if q:
            bucket[key] = q
        else:
            bucket.pop(key, None)

    def _sweep(self, now):
        for key in list(self._session):
            q = self._session[key]
            self._trim(q, now)
            if not q:
                del self._session[key]

    def allow(self, app_id, session):
        with self._lock:
            now, day = self._clock(), self._today()
            if len(self._session) > _SWEEP_AT:
                self._sweep(now)
            day_key, count = self._daily.get(app_id, (day, 0))
            if day_key != day:
                day_key, count = day, 0
            key = (app_id, session)
            sq = self._session.get(key, deque())
            aq = self._app.get(app_id, deque())
            self._trim(sq, now)
            self._trim(aq, now)
            if count >= self.daily_per_app:
                result = "daily"
            elif len(aq) >= self.per_app:
                result = "app"
            elif len(sq) >= self.per_session:
                result = "session"
            else:
                sq.append(now)
                aq.append(now)
                self._daily[app_id] = (day_key, count + 1)
                result = None
            self._keep(self._session, key, sq)
            self._keep(self._app, app_id, aq)
            return result
