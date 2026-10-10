Bonjour Hermione,

**État au 6 octobre 2026 : intervention terminée.** Maxime confirme la publication HTTPS principal/wildcard, le deuxième passage autonome code 2 accepté et la minuterie suivante au 7 octobre à 03:29 heure de Paris. Pépinière vérifie indépendamment le certificat (échéance 4 janvier 2027), reçoit les deux métriques du job avec `failed=0` et voit l’alerte revenue à l’état normal. Les variables natives sont maintenant activées en production et préproduction ; la recette publique en production passe. Aucune nouvelle action sur Hermione n’est demandée. Les instructions et sources ci-dessous sont conservées pour maintenance, sans réinstallation du bootstrap, du job ou de la gateway.

Maxime autorise la publication des aperçus LibreChat Club sur `artefacts.digiconseil.fr` et `*.artefacts.digiconseil.fr`, avec certificat SAN renouvelé automatiquement par DNS-01 Alwaysdata. Fais l'intervention sur Hermione uniquement, via ses procédures habituelles de déploiement. Aucun changement SVE, pare-feu, Docker global, autre domaine ou méthode ACME des certificats existants. Ne jamais afficher token, identifiants Infisical, clés privées, environnement complet ou logs ACME détaillés.

**Préalable DNS à décider par Maxime.** Le 6 octobre 2026, `d.nic.fr` délègue encore le domaine aux deux Alwaysdata ET `ns1/ns2.sendinblue.com`. Ces derniers répondent REFUSED pour SOA, NS, A existant, TXT et CAA, en UDP/TCP. La zone Alwaysdata ne déclare que ses deux serveurs. Demander à Maxime sa décision de retirer les deux Sendinblue dans les **serveurs DNS du domaine chez OVH** ; n'effectue pas toi-même cette modification. Avant émission de production, revérifier la délégation parent et sa convergence vers Alwaysdata. La seule attente de propagation du TXT ne corrige pas cette délégation.

**Infisical désormais préparé sur Pépinière.** Projet `librechat-artefacts`, UUID `73962094-cbd8-464f-91d6-bea7ba041d8c`, environnement `prod`, chemin `/dns-hermione`, clé `ALWAYSDATA_API_TOKEN` : token présent, longueur 32, aucune valeur transmise dans ce message. Identité dédiée `hermione-artefacts-dns01`, UUID `2ced3438-30a3-43f2-9a53-4a18f6ca59ab`, rôles organisation/projet `no-access`, unique privilège `secrets: describeSecret/readValue` avec égalités exactes sur `prod`, `/dns-hermione` et `ALWAYSDATA_API_TOKEN`. Aucun rôle viewer/member/admin ni permission sur un autre secret. Ne rien provisionner avec une identité globale sur Hermione ; elle n'en possède pas.

**La clé permanente est autorisée, émise et qualifiée.** Sa copie est conservée dans le dossier privé `/hermione-bootstrap`, clé `HERMIONE_UNIVERSAL_AUTH`, lui-même refusé HTTP 403 à Hermione. Tests définitifs avec cette clé : lecture du seul token autorisé (longueur 32), refus 403 d'une autre clé existante, racine, autre environnement, autre projet Club, dossier de remise, création/modification/suppression, administration organisation/identité ; liste filtrée au seul token. Tous les témoins synthétiques ont été supprimés. Les clés temporaires de qualification sont révoquées.

**Remise terminée et contrôlée sur Hermione par Maxime le 6 octobre 2026.** Il a exécuté la commande de `club/HERMIONE-IDENTITE.md` et transmis le résultat : « Hermione Infisical : fichier root:root 0600 installé ; token présent, longueur 32 ; lectures hors périmètre refusées ; HTTPS LAN et TLS vérifiés. » Le fichier `/etc/artefacts-dns/infisical-identity.env` est donc prêt pour ce seul job. Ne pas recréer l’identité, réémettre une clé ou relancer le bootstrap. Utiliser exclusivement ce fichier root privé ; aucune configuration shell Infisical globale n’est nécessaire. Les seuls identifiants dédiés ont été reçus par SSH depuis Pépinière `192.168.1.25:3594`, sans valeur affichée ni fichier temporaire ; aucun identifiant global n’a quitté Pépinière. Ce bootstrap n’a installé ni service ACME ni publication gateway. Tu peux poursuivre les contrôles et la préparation ci-dessous ; l’émission de production reste conditionnée à la décision de Maxime et à la vérification de la délégation DNS décrite plus haut.

