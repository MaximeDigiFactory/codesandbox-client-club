Bonjour,

Publier les aperçus LibreChat Club auto-hébergés, sans modifier les autres domaines, SVE, le pare-feu, les services d'authentification ni le Docker global.

Sur Pépinière, le service statique `librechat-artefacts` est déjà démarré, sur son seul réseau `librechat-artefacts-net` (internal), sans port publié. Le nginx-proxy existant le sert avec les Host `artefacts.digiconseil.fr` et `*.artefacts.digiconseil.fr`. Contrôle local : HTTPS vers `192.168.1.25:443`, SNI `agence.digiconseil.fr`, Host conservé, certificat amont vérifié, répond 200. Cette séparation SNI/Host est la même que pour monitoring et librechat-preprod. Le certificat SNI agence est temporaire : surveiller son renouvellement, ne pas désactiver sa vérification.

DNS Alwaysdata à conserver/créer si absent (TTL 300) :

```dns
artefacts.digiconseil.fr.   300 IN A 82.124.220.142
*.artefacts.digiconseil.fr. 300 IN A 82.124.220.142
```

Les noms principal et de test `fixture-preview.artefacts.digiconseil.fr` répondent déjà correctement auprès de `dns1.alwaysdata.com` ; aucun changement DNS effectué sur Pépinière. Ne pas publier d'AAAA faute de routage public IPv6 validé.

**Point indispensable : certificat public SAN `artefacts.digiconseil.fr` ET `*.artefacts.digiconseil.fr`.** Sandpack static-browser-server 1.0.3 crée une origine aléatoire du type `<id>-preview.artefacts.digiconseil.fr` pour chaque aperçu. Le seul certificat du domaine principal ne suffit pas. Un certificat wildcard Let's Encrypt exige DNS-01 (challenge TXT `_acme-challenge.artefacts.digiconseil.fr`). Employer le mécanisme DNS-01/renouvellement existant sur Hermione avec Alwaysdata s'il existe ; sinon préparer ce mécanisme explicitement avant activation. Ne pas ajouter naïvement le wildcard à un `LETSENCRYPT_HOST` géré en HTTP-01, et ne pas toucher à l'acme-companion cassé de Pépinière. Aucun secret DNS/certificat/clé ne doit être affiché.

Sur Hermione, `/home/digiconseil/projects/gateways/docker-compose.yml` et `/home/digiconseil/projects/gateways/pepiniere/nginx.conf` : sauvegarder les deux fichiers, ajouter seulement `artefacts.digiconseil.fr,*.artefacts.digiconseil.fr` à `VIRTUAL_HOST` de `pepiniere-gateway`, préserver toutes les entrées existantes ; installer le certificat wildcard par le mécanisme dédié DNS-01 et son renouvellement. Ajouter ce serveur au relais :

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

Adapter uniquement le `listen` au port interne actuel de pepiniere-gateway s'il diffère de 80 ; conserver le traitement de confiance de X-Forwarded de la gateway actuelle. Le frontal public doit préserver la CSP/CORS du serveur statique, ne pas ajouter X-Frame-Options DENY/SAMEORIGIN, et n'ajouter ni authentification Club ni cookie sur cette origine. Il doit rejeter les Host qui ne correspondent pas à ces domaines. Les fichiers de membres ne transitent pas par ce service statique : leur contenu est rendu localement dans le navigateur.

Valider la syntaxe des configurations puis recréer **uniquement** `pepiniere-gateway` par le mécanisme de déploiement de cette pile. Aucun redémarrage de Docker ni recréation de nginx-proxy/acme-companion. Vérifier les domaines monitoring, librechat, librechat-preprod et deux autres sites après l'opération.

Contrôles publics obligatoires, certificat et CA vérifiés sans `-k` :

```bash
curl -fsS https://artefacts.digiconseil.fr/version.txt
curl -fsS https://fixture-preview.artefacts.digiconseil.fr/__csb_relay/
curl -fsSI -H 'Origin: https://librechat.digiconseil.fr' https://fixture-preview.artefacts.digiconseil.fr/__csb_relay/
```

Le premier doit afficher `PROD-1741371360-5877b84`. Le deuxième contient la page relais. Le troisième doit conserver CORS (origine exacte), CSP et absence de Set-Cookie. Confirmer aussi HTTPS avec une autre origine aléatoire et le renouvellement automatique DNS-01. Envoyer seulement les statuts et métadonnées de certificat, aucun secret.

Retour arrière : restaurer les deux seuls fichiers gateway sauvegardés, retirer seulement cette publication/certificat, recréer uniquement pepiniere-gateway, et recontrôler les domaines existants. Les deux LibreChat n'activent les nouvelles URL d'aperçu qu'après réussite des contrôles publics ci-dessus.
