# Publication privée artefacts sur Gitea

Cible autorisée : `https://git.digiconseil.fr/Digiconseil/librechat-artefacts.git`, privée, HTTPS uniquement. Les commits `5c49d70f3` et suivants sont sur `codex/club-artefacts`. L'ancien distant GitHub est conservé. Aucun autre dépôt déplacé.

## Seul préalable Maxime si le dépôt n'existe pas

Le jeton de monitoring est retrouvé et réutilisable. La création API du dépôt d'organisation répond 403 ; aucun nouveau jeton nécessaire pour le push. Dans [Créer un dépôt](https://git.digiconseil.fr/repo/create) :

1. Propriétaire **Digiconseil**.
2. Nom **librechat-artefacts**.
3. Cocher **Privé**.
4. Laisser désactivée l'initialisation ; aucun README, .gitignore ou licence.
5. Créer le dépôt vide et confirmer qu'il est privé.

Quand prêt, l'agent peut exécuter, sans demande de jeton :

```bash
python3 -B /srv/projects/librechat-artefacts/club/publish-gitea.py
```

Le script refuse une cible publique, vérifie la permission de push, transmet les seules branches/tags locaux par push atomique sans force, contrôle toutes les empreintes distantes, fixe la branche par défaut `codex/club-artefacts` et configure le push par défaut vers le nouveau remote `gitea`. Le remote `origin` GitHub est conservé. L'historique complet du fork est volumineux ; attendre le résultat de transfert. Aucune modification de proxy/limites Gitea/Hermione n'est autorisée par ce script.

## Identifiants : aucune modification

Même source que monitoring : `git credential-store`, fichier `/home/maxime/.git-credentials-monitoring`, action `get`. Le jeton existant reste en clair dans ce fichier 0600 ; aucun affichage, déplacement ou stockage nouveau. Les actions d'approbation/effacement sont ignorées par l'enveloppe de lecture du script. API et Git voient le token seulement en mémoire/pipe ; les sorties d'erreur sont masquées, TLS validé, redirections désactivées.

Qualification locale : gate privé/publique et helper get/approve/reject testés avec identifiants synthétiques. Le push réel reste en attente de la création du dépôt au contrôle initial. Résultats réels consignés après exécution.

Retour arrière local : retirer seulement `remote.pushDefault` et `branch.codex/club-artefacts.pushRemote` si configurés vers gitea, puis retirer seulement le remote `gitea` si créé. Ne pas effacer le dépôt distant, ses branches ou le fichier d'identifiants sans accord. Aucun changement de runtime à annuler.
