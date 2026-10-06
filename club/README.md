# Artefacts Club — service statique auto-hébergé

Déploiement local effectué le 6 octobre 2026. Publication HTTPS publique et activation des variables dans LibreChat **en attente d'Hermione**, protégées par `activate-preview.py`.

Ce dépôt est le fork `MaximeDigiFactory/codesandbox-client-club`, branche `codex/club-artefacts`, basé sur le commit LibreChat-AI `5877b8427e85b457dbb4f92209b1e8a2489cfa3b`. Le ZIP officiel bundler-v12 est vérifié par SHA256 ; sa chaîne version confirme ce commit. Le fichier SOURCE-LOCK.json précise également l'intégrité npm de static-browser-server 1.0.3, version requise par le client Sandpack 2.19.8 de dc10.

Les fichiers de fonctionnement sont dans `club/`, sans correctif LibreChat. Le fork désactive `persistMeasurements` à la source et dans le fichier compilé, et active IS_ONPREM. Le relais statique ajoute la CSP aux réponses HTML générées par son service worker et remplace **trois URL natives fixes** (Tailwind 3.4.17, JSZip 3.10.1, docx-preview 0.3.7) par des assets locaux vérifiés par empreinte. Aucun proxy npm/HTTP arbitraire n'est ajouté ; aucun contenu de membre n'est enregistré par nginx. Les requêtes de la recette Office/HTML ne sortent que vers LibreChat et le sous-domaine d'aperçu. Les artefacts React et leurs dépendances ne sont pas qualifiés par cette recette ; ils peuvent dépendre de registres publics et ne doivent pas être présentés comme entièrement hors ligne.

## Déploiement et publication

```bash
python3 /srv/projects/librechat-artefacts/club/prepare-assets.py
# Pour une reconstruction : docker build -f club/Dockerfile ... puis enregistrer le nouveau RepoDigest.
/srv/projects/deploy.sh deploy librechat-artefacts prod
```

Ne jamais substituer une étiquette à `club/IMAGE.json`/docker-compose.yml. L'image en service est locale, `pull_policy: never` ; son archive de reprise est sous `state/images-artefacts.tar`, ignorée par Git. Projet Infisical `librechat-artefacts` enregistré via deploy.sh, **aucun secret requis**.

Le seul réseau du serveur est `librechat-artefacts-net`, `internal: true`. Le nginx-proxy existant a une appartenance persistée à ce réseau ; pas de proxy-net, réseau applicatif, calcul ou port publié sur le serveur statique. Utilisateur 101, capabilities ALL supprimées, no-new-privileges, rootfs lecture seule, tmpfs 32 Mio, mémoire 256 Mio, 0,5 CPU, 64 PID, journaux 3 × 5 Mio. Le proxy n'a pas été redémarré/recréé par cette intervention.

Transmettre **HERMIONE-MESSAGE.md** à la session Hermione. Les DNS autoritaires sont déjà conformes pour le nom principal et un sous-domaine de test. Le wildcard TLS public est indispensable, avec renouvellement DNS-01 ; un certificat HTTP-01 du seul nom principal ne suffit pas.

Après validation publique et lecture préalable de ROLLBACK.md :

```bash
python3 /srv/projects/librechat-artefacts/club/activate-preview.py
python3 /srv/projects/librechat-artefacts/club/recipes/browser-ui.py --public
```

L'activation vérifie certificat public, origine d'aperçu aléatoire, version, CORS, CSP et absence de Set-Cookie **avant toute modification**. Elle configure les deux variables natives sur les deux web uniquement, préproduction puis production, et utilise deploy.sh. En cas d'échec du second déploiement, le premier reste activé ; la sauvegarde de chaque compose permet son repli ciblé. Pas de modification de secret, de rôle ou de capacités.

Les cookies LibreChat sont host-only ; aucune déclaration Domain=.digiconseil.fr. Le serveur statique n'émet aucun cookie. Sur Hermione, Cookie et Authorization sont supprimés vers cette origine et Set-Cookie masqué. Le service n'est pas une nouvelle barrière d'isolation de l'exécution de code : CodeAPI/NsJail et ses règles restent distincts.

## Recette

FILE-RECIPE.json : génération normale USER, aucune approval, aucun faux lien, feuilles A=30/B=15/total=45. POST-REBOOT-DOWNLOADS.json : originaux inchangés après le redémarrage hôte intervenu pendant la session, sans redémarrage déclenché par Codex.

BROWSER-PREVIEW-LOCAL.json : Chromium 149, Firefox 151, WebKit 26.5, interface dc10 réelle sur compte technique et documents synthétiques. Neuf aperçus (Excel/Word/HTML × trois moteurs) affichent 45 ; douze téléchargements originaux (incluant PDF) sont identiques aux SHA256 de la recette serveur. Word est rendu sans fallback de fidélité. Aucune requête codesandbox.io/csbops.io ni CDN externe pour ces aperçus. Le PDF possède une carte native et se télécharge ; **dc10 n'a pas de lecteur PDF dans le panneau Sandpack**.

La qualification locale remplace dans le seul navigateur la configuration bundler par les URL finales et utilise un relais TLS/DNS jetable, avec certificat de test et autorisation LNA pour l'adresse privée de la fixture Chromium. Aucun certificat ou DNS public n'a été remplacé. Les requêtes de cookies/secrets ne sont jamais enregistrées dans la capture ; seules host/path sont conservées. Le filtre de domaines simulateur n'est pas une extension publicitaire réelle. Chromium n'est pas Chrome de Maxime, WebKit n'est pas Safari réel : recette manuelle nécessaire après publication, bloqueur réel activé. Les conteneurs/clé de test ont été supprimés à la fin.

NATIVE-APPROVAL-PROOF.json : hook natif de l'image exécuté sans implementation de connecteur ; quatre outils allow, dix-sept écritures MCP et un nom synthétique ask. Le dialogue d'une écriture MCP réelle reste à confirmer manuellement ; la sonde réelle Listmonk a été refusée par l'auto-review car un brouillon pourrait être créé en cas de défaut de protection.

Préproduction : YAML accepté et web redéployé ; aucun CodeAPI/tenant n'était raccordé à cette pile. Cette intervention ne copie pas de clés/calcul production en préproduction. Le parcours de génération préproduction n'est pas annoncé comme recetté. Le rendu statique est commun, servi sans données ni cookies ; le raccordement d'un moteur de préproduction isolé est une étape séparée.
