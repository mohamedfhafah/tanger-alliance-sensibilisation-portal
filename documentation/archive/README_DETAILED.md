# Portail de Sensibilisation à la Sécurité Tanger Alliance

## Introduction

Bienvenue dans le guide complet du **Portail de Sensibilisation à la Sécurité Tanger Alliance**, une application web développée pour renforcer la culture de cybersécurité au sein de l'organisation Tanger Alliance. Ce portail est conçu pour former les employés aux meilleures pratiques en matière de sécurité informatique, en les aidant à identifier et à contrer les menaces numériques courantes telles que le phishing, les mots de passe faibles et autres vulnérabilités. Si vous n'avez jamais vu ce projet auparavant, ce document vous fournira une compréhension approfondie de ses objectifs, de son architecture, de ses fonctionnalités, de son état actuel et des étapes futures.

L'objectif principal de ce portail est de créer un environnement de travail sécurisé en éduquant les employés sur les risques de cybersécurité à travers des modules de formation interactifs, des quiz, des simulations de phishing et des outils de suivi de progression. Ce projet s'adresse à tous les employés de Tanger Alliance, qu'ils soient novices ou expérimentés en matière de technologie, et fournit également des outils d'administration pour gérer le contenu et suivre les performances des utilisateurs.

## Contexte et Objectifs

### Problématique
Dans le monde numérique d'aujourd'hui, les cyberattaques sont de plus en plus fréquentes et sophistiquées. Tanger Alliance, en tant qu'entité clé dans le secteur portuaire, gère des données sensibles et des infrastructures critiques qui doivent être protégées contre les menaces telles que le phishing (hameçonnage), les ransomwares, et les fuites de données. Une grande partie de ces attaques exploitent l'erreur humaine, souvent due à un manque de sensibilisation ou de formation. Un employé non formé peut involontairement compromettre la sécurité de l'ensemble de l'organisation en cliquant sur un lien malveillant ou en utilisant un mot de passe faible.

### Solution Proposée
Le Portail de Sensibilisation à la Sécurité répond à cette problématique en offrant une plateforme centralisée pour :
- **Éduquer** les employés à travers des modules de formation sur des sujets clés de cybersécurité.
- **Tester** leurs connaissances via des quiz interactifs.
- **Simuler** des scénarios réels comme des attaques de phishing pour évaluer leur réactivité.
- **Suivre** la progression individuelle et collective pour identifier les lacunes et ajuster les formations.
- **Certifier** les employés qui terminent avec succès les modules, renforçant ainsi leur engagement via la gamification (badges, certificats).

Cette approche proactive vise à transformer chaque employé en un maillon fort de la chaîne de sécurité de Tanger Alliance, réduisant ainsi les risques liés aux erreurs humaines.

## Architecture Technique

### Technologies Utilisées
Le portail est construit avec un stack technologique moderne et robuste, adapté aux applications web sécurisées et évolutives :
- **Framework Backend** : Flask (Python), un framework léger mais puissant pour le développement web.
- **Base de Données** : SQLite (pour le développement) avec SQLAlchemy comme ORM (Object-Relational Mapping) pour gérer les interactions avec la base de données. Une migration vers PostgreSQL est envisageable pour la production.
- **Frontend** : HTML, CSS, JavaScript avec le template AdminLTE pour une interface utilisateur professionnelle et responsive.
- **Authentification** : Flask-Login pour la gestion des sessions utilisateur et Flask-Bcrypt pour le hachage des mots de passe.
- **Email** : Flask-Mail pour l'envoi de notifications et de liens de réinitialisation de mot de passe.
- **Déploiement** : Configurations prêtes pour Gunicorn (serveur WSGI) et potentiellement Nginx comme proxy inverse en production.