**Adresse Infisical : `https://infisical.digiconseil.fr`, connexion LAN directe `192.168.1.25:443`.** Les scripts gardent ce nom pour SNI et vérification de certificat ; `INFISICAL_CONNECT_IP=192.168.1.25` dans le seul fichier privé évite toute modification de DNS système ou `/etc/hosts`. HTTP 200 et TLS vérifiés depuis Pépinière ; la connexion HTTPS LAN et TLS est également confirmée depuis Hermione par la sortie de contrôle transmise par Maxime. API Universal Auth et v3 `secrets/raw`, pas v4 ; jetons d'accès de 300 secondes, connexion fraîche à chaque renouvellement. Toujours utiliser `Client("/etc/artefacts-dns/infisical-identity.env")` ; aucun repli vers un fichier global ou une identité de déploiement. Ne jamais faire d'export CLI de valeurs.

Le profil Alwaysdata `dns@digiconseil.fr` a 2FA et accès au seul service Domaines du seul compte `lightprod.net`. Son token accepte uniquement l'IP source `82.124.220.142`. Aucun accès API Alwaysdata depuis Pépinière. Le token est relu directement du coffre à chaque exécution sur Hermione ; seule sa clé d'identité machine persiste dans le fichier root privé.

**Solution retenue : job acme.sh dédié au seul certificat artefacts.** Il ne change pas le challenge HTTP-01 ou les renouvellements de l'acme-companion existant.

- dépôt privé : `https://git.digiconseil.fr/Digiconseil/librechat-artefacts`, branche `codex/club-artefacts` ; les commits `5c49d70f3` et suivants, la commande et ce message sont publiés ici ;
- dossier `club/dns01/` : `infisical_dns.py`, `renew-hermione.py`, `artefacts-dns-reload`, unité et minuterie systemd ; code complet reproduit en annexe pour transmission sans demander de jeton Git à Hermione ;
- ne récupérer aucun nouveau fichier depuis l'ancien GitHub public ; aucun identifiant Git de Pépinière ne doit être copié sur Hermione ;
- aucune image supplémentaire : le source acme.sh est figé au commit `807da6498377ee5e0cf43a78091f46f12dc59a89`.

1. Sauvegarder les deux fichiers gateway et les seuls éventuels fichiers de certificat artefacts. Repérer le nom réel du conteneur nginx-proxy, son montage `/etc/nginx/certs` et le chemin hôte correspondant, sans afficher son environnement. Vérifier seulement propriétaire root, mode 0600 et réussite du bootstrap pour `/etc/artefacts-dns/infisical-identity.env`, sans lire/afficher son contenu. S'il est absent : arrêter et faire exécuter la commande privée déjà préparée pour Maxime ; ne pas rechercher de config Infisical shell globale. Le dossier de certificats doit rester accessible en écriture au job, et en lecture au proxy, avec clé privée 0600. Aucun changement de propriétaire récursif sur les autres certificats.

2. Installer les trois fichiers Python/reload à `/opt/artefacts-dns/` et le reload à `/usr/local/sbin/artefacts-dns-reload` (0750 root). Installer les sources ACME :

```bash
sudo install -d -m 0755 /opt/artefacts-dns/acme/dnsapi
sudo curl -fsS https://raw.githubusercontent.com/acmesh-official/acme.sh/807da6498377ee5e0cf43a78091f46f12dc59a89/acme.sh -o /opt/artefacts-dns/acme/acme.sh
sudo curl -fsS https://raw.githubusercontent.com/acmesh-official/acme.sh/807da6498377ee5e0cf43a78091f46f12dc59a89/dnsapi/dns_ad.sh -o /opt/artefacts-dns/acme/dnsapi/dns_ad.sh
```

Le job vérifie systématiquement ces SHA-256 avant appel :

