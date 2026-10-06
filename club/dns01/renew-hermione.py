#!/usr/bin/env python3
"""Hermione-only ACME job; never run this on Pepiniere."""
import fcntl, hashlib, os, subprocess, sys
from pathlib import Path
from urllib.parse import quote
sys.dont_write_bytecode = True
from infisical_dns import Client, SafeError, private_process
ACME_SOURCE_DIR = Path("/opt/artefacts-dns/acme")
STATE = Path("/var/lib/artefacts-dns")
DOMAIN = "artefacts.digiconseil.fr"
LOCKS = {
    "acme.sh": "c7d68b021cfd6380ea83a82962abde5b484779fee0b97d38681dfa1396bbc8d7",
    "dnsapi/dns_ad.sh": "44aa59e1429cb58be59a9ce15441b88db92f83c8a11438fe1b21880c91d52313",
}

def purge_saved_key():
    # dns_ad saves its credential; remove it before/after each run so rotation is
    # picked up from Infisical and no old value overrides the fresh environment.
    path = STATE / "account.conf"
    if path.exists():
        lines = path.read_text().splitlines(keepends=True)
        path.write_text("".join(x for x in lines if not x.startswith(("AD_API_KEY=", "SAVED_AD_API_KEY="))))
        path.chmod(0o600)

def invoke(args, env, accept_skip=False):
    cmd = ["/bin/sh", str(ACME_SOURCE_DIR / "acme.sh"), "--home", str(ACME_SOURCE_DIR), "--config-home", str(STATE),
           "--server", "letsencrypt", "--no-color"] + args
    r = subprocess.run(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=900)
    if r.returncode != 0 and not (accept_skip and r.returncode == 2):
        raise SafeError("ACME a échoué ; sortie privée non publiée.")
    return r.returncode

def main():
    private_process()
    if os.environ.get("ARTEFACTS_DNS_EXECUTION_HOST") != "hermione":
        raise SafeError("Exécution autorisée uniquement sur Hermione.")
    os.umask(0o077)
    for name, expected in LOCKS.items():
        if hashlib.sha256((ACME_SOURCE_DIR / name).read_bytes()).hexdigest() != expected:
            raise SafeError("Source ACME différente du commit figé.")
    # State directory is prepared by StateDirectory= of the systemd unit.
    with (STATE / "job.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        client = Client(os.environ["ARTEFACTS_INFISICAL_CREDENTIALS"])
        value = client.get()
        if not value or not value.isascii() or any(c.isspace() for c in value) or ":" in value:
            raise SafeError("Secret absent ou format invalide.")
        env = {"PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
               "HOME": os.environ.get("HOME", "/root"),
               "ARTEFACTS_NGINX_PROXY_CONTAINER": os.environ["ARTEFACTS_NGINX_PROXY_CONTAINER"],
               "AD_API_KEY": quote(value + " account=lightprod.net", safe="")}
        purge_saved_key()
        try:
            installed = (STATE / (DOMAIN + "_ecc") / (DOMAIN + ".cer")).exists()
            if installed:
                invoke(["--renew", "-d", DOMAIN, "--ecc"], env, accept_skip=True)
            else:
                invoke(["--issue", "--dns", "dns_ad", "--dnssleep", "300", "-d", DOMAIN,
                        "-d", "*." + DOMAIN, "--keylength", "ec-256", "--email", "dns@digiconseil.fr"], env)
            # Also reinstalls/reloads on non-renewal days: idempotent recovery if
            # issuance succeeded but installation/reload failed on a previous run.
            certs = Path(os.environ["ARTEFACTS_PROXY_CERTS_DIR"])
            invoke(["--install-cert", "-d", DOMAIN, "--ecc", "--key-file", str(certs / (DOMAIN + ".key")),
                    "--fullchain-file", str(certs / (DOMAIN + ".crt")), "--reloadcmd",
                    "/usr/local/sbin/artefacts-dns-reload"], env)
        finally:
            purge_saved_key()
    print("Artefacts DNS-01: secret lu depuis Infisical; certificat installé; nginx rechargé.")

if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("Artefacts DNS-01: échec; certificat actuel conservé; aucun secret affiché.", file=sys.stderr)
        sys.exit(1)
