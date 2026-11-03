# Campus — Gestion des notes et absences avec DevOps

Prototype de semaine 2 sur un projet estimé à cinq semaines. Interface en français, serveur Python sans dépendances externes et base SQLite.

## Démarrer

Depuis la racine du projet, avec Python 3.14 :

```powershell
python -m app.server
```

Ouvrir http://localhost:8000. Arrêter avec Ctrl+C. La base est créée automatiquement dans `data/school.db`. Trois matières sont initialisées ; aucune donnée personnelle n'est fournie.

Ou avec Docker Desktop démarré :

```powershell
docker compose up --build -d
docker compose ps
docker compose logs web
docker compose down
```

Le volume `school-data` conserve les données entre les redémarrages. Ne pas supprimer ce volume pour une simple remise en route.

## Vérifier

```powershell
python -m unittest discover -s tests -v
docker compose config
```

La CI GitHub Actions exécute les tests et construit l'image à chaque push ou pull request une fois le projet envoyé sur GitHub. Aucun déploiement automatique n'est encore configuré.

## Fonctionnalités livrées

- Ajout et consultation des étudiants et de leur classe.
- Saisie et consultation des notes, validation de 0 à 20.
- Saisie des absences par étudiant, matière et date, avec justification.
- Moyennes simples, nombre d'absences et conservation SQLite.
- API JSON : `GET /api/data`, `POST /api/students`, `POST /api/grades`, `POST /api/absences` ; santé : `GET /health`.
- Tests HTTP et base de données, Dockerfile, Compose et workflow CI.

## Limites du jalon

Prototype local avec données fictives : aucun compte ni contrôle d'accès. Pas encore de modification/suppression, coefficients, export, gestion des séances ou déploiement distant. Les matières sont prédéfinies. Une absence correspond à un enregistrement, pas à une durée. Les moyennes ne sont pas des résultats officiels.

Le serveur HTTP standard convient à cette démonstration locale. Un serveur applicatif adapté, l'authentification et les autorisations sont nécessaires avant une utilisation réelle.

Voir `docs/verification.md` pour les résultats des vérifications locales.