```text
acme.sh          c7d68b021cfd6380ea83a82962abde5b484779fee0b97d38681dfa1396bbc8d7
dnsapi/dns_ad.sh  44aa59e1429cb58be59a9ce15441b88db92f83c8a11438fe1b21880c91d52313
```

Prévoir `python3-requests`, `bash`, `curl`, `openssl` sur Hermione. Ne pas lancer `acme.sh --install`, son cron générique ou son auto-upgrade : l'unité dédiée appelle directement le source figé.

3. Créer `/etc/artefacts-dns/runtime.conf`, sans token, avec les trois paramètres **non sensibles**, adaptés aux chemins/noms réellement constatés :

```ini
ARTEFACTS_INFISICAL_CREDENTIALS=/etc/artefacts-dns/infisical-identity.env
ARTEFACTS_PROXY_CERTS_DIR=/chemin/reel/du/montage/certs
ARTEFACTS_NGINX_PROXY_CONTAINER=nom-reel-du-proxy
```

Installer `artefacts-dns.service` et `.timer` dans `/etc/systemd/system/`. Compléter l'unité par `ReadWritePaths=` contenant **le chemin hôte réel du dossier certs** ; conserver ses protections, limites et `StateDirectory=artefacts-dns`. La règle dédiée `artefacts-dns-job` est désormais chargée dans le monitoring central sur Pépinière : groupe `artefacts-dns`, intervalle 30 s, seuil `> 0`, délai 1 min, routage existant `email-o2switch`. Ne pas recréer cette règle ni changer le routage. Le seuil `> 180` du candidat transféré a été corrigé, car la requête ne renvoie que 0, 1 ou 2. Après la publication, les deux métriques sont reçues avec `host="hermione"` et `failed=0` ; la règle est `inactive` avec santé `ok`. En cas de panne ultérieure, vérifier uniquement sur Hermione la publication, via le textfile déjà collecté par Alloy, de `monitoring_artefacts_dns_job_failed` et `monitoring_artefacts_dns_job_last_attempt_timestamp_seconds` ; les séries centrales doivent porter `host="hermione"`. Publier les valeurs réelles de la dernière tentative, sans fabriquer de succès ni publier de logs sensibles. Confirmer leur arrivée sur Pépinière et le retour à l’état normal après un vrai succès. Aucune dépendance ajoutée à `docker.service`. La minuterie quotidienne avec `Persistent=true` reprend au redémarrage ; `OnBootSec=3min` lance aussi un contrôle après démarrage. Un échec conserve les services web en fonctionnement, signale le job en échec et permet la prochaine tentative automatique.

**Sélecteur Alwaysdata vérifié.** Le fournisseur officiel `dns_ad` n'a que `AD_API_KEY`, pas `AD_ACCOUNT`/`AD_Account`. Alwaysdata exige comme utilisateur HTTP Basic : `TOKEN account=lightprod.net`, avec mot de passe vide. Le job construit en mémoire :

```python
AD_API_KEY = quote(token + " account=lightprod.net", safe="")
```

`dns_ad` place cet identifiant encodé dans son URL ; curl le décode avant de construire Basic. Test local avec faux token : identifiant reçu exactement `TOKEN account=lightprod.net:`. Aucun paramètre `account` ajouté à la query string. Ne pas utiliser l'email du profil comme compte cible. L'accès réel à `domain/` doit voir `digiconseil.fr` depuis Hermione et être refusé pour les ressources hors permission ; vérifier en lecture seule sans publier la réponse. Le test synthétique ne prouve pas les droits réels du token.

Le job désactive les sorties ACME, n'utilise ni debug ni trace HTTP, relit le token Infisical à chaque passage et supprime la copie `AD_API_KEY` que dns_ad tente d'enregistrer dans `account.conf`, avant et après chaque exécution. L'état ACME privé est dans `/var/lib/artefacts-dns` (0700), hors Git ; les clés ACME/certificat doivent y persister. Pas de token dans compose, commande shell tapée, fichier versionné ou journal. Sérialiser ce seul job, et ne pas faire gérer `_acme-challenge.artefacts.digiconseil.fr` par un second client ACME concurrent : dns_ad supprime le premier TXT de ce nom lors du nettoyage.

