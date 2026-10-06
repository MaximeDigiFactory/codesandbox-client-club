# Aperçus auto-hébergés LibreChat Club — activation du 6 octobre 2026

## Résultat

Activation native terminée sur production et préproduction via `activate-preview.py`, avec `deploy.sh` ciblant uniquement chaque web, préproduction puis production. Aucun correctif LibreChat, image, rôle, secret, volume membre, pile CodeAPI/C94, réseau ou pare-feu modifié. Les seules modifications de chaque compose sont deux lignes d’environnement :

```text
SANDPACK_BUNDLER_URL=https://artefacts.digiconseil.fr
SANDPACK_STATIC_BUNDLER_URL=https://preview.artefacts.digiconseil.fr
```

Image LibreChat conservée : `digiconseil/librechat@sha256:399ea676243c60e11db1154a7242bf27501974d6224c8b05d84e2c5c16888fd8`. Le statique dédié conserve son digest `sha256:0d02712af98205df729801700e1419c6c20327263597c185036c2d02b82331ee`. Aucun réseau applicatif/calcul ou port publié ajouté.

## Publication et prérequis

Pépinière vérifie le TLS public du principal et d’un sous-domaine, SAN `artefacts.digiconseil.fr` et `*.artefacts.digiconseil.fr`, certificat jusqu’au 4 janvier 2027. La porte d’activation vérifie également version `PROD-1741371360-5877b84`, empreintes du bundler/relais/assets locaux, origine aléatoire d’aperçu, CORS/CSP et absence de cookie avant toute modification.

Préflights CORS : HTTP 204 pour production et préproduction avec origine exacte ; origine étrangère non autorisée. Aucun Set-Cookie. La CSP des pages générées contient les deux origines LibreChat autorisées. Les URL sont présentes dans les deux conteneurs ; l’API authentifiée de production les expose effectivement au compte technique USER. L’API préconnexion ne contient pas ces champs, conformément au code natif de l’image ; un test anonyme n’est pas un test de leur activation.

La délégation parent `d.nic.fr` interrogée le 6 octobre après publication ne contient plus que `dns1.alwaysdata.com` et `dns2.alwaysdata.com`. L’incohérence Sendinblue observée auparavant n’est plus présente à ce contrôle. Aucune modification DNS par cette session.

Hermione, selon le retour de Maxime : deuxième passage réussi avec code 2 de renouvellement différé accepté, prochaine exécution le 7 octobre à 03:29 heure de Paris ; configuration k3s préservée et aucun redémarrage. Ces contrôles distants sont attribués à son retour, sans prétendre à une intervention SSH sur Hermione.

## Recette publique en production

Interface dc10 réelle, compte technique USER existant, conversation normale et fichiers synthétiques précédemment produits par le moteur natif. Configuration publique réelle, sans surcharge des URL dans le navigateur, vérification TLS activée.

| Moteur automatisé | Excel/Word/HTML | Originaux Excel/Word/PDF/HTML | Requêtes CodeSandbox |
| --- | --- | --- | --- |
| Chromium | 3 aperçus corrects | 4 téléchargements conformes | 0 |
| Firefox | 3 aperçus corrects | 4 téléchargements conformes | 0 |
| WebKit | 3 aperçus corrects | 4 téléchargements conformes | 0 |

Les cartes natives sont présentes. Chaque aperçu affiche les valeurs 30, 15 et total 45 ; aucune erreur Sandpack `static environment timeout`. Les SHA-256 et tailles des douze originaux téléchargés concordent avec `FILE-RECIPE.json`. Le PDF possède une carte native de téléchargement ; cette version ne dispose pas d’un lecteur PDF dans le panneau Sandpack.

Capture expurgée : seuls hôtes et chemins, sans cookies, jetons, en-têtes ou données réelles. Les requêtes de cette recette vont exclusivement vers LibreChat et les sous-domaines artefacts auto-hébergés ; aucune requête codesandbox.io/csbops.io ni CDN externe. Le test bloque ces domaines et les domaines publicitaires dans Playwright : **simulation de blocage, pas une extension antipublicitaire réelle**. Chromium/WebKit ne prouvent pas à eux seuls le fonctionnement de Chrome/Safari installés chez Maxime.