### Structure des Répertoires
Le projet est organisé de manière modulaire pour faciliter la maintenance et l'évolution :
- **`/app`** : Contient le cœur de l'application.
  - **`/app/models`** : Définition des modèles de base de données (User, Module, Quiz, etc.).
  - **`/app/routes`** : Définition des routes/URL pour les différentes fonctionnalités (authentification, dashboard, administration).
  - **`/app/templates`** : Modèles HTML pour l'interface utilisateur.
  - **`/app/static`** : Fichiers statiques (CSS, JS, images) incluant des personnalisations et des bibliothèques comme AdminLTE.
  - **`/app/forms`** : Formulaires Flask-WTF pour la validation des entrées utilisateur.
- **`/migrations`** : Scripts Alembic pour la gestion des évolutions de la base de données.
- **`/tests`** : Tests unitaires et d'intégration pour valider le bon fonctionnement du code.
- **`/scripts`** : Scripts utilitaires pour la gestion de la base de données, les migrations de données, etc.
- **`/docs`** : Documentation supplémentaire du projet.
- Fichiers de configuration : `config.py` (paramètres de l'application), `.env` (variables d'environnement), `gunicorn_config.py` (configuration du serveur).

### Modèle de Base de Données
La base de données est structurée autour de plusieurs entités clés avec des relations bien définies :
1. **User** : Représente un employé ou un administrateur. Contient des informations comme l'email, le mot de passe (haché), le rôle (user/admin), le département, et les dates de création/dernier login.
2. **Module** : Un module de formation (ex. "Gestion des mots de passe") avec un titre, une description, du contenu, un ordre d'affichage et un statut (actif/inactif).
3. **UserProgress** : Suit la progression d'un utilisateur dans un module spécifique (début, fin, score, complété ou non).
4. **Quiz/Question/Choice** : Structure pour les quiz liés aux modules, avec des questions à choix multiples.
5. **Campaign/PhishingSimulation/PhishingTarget** : Entités pour organiser des campagnes de sensibilisation, notamment des simulations de phishing, en suivant si les utilisateurs ont ouvert, cliqué ou signalé un email suspect.
6. **Certificate** : Certificat délivré à un utilisateur pour un module complété, avec une date d'émission et un ID unique.
7. **Badge** : Récompense attribuée pour des réalisations spécifiques, liée à un module.
8. **Setting** : Paramètres de configuration globaux de l'application.

Ces relations permettent un suivi granulaire des activités des utilisateurs et des performances globales.

## Fonctionnalités Principales

### 1. Authentification et Gestion des Utilisateurs
- **Inscription/Connexion** : Les utilisateurs peuvent se connecter avec leur email et mot de passe. Les administrateurs peuvent créer des comptes pour les employés.
- **Réinitialisation de Mot de Passe** : Un système complet de récupération de mot de passe par email est en place. Un utilisateur peut demander un lien de réinitialisation, recevoir un token sécurisé, et changer son mot de passe.
- **Rôles et Permissions** : Deux rôles existent - "user" (employé standard) et "admin" (administrateur). Les administrateurs ont accès à des fonctionnalités supplémentaires de gestion.

### 2. Tableau de Bord Utilisateur
- **Vue d'Ensemble** : Affiche la progression globale de l'utilisateur à travers les modules, avec des statistiques comme le nombre de modules complétés et les certificats obtenus.
- **Badges et Certificats** : Les utilisateurs peuvent voir leurs récompenses, ce qui ajoute un élément de gamification pour les motiver.
- **Navigation Intuitive** : Accès rapide aux modules disponibles et aux simulations de phishing.

### 3. Modules de Formation
- **Contenu Structuré** : Chaque module couvre un sujet spécifique de cybersécurité (ex. gestion des mots de passe, sensibilisation au phishing) avec du texte, des images, et parfois des vidéos ou des ressources interactives.
- **Progression Suivie** : Le système enregistre quand un utilisateur commence et termine un module, ainsi que ses scores aux quiz associés.
- **Accessibilité** : Les modules sont présentés dans un ordre logique, mais les utilisateurs peuvent les parcourir à leur rythme.

