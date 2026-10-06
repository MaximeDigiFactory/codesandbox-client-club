# Publication Gitea et identité Infisical Hermione — 6 octobre 2026

## Résultat Gitea

Dépôt `Digiconseil/librechat-artefacts` créé vide et privé par Maxime puis poussé en HTTPS avec le gestionnaire d'identifiants monitoring existant. Les 11 références locales (2 branches, 9 tags) sont identiques sur Gitea ; `5c49d70f3` et ses suivants sont inclus. Branche par défaut `codex/club-artefacts`. HEAD au premier contrôle : `454b0a21f97471ea16f9a3895d46c2b7f70b68fd`. Les nouveaux livrables de cette intervention sont également destinés exclusivement à ce dépôt privé.

Le transfert initial a retourné HTTP 413. L'historique a été poussé par lots d'ancêtres de premier parent de `main`, puis références finales atomiques, sans force, sans changer de proxy ou de limites serveur. Un contrôle API transitoire HTTP 500 après transfert a été repris ; contrôle complet final réussi.

`origin` GitHub conservé, remote `gitea` ajouté, push par défaut sur Gitea. Même fichier de jeton que monitoring, utilisé en lecture seule et inchangé. Le stockage existant est en clair en 0600 : aucun déplacement sans accord. Voir `PUBLICATION-GITEA.md` et `INVENTAIRE-DEPOTS-IA-2026-10-06.md` pour la répartition des autres dépôts ; rien d'autre déplacé.

## Identité créée et droits exacts

- Nom : `hermione-artefacts-dns01`.
- Identifiant : `2ced3438-30a3-43f2-9a53-4a18f6ca59ab`.
- Organisation et projet : rôle natif `no-access`, aucun rôle supplémentaire.
- Projet : `librechat-artefacts`, UUID `73962094-cbd8-464f-91d6-bea7ba041d8c`.
- Un seul privilège permanent, actions `describeSecret` et `readValue` sur `secrets`.
- Conditions par égalité : `environment=prod`, `secretPath=/dns-hermione`, `secretName=ALWAYSDATA_API_TOKEN`.
- Aucun droit de création/modification/suppression, d'accès aux autres clés, de gestion d'identités ou d'administration du projet/organisation.
- Universal Auth, TTL et TTL maximum de chaque jeton d'accès : 300 secondes.

Le token Alwaysdata est présent, longueur 32 ; sa valeur n'est ni affichée ni recopiée dans un fichier. Pas de test de l'API Alwaysdata depuis Pépinière, dont l'IP source n'est pas celle autorisée.

## Qualification réelle des permissions

Trois clés client de qualification, chacune TTL 300 secondes et un seul login, conservées exclusivement en mémoire puis explicitement révoquées. Aucun secret de bootstrap ni clé client permanente émis à cette étape. Le premier test d'autre environnement sur un dossier inexistant retournait 404 ; le test utile a été refait au dossier racine existant et retourne 403. De même, PATCH/DELETE d'une clé inexistante retournent 404 avant contrôle de droits : ces réponses ne constituent pas une preuve de refus d'écriture, donc un témoin synthétique a servi au test réel.

| Vérification | Résultat |
| --- | --- |
| GET du seul token autorisé | HTTP 200, présent, longueur 32 |
| GET d'une autre clé existante dans le même dossier | HTTP 403 |
| GET du dossier racine | HTTP 403 |
| GET d'un autre environnement dans un dossier existant | HTTP 403 |
| GET dans le projet `librechat-codeapi` Club | HTTP 403 |
| Administration organisation/identité | HTTP 403 |
| Création d'un secret | HTTP 403 |
| Modification du témoin existant | HTTP 403 |
| Suppression du témoin existant | HTTP 403 |
| Liste des secrets du dossier autorisé | HTTP 200, seulement `ALWAYSDATA_API_TOKEN` |
| Témoin après refus d'écriture | Valeur synthétique inchangée |
| Nettoyage des témoins et révocation des clés de qualification | Confirmés |

Aucune valeur réelle modifiée, aucune donnée cliente utilisée, aucun fichier temporaire ou test SVE.

## Réseau, remise et point en attente

