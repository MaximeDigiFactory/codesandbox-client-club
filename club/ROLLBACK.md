# Repli — artefacts Club, 6 octobre 2026

Avant chaque déploiement, conserver le YAML et le compose de la seule pile ciblée. Aucun volume utilisateur ni image LibreChat ne change.

1. **Approbations et consigne native** : restaurer `/srv/projects/librechat/state/20261006-artefacts/librechat.yaml` vers `/srv/projects/librechat/librechat.yaml`, et l'équivalent préproduction. Redéployer seulement le web :

```bash
/srv/projects/deploy.sh deploy librechat/preprod prod --service=librechat-preprod --no-deps
/srv/projects/deploy.sh deploy librechat prod --service=librechat --no-deps
```

Les capacités, rôles USER/ADMIN, secrets, fichiers existants et connecteurs ne changent pas. Les confirmations natives de code reviennent avec l'ancien YAML.

2. **Variables d'aperçu** : l'activation sauvegarde chaque compose sous `state/20261006-artefacts/docker-compose.before-preview.yml`. Restaurer ces deux fichiers puis exécuter les deux déploiements ciblés ci-dessus. Ne pas restaurer un autre compose historique : préserver le raccordement CodeAPI de production. Le bundler externe précédent redevient utilisé ; son blocage navigateur antérieur peut revenir.

3. **Service statique** : `docker stop librechat-artefacts`, sans suppression d'image. Pour revenir à la première image de cette intervention, utiliser `previousImage` de `club/IMAGE.json` dans le seul service `bundler`, puis `/srv/projects/deploy.sh deploy librechat-artefacts prod`. Le digest final est conservé localement et dans l'archive privée sous `state/`.

4. **Publication locale** : une fois les URL LibreChat revenues à leur état précédent et le statique arrêté, restaurer uniquement l'ajout `librechat-artefacts-net` dans `/srv/projects/nginx-proxy/docker-compose.yml` (la sauvegarde privée `state/nginx-proxy-compose.before.yml` est une référence ; préserver les autres modifications intervenues depuis). Déconnecter seulement `nginx-proxy` de `librechat-artefacts-net`. Aucun redémarrage du proxy ou de Docker requis. Le réseau reste supprimable lorsqu'il n'a plus de conteneur.

5. **Hermione** : procédure dans `HERMIONE-MESSAGE.md`, restauration des deux fichiers gateway sauvegardés et retrait de cette seule publication/certificat. Aucun retrait du wildcard DNS général existant ni changement des autres domaines.

Le garde nftables et les piles de calcul/C94 ne sont jamais modifiés par ce repli. L'ordre recommandé est URL LibreChat → publication Hermione → arrêt du statique → retrait du seul réseau de publication.
