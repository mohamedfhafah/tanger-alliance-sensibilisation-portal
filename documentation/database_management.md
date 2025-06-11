# Guide de gestion de base de données

Ce document décrit les procédures et outils de gestion de base de données pour le portail de sécurité Tanger Alliance.

## Table des matières

1. [Structure de la base de données](#structure-de-la-base-de-données)
2. [Gestion des migrations avec Alembic](#gestion-des-migrations-avec-alembic)
3. [Migration vers PostgreSQL](#migration-vers-postgresql)
4. [Configuration multi-environnements](#configuration-multi-environnements)
5. [Sauvegarde automatique](#sauvegarde-automatique)
6. [Surveillance et alertes](#surveillance-et-alertes)
7. [Tests automatisés](#tests-automatisés)
8. [Bonnes pratiques](#bonnes-pratiques)
9. [Évolutions futures](#évolutions-futures)

## Structure de la base de données

Le portail utilise SQLAlchemy ORM avec les modèles suivants :

- **User** - Gestion des utilisateurs et authentification
- **Module** - Modules de formation de sensibilisation
- **UserProgress** - Suivi de progression des utilisateurs dans les modules
- **Quiz** - Quiz d'évaluation des connaissances
- **Question** - Questions associées aux quiz
- **Choice** - Choix de réponses pour les questions
- **Campaign** - Campagnes de sensibilisation
- **PhishingSimulation** - Simulations de phishing
- **PhishingTarget** - Cibles des campagnes de phishing
- **Certificate** - Certificats de complétion des modules
- **Setting** - Paramètres de configuration du portail

## Gestion des migrations avec Alembic

Alembic est utilisé pour gérer les migrations de schéma de base de données de manière versionnée.

### Initialisation d'Alembic (déjà effectuée)

```bash
cd /chemin/vers/projet
alembic init migrations
```

La configuration d'Alembic se trouve dans les fichiers :
- `alembic.ini` - Configuration principale d'Alembic
- `migrations/env.py` - Script d'environnement Alembic qui connecte à notre application Flask

### Créer une nouvelle migration

Pour créer une nouvelle migration automatique basée sur les changements apportés aux modèles :

```bash
cd /chemin/vers/projet
alembic revision --autogenerate -m "Description de la migration"
```

### Appliquer les migrations

Pour mettre à jour la base de données avec les dernières migrations :

```bash
alembic upgrade head
```

Pour mettre à jour jusqu'à une version spécifique :

```bash
alembic upgrade <revision_id>
```

### Revenir à une version antérieure

```bash
alembic downgrade <revision_id>
```

Pour revenir à la version précédente :

```bash
alembic downgrade -1
```

### Historique des migrations

```bash
alembic history
```

## Migration vers PostgreSQL

Pour des environnements de production, il est recommandé de migrer de SQLite vers PostgreSQL.

### Prérequis

- PostgreSQL installé et configuré
- Pilote Python pour PostgreSQL (`psycopg2` ou `psycopg2-binary`)

### Étapes de migration

1. Installer les dépendances nécessaires :
   ```bash
   pip install psycopg2-binary
   ```

2. Créer une base de données PostgreSQL :
   ```bash
   createdb portail_securite
   ```

3. Exécuter le script de migration :
   ```bash
   python scripts/migrate_to_postgres.py --sqlite-db instance/app.db --pg-uri postgresql://user:password@localhost/portail_securite
   ```

4. Mettre à jour la configuration dans `config.py` pour utiliser PostgreSQL :
   ```python
   SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/portail_securite'
   ```

### Options du script de migration

- `--sqlite-db` - Chemin vers le fichier SQLite source
- `--pg-uri` - URI de connexion PostgreSQL
- `--skip-existing` - Ne pas écraser les données existantes dans PostgreSQL

## Configuration multi-environnements

Le portail supporte désormais plusieurs environnements de déploiement avec des configurations spécifiques.

### Types d'environnements disponibles

- **Development** : Utilise SQLite pour le développement local
- **Testing** : Utilise SQLite en mémoire pour les tests automatisés
- **Production** : Utilise PostgreSQL avec journalisation avancée
- **Docker** : Configuration optimisée pour les conteneurs Docker

### Configuration des environnements

La configuration est définie dans le fichier `config.py` et est organisée en classes Python :

```python
class Config:
    # Configuration de base commune à tous les environnements
    
class DevelopmentConfig(Config):
    # Configuration spécifique au développement
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL', 'sqlite:///tanger_alliance.db')
    
class ProductionConfig(Config):
    # Configuration de production avec PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:password@localhost:5432/portail_securite'
```

### Sélection de l'environnement

L'environnement est défini par la variable d'environnement `FLASK_CONFIG` :

```bash
# Développement (par défaut)
export FLASK_CONFIG=development

# Production
export FLASK_CONFIG=production

# Tests
export FLASK_CONFIG=testing
```

### Journalisation avancée en production

En mode production :
- Les erreurs sont journalisées dans `logs/portail_securite.log`
- Les erreurs critiques sont envoyées par email aux administrateurs
- Les sauvegardes sont activées automatiquement

## Sauvegarde automatique

Le système intègre une solution de sauvegarde automatique de la base de données.

### Configuration manuelle

1. Modifier les paramètres dans `backup_config.ini` :
   ```ini
   [backup]
   db_type = sqlite  # ou postgres après migration
   source = tanger_alliance.db  # ou URI PostgreSQL
   backup_dir = backups
   retention = 30  # Jours de conservation des sauvegardes
   ```

2. Exécuter une sauvegarde manuellement :
   ```bash
   python scripts/backup_database.py --db-type sqlite --source tanger_alliance.db --backup-dir backups
   ```
   
   Ou avec le fichier de configuration :
   ```bash
   python scripts/backup_database.py --config backup_config.ini
   ```

### Configuration automatique

Pour configurer la sauvegarde automatique via cron :

```bash
./scripts/configure_backup_cron.sh
```

Ce script :
- Configure une tâche cron pour la sauvegarde quotidienne à 3h du matin
- Crée le répertoire de sauvegarde
- Effectue une sauvegarde de test

### Intégration à l'application

Lorsque l'application démarre en mode production, elle configure automatiquement les sauvegardes via le module `app.utils.backup`. Ce module :

- Vérifie que le script de sauvegarde existe et est exécutable
- Enregistre un gestionnaire d'erreurs pour les sauvegardes
- Permet de déclencher des sauvegardes manuelles depuis le code

### Restauration d'une sauvegarde

#### Pour SQLite :
```bash
cp backups/tanger_alliance.db_20250601_030000.bak tanger_alliance.db
```

#### Pour PostgreSQL :
```bash
psql -U postgres -d portail_securite -f backups/portail_securite_20250601_030000.sql
```

## Surveillance et alertes

Le portail dispose désormais d'un système complet de surveillance des sauvegardes et d'alertes.

### Surveillance des sauvegardes

Le script `scripts/monitor_backups.py` vérifie :
- L'existence de sauvegardes récentes
- L'âge des sauvegardes (alerte si trop anciennes)
- L'intégrité des fichiers de sauvegarde SQLite

```bash
python scripts/monitor_backups.py --backup-dir backups --alert-email admin@tangeralliance.com --max-age-hours 24
```

### Configuration des alertes

Les alertes sont envoyées par email en cas de problème. La configuration peut se faire via :

1. Les arguments du script :
   ```bash
   python scripts/monitor_backups.py --smtp-server smtp.gmail.com --smtp-port 587 --smtp-user user@example.com --smtp-password mot_de_passe
   ```

2. Un fichier de configuration :
   ```bash
   python scripts/monitor_backups.py --config monitoring_config.ini
   ```
   
   Format du fichier de configuration :
   ```ini
   [Monitoring]
   max_age_hours = 24
   
   [Email]
   smtp_server = smtp.gmail.com
   smtp_port = 587
   smtp_user = user@example.com
   smtp_password = mot_de_passe
   from_email = backup-monitor@tangeralliance.com
   smtp_use_tls = true
   ```

### Types d'alertes

Le système envoie des alertes dans les cas suivants :

1. **Aucune sauvegarde** trouvée dans le répertoire
2. **Sauvegarde trop ancienne** (dépasse le seuil max_age_hours)
3. **Sauvegarde corrompue** (impossible d'ouvrir ou de lire le fichier SQLite)
4. **Échec de la sauvegarde** (erreur lors de l'exécution du script de sauvegarde)

### Intégration dans l'application

En mode production, le module `app.utils.backup` assure :

- La détection des échecs de sauvegarde
- L'envoi d'alertes par email
- La limitation des notifications (pas plus d'une alerte toutes les 24h pour le même problème)

## Tests automatisés

Le portail intègre désormais des tests automatisés pour les fonctionnalités liées à la base de données.

### Tests unitaires

Les tests unitaires se trouvent dans le répertoire `tests/` et couvrent :

- Les fonctions de sauvegarde (`test_backup_sqlite`, `test_cleanup_old_backups`, etc.)
- Les fonctions de migration (`test_get_table_names`, `test_parse_args`, etc.)

### Exécution des tests

Pour exécuter tous les tests :

```bash
python scripts/run_tests.py
```

Ou via unittest directement :

```bash
python -m unittest discover -s tests
```

### Intégration continue (CI/CD)

Le portail est configuré avec GitHub Actions pour l'intégration continue. Le workflow `.github/workflows/test.yml` :

- S'exécute automatiquement à chaque push sur les branches principales
- Lance les tests unitaires
- Vérifie le code avec flake8
- Génère des rapports de couverture
- Vérifie la migration SQLite vers PostgreSQL

## Bonnes pratiques

1. **Toujours effectuer une sauvegarde** avant de migrer le schéma ou de transférer les données.
2. **Tester les migrations** dans un environnement de développement avant la production.
3. **Versionner les fichiers de migration** avec le code source.
4. **Ne pas modifier les fichiers de migration** après qu'ils aient été appliqués en production.
5. **Préférer PostgreSQL** pour les déploiements en production pour de meilleures performances et fiabilité.
6. **Vérifier régulièrement** les sauvegardes automatiques et tester la restauration.
7. **Utiliser le bon environnement** (development, testing, production) selon le contexte.
8. **Examiner les logs** régulièrement pour détecter des problèmes potentiels.
9. **Surveiller l'espace disque** utilisé par les sauvegardes et ajuster la politique de rétention si nécessaire.
10. **Tester la restauration** de sauvegardes périodiquement pour s'assurer qu'elles sont fonctionnelles.

## Évolutions futures

Les améliorations suivantes sont envisagées pour renforcer la gestion de base de données :

1. **Réplication des sauvegardes** : Mettre en place une copie des sauvegardes sur un stockage distant (AWS S3, Google Cloud Storage)
   ```
   - Synchronisation automatique avec un bucket S3
   - Chiffrement des sauvegardes dans le cloud
   - Politique de rétention distincte pour les sauvegardes distantes
   ```

2. **Interface d'administration** : Ajouter une section dans l'interface d'administration pour surveiller l'état des sauvegardes
   ```
   - Tableau de bord montrant l'état des sauvegardes récentes
   - Possibilité de lancer des sauvegardes manuelles
   - Visualisation des logs de sauvegarde
   - Statistiques sur l'utilisation de l'espace disque
   ```

3. **Restauration automatique** : Développer un script pour restaurer automatiquement une base de données à partir d'une sauvegarde
   ```
   - Interface de sélection de la sauvegarde à restaurer
   - Validation des sauvegardes avant restauration
   - Restauration vers une base temporaire pour vérification
   - Bascule automatique en cas de corruption de la base principale
   ```

4. **Haute disponibilité** : Configuration d'une réplication PostgreSQL en temps réel
   ```
   - Configuration master-slave pour PostgreSQL
   - Basculement automatique en cas de défaillance
   - Répartition des lectures sur les instances slaves
   ```