4. Après token présent, délégation corrigée/contrôlée et identité de lecture prête, vérifier les unités puis lancer seulement ce job :

```bash
sudo systemctl daemon-reload
sudo systemctl start artefacts-dns.service
sudo systemctl enable --now artefacts-dns.timer
```

Première exécution : émission Let's Encrypt DNS-01, SAN principal + wildcard, clé ec-256, attente TXT 300 s, installation `artefacts.digiconseil.fr.key/.crt` dans le montage certs ; validation nginx et reload gracieux. Exécutions suivantes : `--renew` sans force, renouvellement seulement lorsque dû, réinstallation/reload pour récupérer aussi un éventuel échec d'installation précédent. Le code 2 de renouvellement différé est accepté. Vérifier une deuxième exécution sans ressaisie de secret et la prochaine échéance de la minuterie. Le cycle automatique est entièrement prévu par ces fichiers ; il doit être qualifié sur Hermione, et ne dépendra ensuite d'aucune action de Maxime. Conserver l'alerte de certificat expirant pour détecter une panne durable de DNS/Infisical/Alwaysdata.

5. Publication : sur Pépinière, le statique `librechat-artefacts` fonctionne déjà sur le seul réseau `librechat-artefacts-net` internal, sans port publié. Sa version attendue est `PROD-1741371360-5877b84`. Les DNS A principal et wildcard répondent `82.124.220.142`, TTL 300 ; ne pas ajouter d'AAAA sans route IPv6 validée. Sur Hermione, dans `/home/digiconseil/projects/gateways/docker-compose.yml`, ajouter seulement `artefacts.digiconseil.fr,*.artefacts.digiconseil.fr` au `VIRTUAL_HOST` de `pepiniere-gateway`, préserver toutes les entrées et son `LETSENCRYPT_HOST` actuel. **Ne pas ajouter ces deux noms au challenge HTTP-01 existant, ni définir un CERT_NAME global sur la gateway multi-domaines.** Le nom de fichier parent `artefacts.digiconseil.fr.crt/.key` permet à nginx-proxy sa sélection native pour le principal et le wildcard ; vérifier sur la version effective de ton proxy.

Dans `pepiniere/nginx.conf`, ajouter le serveur ci-dessous. Adapter seulement son `listen` au port interne existant, et conserver les règles actuelles de confiance X-Forwarded :

```nginx
server {
    listen 80;
    server_name artefacts.digiconseil.fr *.artefacts.digiconseil.fr;
    location / {
        proxy_pass https://192.168.1.25:443;
        proxy_ssl_server_name on;
        proxy_ssl_name agence.digiconseil.fr;
        proxy_ssl_verify on;
        proxy_ssl_trusted_certificate /etc/ssl/certs/ca-certificates.crt;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Cookie "";
        proxy_set_header Authorization "";
        proxy_hide_header Set-Cookie;
        proxy_read_timeout 60s;
    }
}
```

L'amont répond déjà en TLS vérifié via SNI agence, Host artefacts conservé, à `192.168.1.25:443`. Surveiller aussi le renouvellement de ce certificat amont ; ne jamais désactiver `proxy_ssl_verify`. Préserver CSP/CORS, aucune authentification Club ni cookie, aucun X-Frame-Options DENY/SAMEORIGIN. Rejeter les Host étrangers. Aucun fichier membre envoyé au service statique : rendu navigateur. Valider puis recréer **uniquement pepiniere-gateway** via sa procédure habituelle. Reload nginx gracieux après certificat, aucun redémarrage Docker ou recréation du frontal/companion.

6. Contrôles sans `-k`, puis témoin d'une autre origine aléatoire :

```bash
curl -fsS https://artefacts.digiconseil.fr/version.txt
curl -fsS https://fixture-preview.artefacts.digiconseil.fr/__csb_relay/
curl -fsSI -H 'Origin: https://librechat.digiconseil.fr' https://fixture-preview.artefacts.digiconseil.fr/__csb_relay/
```

