"""Small signed, expiring dashboard session cookie. No credentials in browser storage."""
import base64
import hashlib
import hmac
import os
import secrets
import time

COOKIE = "hermes_admin"
TTL = 3600

def _key():
    key = os.environ.get("HERMES_DASHBOARD_SESSION_KEY", "")
    if len(key) < 32:
        raise RuntimeError("Dashboard session key missing or too short")
    return key.encode()

def login(password):
    expected = os.environ.get("HERMES_DASHBOARD_PASSWORD", "")
    if len(expected) < 16 or not isinstance(password, str):
        return None
    if not hmac.compare_digest(password, expected):
        return None
    payload = f"{int(time.time()) + TTL}:{secrets.token_hex(16)}"
    signature = hmac.new(_key(), payload.encode(), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{payload}:{signature}".encode()).decode()

def valid(cookie_header):
    if not cookie_header:
        return False
    cookies = dict(part.strip().split("=", 1) for part in cookie_header.split(";") if "=" in part)
    token = cookies.get(COOKIE, "")
    if len(token) > 512:
        return False
    try:
        raw = base64.urlsafe_b64decode(token.encode()).decode()
        expiry, nonce, signature = raw.split(":")
        if int(expiry) < int(time.time()) or int(expiry) > int(time.time()) + TTL:
            return False
        expected = hmac.new(_key(), f"{expiry}:{nonce}".encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected)
    except (ValueError, UnicodeError, RuntimeError):
        return False