Le droit `USER.permissions.RUN_CODE.USE=true` est confirmé côté serveur, sans changement de rôle. La génération initiale Excel multi-feuilles, Word, PDF et HTML, l’absence d’approbation code et de faux liens sont documentées dans `FILE-RECIPE.json` ; cette activation recettait le nouveau rendu et les téléchargements existants, sans réexécuter inutilement la génération.

## Monitoring et préproduction

Pépinière reçoit les deux métriques avec `host="hermione"`, `failed=0` et timestamp réel récent. L’alerte `artefacts-dns-job` revient à `inactive`, santé `ok`, sans modifier son seuil ou le routage existant. La règle et son routage sont versionnés dans `infra/monitoring`, commit `dc9537d5c`.

Préproduction : deux variables déployées et vérifiées dans le conteneur, origine CORS/CSP autorisée. Le compte technique production n’existe pas dans sa base et aucun moteur/tenant CodeAPI dédié n’est raccordé à cette pile. Aucun compte/secret/moteur de production n’a été copié en préproduction. **La génération complète en préproduction n’est donc pas annoncée comme recettée.** Son raccordement à un moteur de préproduction isolé demeure une intervention séparée ; aucune nouvelle pile n’est ajoutée pour cette activation.

Les autres changements locaux préexistants (`oidc-client.proposed.json` en préproduction, sauvegarde YAML de labels en production) sont laissés intacts et exclus des commits.

## Retour arrière

Avant déploiement, chaque compose a été sauvegardé dans `state/20261006-artefacts/docker-compose.before-preview.yml`. Retirer uniquement les deux variables ci-dessus du compose de l’instance concernée, ou restaurer sa sauvegarde si aucun autre changement n’est intervenu, puis redéployer uniquement son web :

```bash
/srv/projects/deploy.sh deploy librechat/preprod prod --service=librechat-preprod --no-deps
/srv/projects/deploy.sh deploy librechat prod --service=librechat --no-deps
```

Ne pas retirer la publication HTTPS avant ce repli des URL. Aucun arrêt de CodeAPI/C94, suppression de fichiers/volumes, retrait de rôles USER, modification de secret ou intervention sur Docker global. Le retour à l’ancien bundler peut réintroduire son blocage par le navigateur. Procédure détaillée : `club/ROLLBACK.md` du dépôt artefacts.

## Tests manuels à faire par Maxime

1. Dans une conversation normale, activer l’exécution de code depuis le menu « + » et demander un vrai fichier ; aucune fenêtre d’approbation code, aucun lien fictif, carte native présente.
2. Envoyer un Excel à plusieurs feuilles et vérifier les sommes ; produire un nouvel Excel, contrôler son aperçu, télécharger et ouvrir le fichier dans Excel/LibreOffice.
3. Produire un Word et une page HTML : aperçus lisibles, originaux téléchargeables ; ouvrir le Word dans Word/LibreOffice.
4. Produire un PDF, télécharger et ouvrir le vrai fichier dans un lecteur PDF ; ne pas attendre de panneau Sandpack PDF.
5. Refaire les aperçus avec Chrome, Firefox et Safari réels, bloqueur activé. Dans les outils réseau, filtre `codesandbox` : aucune requête ; pas de timeout Sandpack.
6. Pour une écriture MCP de test choisie par Maxime, vérifier que la confirmation reste demandée, puis annuler si l’écriture n’est pas souhaitée.

## Preuves

Dépôt privé `Digiconseil/librechat-artefacts`, sous `club/` : `PUBLIC-ACTIVATION-PROOF-20261006.json`, `BROWSER-PREVIEW-PUBLIC.json`, `BROWSER-PREVIEW-PUBLIC-SUMMARY.json`, `FILE-RECIPE.json`. Compte technique et données synthétiques uniquement ; aucun secret dans ces preuves.
