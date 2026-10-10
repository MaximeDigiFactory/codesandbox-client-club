#!/usr/bin/env python3
"""Private Gitea HTTPS publication using monitoring credential-store, read-only."""
import ctypes, hashlib, os, resource, shlex, subprocess, sys
from pathlib import Path
import requests
BASE = "https://git.digiconseil.fr"
URL = BASE + "/Digiconseil/librechat-artefacts.git"
API = BASE + "/api/v1/repos/Digiconseil/librechat-artefacts"
ROOT = Path(__file__).resolve().parents[1]
BRANCH = "codex/club-artefacts"

class Failure(Exception):
    pass

def git(args, env=None):
    r = subprocess.run(["git", "-C", str(ROOT)] + args, env=env,
                       capture_output=True, text=True, timeout=1200)
    if r.returncode:
        raise Failure("Git a échoué (code %d) ; sortie masquée." % r.returncode)
    return r.stdout

def checked(r):
    if not 200 <= r.status_code < 300:
        raise Failure("Gitea HTTP %d ; réponse masquée." % r.status_code)
    return r.json()

def ensure_repository(session):
    r = session.get(API, timeout=30, allow_redirects=False)
    if r.status_code == 404:
        checked(session.post(BASE + "/api/v1/orgs/Digiconseil/repos",
             json={"name": "librechat-artefacts", "private": True, "auto_init": False,
                   "default_branch": BRANCH,
                   "description": "Aperçus LibreChat Club et documentation de publication"},
             timeout=30, allow_redirects=False))
        r = session.get(API, timeout=30, allow_redirects=False)
    repo = checked(r)
    if repo.get("private") is not True or repo.get("clone_url") != URL:
        raise Failure("Destination non privée ou URL inattendue : push refusé.")
    if not repo.get("permissions", {}).get("push"):
        raise Failure("Le compte n'a pas le droit de pousser ce dépôt.")
    return repo

def existing_credentials():
    # Use exactly monitoring's credential-store backend, get action only.
    result = subprocess.run(["git", "-c", "safe.directory=/srv/projects/monitoring",
        "-C", "/srv/projects/monitoring", "config", "--local", "--get", "credential.helper"],
        capture_output=True, text=True, check=True)
    args = shlex.split(result.stdout.strip())
    if not args or args[0] != "store":
        raise Failure("Le gestionnaire monitoring n'est plus credential-store : opération refusée.")
    path = next((x.split("=", 1)[1] for x in args[1:] if x.startswith("--file=")), None)
    if path is None and "--file" in args:
        path = args[args.index("--file") + 1]
    if not path:
        raise Failure("Fichier d'identifiants monitoring non identifié.")
    file = Path(path)
    before = hashlib.sha256(file.read_bytes()).digest()
    result = subprocess.run(["git", "credential-store", "--file=" + path, "get"],
        input="protocol=https\nhost=git.digiconseil.fr\n\n", capture_output=True, text=True, check=True)
    values = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
    if not values.get("username") or not values.get("password"):
        raise Failure("Identifiant HTTPS Gitea absent du gestionnaire monitoring.")
    return values, file, before

def main():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    if ctypes.CDLL(None).prctl(4, 0, 0, 0, 0):
        raise Failure("Protection du processus indisponible.")
    if git(["status", "--porcelain"]).strip():
        raise Failure("Dépôt local modifié : committer les seuls changements voulus avant publication.")
    if git(["branch", "--show-current"]).strip() != BRANCH:
        raise Failure("Branche attendue : " + BRANCH)
    git(["merge-base", "--is-ancestor", "5c49d70f3", "HEAD"])
    values, credential_file, credential_digest = existing_credentials()
    token = values["password"]
    session = requests.Session(); session.trust_env = False
    session.headers["Authorization"] = "token " + token
    repo = ensure_repository(session)
    print("Destination vérifiée : Digiconseil/librechat-artefacts, privée, écriture autorisée.", flush=True)
    remote = subprocess.run(["git", "-C", str(ROOT), "remote", "get-url", "gitea"],
                            capture_output=True, text=True)
    if remote.returncode:
        git(["remote", "add", "gitea", URL])
    elif remote.stdout.strip() != URL:
        raise Failure("Le remote gitea existant cible une autre URL.")
    # Git uses the SAME store file/backend, but ignores store/erase actions.
    # Thus the old plaintext credential file is never rewritten by approval.
    readonly_helper = ("!f() { if [ \"$1\" = get ]; then git credential-store --file="
                       + shlex.quote(str(credential_file)) + " get; fi; }; f")
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
           "HOME": os.environ.get("HOME", "/home/maxime"),
           "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_CONFIG_COUNT": "4",
           "GIT_CONFIG_KEY_0": "credential.helper", "GIT_CONFIG_VALUE_0": "",
           "GIT_CONFIG_KEY_1": "credential.helper", "GIT_CONFIG_VALUE_1": readonly_helper,
           "GIT_CONFIG_KEY_2": "http.sslVerify", "GIT_CONFIG_VALUE_2": "true",
           "GIT_CONFIG_KEY_3": "http.followRedirects", "GIT_CONFIG_VALUE_3": "false",
           "GIT_TERMINAL_PROMPT": "0", "GIT_ASKPASS": "/bin/false"}
    refs = dict(line.split(" ", 1) for line in git(["for-each-ref", "--format=%(refname) %(objectname)",
                                                   "refs/heads/", "refs/tags/"]).splitlines())
    git(["push", "--atomic", "gitea"] + [r + ":" + r for r in refs], env)
    published = {ref:sha for line in git(["ls-remote", "gitea"], env).splitlines()
                 for sha,ref in [line.split("\t", 1)]}
    if any(published.get(ref) != sha for ref,sha in refs.items()):
        raise Failure("Les références distantes ne correspondent pas à toutes les références locales.")
    # New repository default is the deployment branch; repair after first push if needed.
    repo = checked(session.get(API, timeout=30, allow_redirects=False))
    if repo.get("default_branch") != BRANCH:
        checked(session.patch(API, json={"default_branch": BRANCH}, timeout=30, allow_redirects=False))
    final = checked(session.get(API, timeout=30, allow_redirects=False))
    if final.get("private") is not True or final.get("default_branch") != BRANCH:
        raise Failure("Contrôle final confidentialité/branche incomplet.")
    git(["config", "remote.pushDefault", "gitea"])
    git(["config", "branch." + BRANCH + ".pushRemote", "gitea"])
    if hashlib.sha256(credential_file.read_bytes()).digest() != credential_digest:
        raise Failure("Le fichier d'identifiants a changé extérieurement pendant l'opération.")
    print("Push HTTPS vérifié : %d références ; HEAD %s ; dépôt privé ; branche %s."
          % (len(refs), git(["rev-parse", "--short", "HEAD"]).strip(), BRANCH))
    print("Origine GitHub conservée ; push par défaut sur Gitea ; fichier de jeton existant inchangé.")

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("Opération annulée ; aucun jeton affiché.", file=sys.stderr); sys.exit(1)
    except Failure as e:
        print(str(e), file=sys.stderr); sys.exit(1)
    except Exception:
        print("Échec réseau/terminal ; détails masqués. Vérifier l'état du dépôt Gitea avant reprise.",
              file=sys.stderr); sys.exit(1)