### 4. Quiz Interactifs
- **Évaluation des Connaissances** : Chaque module est souvent suivi d'un quiz à choix multiples pour tester la compréhension.
- **Feedback Immédiat** : Les utilisateurs reçoivent des retours sur leurs réponses, avec des explications pour les erreurs.
- **Score de Réussite** : Un score minimum (souvent 70%) est requis pour valider un module.

### 5. Simulations de Phishing
- **Scénarios Réalistes** : Les administrateurs peuvent créer des campagnes simulant des emails de phishing pour tester la vigilance des employés.
- **Suivi des Réactions** : Le système enregistre si un utilisateur a ouvert l'email, cliqué sur un lien, ou signalé l'email comme suspect.
- **Rapports** : Des données sont collectées pour évaluer le niveau de sensibilisation global de l'organisation.

### 6. Interface d'Administration
- **Gestion des Utilisateurs** : Les administrateurs peuvent ajouter, modifier ou supprimer des comptes utilisateur, et voir leurs progrès.
- **Gestion du Contenu** : Création et modification des modules de formation, des quiz et des campagnes de phishing.
- **Statistiques Globales** : Vue d'ensemble des performances de tous les utilisateurs, taux de complétion des modules, et résultats des simulations.

### 7. Système de Notifications
- **Emails** : Notifications pour les réinitialisations de mot de passe et potentiellement pour les rappels de formation.
- **Alertes Internes** : Messages flash pour informer les utilisateurs des actions réussies ou des erreurs (ex. "Mot de passe mis à jour avec succès").

## Interface Utilisateur

L'interface est basée sur le thème AdminLTE, qui offre un design moderne, professionnel et responsive adapté à tous les appareils (ordinateurs, tablettes, smartphones). Voici les éléments clés :
- **Barre de Navigation** : Accès rapide au tableau de bord, aux modules, et à l'administration (pour les admins).
- **Cartes et Graphiques** : Visualisation des statistiques de progression sous forme de cartes (ex. "Modules Complétés : 3/6") et de graphiques.
- **Système de Progression** : Barres de progression visuelles pour motiver les utilisateurs à compléter leurs formations.
- **Design Thématique** : Utilisation de couleurs et d'icônes liées à la sécurité (boucliers, cadenas) pour renforcer l'identité du portail.

## Sécurité de l'Application

La sécurité est une priorité absolue pour une application traitant de la cybersécurité elle-même :
- **Hachage des Mots de Passe** : Les mots de passe sont stockés sous forme hachée avec Bcrypt.
- **Tokens Sécurisés** : Les tokens de réinitialisation de mot de passe sont générés avec des serializers sécurisés et ont une durée de vie limitée.
- **Protection des Routes** : Les pages sensibles sont protégées par des décorateurs qui vérifient si l'utilisateur est connecté et a les permissions nécessaires.
- **Validation des Formulaires** : Les entrées utilisateur sont validées pour prévenir les attaques par injection.

## État Actuel du Projet

### Fonctionnalités Complétées
1. **Authentification** : Système complet de connexion, déconnexion et réinitialisation de mot de passe.
2. **Tableau de Bord** : Interface utilisateur avec suivi de progression, badges et certificats.
3. **Modules de Formation** : Contenu structuré avec plusieurs modules déjà implémentés (ex. gestion des mots de passe, phishing).
4. **Quiz** : Système fonctionnel avec feedback immédiat et scores.
5. **Administration** : Interface pour gérer utilisateurs et contenus.
6. **Simulations de Phishing** : Structure de base pour créer des campagnes et suivre les interactions (bien que l'envoi réel d'emails ne soit pas encore implémenté).

