# Portail de Sensibilisation à la Sécurité - Tanger Alliance

Ce projet est un portail web interactif conçu pour former les employés de Tanger Alliance aux meilleures pratiques de sécurité informatique, notamment la gestion des mots de passe, la sensibilisation au phishing, et la protection des données sensibles.

## Fonctionnalités

- **Authentification sécurisée** : Système de connexion et d'inscription avec validation des mots de passe
- **Modules de formation** : Contenus éducatifs sur différents aspects de la sécurité
- **Quiz et évaluations** : Tests pour valider les connaissances acquises
- **Simulations de phishing** : Exercices pratiques pour apprendre à identifier les tentatives de phishing
- **Tableau de bord** : Suivi de la progression et des performances
- **Certificats** : Attestations de compétences après réussite des modules

## Structure du projet

```
Projet_Portail_Securite/
├── app/
│   ├── forms/         # Formulaires Flask-WTF
│   ├── models/        # Modèles de base de données
│   ├── routes/        # Routes et contrôleurs
│   ├── static/        # Fichiers statiques (CSS, JS, images)
│   ├── templates/     # Templates Jinja2
│   └── __init__.py    # Initialisation de l'application
├── venv/              # Environnement virtuel Python
├── app.py             # Point d'entrée de l'application
├── config.py          # Configuration de l'application
├── requirements.txt   # Dépendances Python
├── journal_de_travail.md  # Journal de développement
└── todolist.md        # Liste des tâches à accomplir
```

## Installation

1. Cloner le dépôt
2. Créer un environnement virtuel Python :
   ```
   python -m venv venv
   ```
3. Activer l'environnement virtuel :
   - Sur Windows : `venv\Scripts\activate`
   - Sur macOS/Linux : `source venv/bin/activate`
4. Installer les dépendances :
   ```
   pip install -r requirements.txt
   ```
5. Lancer l'application :
   ```
   python app.py
   ```
6. Accéder à l'application dans votre navigateur à l'adresse : `http://localhost:5000`

## Contexte

Ce portail est développé dans le cadre d'un projet visant à améliorer la posture de sécurité de Tanger Alliance, un acteur majeur du secteur portuaire et logistique. Le contenu est spécifiquement adapté aux enjeux et risques rencontrés dans ce contexte.

## Technologies utilisées

- **Backend** : Python, Flask
- **Base de données** : SQLAlchemy (SQLite en développement, PostgreSQL en production)
- **Frontend** : HTML5, CSS3, JavaScript, Bootstrap 5
- **Authentification** : Flask-Login, Bcrypt
- **Formulaires** : Flask-WTF
- **Administration** : Flask-Admin

## Auteur

Développé pour Tanger Alliance par Mohamed FHAFAH
