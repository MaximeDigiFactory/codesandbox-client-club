# Identité Infisical Hermione — remise sécurisée

État au 6 octobre 2026 : identité et ACL créées ; émission de clé et dossier de remise proposés, en attente de validation explicite. **Ne pas lancer cette commande avant confirmation de préparation de la clé.**

Identité `hermione-artefacts-dns01`, UUID `2ced3438-30a3-43f2-9a53-4a18f6ca59ab`. Organisation et projet : `no-access`. Seul privilège : `secrets`, actions `describeSecret` et `readValue`, avec égalités exactes `environment=prod`, `secretPath=/dns-hermione`, `secretName=ALWAYSDATA_API_TOKEN`. Aucun rôle viewer/member/admin, aucun droit de modification ni de gestion des identités. Jetons d'accès limités à 300 secondes. La clé client permanente est proposée pour permettre les renouvellements sans intervention humaine ; elle sera révocable côté Infisical.

Adresse : `https://infisical.digiconseil.fr`, connexion directe à `192.168.1.25:443` avec ce nom conservé pour SNI et vérification du certificat. Réponse `/api/status` HTTP 200 sur le LAN, TLS vérifié depuis Pépinière. Aucun `/etc/hosts` ni proxy modifié. La commande ci-dessous vérifiera réellement cet accès depuis Hermione.

## Une commande sur Hermione

Exécuter depuis le compte habituel de Maxime, disposant de sudo sur Hermione et de son accès SSH à `maxime@192.168.1.25`. Les éventuelles saisies des mots de passe sudo et SSH sont masquées par leurs outils ; aucune saisie/copie manuelle d'un secret Infisical et aucune interface Infisical nécessaire. L'accès SSH réutilise une clé existante ou demande le mot de passe ; aucun identifiant global Infisical ne quitte Pépinière.

La clé SSH de Pépinière est épinglée dans `KnownHostsCommand` : aucun fichier `known_hosts` nouveau. Le code de l'installateur est contrôlé par SHA-256 avant exécution root. Source à relire : `club/dns01/install-hermione-identity.py`. Ce bootstrap ne crée aucune unité, n'effectue aucun déploiement et ne modifie aucun fichier gateway, DNS ou pare-feu.

```bash
sudo -v && ssh -T -F /dev/null \
  -o UserKnownHostsFile=/dev/null -o GlobalKnownHostsFile=/dev/null \
  -o StrictHostKeyChecking=yes -o HostKeyAlgorithms=ssh-ed25519 \
  -o 'KnownHostsCommand=/bin/echo 192.168.1.25 ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAII4lqioIbKRKpsx7YgqipTpztACDrIFQwF9548/GW5aQ' \
  maxime@192.168.1.25 \
  '/usr/bin/python3 -B /srv/projects/librechat-artefacts/club/dns01/handoff-hermione.py' \
  | sudo -n /usr/bin/python3 -B -c '
import ctypes,hashlib,json,resource,sys
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
if ctypes.CDLL(None).prctl(4,0,0,0,0): raise SystemExit("Protection impossible")
try:
    data=json.loads(sys.stdin.read(16384))
    if set(data)!={"installer","credentials"} or hashlib.sha256(data["installer"].encode()).hexdigest()!="f94c9564a2b762c6d3b746b4b21f432369f8f3cc248e4ad55abfd111e50a7ac6": raise ValueError()
except Exception:
    raise SystemExit("Remise invalide; détails masqués")
exec(compile(data["installer"],"hermione-identity-installer","exec"),{"__name__":"__main__","IDENTITY_CREDENTIALS":data["credentials"]})
'
```

Le seul fichier de credentials créé est `/etc/artefacts-dns/infisical-identity.env`, root:root 0600, répertoire protégé. Les valeurs passent uniquement en mémoire et dans le flux SSH chiffré, jamais en argument de processus, environnement de la commande SSH, terminal, historique ou fichier temporaire. Le token Alwaysdata reste dans Infisical. Un fichier existant différent, un lien symbolique ou des permissions incorrectes provoquent un refus sans écrasement. Une erreur de vérification après création retire seulement le fichier nouvellement créé. SSH indisponible ou authentification refusée : arrêt avant installation.

Le dossier Infisical de remise proposé est `librechat-artefacts / prod / /hermione-bootstrap`, clé `HERMIONE_UNIVERSAL_AUTH` (JSON clientId/clientSecret). Il est inaccessible à l'identité Hermione. Le helper de Pépinière refuse toute exécution hors du tube SSH provenant d'Hermione `192.168.1.50`. Ne jamais exécuter/exporter ce helper directement ni envoyer sa sortie dans un terminal ou un fichier.

L'installateur vérifie la connexion, l'identité attendue, la présence et longueur du token et les refus d'accès à une autre clé, au dossier racine et au dossier de remise. Il refait ces contrôles après installation. Il ne teste pas l'API Alwaysdata et ne lance pas ACME. Sortie attendue : fichier root:root 0600 installé ; token présent, longueur 32 ; lectures hors périmètre refusées ; HTTPS LAN et TLS vérifiés.

## Retrait et rotation

L'identité est propre au seul job artefacts : arrêter seulement ce job avant de révoquer sa clé client côté Infisical, puis supprimer uniquement son fichier de credentials et le secret de remise si la suppression complète est décidée. Aucun identifiant global changé. Pour une rotation, émettre/remettre une nouvelle clé après autorisation et contrôle du fichier cible, qualifier le job, puis révoquer l'ancienne. Aucune modification de la clé Alwaysdata existante.
