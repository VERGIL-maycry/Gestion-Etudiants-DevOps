# Vérification locale — 3 novembre 2026

- `python -m unittest discover -s tests -v` : 3 tests réussis, couvrant le parcours métier, la persistance après réinitialisation, les saisies invalides, la page et la santé HTTP.
- `docker compose config` : configuration valide.
- `docker compose up --build -d` : image construite et conteneur démarré.
- Requêtes HTTP depuis le conteneur : `/health` retourne 200 et `{"status":"ok"}` ; `/` retourne 200.
- Interface consultée dans un navigateur ; captures du tableau de bord, des formulaires et des résultats.
- CI GitHub : fichier fourni, aucune exécution distante vérifiée. Aucun dépôt GitHub ni déploiement distant créé.

Relancer les commandes après toute modification de l'application pour vérifier son fonctionnement.
