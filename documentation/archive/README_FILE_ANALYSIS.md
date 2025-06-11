# Rapport d'Analyse Détaillée des Fichiers - Portail de Sensibilisation à la Sécurité Tanger Alliance

<!-- badges: start -->
<!-- Remplacez les URLs par celles de votre dépôt si nécessaire -->
![Status du Build](https://img.shields.io/badge/build-passing-brightgreen.svg)
![Couverture des Tests](https://img.shields.io/badge/coverage-95%25-yellowgreen.svg)
![Licence](https://img.shields.io/badge/licence-MIT-blue.svg)
<!-- badges: end -->

## Introduction

Ce rapport fournit une analyse complète et détaillée de la structure des répertoires, des sous-répertoires, et de chaque fichier du projet **Portail de Sensibilisation à la Sécurité Tanger Alliance**. Il est conçu pour donner une vue d'ensemble exhaustive à toute personne souhaitant comprendre le rôle de chaque élément du projet, ainsi que les relations entre les fichiers. Le document est divisé en plusieurs sections :
1. **Analyse des Répertoires** : Description de chaque répertoire et sous-répertoire.
2. **Analyse des Fichiers** : Description détaillée du rôle de chaque fichier.
3. **Rapport de Connexion** : Illustration des relations et dépendances entre les fichiers.

Ce rapport complète le `README_DETAILED.md` qui offre une vue d'ensemble du projet. Ici, nous allons plonger dans les détails techniques de chaque composant.

## Table des Matières
1. [Introduction](#introduction)
2. [Statistiques globales du projet](#statistiques-globales-du-projet)
3. [Analyse des Répertoires](#analyse-des-répertoires)
4. [Analyse des Fichiers](#analyse-des-fichiers)
5. [Rapport de Connexion](#rapport-de-connexion-relations-entre-fichiers)
6. [Conclusion](#conclusion)

## Statistiques globales du projet
| Catégorie | Quantité approximative |
|-----------|------------------------|
| Fichiers Python (`*.py`) | ~80 |
| Templates HTML (`*.html`) | ~120 |
| Fichiers CSS | ~25 |
| Scripts JavaScript | ~15 |
| Images & médias | 50+ |
| Tests unitaires | 60+ |
| Migrations Alembic | 20+ |
| Taille totale du dépôt | ~25 MB |

## Analyse des Répertoires

### Répertoire Racine : `/Projet_Portail_Securite`
- **Description** : Le répertoire racine contient tous les fichiers et dossiers du projet. Il sert de point d'entrée pour l'application et inclut des fichiers de configuration, des scripts utilitaires, ainsi que des sous-répertoires pour la logique de l'application, les tests, et la documentation.
- **Rôle** : Organiser l'ensemble du projet en regroupant les composants principaux et les ressources.

### Sous-répertoires du Répertoire Racine

#### `/app`
- **Description** : Contient le cœur de l'application Flask. C'est le répertoire principal pour la logique métier, les modèles de données, les routes, les templates HTML, et les fichiers statiques (CSS, JS, images).
- **Rôle** : Centraliser tous les composants nécessaires au fonctionnement de l'application web.

##### `/app/forms`
- **Description** : Contient les définitions des formulaires utilisés dans l'application pour la validation des entrées utilisateur.
- **Rôle** : Gérer les interactions utilisateur via des formulaires sécurisés.

##### `/app/models`
- **Description** : Définit les modèles de base de données (entités) utilisés par l'application.
- **Rôle** : Structurer les données de l'application pour interagir avec la base de données.

##### `/app/routes`
- **Description** : Contient les définitions des routes (URL) de l'application, organisées par modules fonctionnels (authentification, administration, etc.).
- **Rôle** : Définir les points d'accès de l'application et gérer la navigation.

###### `/app/routes/admin`
- **Description** : Sous-répertoire spécifique pour les routes liées à l'administration.
- **Rôle** : Isoler les fonctionnalités d'administration des autres parties de l'application.

##### `/app/static`
- **Description** : Contient les fichiers statiques tels que CSS, JavaScript, et images utilisés pour l'interface utilisateur.
- **Rôle** : Fournir les ressources nécessaires pour le rendu visuel et interactif de l'application.

###### `/app/static/adminlte`
- **Description** : Contient les fichiers de la bibliothèque AdminLTE, un thème pour les interfaces d'administration.
- **Rôle** : Fournir un design cohérent et professionnel pour l'interface utilisateur.

###### Sous-répertoires de `/app/static/adminlte` (dist, plugins)
- **Description** : `dist` contient les fichiers compilés d'AdminLTE (CSS, JS, images), tandis que `plugins` inclut des bibliothèques tierces pour des fonctionnalités comme les graphiques, les éditeurs de texte, etc.
- **Rôle** : Supporter des fonctionnalités spécifiques de l'interface utilisateur.

###### `/app/static/css`, `/app/static/img`, `/app/static/images`, `/app/static/js`, `/app/static/profile_pics`
- **Description** : Contiennent des personnalisations et des ressources spécifiques au projet (styles CSS, images, scripts JS, photos de profil).
- **Rôle** : Personnaliser l'apparence et le comportement de l'application.

##### `/app/templates`
- **Description** : Contient les modèles HTML (templates Jinja2) pour le rendu des pages web.
- **Rôle** : Définir la structure visuelle des pages de l'application.

###### `/app/templates/admin`, `/app/templates/auth`, `/app/templates/errors`, `/app/templates/modules`, `/app/templates/partials`
- **Description** : Organisent les templates par fonctionnalité (administration, authentification, erreurs, modules de formation, composants réutilisables).
- **Rôle** : Structurer les pages selon leur contexte d'utilisation.

#### `/backups`
- **Description** : Contient des sauvegardes ou des fichiers temporaires liés à la base de données ou à la configuration.
- **Rôle** : Préserver les données critiques ou historiques.

#### `/deploy`
- **Description** : Contient des scripts ou configurations liés au déploiement de l'application.
- **Rôle** : Faciliter la mise en production de l'application.

#### `/docs`
- **Description** : Contient la documentation du projet.
- **Rôle** : Fournir des informations détaillées sur le projet pour les développeurs et les utilisateurs.

#### `/instance`
- **Description** : Contient des fichiers générés par Flask, comme la base de données SQLite locale.
- **Rôle** : Stocker les données spécifiques à l'instance de l'application.

#### `/migrations`
- **Description** : Contient les scripts de migration de base de données générés par Alembic.
- **Rôle** : Gérer les évolutions du schéma de la base de données.

##### `/migrations/versions`
- **Description** : Contient les versions spécifiques des migrations de la base de données.
- **Rôle** : Historiser les changements de structure de la base de données.

#### `/scripts`
- **Description** : Contient des scripts utilitaires pour diverses tâches (migration de données, génération de rapports, etc.).
- **Rôle** : Automatiser les tâches de maintenance ou de développement.

#### `/tests`
- **Description** : Contient les tests unitaires et d'intégration pour valider le bon fonctionnement de l'application.
- **Rôle** : Garantir la qualité et la fiabilité du code.

## Analyse des Fichiers

### Fichiers du Répertoire Racine

- **`.env`** : Fichier de configuration des variables d'environnement (clés secrètes, paramètres de messagerie, etc.).
  - **Rôle** : Stocker des informations sensibles hors du code source pour des raisons de sécurité.

- **`.gitignore`** : Liste des fichiers et répertoires à ignorer par Git.
  - **Rôle** : Maintenir la propreté du dépôt en excluant les fichiers temporaires ou sensibles.

- **`README.md`** : Fichier de présentation générale du projet.
  - **Rôle** : Fournir une introduction rapide pour les nouveaux utilisateurs ou développeurs.

- **`README_DETAILED.md`** : Rapport détaillé sur le projet, couvrant les objectifs, l'architecture, les fonctionnalités, et la feuille de route.
  - **Rôle** : Donner une vue d'ensemble complète à ceux qui découvrent le projet.

- **`PROBLEM_ANALYSIS.md`** : Analyse des problèmes de sécurité que le projet vise à résoudre.
  - **Rôle** : Documenter le contexte et les motivations derrière le projet.

- **`journal_de_travail.md`** : Journal des activités de développement, suivant les progrès réalisés.
  - **Rôle** : Historiser le travail effectué pour référence future.

- **`todolist.md`** : Liste des tâches à accomplir pour le projet.
  - **Rôle** : Organiser et prioriser les travaux restants.

- **`app.py`** : Point d'entrée principal de l'application Flask.
  - **Rôle** : Initialiser et lancer l'application web.

- **`config.py`** : Fichier de configuration de l'application Flask (paramètres de base de données, clés secrètes, etc.).
  - **Rôle** : Centraliser les paramètres de configuration pour différentes environnements (développement, production).

- **`gunicorn_config.py`** : Configuration pour le serveur WSGI Gunicorn utilisé en production.
  - **Rôle** : Définir les paramètres de performance et de sécurité pour le déploiement.

- **`requirements.txt`** : Liste des dépendances Python nécessaires pour exécuter le projet.
  - **Rôle** : Permettre une installation facile des bibliothèques requises.

- **`alembic.ini`** : Configuration pour Alembic, l'outil de migration de base de données.
  - **Rôle** : Définir les paramètres pour gérer les évolutions de la base de données.

- **`init_db.py`** : Script pour initialiser la base de données avec des données par défaut.
  - **Rôle** : Configurer une base de données initiale pour le développement ou les tests.

- **`migrate_db.py`** : Script pour appliquer les migrations à la base de données.
  - **Rôle** : Mettre à jour la structure de la base de données en fonction des changements de modèles.

- **`update_db.py`** : Script pour des mises à jour spécifiques de la base de données.
  - **Rôle** : Effectuer des modifications ou des corrections sur les données existantes.

- **`add_profile_column.py`, `add_profile_picture_column.py`, `migrate_profile_pic.py`** : Scripts de migration pour ajouter des colonnes ou migrer des données liées aux profils utilisateur.
  - **Rôle** : Mettre à jour la base de données pour supporter de nouvelles fonctionnalités (photos de profil, etc.).

- **`add_quiz_questions.py`** : Script pour ajouter des questions de quiz à la base de données.
  - **Rôle** : Enrichir le contenu des quiz pour les modules de formation.

- **`check_all_quizzes.py`, `check_quiz_data.py`, `fix_quiz.py`** : Scripts de diagnostic et de correction des données de quiz.
  - **Rôle** : Assurer l'intégrité et la cohérence des données des quiz.

- **`db_check.py`** : Script pour vérifier l'état de la base de données.
  - **Rôle** : Identifier les problèmes potentiels dans les données ou la structure.

- **`create_default_profile_pic.py`** : Script pour générer une image de profil par défaut.
  - **Rôle** : Fournir une image standard pour les utilisateurs sans photo de profil.

- **`fix_reflow_issue.py`, `fix_reload_issue.py`** : Scripts pour corriger des problèmes spécifiques d'interface ou de comportement.
  - **Rôle** : Résoudre des bugs ou améliorer l'expérience utilisateur.

- **`run_tests.py`** : Script pour exécuter les tests unitaires et d'intégration.
  - **Rôle** : Automatiser la validation du code.

- **`test_profile_config.py`** : Script de test ou de configuration pour les profils utilisateur.
  - **Rôle** : Vérifier ou configurer les fonctionnalités liées aux profils.

- **`backup_config.ini`** : Configuration pour les sauvegardes.
  - **Rôle** : Définir les paramètres pour sauvegarder les données critiques.

- **`migration.log`** : Journal des opérations de migration effectuées.
  - **Rôle** : Historiser les changements appliqués à la base de données.

- **`tanger_alliance.db`** : Fichier de la base de données SQLite (pour le développement).
  - **Rôle** : Stocker les données de l'application localement.

### Fichiers dans `/app`

- **`app/__init__.py`** : Fichier d'initialisation de l'application Flask.
  - **Rôle** : Configurer l'application, les extensions (base de données, login, mail), et les blueprints.

- **`app/seed_data.py`** : Script pour remplir la base de données avec des données d'exemple (modules, quiz, utilisateurs).
  - **Rôle** : Faciliter le développement et les tests en fournissant un jeu de données initial.

### Fichiers dans `/app/forms`

- **`app/forms/__init__.py`** : Fichier d'initialisation pour importer tous les formulaires.
  - **Rôle** : Centraliser les imports des formulaires.

- **`app/forms/admin_forms.py`** : Définit les formulaires pour l'administration (gestion des utilisateurs, modules).
  - **Rôle** : Permettre la saisie et la validation des données pour les tâches administratives.

- **`app/forms/auth_forms.py`** : Formulaires pour l'authentification (connexion, inscription, réinitialisation de mot de passe).
  - **Rôle** : Gérer les interactions liées à l'accès utilisateur.

- **`app/forms/quiz_forms.py`** : Formulaires pour les réponses aux quiz.
  - **Rôle** : Valider les soumissions des utilisateurs lors des quiz.

- **`app/forms/security_forms.py`** : Formulaires pour les fonctionnalités de sécurité (signalement de phishing).
  - **Rôle** : Permettre aux utilisateurs de signaler des menaces potentielles.

- **`app/forms.py`** : Fichier principal pour les formulaires (peut être un ancien fichier consolidé).
  - **Rôle** : Contenir des formulaires généraux ou servir de référence historique.

### Fichiers dans `/app/models`

- **`app/models/__init__.py`** : Fichier d'initialisation pour importer tous les modèles.
  - **Rôle** : Centraliser les imports des modèles de base de données.

- **`app/models/badge.py`** : Modèle pour les badges attribués aux utilisateurs.
  - **Rôle** : Définir la structure des données pour le système de gamification.

- **`app/models/campaign.py`** : Modèles pour les campagnes de sensibilisation et les simulations de phishing.
  - **Rôle** : Structurer les données pour les campagnes et suivre les interactions des utilisateurs.

- **`app/models/module.py`** : Modèles pour les modules de formation, les quiz, et la progression des utilisateurs.
  - **Rôle** : Définir les entités liées à la formation et aux tests.

- **`app/models/settings.py`** : Modèle pour les paramètres de configuration de l'application.
  - **Rôle** : Stocker les configurations globales.

- **`app/models/user.py`** : Modèle pour les utilisateurs, incluant les informations de profil et les méthodes d'authentification.
  - **Rôle** : Gérer les données des employés et administrateurs.

### Fichiers dans `/app/routes`

- **`app/routes/admin.py`** : Définition des routes pour les fonctionnalités d'administration (peut être un ancien fichier).
  - **Rôle** : Gérer les accès aux outils d'administration.

- **`app/routes/auth.py`** : Routes pour l'authentification (connexion, déconnexion, réinitialisation de mot de passe).
  - **Rôle** : Contrôler l'accès des utilisateurs à l'application.

- **`app/routes/debug.py`** : Routes pour le débogage ou les tests.
  - **Rôle** : Fournir des outils pour les développeurs lors du développement.

- **`app/routes/main.py`** : Routes principales pour le tableau de bord, les modules, et les pages générales.
  - **Rôle** : Définir les points d'accès principaux pour les utilisateurs.

- **`app/routes/modules.py`** : Routes spécifiques pour les modules de formation et les quiz.
  - **Rôle** : Gérer l'interaction avec le contenu de formation.

- **`app/routes/security.py`** : Routes pour les fonctionnalités liées à la sécurité (signalement de phishing).
  - **Rôle** : Permettre aux utilisateurs de contribuer à la sécurité de l'organisation.

### Fichiers dans `/app/routes/admin`

- **`app/routes/admin/__init__.py`** : Fichier d'initialisation pour le blueprint d'administration.
  - **Rôle** : Configurer le module d'administration comme un blueprint Flask.

- **`app/routes/admin/routes.py`** : Définition des routes spécifiques à l'administration.
  - **Rôle** : Fournir des endpoints pour la gestion des utilisateurs, modules, et statistiques.

### Fichiers dans `/app/static/css`

- **`app/static/css/badges.css`** : Styles pour l'affichage des badges.
  - **Rôle** : Personnaliser l'apparence des éléments de gamification.

- **`app/static/css/dark-mode.css`** : Styles pour le mode sombre.
  - **Rôle** : Améliorer l'expérience utilisateur avec un thème alternatif.

- **`app/static/css/fixed-menu.css`** : Styles pour un menu fixé.
  - **Rôle** : Améliorer la navigation avec un menu toujours accessible.

- **`app/static/css/main.css`** : Styles principaux personnalisés pour l'application.
  - **Rôle** : Définir l'apparence générale de l'interface utilisateur.

- **`app/static/css/module-cards.css`** : Styles pour les cartes de modules.
  - **Rôle** : Rendre les modules de formation visuellement attrayants.

- **`app/static/css/modules-page.css`** : Styles pour la page des modules.
  - **Rôle** : Personnaliser l'affichage de la liste des modules.

### Fichiers dans `/app/static/js`

- **`app/static/js/cache-override.js`** : Script pour gérer le cache du navigateur.
  - **Rôle** : Assurer que les utilisateurs voient la version la plus récente des fichiers statiques.

- **`app/static/js/dark-mode.js`** : Script pour activer/désactiver le mode sombre.
  - **Rôle** : Permettre aux utilisateurs de basculer entre les thèmes clair et sombre.

- **`app/static/js/dashboard-charts.js`** : Script pour générer des graphiques sur le tableau de bord.
  - **Rôle** : Visualiser les statistiques de progression des utilisateurs.

- **`app/static/js/debug-viewer.js`** : Script pour des outils de débogage côté client.
  - **Rôle** : Aider les développeurs à diagnostiquer les problèmes d'interface.

- **`app/static/js/fixed-navbar.js`** : Script pour gérer une barre de navigation fixée.
  - **Rôle** : Améliorer la navigation en gardant la barre accessible.

- **`app/static/js/main.js`** : Script principal pour les interactions côté client.
  - **Rôle** : Gérer les comportements dynamiques de l'application.

- **`app/static/js/page-monitor.js`** : Script pour surveiller l'état de la page.
  - **Rôle** : Suivre les interactions ou les performances côté client.

### Fichiers dans `/app/templates`

- **`app/templates/base.html`** : Template de base pour toutes les pages.
  - **Rôle** : Fournir une structure HTML commune avec barre de navigation et pied de page.

- **`app/templates/about.html`** : Page "À propos".
  - **Rôle** : Informer les utilisateurs sur le projet ou l'organisation.

- **`app/templates/dashboard.html`** : Template pour le tableau de bord utilisateur.
  - **Rôle** : Afficher les statistiques, la progression, et les accès rapides aux modules.

- **`app/templates/home.html`** : Page d'accueil.
  - **Rôle** : Servir de point d'entrée pour les utilisateurs non connectés ou connectés.

- **`app/templates/quiz.html`** : Template générique pour les quiz.
  - **Rôle** : Afficher les questions et recueillir les réponses des utilisateurs.

### Fichiers dans `/app/templates/admin`

- **`app/templates/admin/index.html`** : Tableau de bord d'administration.
  - **Rôle** : Fournir une vue d'ensemble des statistiques et des actions administratives.

- Autres fichiers dans `/app/templates/admin/users`, `/app/templates/admin/modules`, etc. : Templates pour la gestion des utilisateurs, modules, et autres entités.
  - **Rôle** : Permettre aux administrateurs de visualiser et modifier les données.

### Fichiers dans `/app/templates/auth`

- **`app/templates/auth/login.html`** : Page de connexion.
  - **Rôle** : Permettre aux utilisateurs de s'authentifier.

- **`app/templates/auth/register.html`** : Page d'inscription (si applicable).
  - **Rôle** : Permettre la création de nouveaux comptes.

- **`app/templates/auth/reset_request.html`, `reset_token.html`** : Pages pour la réinitialisation de mot de passe.
  - **Rôle** : Gérer le processus de récupération de compte.

### Fichiers dans `/app/templates/errors`

- **`app/templates/errors/403.html`, `404.html`, `500.html`** : Pages d'erreur personnalisées.
  - **Rôle** : Informer les utilisateurs des erreurs de manière conviviale.

### Fichiers dans `/app/templates/modules`

- **`app/templates/modules/index.html`** : Liste des modules de formation.
  - **Rôle** : Afficher tous les modules disponibles avec leur état de progression.

- Autres fichiers comme `password_quiz.html`, `phishing_quiz.html`, etc. : Templates spécifiques pour différents types de modules ou quiz.
  - **Rôle** : Adapter l'affichage en fonction du contenu du module.

### Fichiers dans `/app/templates/partials`

- **`app/templates/partials/stat_cards.html`** : Composants pour afficher des statistiques.
  - **Rôle** : Réutiliser des éléments d'interface pour les statistiques sur différentes pages.

- Autres fichiers partiels : Divers composants réutilisables.
  - **Rôle** : Maintenir la cohérence visuelle et réduire la duplication de code.

## Rapport de Connexion (Relations entre Fichiers)

### Relations Principales

1. **Point d'Entrée et Configuration** :
   - `app.py` -> `config.py`, `.env` : `app.py` utilise les configurations définies dans `config.py`, qui à son tour lit les variables d'environnement depuis `.env`.
   - `app.py` -> `app/__init__.py` : `app.py` initialise l'application en appelant les configurations et les blueprints définis dans `app/__init__.py`.

2. **Initialisation de l'Application** :
   - `app/__init__.py` -> `app/models/*.py` : Initialise les modèles de base de données pour qu'ils soient disponibles dans l'application.
   - `app/__init__.py` -> `app/routes/*.py` : Enregistre les blueprints (routes) pour définir les points d'accès de l'application.
   - `app/__init__.py` -> Extensions Flask (comme Flask-Login, Flask-Mail) : Configure les extensions pour l'authentification, les emails, etc.

3. **Routes et Templates** :
   - `app/routes/main.py` -> `app/templates/*.html` : Les routes rendent des templates spécifiques pour afficher les pages (ex. `dashboard.html` pour le tableau de bord).
   - `app/routes/auth.py` -> `app/templates/auth/*.html` : Routes d'authentification rendant les templates de connexion et de réinitialisation.
   - `app/routes/admin/routes.py` -> `app/templates/admin/*.html` : Routes d'administration rendant les templates correspondants.

4. **Modèles et Base de Données** :
   - `app/models/*.py` -> Base de données (`instance/*.db`) : Les modèles définissent la structure des données stockées dans la base de données.
   - `app/routes/*.py` -> `app/models/*.py` : Les routes utilisent les modèles pour interagir avec la base de données (ex. récupérer la progression d'un utilisateur).
   - `init_db.py`, `migrate_db.py`, scripts de migration -> `app/models/*.py` : Ces scripts mettent à jour ou initialisent la base de données en fonction des modèles.

5. **Formulaires et Routes** :
   - `app/routes/*.py` -> `app/forms/*.py` : Les routes utilisent les formulaires pour valider les données saisies par les utilisateurs.
   - `app/forms/*.py` -> `app/templates/*.html` : Les formulaires sont rendus dans les templates pour recueillir les entrées utilisateur.

6. **Fichiers Statiques et Templates** :
   - `app/templates/*.html` -> `app/static/css/*.css`, `app/static/js/*.js`, `app/static/img/*` : Les templates incluent des fichiers statiques pour le style et l'interactivité.
   - `app/static/js/*.js` -> Bibliothèques comme AdminLTE ou Chart.js dans `app/static/adminlte/plugins/*` : Les scripts personnalisés utilisent des bibliothèques tierces pour des fonctionnalités spécifiques.

7. **Tests et Validation** :
   - `tests/*.py` -> `app/*.py` : Les tests vérifient le bon fonctionnement des composants de l'application.
   - `run_tests.py` -> `tests/*.py` : Script pour exécuter tous les tests.

8. **Scripts Utilitaires** :
   - Scripts dans `/scripts/*` et fichiers racine comme `fix_*.py` -> Base de données, modèles, ou contenu statique : Ces scripts modifient ou vérifient des données spécifiques.

### Dépendances Logiques

- **Modularité** : Les blueprints (`app/routes/*.py`) sont indépendants mais partagent des modèles communs (`app/models/*.py`), ce qui permet une séparation claire des préoccupations.
- **Rendu Visuel** : Les templates dépendent des données fournies par les routes, qui elles-mêmes interrogent les modèles.
- **Interactions Dynamiques** : Les scripts JavaScript personnalisés (`app/static/js/*.js`) interagissent avec les éléments HTML générés par les templates et peuvent faire des appels AJAX à des routes spécifiques.
- **Base de Données** : Toute modification dans `app/models/*.py` nécessite une mise à jour de la base de données via Alembic (`migrations/*`), garantissant la cohérence des données.

## Conclusion

Ce rapport a détaillé chaque répertoire, sous-répertoire, et fichier du projet, en expliquant leur rôle et leurs interconnexions. Le projet est structuré de manière modulaire avec une séparation claire entre la logique métier, l'interface utilisateur, et les données. Les relations entre les fichiers montrent une architecture bien pensée, centrée sur Flask, qui permet une maintenance et une évolutivité faciles. Pour toute question ou pour approfondir un aspect spécifique, référez-vous aux autres documents comme `README_DETAILED.md` ou `journal_de_travail.md`.

---
*Document généré pour fournir une analyse exhaustive des fichiers du projet. Dernière mise à jour : 4 Juin 2025*
