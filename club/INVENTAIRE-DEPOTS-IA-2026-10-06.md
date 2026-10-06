# Dépôts de la plateforme IA — 6 octobre 2026

Inventaire en lecture seule des checkouts de Pépinière et de leurs remotes. Métadonnées des dépôts GitHub ci-dessous vérifiées avec l'authentification existante ; trois dépôts Gitea vérifiés avec le gestionnaire monitoring. Aucun dépôt déplacé, aucun code/runtime SVE modifié ou testé. Les versions locales peuvent comporter des commits non poussés : cette liste situe les dépôts, elle ne certifie pas leur synchronisation.

## Gitea

| Checkout | Dépôt | Confidentialité |
| --- | --- | --- |
| `/srv/projects/librechat-preprod` | [Digiconseil/librechat-preprod](https://git.digiconseil.fr/Digiconseil/librechat-preprod) | Privé, API vérifiée |
| `/srv/projects/websearch` | [Digiconseil/websearch-c94](https://git.digiconseil.fr/Digiconseil/websearch-c94) | Privé, API vérifiée |
| `/srv/projects/monitoring` | [infra/monitoring](https://git.digiconseil.fr/infra/monitoring) | Privé, API vérifiée |
| `/srv/projects/librechat-artefacts` | [Digiconseil/librechat-artefacts](https://git.digiconseil.fr/Digiconseil/librechat-artefacts) | Destination privée autorisée ; création UI encore nécessaire au contrôle |

L'API Gitea indique 1.24.6. Le jeton existant permet de lire les trois dépôts et d'utiliser les droits du compte pour le push ; la création d'un dépôt d'organisation par API retourne 403 faute de scope organization. L'API privée interdit l'inventaire global sans scope organisation : la liste ci-dessus porte sur les checkouts vérifiés, pas tous les dépôts du serveur.

## GitHub — dépôts DigiConseil vérifiés

| Checkout/composant | Dépôt sous MaximeDigiFactory | Confidentialité |
| --- | --- | --- |
| LibreChat Club | [digiconseil-librechat-classique](https://github.com/MaximeDigiFactory/digiconseil-librechat-classique) | Privé |
| CodeAPI Club | [digiconseil-librechat-codeapi](https://github.com/MaximeDigiFactory/digiconseil-librechat-codeapi) | Privé |
| Ancien distant artefacts | [codesandbox-client-club](https://github.com/MaximeDigiFactory/codesandbox-client-club) | **Public** ; nouveaux commits locaux non poussés sur GitHub |
| LibreChat SVE | [sve-librechat](https://github.com/MaximeDigiFactory/sve-librechat) | Privé |
| CodeAPI SVE | [sve-codeapi](https://github.com/MaximeDigiFactory/sve-codeapi) | Privé |
| assistant-gateway | [assistant-gateway](https://github.com/MaximeDigiFactory/assistant-gateway) | Privé |
| agent-gateway | [agent-gateway](https://github.com/MaximeDigiFactory/agent-gateway) | Privé |
| assistant-ia-infra | [assistant-ia-infra](https://github.com/MaximeDigiFactory/assistant-ia-infra) | Privé |
| MCP Google | [mcp-google](https://github.com/MaximeDigiFactory/mcp-google) | Privé |
| Miroir MCP Dolibarr | [mcp-dolibarr-mirror](https://github.com/MaximeDigiFactory/mcp-dolibarr-mirror) | Privé |
| Colanode, composant adjacent | [colanode-digiconseil](https://github.com/MaximeDigiFactory/colanode-digiconseil) | Privé |
| Keycloak, retiré de la cible par ADR 0036 | [keycloak-digiconseil](https://github.com/MaximeDigiFactory/keycloak-digiconseil) | Privé, dépôt toujours présent |

Les alias SSH github-gateway/github-agent-gateway/github-infra/github-mcp-google sont des accès à GitHub ; ils ne constituent pas un serveur Git supplémentaire. Ils n'ont pas été changés.

## GitHub — origines tierces et disponibilité limitée

- MCP Dolibarr : origine publique [digitalfactorysn/mcp-dolibarr](https://github.com/digitalfactorysn/mcp-dolibarr), et miroir privé DigiConseil ci-dessus.
- Vexa : origine publique [Vexa-ai/vexa](https://github.com/Vexa-ai/vexa), checkout `/srv/projects/vexa-next`.
- `/srv/projects/agent-mcp` référence `Volderogue/agent-mcp` ; `/srv/projects/mcp/mcp-mail` référence `Volderogue/mcp-mail`. Ces deux remotes GitHub sont configurés, mais leur dépôt distant n'est pas vérifiable avec l'identité GitHub disponible ; ne pas les considérer accessibles sans contrôle de leur propriétaire.

## Git local sans distant déclaré / dossiers sans checkout propre

Git local sans remote : `litellm`, `litellm-sve`, `nginx-proxy`, `voicebot`, `mcp/mcp-acquisition-api`, `mcp/mcp-listmonk`, `colanode-stack`, ainsi que les piles SVE `sve-autocad-bridge`, `sve-autocad-relay`, `sve-urbanisme`. Aucun remote ajouté à ces dépôts.

Dossiers sans `.git` propre : `ollama`, `kokoro`, `whisperx-api`, `searxng`, `firecrawl`, `infisical`. Certains contenus sont également présents dans `assistant-ia-infra` ou dans une pile qui les déploie ; cette observation ne signifie pas qu'aucune copie n'est versionnée ailleurs. Les autres applications métier du serveur ne font pas partie de ce relevé IA.

## Authentification retrouvée et proposition

Monitoring configure localement `git credential-store --file=/home/maxime/.git-credentials-monitoring`. Fichier propriétaire UID 1003, mode 0600. **Le jeton est enregistré en clair**, jamais affiché ni copié dans les rapports. Les URL des trois remotes Gitea ne contiennent pas de token. Aucun jeton Gitea dans l'environnement courant, ni helper Gitea dans la configuration Git globale.

La publication artefacts réutilise exactement ce backend/fichier via `get`. Une enveloppe Git ignore `store`/`erase` pendant le push pour que le fichier existant reste inchangé. Pas de nouvelle clé, pas de déplacement, pas de modification des scopes, pas d'écriture d'identifiants. Le fichier est comparé avant/après en mémoire.

Proposition à décider par Maxime : conserver le jeton dans un coffre (Infisical avec projet/chemin Git dédié et identité de lecture limitée, ou gestionnaire d'identifiants chiffré), brancher un helper en lecture, qualifier les pushes des dépôts consommateurs puis retirer la copie en clair. Aucune étape de cette migration appliquée. Aucune règle unifiée GitHub/Gitea décidée dans cette intervention.
