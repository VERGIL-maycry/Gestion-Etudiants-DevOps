# Présentation d’avancement - Semaine 2

## 1. Notre projet

Notre projet est une plateforme de gestion des notes et des absences avec DevOps.
L’objectif est de centraliser les informations des étudiants dans une seule application.

## 2. Ce qui fonctionne aujourd’hui

- Ajouter un étudiant et sa classe.
- Enregistrer une note sur 20 et afficher la moyenne.
- Enregistrer une absence, justifiée ou non.
- Conserver les données dans une base SQLite.

## 3. La partie DevOps

- Docker permet de lancer l’application de la même manière sur nos machines.
- Trois tests automatiques passent en local.
- Le workflow GitHub Actions est préparé pour tester et construire l’image Docker à chaque push. Il reste à le vérifier sur GitHub.

Architecture simple : navigateur → application Python → base SQLite.

## 4. Démonstration rapide

Ouvrir http://localhost:8000.
Ajouter un étudiant fictif, saisir une note de 16 sur 20, puis enregistrer une absence.
Montrer que la moyenne et le compteur d’absences sont mis à jour.

## 5. La suite du projet

- Semaine 3 : ajouter la connexion et les rôles (administrateur, enseignant, étudiant).
- Semaine 4 : préparer le déploiement et son automatisation.
- Semaine 5 : terminer les tests, corriger et préparer la soutenance finale.

À ce stade, nous avons un prototype local fonctionnel. La prochaine priorité est de sécuriser les accès.
