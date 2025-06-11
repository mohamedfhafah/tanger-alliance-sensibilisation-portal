# 📝 JOURNAL DE TRAVAIL - PORTAIL DE SENSIBILISATION SÉCURITÉ TANGER ALLIANCE

> *Projet démarré le 28 mai 2025*  
> *Stagiaire: Mohamed Fhafah*  
> *Durée: 25 jours ouvrables*

## 📊 TABLEAU DE BORD DU PROJET

| Indicateur | Statut | Commentaire |
|------------|--------|-------------|
| **Avancement global** | 0% | Projet en phase de démarrage |
| **Jalons atteints** | 0/5 | - |
| **Tâches complétées** | 0/~150 | - |
| **Jours écoulés** | 0/25 | - |
| **Risques identifiés** | 0 | - |

---

## 📅 SEMAINE 1 (J1-J5)

### JOUR 1 - 28 mai 2025

**🎯 Objectifs du jour :**
- Initialisation du projet
- Organisation du travail
- Préparation de l'environnement

**📋 Tâches réalisées :**
- Création du répertoire de projet
- Mise en place des fichiers de suivi (todolist et journal de travail)
- Analyse des documents de Tanger Alliance pour identifier les besoins
- Création du dépôt GitHub
- Mise en place de la structure des dossiers
- Définition des objectifs et de la portée du projet
- Planification des jalons clés
- Recherche des technologies à utiliser
- Installation et configuration de l'environnement de développement
- Création de l'environnement virtuel Python
- Installation des dépendances (Flask, SQLAlchemy, Flask-Login, Flask-Admin, Flask-WTF, etc.)
- Mise en place de la structure de l'application Flask
- Création des modèles de base de données (User, Module, Quiz, UserProgress, Campaign, etc.)
- Implémentation des formulaires d'authentification
- Création des templates de base (layout, pages d'accueil, connexion, inscription, tableau de bord)
- Intégration de Bootstrap 5 pour l'interface utilisateur
- Création des fichiers statiques (CSS, JavaScript)
- Rédaction du README.md avec les instructions d'installation et d'utilisation

**💡 Apprentissages :**
- Importance de bien comprendre le contexte métier (terminal portuaire)
- Identification des politiques de sécurité spécifiques à intégrer
- Utilisation d'un système de validation de mot de passe robuste avec vérification de complexité
- Mise en place d'une structure modulaire pour faciliter l'ajout de nouveaux modules de formation
- Implémentation d'un système de suivi de progression des utilisateurs

**🚧 Obstacles rencontrés :**
- Aucun pour le moment
- Quelques problèmes lors de l'installation des dépendances, résolus en simplifiant le fichier requirements.txt
- Adaptation du design pour répondre aux exigences de sécurité tout en maintenant une bonne expérience utilisateur

**⏭️ Prochaines étapes :**
- Compléter le contenu des modules de formation (Gestion des mots de passe, Phishing, etc.)
- Implémenter les fonctionnalités de quiz et d'évaluation
- Développer le système de simulation de phishing
- Mettre en place les fonctionnalités d'administration

---

### JOUR 2 - 29 mai 2025

**🎯 Objectifs du jour :**
- Débogage de l'affichage de la date dans le footer.
- Amélioration de l'interface utilisateur (UI) et de l'expérience utilisateur (UX) de la page d'accueil.
- Initialisation de la base de données avec des données de test.
- Mise à jour de la documentation du projet.

**📋 Tâches réalisées :**
- Correction de l'erreur Jinja2 `UndefinedError: 'now' is undefined` dans `base.html` en passant la variable `now` au template.
- Améliorations de l'affichage de la page d'accueil (`home.html`):
    - Assuré une hauteur égale pour les cartes de présentation des modules (`h-100`).
    - Ajustement du padding du footer (`main.css`).
    - Optimisation de l'espacement vertical entre les sections (`mt-5`, `mb-5`).
    - Résolution du problème de chevauchement du pied de page en utilisant une solution Flexbox (`main.css`).
- Création et exécution du script `init_db.py` pour initialiser la base de données SQLite et insérer les données de test (utilisateurs, modules).
- Mise à jour des fichiers `todolist.md` et `journal_de_travail.md`.

**💡 Apprentissages :**
- Importance de fournir explicitement le contexte (comme `datetime.utcnow()`) aux templates Jinja2.
- Techniques CSS pour l'alignement et l'espacement (Bootstrap classes, Flexbox).
- Implémentation d'un "sticky footer" avec Flexbox pour une meilleure mise en page.
- Processus d'initialisation et de "seeding" d'une base de données Flask-SQLAlchemy.

**🚧 Obstacles rencontrés :**
- Le pied de page qui chevauchait le contenu a nécessité plusieurs itérations pour trouver la solution Flexbox adéquate.

**⏭️ Prochaines étapes :**
- Commencer le développement du contenu et de la logique pour le premier module de formation (par exemple, Gestion des mots de passe).
- Définir la structure des quiz et leur intégration.

---

## 📈 JOURNAL DES JALONS

### JALON 1: Portail avec authentification fonctionnelle
**Date cible :** J5  
**Statut :** Non commencé  
**Tâches critiques :**
- Mettre en place la structure du projet Flask
- Configurer la base de données
- Créer le système d'authentification
- Développer les templates de base

### JALON 2: Premier module complet avec quiz
**Date cible :** J10  
**Statut :** Non commencé  
**Tâches critiques :**
- Développer le module Mots de passe
- Créer le système de quiz
- Implémenter le suivi de progression

### JALON 3: Simulateur phishing basique
**Date cible :** J15  
**Statut :** Non commencé  
**Tâches critiques :**
- Créer les templates d'emails phishing
- Développer le système de tracking
- Implémenter le feedback pédagogique

### JALON 4: Dashboard utilisateur et admin fonctionnels
**Date cible :** J20  
**Statut :** Non commencé  
**Tâches critiques :**
- Développer le dashboard utilisateur
- Créer le panel administrateur
- Implémenter les statistiques et rapports

### JALON 5: Version finale stable pour soutenance
**Date cible :** J25  
**Statut :** Non commencé  
**Tâches critiques :**
- Finaliser tous les modules
- Tester l'application complète
- Préparer la documentation
- Créer la présentation pour soutenance

---

## 📊 SUIVI DES TÂCHES COMPLÉTÉES

### 🔧 SETUP INITIAL
| Date | Tâche | Commentaire |
|------|-------|-------------|
| - | - | - |

### 🗄️ BASE DE DONNÉES
| Date | Tâche | Commentaire |
|------|-------|-------------|
| 29/05/2025 | Initialiser base de données SQLite | Via `init_db.py` |
| 29/05/2025 | Insérer données test et admin par défaut | Via `init_db.py` (appelant `seed_data`) |

### 🔐 AUTHENTIFICATION
| Date | Tâche | Commentaire |
|------|-------|-------------|
| - | - | - |

### 🏠 INTERFACE PRINCIPALE
| Date | Tâche | Commentaire |
|------|-------|-------------|
| 29/05/2025 | Correction erreur Jinja2 'now' is undefined | Affichage date footer OK |
| 29/05/2025 | Amélioration affichage `home.html` | Hauteur cartes, espacements verticaux et footer |
| 29/05/2025 | Résolution chevauchement footer | Implémentation Flexbox pour sticky footer |

### 📚 MODULE 1 - MOTS DE PASSE
| Date | Tâche | Commentaire |
|------|-------|-------------|
| - | - | - |

### 🎣 MODULE 2 - PHISHING
| Date | Tâche | Commentaire |
|------|-------|-------------|
| - | - | - |

---

## 📝 NOTES TECHNIQUES ET DÉCISIONS

### Architecture
- *À compléter au fur et à mesure*

### Choix techniques
- Stack technologique: Python/Flask, SQLAlchemy, Bootstrap 5, AdminLTE
- Base de données: SQLite (dev) → PostgreSQL (prod)
- Authentification: Flask-Login
- Front-end: AdminLTE template avec personnalisation Tanger Alliance

### Défis rencontrés et solutions
- *À compléter au fur et à mesure*

---

## 📚 RESSOURCES IMPORTANTES

### Documents de référence Tanger Alliance
- Politique de gestion des mots de passe
- Analyse des vulnérabilités
- Procédures de gestion des vulnérabilités
- Résumé général des documents

### Liens utiles
- [Documentation Flask](https://flask.palletsprojects.com/)
- [Documentation SQLAlchemy](https://docs.sqlalchemy.org/)
- [Documentation AdminLTE](https://adminlte.io/docs/3.1/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.0/)

---

*Ce journal est mis à jour quotidiennement pour suivre l'avancement du projet et documenter les décisions importantes.*

### Jeudi 29 mai 2025 (Suite)

- **Objectif(s) du jour :**
    - Finaliser et tester l'authentification.
    - Résoudre le problème d'accès incorrect à la section Administration.
- **Réalisations :**
    - Investigation approfondie du problème où les utilisateurs non-administrateurs voyaient le lien "Administration".
        - Vérification de la base de données : les rôles étaient corrects ('user').
        - Vérification du modèle User et de la méthode `is_admin()` : correcte.
        - Ajout de messages de débogage dans le template `base.html`.
    - **Identification de la cause racine :** La méthode `current_user.is_admin` était référencée sans être appelée (manque de `()`) dans la condition Jinja du template `base.html`.
    - **Correction :** Modifié `current_user.is_admin` en `current_user.is_admin()` dans `app/templates/base.html`.
    - Test de la correction : Le lien "Administration" est maintenant correctement masqué pour les utilisateurs non-administrateurs et visible pour les administrateurs.
    - L'authentification complète (inscription, connexion, déconnexion, protection des routes, accès admin) est maintenant considérée comme testée et fonctionnelle.
- **Problèmes rencontrés & Solutions :**
    - Le bug d'accès admin était subtil et a nécessité une analyse pas à pas. L'ajout de logs de débogage dans le template a été crucial.
- **Prochaines étapes :**
    - Passer aux tâches de l'interface principale (Dashboard, etc.).
- **Réalisations (suite) :**
    - Vérification de l'implémentation des messages flash :
        - Le template `base.html` contient déjà le code nécessaire pour afficher les `get_flashed_messages()`.
        - Les routes, comme `auth.login`, utilisent déjà `flash()` pour les notifications utilisateur.
    - Le système de notifications est donc fonctionnel.
- **Réalisations (suite) :**
    - Vérification de l'intégration de la sidebar de navigation :
        - Confirmé que `url_for()` pour toutes les entrées de la sidebar (Accueil, Tableau de bord, Modules, Quiz, Profil, Admin, À Propos) pointent vers des routes valides.
        - La logique de mise en surbrillance de l'élément actif (`class="active"`) basée sur `request.endpoint` est correcte pour tous les liens.
        - Les templates cibles (`modules.html`, `quiz.html`, `profile.html`) existent.
    - La navigation par la sidebar est considérée comme fonctionnelle et intégrée.
- **Réalisations (suite) :**
    - Création de la page de profil utilisateur avec fonctionnalité de mise à jour :
        - Ajout de `UpdateProfileForm` dans `app/forms.py` (champs: username, department).
        - Mise à jour de la route `main.profile` dans `app/routes/main.py` pour gérer la logique du formulaire (GET et POST).
        - Modification du template `app/templates/profile.html` pour afficher le formulaire et permettre la soumission.
    - La page profil permet maintenant aux utilisateurs de modifier leur nom d'utilisateur et département.
- **Réalisations (suite) :**
    - Finalisation de la tâche "Créer dashboard principal avec layout AdminLTE" :
        - Le layout AdminLTE est correctement implémenté pour `dashboard.html`.
        - Les "small boxes" affichent des données dynamiques (actuellement fictives, en attente de la logique métier).
        - La structure de base du dashboard est considérée comme complète pour cette tâche P0.
- **Réalisations (suite) :**
    - Vérification de l'implémentation du design responsive mobile :
        - Examen des templates principaux (`dashboard.html`, `profile.html`, `base.html`, formulaires d'authentification).
        - L'utilisation des classes de grille d'AdminLTE/Bootstrap assure une base responsive.
        - Aucun problème majeur de responsivité identifié à ce stade. La tâche est considérée comme complétée pour l'implémentation de base.
- **Réalisations (suite) :**
    - Test de la navigation complète de l'application :
        - Simulation de la navigation en tant qu'utilisateur normal et administrateur.
        - Vérification du fonctionnement des liens de la sidebar, de la logique d'activation, de l'accès aux pages protégées et des formulaires de base (connexion, profil).
        - La navigation principale est considérée comme fonctionnelle.
- **Réalisations (suite) :**
    - Début du Module 1 - Mots de Passe :
        - Création du template `app/templates/modules/password_policy_module.html`.
        - Ajout de la route `main.module_password_policy` dans `app/routes/main.py`.
        - Mise à jour de `app/templates/modules.html` pour lier vers le nouveau module.
        - Rédaction et intégration du contenu d'introduction pour la politique des mots de passe de Tanger Alliance dans `password_policy_module.html`.
- **Réalisations (suite) :**
    - Module 1 - Mots de Passe (suite) :
        - Rédaction et intégration de la section sur les critères de complexité des mots de passe (longueur min 12c, rotation 90j, variété des caractères, unicité, etc.) dans `password_policy_module.html`.
- **Réalisations (suite) :**
    - Module 1 - Mots de Passe (suite) :
        - Création et intégration de la section "Exemples de Bons et Mauvais Mots de Passe" avec des explications claires dans `password_policy_module.html`.
- **Réalisations (suite) :**
    - Module 1 - Mots de Passe (suite) :
        - Rédaction et intégration de la section "Utilisation d'un Gestionnaire de Mots de Passe" (définition, avantages, recommandations, conseils d'utilisation sécurisée) dans `password_policy_module.html`.
- **Réalisations (suite) :**
    - Module 1 - Mots de Passe (suite) :
        - Mise en place d'une interface de navigation séquentielle dans `password_policy_module.html` avec affichage par sections et boutons Précédent/Suivant via JavaScript.
- **Réalisations (suite) :**
    - Module 1 - Mots de Passe (suite) :
        - Création et intégration d'un quiz de 10 questions (QCM et Vrai/Faux) dans la section 5 de `password_policy_module.html`.
- **Réalisations (suite) :**
    - Module 1 - Mots de Passe (suite) :
        - Implémentation du système de scoring pour le quiz dans `password_policy_module.html` via JavaScript, avec un seuil de réussite de 80% et affichage du résultat.

### JOUR 3 - 30 mai 2025

**🎯 Objectifs du jour (prévisionnels) :**
- Continuer développement Module 1 (Mots de Passe)
- Commencer Module 2 (Phishing)

**📋 Tâches réalisées (réelles) :**
- **Réalisations (30 mai 2025) :**
    - Module 1 - Mots de Passe (suite) :
        - Modification de la route `main.module_password_policy` dans `app/routes/main.py` pour récupérer et passer l'ID du module "Politique des Mots de Passe" au template `password_policy_module.html`.
        - Création d'une nouvelle route `/save_module_progress` (POST) dans `app/routes/main.py` pour recevoir l'ID du module et le score du quiz, puis enregistrer ou mettre à jour la progression de l'utilisateur (modèle `UserProgress`) en base de données. La route gère la création de nouvelles entrées de progression et la mise à jour des existantes, y compris le statut `completed` et `completed_at` basé sur un seuil de 80%.
        - Mise à jour du script JavaScript dans `app/templates/modules/password_policy_module.html` pour récupérer l'ID du module depuis un attribut `data-module-id` et pour envoyer une requête `fetch` (POST) à la route `/save_module_progress` avec l'ID du module et le score obtenu au quiz. La logique de gestion des réponses (succès/erreur) de la sauvegarde a été ajoutée avant la redirection de l'utilisateur.

---
