# Projet n° 5 — Système de gestion des étudiants avec architecture DevOps

Le registre s’adresse aux agents de scolarité des universités et écoles supérieures. Il permet de créer, consulter, rechercher, modifier et supprimer des fiches étudiantes. La recherche accepte un matricule entier ou partiel. La suppression demande une confirmation.

## Démarrer la démonstration

Ouvrir PowerShell dans le dossier contenant `app.py`. Avec Python 3.11 ou supérieur installé, lancer les commandes suivantes.

```powershell
python -B app.py --seed --db data/demo.db
```

Ouvrir [le registre local](http://127.0.0.1:8000/). Les trois fiches de départ sont fictives. Pour arrêter le serveur, utiliser **Ctrl+C**. Le fichier `data/demo.db` conserve les modifications. Pour répéter avec un registre neuf, lancer avec un autre nom de fichier, par exemple `--db data/repetition.db`.

## Démo de deux minutes

1. Montrer les fiches `ETU-001` et `ETU-002`. Elles portent le même nom et le même prénom.
2. Créer `ETU-003`, Lina El Amrani, Informatique, S5. Rechercher `etu-003` et montrer que la fiche apparaît.
3. Tenter de créer une nouvelle fiche avec `etu-001`. Montrer le message « Ce matricule est déjà utilisé », puis retrouver la fiche d’origine.
4. Si le temps le permet, modifier le niveau de `ETU-003`, puis montrer la confirmation de suppression.

## Architecture

```text
Navigateur (formulaires HTML / CSS)
              ↕ HTTP
Application Python (routes, validation, opérations sur les fiches)
              ↕ SQL paramétré
SQLite (fichier persistant)
```

La table `etudiants` contient un identifiant technique interne et cinq champs métier obligatoires. Le matricule est stocké en texte, normalisé en majuscules et protégé par une contrainte `UNIQUE`. L’identifiant interne reste stable si le matricule est modifié. Une tentative de doublon reçoit une réponse HTTP 409 et conserve la fiche existante.

Python et SQLite permettent une démonstration locale avec la bibliothèque standard. Cette version est prévue pour un poste de démonstration avec des données fictives. Pour un usage en établissement, la prochaine version devra gérer les comptes, les droits, les sauvegardes et la journalisation des opérations.

## Tests et DevOps

```powershell
python -B -m unittest -v
```

Six tests couvrent la création et la persistance, la recherche, le doublon, la validation, la modification et la suppression, le point de contrôle et la protection de base des formulaires. Ils utilisent une base temporaire.

Pour utiliser Docker Desktop, arrêter d’abord le serveur Python s’il utilise le port 8000. Puis lancer les commandes suivantes.

```powershell
docker compose up --build --detach --wait
Invoke-RestMethod http://127.0.0.1:8000/health
docker compose logs --tail 20
docker compose down
```

Le volume Compose `donnees` garde la base après `docker compose down`. Le conteneur démarre avec un registre vide à sa première exécution. L’URL `/health` vérifie que l’application accède à la table des étudiants.

Le workflow `.github/workflows/ci.yml` exécute les tests, construit l’image et vérifie le service sous Docker à chaque push ou pull request. Pour le faire tourner à distance, ajouter le projet à un dépôt GitHub et ouvrir l’onglet **Actions**. Le projet contient la configuration CI. Un déploiement distant reste une étape distincte.

État de la vérification sur le poste de préparation. Les six tests et le service HTTP en Python ont été vérifiés. La configuration Compose est valide. Docker Desktop n’a pas démarré et l’exécution dans le conteneur reste à vérifier, ainsi que le premier passage du workflow sur GitHub.

## Présentation d’avancement — 10 novembre 2026

| Étape | Résultat à présenter |
|---|---|
| Semaine 1 · Cadrage | Public cible, agent de scolarité, périmètre de la fiche. |
| Semaine 2 · Conception | Parcours HTTP, application Python, table SQLite, matricule unique. |
| Semaine 3 · Réalisation | Démonstration du registre, tests locaux, conteneur et workflow CI configurés. |

Les semaines structurent les lots de travail présentés. L’état d’avancement décrit les livrables disponibles au moment de l’oral.
