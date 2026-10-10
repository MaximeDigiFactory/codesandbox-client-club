#!/usr/bin/env python3
"""AUTHORIZED PROVISIONING ONLY: store/qualify the scoped identity in Infisical."""
import json, sys, uuid
import requests
from infisical_dns import Client, SafeError, checked, private_process, PROJECT_ID
IDENTITY_ID = "2ced3438-30a3-43f2-9a53-4a18f6ca59ab"
BOOTSTRAP_PATH = "/hermione-bootstrap"
BOOTSTRAP_KEY = "HERMIONE_UNIVERSAL_AUTH"
EXPECTED = [{"subject": "secrets", "action": ["describeSecret", "readValue"],
             "conditions": {"environment": {"$eq": "prod"},
                            "secretPath": {"$eq": "/dns-hermione"},
                            "secretName": {"$eq": "ALWAYSDATA_API_TOKEN"}}}]

def main():
    private_process()
    admin = Client()
    org = "d77da6c1-17f2-460b-a1d4-77a294890bf9"
    org_memberships = checked(admin.session.get(admin.base + "/api/v1/identities", params={"orgId": org, "limit": 100}, timeout=20, allow_redirects=False))["identities"]
    membership = next(x for x in org_memberships if x["identityId"] == IDENTITY_ID)
    project_membership = checked(admin.session.get(admin.base + "/api/v2/workspace/" + PROJECT_ID + "/identity-memberships/" + IDENTITY_ID, timeout=20, allow_redirects=False))["identityMembership"]
    if membership["role"] != "no-access" or len(project_membership["roles"]) != 1 or project_membership["roles"][0]["role"] != "no-access":
        raise SafeError("Rôles de base trop larges; émission interdite.")
    listing = checked(admin.session.get(admin.base + "/api/v2/identity-project-additional-privilege",
        params={"identityId": IDENTITY_ID, "projectId": PROJECT_ID}, timeout=20, allow_redirects=False))["privileges"]
    if len(listing) != 1:
        raise SafeError("Nombre de privilèges inattendu.")
    grant = checked(admin.session.get(admin.base + "/api/v2/identity-project-additional-privilege/" + listing[0]["id"], timeout=20, allow_redirects=False))["privilege"]
    actual = [{k: x[k] for k in ("subject", "action", "conditions")} for x in grant["permissions"]]
    if actual != EXPECTED or any(x.get("inverted", False) for x in grant["permissions"]):
        raise SafeError("Le privilège diffère de la lecture d'une seule clé.")
    params = {"workspaceId": PROJECT_ID, "environment": "prod", "path": "/"}
    folders = checked(admin.session.get(admin.base + "/api/v1/folders", params=params, timeout=20, allow_redirects=False))["folders"]
    if not any(x["name"] == "hermione-bootstrap" for x in folders):
        checked(admin.session.post(admin.base + "/api/v1/folders", json={**params, "name": "hermione-bootstrap"}, timeout=20, allow_redirects=False))
    bp = {**admin.params, "secretPath": BOOTSTRAP_PATH, "expandSecretReferences": "false"}
    bu = admin.base + "/api/v3/secrets/raw/" + BOOTSTRAP_KEY
    existing = admin.session.get(bu, params=bp, timeout=20, allow_redirects=False)
    if existing.status_code == 404:
        ua = checked(admin.session.get(admin.base + "/api/v1/auth/universal-auth/identities/" + IDENTITY_ID, timeout=20, allow_redirects=False))["identityUniversalAuth"]
        issued = checked(admin.session.post(admin.base + "/api/v1/auth/universal-auth/identities/" + IDENTITY_ID + "/client-secrets",
            json={"description": "Hermione DNS-01; remise SSH privée; renouvellement autonome", "ttl": 0, "numUsesLimit": 0}, timeout=20, allow_redirects=False))
        credentials = {"clientId": ua["clientId"], "clientSecret": issued["clientSecret"]}
        try:
            checked(admin.session.post(bu, json={**admin.params, "secretPath": BOOTSTRAP_PATH,
                "secretValue": json.dumps(credentials, separators=(",", ":"))}, timeout=20, allow_redirects=False))
        except Exception:
            response = admin.session.post(admin.base + "/api/v1/auth/universal-auth/identities/" + IDENTITY_ID +
                "/client-secrets/" + issued["clientSecretData"]["id"] + "/revoke", timeout=20, allow_redirects=False)
            if not response.ok:
                raise SafeError("Enregistrement échoué; révocation non confirmée.")
            raise SafeError("Enregistrement échoué; identifiant révoqué.")
    else:
        checked(existing)
    credentials = json.loads(checked(admin.session.get(bu, params=bp, timeout=20, allow_redirects=False))["secret"]["secretValue"])
    restricted = requests.Session(); restricted.trust_env = False
    login = checked(restricted.post(admin.base + "/api/v1/auth/universal-auth/login", json=credentials, timeout=20, allow_redirects=False))
    restricted.headers["Authorization"] = "Bearer " + login["accessToken"]
    value = checked(restricted.get(admin.url, params={**admin.params, "expandSecretReferences": "false"}, timeout=20, allow_redirects=False))["secret"]["secretValue"]
    if value != admin.get() or not value:
        raise SafeError("Lecture autorisée non confirmée.")
    print("Lecture autorisée : token présent, longueur %d." % len(value))
    canary_key = "HERMIONE_ACL_CANARY_" + uuid.uuid4().hex
    create_key = canary_key + "_CREATE"
    canary_url = admin.base + "/api/v3/secrets/raw/" + canary_key
    checked(admin.session.post(canary_url, json={**admin.params, "secretValue": "synthetic-nonsecret-canary"}, timeout=20, allow_redirects=False))
    try:
        probes = [
            ("autre clé existante même dossier", "GET", canary_url, admin.params, None),
            ("dossier racine", "GET", admin.url, {**admin.params, "secretPath": "/"}, None),
            ("autre environnement", "GET", admin.url, {**admin.params, "environment": "dev", "secretPath": "/"}, None),
            ("dossier de remise", "GET", bu, bp, None),
            ("écriture", "PATCH", canary_url, None, {**admin.params, "secretValue": "synthetic-changed-canary"}),
            ("suppression", "DELETE", canary_url, None, admin.params),
            ("création", "POST", admin.base + "/api/v3/secrets/raw/" + create_key, None, {**admin.params, "secretValue": "synthetic-created-canary"}),
            ("administration organisation", "GET", admin.base + "/api/v1/identities", {"orgId": "d77da6c1-17f2-460b-a1d4-77a294890bf9"}, None),
            ("gestion clé d'identité", "GET", admin.base + "/api/v1/auth/universal-auth/identities/" + IDENTITY_ID + "/client-secrets", None, None),
        ]
        workspaces = checked(admin.session.get(admin.base + "/api/v1/workspace", timeout=20, allow_redirects=False))["workspaces"]
        other = next(w["id"] for w in workspaces if w["id"] != PROJECT_ID and w.get("name") == "librechat-codeapi")
        probes.append(("autre projet Club", "GET", admin.url, {**admin.params, "workspaceId": other, "secretPath": "/"}, None))
        for label, method, url, params, body in probes:
            response = restricted.request(method, url, params=params, json=body, timeout=20, allow_redirects=False)
            print("Refus %s : HTTP %d." % (label, response.status_code))
            if response.status_code != 403:
                raise SafeError("Refus strict non confirmé; remise interdite.")
        visible = checked(restricted.get(admin.base + "/api/v3/secrets/raw", params={**admin.params, "expandSecretReferences": "false", "include_imports": "false"}, timeout=20, allow_redirects=False))["secrets"]
        if [x["secretKey"] for x in visible] != ["ALWAYSDATA_API_TOKEN"]:
            raise SafeError("Liste de secrets trop large; remise interdite.")
        current = checked(admin.session.get(canary_url, params=admin.params, timeout=20, allow_redirects=False))["secret"]["secretValue"]
        if current != "synthetic-nonsecret-canary":
            raise SafeError("Témoin altéré; remise interdite.")
    finally:
        for key in [canary_key, create_key]:
            response = admin.session.delete(admin.base + "/api/v3/secrets/raw/" + key, json=admin.params, timeout=20, allow_redirects=False)
            if response.status_code not in (200, 404):
                raise SafeError("Nettoyage du témoin non confirmé.")
    print("Qualification stricte réussie. Identifiants uniquement en coffre, aucun fichier de secret créé.")

if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("Qualification échouée; détails et identifiants masqués.", file=sys.stderr)
        sys.exit(1)
