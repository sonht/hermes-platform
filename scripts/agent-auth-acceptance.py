"""Authenticated acceptance check for https://hermes.kcb.vn/agent over the tailnet.

Reads the dashboard credentials from the env file into memory only. Prints status codes and
cookie names/attributes, never credential, cookie or ticket values. Logs in, then logs out.
Note: opening /api/pty with a ticket briefly spawns the dashboard's PTY child.

Usage: python3 -I scripts/agent-auth-acceptance.py deploy/rocky/dashboard-production.env 100.110.57.61
"""
import base64
import http.client
import json
import os
import re
import socket
import ssl
import struct
import sys

ENV, IP = sys.argv[1], sys.argv[2]
HOST = "hermes.kcb.vn"
ORIGIN = f"https://{HOST}"
creds = dict(l.rstrip("\n").split("=", 1) for l in open(ENV) if "=" in l and not l.startswith("#"))

_getaddrinfo = socket.getaddrinfo
socket.getaddrinfo = lambda h, *a, **k: _getaddrinfo(IP if h == HOST else h, *a, **k)

jar = {}
results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}: {name} {detail}")


def req(method, path, body=None, headers=None):
    conn = http.client.HTTPSConnection(HOST, 443, timeout=15, context=ssl.create_default_context())
    h = {"Host": HOST, "User-Agent": "agent-acceptance", "Origin": ORIGIN}
    if jar:
        h["Cookie"] = "; ".join(f"{k}={v}" for k, v in jar.items())
    if body is not None:
        h["Content-Type"] = "application/json"
    h.update(headers or {})
    conn.request(method, path, body=body, headers=h)
    r = conn.getresponse()
    data = r.read()
    for name, val in r.getheaders():
        if name.lower() != "set-cookie":
            continue
        parts = [p.strip() for p in val.split(";")]
        ck, cv = parts[0].split("=", 1)
        attrs = "; ".join(a for a in parts[1:] if not a.lower().startswith("expires"))
        if cv == "" or "max-age=0" in attrs.lower():
            jar.pop(ck, None)
        else:
            jar[ck] = cv
            print(f"  Set-Cookie {ck}=<redacted>; {attrs}")
    conn.close()
    return r.status, data


def ws(path, origin=ORIGIN, cookie=True, ticket=False):
    """Return (status line, first frame summary) of a WebSocket upgrade."""
    q = ""
    if ticket:
        st, body = req("POST", "/agent/api/auth/ws-ticket", b"{}")
        if st != 200:
            return f"ticket {st}", ""
        q = "?ticket=" + json.loads(body)["ticket"]
    t = ssl.create_default_context().wrap_socket(socket.create_connection((HOST, 443), timeout=8),
                                                 server_hostname=HOST)
    lines = [f"GET {path}{q} HTTP/1.1", f"Host: {HOST}", "Upgrade: websocket", "Connection: Upgrade",
             f"Sec-WebSocket-Key: {base64.b64encode(os.urandom(16)).decode()}", "Sec-WebSocket-Version: 13"]
    if origin:
        lines.append(f"Origin: {origin}")
    if cookie and jar:
        lines.append("Cookie: " + "; ".join(f"{k}={v}" for k, v in jar.items()))
    t.sendall(("\r\n".join(lines) + "\r\n\r\n").encode())
    buf = b""
    while b"\r\n\r\n" not in buf:
        d = t.recv(4096)
        if not d:
            break
        buf += d
    head, _, rest = buf.partition(b"\r\n\r\n")
    status = head.split(b"\r\n", 1)[0].decode()
    frame = ""
    if " 101 " in status:
        try:
            t.settimeout(3)
            while len(rest) < 2:
                rest += t.recv(4096)
            op, ln = rest[0] & 0x0F, rest[1] & 0x7F
            while len(rest) < 2 + min(ln, 125):
                rest += t.recv(4096)
            frame = f"close={struct.unpack('!H', rest[2:4])[0]}" if op == 8 and ln >= 2 else f"data opcode={op}"
        except socket.timeout:
            frame = "open, no frame in 3s"
    t.close()
    return status, frame


st, body = req("POST", "/agent/auth/password-login", json.dumps({
    "provider": "basic", "username": creds["HERMES_DASHBOARD_BASIC_AUTH_USERNAME"],
    "password": creds["HERMES_DASHBOARD_BASIC_AUTH_PASSWORD"], "next": "/agent/"}))
check("login", st == 200, f"-> {st}")
check("session cookies Path=/agent + Secure", bool(jar) and all(k.startswith("__Secure-") for k in jar),
      f"names={sorted(jar)}")

st, _ = req("GET", "/agent/api/auth/me")
check("session /agent/api/auth/me", st == 200, f"-> {st}")

st, body = req("GET", "/agent/")
html = body.decode("utf-8", "replace")
check("index /agent/ with base path", st == 200 and "__HERMES_BASE_PATH__" in html, f"-> {st}")
assets = sorted(set(re.findall(r'(?:src|href)="(/[^"]+\.(?:js|css))"', html)))
bad = [(a, s) for a in assets for s in [req("GET", a)[0]] if s != 200 or not a.startswith("/agent/")]
check("JS/CSS assets under /agent", bool(assets) and not bad, f"count={len(assets)} bad={bad}")

for sub in ("/agent/sessions", "/agent/config", "/agent/chat"):
    st, body = req("GET", sub)
    check(f"refresh sub-route {sub}", st == 200 and b"__HERMES_BASE_PATH__" in body, f"-> {st}")

for api in ("/agent/api/config", "/agent/api/sessions"):
    st, _ = req("GET", api)
    check(f"authenticated API {api}", st == 200, f"-> {st}")

for p in ("/agent/api/pty", "/agent/api/ws", "/agent/api/console"):
    s, f = ws(p, ticket=True)
    check(f"WS {p} with ticket", " 101 " in s and f.startswith("data"), f"-> {s} {f}")
    s, f = ws(p)
    check(f"WS {p} cookie only (ticket required)", " 101 " not in s, f"-> {s}")
s, f = ws("/agent/api/display/ws")
check("WS /agent/api/display/ws without display ticket closes 4401", f == "close=4401", f"-> {s} {f}")

st, _ = req("POST", "/agent/auth/logout", b"{}")
check("logout", st in (200, 204, 302, 303), f"-> {st}")
st, _ = req("GET", "/agent/api/config")
check("API refused after logout", st == 401, f"-> {st}")
for p in ("/agent/api/pty", "/agent/api/ws"):
    s, _ = ws(p, cookie=False)
    check(f"WS {p} unauthenticated refused", " 101 " not in s, f"-> {s}")

print(f"SUMMARY: {sum(results)}/{len(results)} passed")
sys.exit(0 if all(results) else 1)