Confirmer TLS/chaîne/SAN, CORS exact prod et préprod, CSP conservée, absence de Set-Cookie, préflight CORS, un autre Host aléatoire ; monitoring, LibreChat, préproduction et deux autres domaines toujours fonctionnels. Retourner seulement métadonnées de certificat, statuts, échéance minuterie et résultat de deuxième exécution. Aucun secret ni environnement. Pépinière activera ensuite les variables natives avec sa porte HTTPS/empreintes d'assets et recettera Excel, Word, HTML dans les trois moteurs.

**Retour arrière avant intervention :** sauvegarder les deux seuls fichiers gateway et les fichiers artefacts existants ; en cas d'échec restaurer seulement ceux-ci, recréer pepiniere-gateway, puis contrôler les autres domaines. Désactiver/arrêter uniquement `artefacts-dns.timer` et `.service`, retirer uniquement cette publication/certificat si nouveau. Garder le répertoire d'état privé pour rétablissement ; ne retirer aucune autre minuterie, certificat, règle réseau ou entrée DNS partagée. Le retrait du secret ou de son identité demande de vérifier qu'ils n'ont aucun autre consommateur. Le repli de l'aperçu LibreChat se fait sur Pépinière avant retrait de publication, selon `club/ROLLBACK.md`.

Sources vérifiées : [Infisical, privilèges supplémentaires](https://infisical.com/docs/documentation/platform/access-controls/additional-privileges), [OpenSSH, KnownHostsCommand](https://man.openbsd.org/ssh_config#KnownHostsCommand), [Alwaysdata, compte dans HTTP Basic](https://help.alwaysdata.com/en/docs/development/api/usage/), [dns_ad figé](https://github.com/acmesh-official/acme.sh/blob/807da6498377ee5e0cf43a78091f46f12dc59a89/dnsapi/dns_ad.sh), [acme.sh renouvellement/installation](https://github.com/acmesh-official/acme.sh), [nginx-proxy certificats wildcard](https://github.com/nginx-proxy/nginx-proxy/blob/main/docs/README.md#wildcard-certificates).


---

Annexe — fichiers à installer sur Hermione, également versionnés dans le dépôt Gitea privé. Ils sont reproduits ici pour la seule transmission demandée à Hermione, sans exiger un accès Git à cet hôte. Aucun token réel dans ces fichiers. Ne pas publier cette annexe dans un dépôt public. Les deux sources ACME sont téléchargées séparément depuis les URL figées ci-dessus.

### /opt/artefacts-dns/infisical_dns.py

```python
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
```

### /opt/artefacts-dns/renew-hermione.py

```python
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
```

### /usr/local/sbin/artefacts-dns-reload

```sh
#!/bin/sh
set -eu
# Container name is a non-secret setting inherited from the ACME job.
: "${ARTEFACTS_NGINX_PROXY_CONTAINER:?Hermione must supply the existing proxy name}"
/usr/bin/docker exec "$ARTEFACTS_NGINX_PROXY_CONTAINER" nginx -t >/dev/null 2>&1
/usr/bin/docker exec "$ARTEFACTS_NGINX_PROXY_CONTAINER" nginx -s reload >/dev/null 2>&1
```

### /etc/systemd/system/artefacts-dns.service

```ini
[Unit]
Description=Certificat artefacts Club DNS-01 Alwaysdata (Hermione uniquement)
Wants=network-online.target
After=network-online.target docker.service

[Service]
Type=oneshot
User=root
UMask=0077
Environment=ARTEFACTS_DNS_EXECUTION_HOST=hermione
EnvironmentFile=/etc/artefacts-dns/runtime.conf
ExecStart=/usr/bin/python3 -B /opt/artefacts-dns/renew-hermione.py
StateDirectory=artefacts-dns
StateDirectoryMode=0700
TimeoutStartSec=35min
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
# Hermione must add the resolved proxy certificate directory as ReadWritePaths.
ReadWritePaths=/var/lib/artefacts-dns
CapabilityBoundingSet=
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX
MemoryMax=192M
CPUQuota=50%
TasksMax=64
```

### /etc/systemd/system/artefacts-dns.timer

```ini
[Unit]
Description=Renouvellement automatique du seul certificat artefacts Club

[Timer]
OnBootSec=3min
OnCalendar=*-*-* 03:17:00
RandomizedDelaySec=15min
Persistent=true
Unit=artefacts-dns.service

[Install]
WantedBy=timers.target
```
