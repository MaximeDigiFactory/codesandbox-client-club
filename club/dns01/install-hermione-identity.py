#!/usr/bin/env python3
"""In-memory installer received over host-key-pinned SSH. No temporary files."""
import ctypes, http.client, json, os, re, resource, shlex, socket, ssl, stat
from pathlib import Path
from urllib.parse import urlencode
IDENTITY_ID = "2ced3438-30a3-43f2-9a53-4a18f6ca59ab"
PROJECT_ID = "73962094-cbd8-464f-91d6-bea7ba041d8c"
TARGET = Path("/etc/artefacts-dns/infisical-identity.env")

class LANConnection(http.client.HTTPSConnection):
    def __init__(self):
        super().__init__("infisical.digiconseil.fr", timeout=20, context=ssl.create_default_context())
    def connect(self):
        raw = socket.create_connection(("192.168.1.25", 443), self.timeout)
        try:
            self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
        except Exception:
            raw.close()
            raise

def request(method, path, body=None, token=None):
    conn = LANConnection()
    headers = {"Content-Type": "application/json", "Accept-Encoding": "identity"}
    if token:
        headers["Authorization"] = "Bearer " + token
    try:
        conn.request(method, path, body=json.dumps(body) if body is not None else None, headers=headers)
        r = conn.getresponse()
        raw = r.read(1048577)
        if len(raw) > 1048576:
            raise RuntimeError("Réponse trop grande.")
        return r.status, json.loads(raw) if raw else {}
    finally:
        conn.close()

def verify(credentials):
    status, auth = request("POST", "/api/v1/auth/universal-auth/login", credentials)
    if status != 200:
        raise RuntimeError("Connexion refusée.")
    import base64
    payload = auth["accessToken"].split(".")[1]
    claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    if claims.get("identityId") != IDENTITY_ID:
        raise RuntimeError("Identité reçue inattendue.")
    params = {"workspaceId": PROJECT_ID, "environment": "prod", "secretPath": "/dns-hermione", "type": "shared", "expandSecretReferences": "false"}
    status, data = request("GET", "/api/v3/secrets/raw/ALWAYSDATA_API_TOKEN?" + urlencode(params), token=auth["accessToken"])
    if status != 200 or not data.get("secret", {}).get("secretValue"):
        raise RuntimeError("Token absent ou lecture refusée.")
    length = len(data["secret"]["secretValue"])
    for key, path in [("ALWAYSDATA_API_TOKEN", "/"), ("HERMIONE_UNIVERSAL_AUTH", "/hermione-bootstrap"), ("HERMIONE_UNAUTHORIZED_KEY", "/dns-hermione")]:
        status, _ = request("GET", "/api/v3/secrets/raw/" + key + "?" + urlencode({**params, "secretPath": path}), token=auth["accessToken"])
        if status != 403:
            raise RuntimeError("Refus hors périmètre non confirmé.")
    return length

def main(credentials):
    if os.geteuid() != 0:
        raise RuntimeError("Root requis.")
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    if ctypes.CDLL(None).prctl(4, 0, 0, 0, 0):
        raise RuntimeError("Protection du processus impossible.")
    os.umask(0o077)
    if set(credentials) != {"clientId", "clientSecret"}:
        raise RuntimeError("Format inattendu.")
    if not re.fullmatch(r"[A-Za-z0-9_-]{16,128}", credentials["clientId"]) or not re.fullmatch(r"[A-Za-z0-9._~+/=-]{16,512}", credentials["clientSecret"]):
        raise RuntimeError("Identifiants invalides.")
    # Verify before creating the sole persistent credential file.
    verify(credentials)
    if TARGET.parent.is_symlink():
        raise RuntimeError("Dossier symbolique refusé.")
    TARGET.parent.mkdir(mode=0o700, exist_ok=True)
    ds = TARGET.parent.stat()
    if ds.st_uid != 0 or ds.st_mode & 0o022:
        raise RuntimeError("Dossier de credentials non protégé.")
    values = {"INFISICAL_DOMAIN": "https://infisical.digiconseil.fr", "INFISICAL_CONNECT_IP": "192.168.1.25",
              "INFISICAL_CLIENT_ID": credentials["clientId"], "INFISICAL_CLIENT_SECRET": credentials["clientSecret"]}
    contents = "".join(key + "=" + shlex.quote(value) + "\n" for key, value in values.items()).encode()
    created = False
    try:
        fd = os.open(TARGET, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        created = True
        try:
            remaining = contents
            while remaining:
                remaining = remaining[os.write(fd, remaining):]
            os.fsync(fd)
        finally:
            os.close(fd)
    except FileExistsError:
        pass
    try:
        fd = os.open(TARGET, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            metadata = os.fstat(fd)
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_uid != 0 or metadata.st_gid != 0 or stat.S_IMODE(metadata.st_mode) != 0o600 or metadata.st_nlink != 1:
                raise RuntimeError("Fichier existant non privé root:root 0600.")
            if os.read(fd, 4096) != contents:
                raise RuntimeError("Un autre fichier existe; remplacement refusé.")
        finally:
            os.close(fd)
        length = verify(credentials)
    except Exception:
        if created:
            TARGET.unlink()
        raise
    print("Hermione Infisical : fichier root:root 0600 installé ; token présent, longueur %d ; lectures hors périmètre refusées ; HTTPS LAN et TLS vérifiés." % length)

if __name__ == "__main__":
    try:
        main(IDENTITY_CREDENTIALS)
    except Exception:
        print("Installation Hermione refusée ou vérification échouée; aucun identifiant ni token affiché.")
        raise SystemExit(1)
