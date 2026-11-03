# Présentation d’avancement — Semaine 2

**Projet :** plateforme de gestion des notes et absences avec DevOps  
**Binôme :** [votre nom] et [nom du camarade]  
**Durée prévue :** 5 semaines · **Jalon présenté :** prototype fonctionnel local

Ce support décrit les livrables disponibles à la fin de cette préparation. Il ne constitue pas une preuve d'un historique de deux semaines. Remplacer les noms et ajuster la répartition aux contributions réelles.

## Diapositive 1 — Contexte et objectif (40 secondes)

Centraliser les étudiants, les notes et les absences dans une interface commune. Réduire la dispersion des fichiers et préparer une livraison reproductible grâce à Docker et à l'intégration continue.

## Diapositive 2 — Périmètre et besoins (50 secondes)

Le prototype couvre l'inscription d'un étudiant, la saisie d'une note sur 20 et l'enregistrement d'une absence justifiée ou non. Le tableau de bord affiche les moyennes simples et les absences. Les rôles cibles sont administrateur, enseignant et étudiant ; ils ne sont pas encore implémentés.

## Diapositive 3 — Architecture (50 secondes)

Navigateur HTML/CSS/JavaScript → API HTTP Python → SQLite.

Docker Compose démarre l'application et monte un volume persistant. Les tests utilisent une base temporaire isolée. GitHub Actions est configuré pour lancer les tests puis construire l'image ; son exécution distante devra être montrée après un premier push sur GitHub.

Choix : limiter les dépendances pour obtenir un premier parcours démontrable. SQLite convient à ce jalon local ; la concurrence, les sauvegardes et le choix de la base cible seront réévalués avant déploiement.

## Diapositive 4 — Livrables disponibles (1 minute)

| Lot | État | Preuve à montrer |
| --- | --- | --- |
| Besoins et planning | Documentés | Ce support et le README |
| Modèle de données | Implémenté | Tables étudiants, matières, notes et absences |
| Premier parcours métier | Fonctionnel | Démonstration dans le navigateur |
| Validation des entrées | Implémentée | Note hors intervalle refusée |
| Persistance | Implémentée | Données conservées au redémarrage |
| Tests | Disponibles | Commande unittest et résultat local |
| Conteneurisation | Configurée | Dockerfile et Compose ; vérifier le résultat local |
| CI | Configurée | Workflow ; preuve distante après push |
| Authentification / CD | À réaliser | Planning semaines 3 et 4 |

## Diapositive 5 — Démonstration (2 minutes)

1. Lancer `python -m app.server`, ouvrir http://localhost:8000.
2. Ajouter « Étudiant Démo » en classe « GI-2 ».
3. Saisir une note de 16 en DevOps et une note de 12 en développement web : moyenne simple attendue 14.
4. Enregistrer une absence non justifiée : le compteur augmente.
5. Actualiser pour montrer la conservation des données.
6. Montrer `python -m unittest discover -s tests -v` dans un second terminal.

Utiliser des données fictives. La démonstration ajoute réellement des enregistrements ; éviter les doublons en vérifiant la liste avant de recommencer.

## Diapositive 6 — Planning et répartition proposée (1 minute)

| Semaine | Objectif / critère de fin | Répartition proposée |
| --- | --- | --- |
| 1 | Cadrage, cas d'utilisation, modèle de données | Les deux membres |
| 2 | Parcours étudiant → note → absence, persistance, tests, Docker et CI configurée | A : API / base ; B : interface / DevOps ; revue croisée |
| 3 | Comptes, rôles et autorisations testés ; modification et suppression encadrées | A : sécurité API ; B : écrans et tests |
| 4 | Environnement de test distant, pipeline de déploiement, journaux et sauvegarde restaurable | B : pipeline / infra ; A : intégration / sauvegarde |
| 5 | Recette, corrections, documentation et soutenance finale | Les deux membres |

Ce planning est une proposition de suivi, pas une déclaration de travaux passés. Ne pas présenter un pourcentage de réalisation sans estimation détaillée des tâches restantes.

## Diapositive 7 — Limites et prochaine étape (40 secondes)

Le jalon démontre le fonctionnement métier minimal et prépare l'automatisation. Il reste à protéger les accès, compléter la gestion des données et valider un déploiement. La priorité de la semaine 3 est de garantir qu'un enseignant ne puisse intervenir que sur son périmètre et qu'un étudiant ne consulte que ses propres résultats.

## Modèle de données

| Table | Champs principaux | Relation |
| --- | --- | --- |
| students | id, name, class_name | Un étudiant possède plusieurs notes et absences |
| subjects | id, name | Une matière possède plusieurs notes et absences |
| grades | id, student_id, subject_id, value | Clés étrangères vers étudiant et matière |
| absences | id, student_id, subject_id, date, justified | Clés étrangères vers étudiant et matière |

## Questions à valider avec le professeur

- Les notes doivent-elles avoir des coefficients et un type d'évaluation ?
- Une absence se mesure-t-elle par séance, heure ou journée ?
- Quelle infrastructure de déploiement et quelle stack sont imposées ?
- Quels droits précis sont attendus pour les trois rôles ?