### Fonctionnalités en Cours ou Manquantes
1. **Envoi Réel d'Emails de Phishing** : La simulation est en place, mais l'intégration avec un serveur de messagerie pour envoyer de vrais emails simulés reste à faire.
2. **Analyses Avancées** : Des rapports plus détaillés pour les administrateurs (graphiques interactifs, export de données).
3. **Gamification Étendue** : Ajout de classements ou de défis communautaires pour augmenter l'engagement.
4. **Intégrations Externes** : Connexion avec des systèmes comme Active Directory pour la gestion des utilisateurs ou avec un SIEM pour corréler les données de sécurité.
5. **Notifications Automatiques** : Rappels pour les modules non terminés ou les nouvelles campagnes.

### Problèmes Connus
- Certains templates ou contenus de modules peuvent être incomplets.
- La couverture des tests unitaires doit être augmentée pour garantir la stabilité.
- La performance peut être un problème avec un grand nombre d'utilisateurs si la base de données n'est pas optimisée.

## Comment Contribuer ou Déployer

### Prérequis
- Python 3.8+ et pip pour installer les dépendances.
- Un environnement virtuel (venv) est recommandé.
- Accès à un serveur de messagerie SMTP pour les fonctionnalités d'email.

### Installation
1. Clonez le dépôt du projet (si applicable).
2. Naviguez vers le répertoire du projet : `cd Projet_Portail_Securite`.
3. Créez et activez un environnement virtuel : `python -m venv venv` puis `source venv/bin/activate` (sur macOS/Linux).
4. Installez les dépendances : `pip install -r requirements.txt`.
5. Configurez les variables d'environnement dans un fichier `.env` (clé secrète, configuration email, etc.).
6. Initialisez la base de données : `python init_db.py` ou utilisez les scripts de migration si nécessaire.
7. Lancez l'application : `python app.py` pour un environnement de développement.

### Déploiement en Production
- Utilisez Gunicorn comme serveur WSGI : `gunicorn -c gunicorn_config.py app:app`.
- Configurez un proxy inverse comme Nginx pour gérer les requêtes statiques et la sécurité.
- Envisagez une base de données PostgreSQL pour la production.
- Sécurisez l'application avec HTTPS et des en-têtes de sécurité appropriés.

## Feuille de Route Future

1. **Court Terme (1-3 mois)** :
   - Finaliser le système de simulation de phishing avec envoi d'emails.
   - Ajouter des tableaux de bord analytiques avancés pour les administrateurs.
   - Compléter le contenu des modules existants et en ajouter de nouveaux.
2. **Moyen Terme (3-6 mois)** :
   - Implémenter des fonctionnalités de gamification supplémentaires (classements, défis).
   - Intégrer le portail avec des systèmes externes (Active Directory, SIEM).
   - Améliorer l'accessibilité pour se conformer aux normes WCAG.
3. **Long Terme (6-12 mois)** :
   - Support multilingue pour atteindre un public plus large.
   - Développement d'une application mobile complémentaire.
   - Ajout de simulations avancées (ex. ransomware, ingénierie sociale).

## Conclusion

Le Portail de Sensibilisation à la Sécurité Tanger Alliance est une initiative stratégique pour protéger l'organisation contre les cybermenaces en formant ses employés. Avec une base technique solide, des fonctionnalités clés déjà en place, et un plan clair pour les améliorations futures, ce projet a le potentiel de devenir un outil essentiel dans la lutte contre les erreurs humaines en cybersécurité. Que vous soyez un employé cherchant à améliorer vos compétences, un administrateur gérant la formation, ou un développeur contribuant au code, ce portail offre une solution complète et évolutive.

Si vous avez des questions ou souhaitez contribuer, n'hésitez pas à explorer le code, à lire les journaux de travail (`journal_de_travail.md`), ou à consulter la liste des tâches (`todolist.md`) pour voir les priorités actuelles.

---
*Document généré pour fournir une vue d'ensemble exhaustive du projet. Dernière mise à jour : Juin 2025*
