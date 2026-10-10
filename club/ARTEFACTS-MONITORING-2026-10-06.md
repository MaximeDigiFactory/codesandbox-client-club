# Règle du job artefacts — 6 octobre 2026

Maxime a transféré par SSH depuis Hermione le candidat `club/artefacts-job-alert.candidate.json`. Il est conservé tel quel pour traçabilité. La règle validée est installée dans le dépôt `infra/monitoring`, fichier `config/grafana/provisioning/alerting/artefacts-dns.yml`, et chargée dans Grafana sur Pépinière sans redémarrage.

Seule correction du candidat : le seuil `> 180` devient `> 0`. La requête ne renvoie que 0, 1 ou 2 ; le seuil original empêchait le déclenchement en cas d’échec/ancienneté/absence. UID `artefacts-dns-job`, groupe distinct `artefacts-dns`, dossier Monitoring, intervalle 30 s, délai 1 min. Ne pas réutiliser le candidat original sans cette correction.

Neuf scénarios PromQL et la syntaxe sont validés avec promtool existant. Comparaison avant/après : 28 autres règles, politiques, contacts, templates et plages muettes inchangés. Aucun destinataire ou route ajouté ; route effective `email-o2switch`. Aucun email de test envoyé, secret affiché ou fichier temporaire de secret. Aucun nouveau service hôte, modification Docker, pare-feu ou intervention sur Hermione/SVE.

Contrôle réel : règle `firing`, santé `ok`, Alertmanager `active`, ni silencée ni inhibée, destinataire `email-o2switch`. Cause observée : absence dans Prometheus des deux métriques du job Hermione ; le repli de la requête renvoie 1. Cela ne prouve pas un échec ACME. Le message pour Hermione demande de vérifier la publication/collecte des deux séries avec `host="hermione"`, sans fabriquer de timestamp ou de succès.

Rapport complet et retour arrière : `/srv/projects/monitoring/reports/artefacts-dns-alert-20261006.md`. Retrait de cette seule règle : `cd /srv/projects/monitoring && python3 -B scripts/artefacts-alert-control.py rollback`. Le script utilise la directive native `deleteRules`, contrôle le retrait et la conservation des autres règles/notifications, puis retire seulement le fichier dédié. Retirer simplement le fichier de provisionnement ne supprime pas nécessairement la règle en base.

Référence : [Grafana, provisionnement et suppression ciblée](https://grafana.com/docs/grafana/latest/alerting/set-up/provision-alerting-resources/file-provisioning/).