URL canonique `https://infisical.digiconseil.fr`, amont LAN `192.168.1.25:443`. Contrôle depuis Pépinière avec résolution LAN : `/api/status` HTTP 200 et TLS validé. Les deux clients préparés (renouvellement et installateur) atteignent cet amont directement tout en conservant SNI/Host/validation de certificat ; un mauvais nom TLS est effectivement refusé. Aucun DNS système, pare-feu ou proxy modifié. L'accès effectif depuis Hermione sera testé par la commande Maxime.

**En attente de validation : clé machine sans expiration, conservation dans Infisical `prod / /hermione-bootstrap / HERMIONE_UNIVERSAL_AUTH`, remise par SSH.** Le contrôle automatique a refusé ce mécanisme permanent faute d'accord explicite sur stockage et durée ; la question a été envoyée à Maxime. Aucun contournement : identité/ACL préparées et tests éphémères terminés, mais mécanisme permanent non exécuté.

Les fichiers de préparation sont prêts à relire : `dns01/provision-hermione-identity.py`, `dns01/handoff-hermione.py`, `dns01/install-hermione-identity.py`. La remise future ne donne pas de rôle supplémentaire à Hermione : le dossier de remise est hors de son unique permission. Le helper source utilise le coffre existant sur Pépinière et exporte uniquement l'identité dédiée dans un tube SSH depuis Hermione `192.168.1.50` ; aucun identifiant global ne quitte Pépinière.

`HERMIONE-IDENTITE.md` contient une commande unique : contrôle de clé hôte SSH sans fichier known_hosts, saisies de mots de passe sans écho si nécessaire, SHA-256 de l'installateur vérifié avant exécution root, création du seul fichier privé `/etc/artefacts-dns/infisical-identity.env`, propriétaire root:root 0600. Pas d'interface Infisical, pas de valeur dans argv/historique/terminal, pas de fichier temporaire. Le token Alwaysdata demeure uniquement dans Infisical ; seul le couple dédié Universal Auth est installé comme demandé.

Qualification locale de l'installateur : simulation mémoire d'installation, refus d'écrasement et nettoyage sur erreur après création ; succès. Syntaxe Python validée, exporter hors SSH refusé avec stdout vide ; options SSH valides. Aucun de ces tests n'a installé de fichier sur Hermione.

## Handoff et suite

Le message complet actualisé est `HERMIONE-MESSAGE.md`, avec les sources en annexe pour que l'agent distant n'ait pas besoin d'un accès Git/Infisical global. Il emploie exclusivement ce fichier root privé et cette identité, ainsi que la connexion LAN vérifiée. Publication/certificat/renouvellement, compte Alwaysdata `lightprod.net`, source acme.sh figée et garde-fous des autres domaines conservés.

L'émission du certificat et sa deuxième exécution autonome restent à qualifier sur Hermione après remise. La délégation parent AFNIC incohérente reste un préalable à décider/vérifier par Maxime selon le message, sans changement DNS par cet agent. Aucune activation d'aperçu LibreChat ou modification de production/préproduction dans cette intervention ; `activate-preview.py` attend la publication HTTPS qualifiée.

## Retour arrière

Gitea : supprimer seulement les configurations locales de push et le nouveau remote si souhaité, sans effacer le dépôt distant ou le jeton existant. Identité : aucun consommateur actif pour le moment ; révocation/suppression de la seule identité dédiée et de son seul privilège si abandon. Après installation éventuelle, arrêter seulement le job artefacts, révoquer sa clé machine puis supprimer uniquement son fichier et le secret de remise si décidé. Ne toucher aucun identifiant global, certificat voisin, Docker global, SVE ou pare-feu.

Références : [Infisical RBAC](https://infisical.com/docs/documentation/platform/access-controls/role-based-access-controls), [privilèges supplémentaires](https://infisical.com/docs/documentation/platform/access-controls/additional-privileges), [OpenSSH KnownHostsCommand](https://man.openbsd.org/ssh_config#KnownHostsCommand). Schémas et contrôles d'actions également vérifiés dans le code installé d'Infisical, sans modifier son conteneur ni afficher sa configuration secrète.
