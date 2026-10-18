"""App registry: which software may embed the chat widget and where its knowledge lives."""
import json
import re
from pathlib import Path

_KEY = re.compile(r"^[a-z0-9-]{1,32}$")
_ORIGIN = re.compile(r"^https?://[A-Za-z0-9.-]+(:\d{1,5})?$")


class AppRegistry:
    def __init__(self, apps: dict):
        self._apps = apps

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        for key, app in data.items():
            if not _KEY.match(key):
                raise ValueError(f"invalid app id: {key!r}")
            origins = app.get("origins")
            if not isinstance(origins, list) or not origins:
                raise ValueError(f"{key}: origins required")
            for origin in origins:
                if not isinstance(origin, str) or not _ORIGIN.match(origin):
                    raise ValueError(f"{key}: invalid origin {origin!r}")
            if not isinstance(app.get("knowledge"), str) or not app.get("name"):
                raise ValueError(f"{key}: name and knowledge required")
        return cls(data)

    def get(self, app_id):
        return self._apps.get(app_id) if isinstance(app_id, str) else None

    def origin_allowed(self, app_id, origin):
        app = self.get(app_id)
        if app is None:
            return False
        return origin is None or origin in app["origins"]
