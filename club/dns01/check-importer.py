#!/usr/bin/env python3
"""No remote writes: verify transport and masked TTY behavior with synthetic data."""
import base64, contextlib, http.server, io, json, os, pty, runpy, select, subprocess, sys, threading, time
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import infisical_dns as api
FIXTURE = "SYNTHETIC_ONLY_CANARY_20261006"

class Response:
    def __init__(self, code, data):
        self.status_code = code; self.ok = code < 300; self.data = data
    def json(self):
        return self.data

class Session:
    def __init__(self):
        self.headers = {}; self.saved = None; self.calls = []; self.trust_env = True
    def call(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        assert kwargs.get("allow_redirects") is False
        if url.endswith("/login"):
            return Response(200, {"accessToken": "SYNTHETIC_AUTH"})
        if url.endswith("/folders"):
            return Response(200, {"folders": [{"name": "dns-hermione"}]})
        assert kwargs.get("params", kwargs.get("json"))["secretPath"] == "/dns-hermione"
        if method == "GET":
            return Response(404, {}) if self.saved is None else Response(200, {"secret": {"secretValue": self.saved}})
        self.saved = kwargs["json"]["secretValue"]
        return Response(200, {"secret": {"secretValue": self.saved}})
    def post(self, u, **k): return self.call("POST", u, **k)
    def patch(self, u, **k): return self.call("PATCH", u, **k)
    def get(self, u, **k): return self.call("GET", u, **k)

fake = Session()
with patch.object(api.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, b"https://fixture.invalid\0id\0secret\0")), patch.object(api.requests, "Session", return_value=fake):
    client = api.Client(); client.ensure_folder()
    assert client.store(FIXTURE) == len(FIXTURE)
    assert client.store(FIXTURE + "_ROTATED") == len(FIXTURE + "_ROTATED")
    assert [x[0] for x in fake.calls if x[0] != "GET" and "/secrets/" in x[1]] == ["POST", "PATCH"]
    assert fake.trust_env is False

# Real getpass on a controlling pseudo-terminal: the synthetic token must not echo.
code = """
import sys,runpy
sys.path.insert(0,sys.argv[1])
import infisical_dns
class Client:
 def ensure_folder(self): pass
 def store(self,v): return len(v)
infisical_dns.Client=Client
runpy.run_path(sys.argv[1]+'/store-token.py',run_name='__main__')
"""
pid, fd = pty.fork()
if pid == 0:
    os.execv(sys.executable, [sys.executable, "-B", "-c", code, str(HERE)])
output = b""; sent = False; deadline = time.monotonic() + 10
while time.monotonic() < deadline:
    ready, _, _ = select.select([fd], [], [], 0.5)
    if ready:
        try: block = os.read(fd, 4096)
        except OSError: break
        if not block: break
        output += block
        if b"Token Alwaysdata" in output and not sent:
            os.write(fd, FIXTURE.encode() + b"\n"); sent = True
_, status = os.waitpid(pid, 0); os.close(fd)
assert status == 0 and sent and FIXTURE.encode() not in output
assert ("longueur : %d" % len(FIXTURE)).encode() in output

# Local curl synthetic credential confirms dns_ad URL credentials decode to Basic account=.
from urllib.parse import quote
seen = []
class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        seen.append(base64.b64decode(self.headers["Authorization"].split()[1]).decode())
        self.send_response(200); self.end_headers()
    def log_message(self, *args): pass
server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
t = threading.Thread(target=server.handle_request); t.start()
u = quote(FIXTURE + " account=lightprod.net", safe="")
r = subprocess.run(["curl", "--silent", "--fail", "http://"+u+":@127.0.0.1:"+str(server.server_port)+"/v1/domain/"], capture_output=True)
t.join(); server.server_close()
assert r.returncode == 0 and seen == [FIXTURE + " account=lightprod.net:"]
print("PASS: create/update and readback; private path; redirects/proxies disabled; real TTY no echo; dns_ad delegated Basic account selector. Only synthetic data; no remote write.")
