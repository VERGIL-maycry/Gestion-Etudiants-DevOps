# Vérification locale — 3 novembre 2026

- `python -m unittest discover -s tests -v` : 3 tests réussis, couvrant le parcours métier, la persistance après réinitialisation, les saisies invalides, la page et la santé HTTP.
- `docker compose config` : configuration valide.
- `docker compose up --build -d` : image construite et conteneur démarré.
- Requêtes HTTP depuis le conteneur : `/health` retourne 200 et `{"status":"ok"}` ; `/` retourne 200.
- Aucune vérification visuelle dans un navigateur n'a été réalisée.
- CI GitHub : fichier fourni, aucune exécution distante vérifiée. Aucun dépôt GitHub ni déploiement distant créé.

Les résultats sont ceux de cette session locale ; relancer les commandes avant la présentation pour disposer de preuves à jour.
