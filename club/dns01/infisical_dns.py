"""Private in-memory Infisical client; no CLI exports or response logging."""
import ctypes, http.client, os, resource, socket, ssl, subprocess
from urllib.parse import urlsplit
import requests
PROJECT_ID = "73962094-cbd8-464f-91d6-bea7ba041d8c"
PROJECT_NAME = "librechat-artefacts"
ENVIRONMENT = "prod"
SECRET_PATH = "/dns-hermione"
SECRET_NAME = "ALWAYSDATA_API_TOKEN"

class SafeError(Exception):
    pass

def private_process():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    if ctypes.CDLL(None).prctl(4, 0, 0, 0, 0) != 0:
        raise SafeError("Impossible de protéger le processus ; opération refusée.")

def checked(response):
    if not 200 <= response.status_code < 300:
        raise SafeError("Infisical : échec HTTP %d ; contenu masqué." % response.status_code)
    return response.json()

class LANHTTPSConnection(http.client.HTTPSConnection):
    """Connect privately while retaining the canonical TLS SNI and hostname check."""
    def __init__(self, host, address, timeout=20):
        super().__init__(host, timeout=timeout, context=ssl.create_default_context())
        self.address = address

    def connect(self):
        raw = socket.create_connection((self.address, self.port), self.timeout)
        try:
            self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
        except Exception:
            raw.close()
            raise

class LANAdapter(requests.adapters.BaseAdapter):
    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        url = urlsplit(request.url)
        if url.scheme != "https" or url.hostname != "infisical.digiconseil.fr" or url.port not in (None, 443) or verify is not True:
            raise SafeError("Destination/TLS Infisical non autorisés.")
        connection = LANHTTPSConnection(url.hostname, "192.168.1.25", timeout=timeout or 20)
        try:
            headers = dict(request.headers)
            headers["Accept-Encoding"] = "identity"
            connection.request(request.method, url.path + ("?" + url.query if url.query else ""), body=request.body, headers=headers)
            raw = connection.getresponse()
            data = raw.read(2 * 1024 * 1024 + 1)
            if len(data) > 2 * 1024 * 1024:
                raise SafeError("Réponse Infisical trop grande.")
            response = requests.Response()
            response.status_code = raw.status
            response.headers = requests.structures.CaseInsensitiveDict(raw.getheaders())
            response._content = data
            response.encoding = "utf-8"
            response.request = request
            response.url = request.url
            return response
        finally:
            connection.close()

    def close(self):
        pass

class Client:
    def __init__(self, credentials="/srv/projects/.env.infisical"):
        # Read the existing trusted shell-format configuration through a private pipe.
        # No credential appears in argv; no stdout/stderr from source is forwarded.
        shell = ('set +x; source "$1" >/dev/null 2>&1 || exit 1; '
                 'printf "%s\\0" "$INFISICAL_DOMAIN" "$INFISICAL_CLIENT_ID" '
                 '"$INFISICAL_CLIENT_SECRET" "${INFISICAL_CONNECT_IP:-}"')
        r = subprocess.run(["bash", "--noprofile", "--norc", "-c", shell, "credentials", credentials],
                           env={"PATH": "/usr/local/bin:/usr/bin:/bin"}, capture_output=True, check=True, timeout=10)
        domain, client_id, client_secret, connect_ip, _ = r.stdout.decode().split("\0")
        if not all((domain, client_id, client_secret)) or not domain.startswith("https://"):
            raise SafeError("Configuration Infisical HTTPS incomplète ; opération refusée.")
        self.base = domain.rstrip("/")
        self.session = requests.Session()
        self.session.trust_env = False
        if connect_ip:
            if connect_ip != "192.168.1.25" or self.base != "https://infisical.digiconseil.fr":
                raise SafeError("Adresse LAN Infisical inattendue.")
            self.session.mount(self.base + "/", LANAdapter())
        auth = checked(self.session.post(self.base + "/api/v1/auth/universal-auth/login",
                   json={"clientId": client_id, "clientSecret": client_secret}, timeout=20,
                   allow_redirects=False))
        self.session.headers["Authorization"] = "Bearer " + auth["accessToken"]
        self.params = {"workspaceId": PROJECT_ID, "environment": ENVIRONMENT,
                       "secretPath": SECRET_PATH, "type": "shared"}
        self.url = self.base + "/api/v3/secrets/raw/" + SECRET_NAME

    def ensure_folder(self):
        params = {"workspaceId": PROJECT_ID, "environment": ENVIRONMENT, "path": "/"}
        folders = checked(self.session.get(self.base + "/api/v1/folders", params=params,
                                           timeout=20, allow_redirects=False))["folders"]
        if not any(f["name"] == "dns-hermione" for f in folders):
            checked(self.session.post(self.base + "/api/v1/folders",
                      json={**params, "name": "dns-hermione"}, timeout=20, allow_redirects=False))

    def get(self, missing_ok=False):
        r = self.session.get(self.url, params={**self.params, "expandSecretReferences": "false"},
                             timeout=20, allow_redirects=False)
        if missing_ok and r.status_code == 404:
            return None
        return checked(r)["secret"]["secretValue"]

    def store(self, value):
        old = self.get(missing_ok=True)
        method = self.session.post if old is None else self.session.patch
        checked(method(self.url, json={**self.params, "secretValue": value}, timeout=20,
                       allow_redirects=False))
        stored = self.get()
        if stored != value:
            raise SafeError("La relecture ne confirme pas la valeur ; contenu masqué.")
        return len(stored)
