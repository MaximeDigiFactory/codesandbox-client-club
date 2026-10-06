#!/usr/bin/env python3
"""Private SSH stream to Hermione's installer. Never execute directly/display stdout."""
import json, os, sys
from pathlib import Path
from infisical_dns import Client, checked, private_process

def main():
    private_process()
    connection = os.environ.get("SSH_CONNECTION", "").split()
    if len(connection) != 4 or connection[0] != "192.168.1.50" or sys.stdout.isatty():
        raise RuntimeError("Remise réservée au tube SSH depuis Hermione.")
    client = Client()
    data = checked(client.session.get(client.base + "/api/v3/secrets/raw/HERMIONE_UNIVERSAL_AUTH",
        params={**client.params, "secretPath": "/hermione-bootstrap", "expandSecretReferences": "false"}, timeout=20, allow_redirects=False))
    credentials = json.loads(data["secret"]["secretValue"])
    if set(credentials) != {"clientId", "clientSecret"}:
        raise RuntimeError("Identifiants inattendus.")
    # This stdout is an encrypted SSH channel and must be piped directly to root.
    json.dump({"installer": Path(__file__).with_name("install-hermione-identity.py").read_text(),
               "credentials": credentials}, sys.stdout, separators=(",", ":"))

if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("Remise Hermione refusée/indisponible; détails masqués.", file=sys.stderr)
        sys.exit(1)
