#!/bin/bash
# Script de déploiement en production du Portail de Sécurité Tanger Alliance
# Ce script effectue toutes les étapes nécessaires pour déployer l'application en production
# Usage: ./deploy_to_production.sh [--no-backup]

set -e  # Arrêt du script en cas d'erreur

# Couleurs pour l'affichage
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Répertoire du projet
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo -e "${RED}Erreur: environnement virtuel non trouvé${NC}"
    echo "Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
source venv/bin/activate

# Vérifier les options
BACKUP=true
for arg in "$@"; do
    case $arg in
        --no-backup)
            BACKUP=false
            shift
            ;;
    esac
done

echo -e "${GREEN}=== Déploiement du Portail de Sécurité Tanger Alliance ===${NC}"
echo -e "${YELLOW}Répertoire du projet: ${PROJECT_DIR}${NC}"

# 1. Sauvegarde préalable si l'option est activée
if [ "$BACKUP" = true ]; then
    echo -e "${GREEN}[1/7] Sauvegarde préalable de la base de données...${NC}"
    python scripts/backup_database.py --config backup_config.ini
    if [ $? -ne 0 ]; then
        echo -e "${RED}Échec de la sauvegarde. Interruption du déploiement.${NC}"
        exit 1
    fi
    echo -e "${GREEN}Sauvegarde terminée avec succès.${NC}"
else
    echo -e "${YELLOW}[1/7] Sauvegarde ignorée (--no-backup spécifié)${NC}"
fi

# 2. Mise à jour des dépendances
echo -e "${GREEN}[2/7] Mise à jour des dépendances...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# 3. Migration de la base de données
echo -e "${GREEN}[3/7] Migration de la base de données...${NC}"
export FLASK_CONFIG=production

# Si c'est la première migration vers PostgreSQL
if [ -f "tanger_alliance.db" ] && ! python -c "import os, sys; from sqlalchemy import create_engine, text; engine = create_engine(os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/portail_securite')); try: conn = engine.connect(); result = conn.execute(text('SELECT * FROM alembic_version LIMIT 1')); has_data = result.fetchone() is not None; conn.close(); sys.exit(0 if has_data else 1); except: sys.exit(1)" 2>/dev/null; then
    echo -e "${YELLOW}Première migration vers PostgreSQL détectée${NC}"
    python scripts/migrate_to_postgres.py --sqlite-db tanger_alliance.db --pg-url "${DATABASE_URL:-postgresql://postgres:password@localhost:5432/portail_securite}"
else
    # Sinon, appliquer les migrations Alembic
    echo -e "${YELLOW}Application des migrations Alembic...${NC}"
    alembic upgrade head
fi

# 4. Exécution des tests
echo -e "${GREEN}[4/7] Exécution des tests...${NC}"
export FLASK_CONFIG=testing
python scripts/run_tests.py
TEST_STATUS=$?
export FLASK_CONFIG=production

if [ $TEST_STATUS -ne 0 ]; then
    echo -e "${RED}Tests échoués. Interruption du déploiement.${NC}"
    exit 1
fi
echo -e "${GREEN}Tests passés avec succès.${NC}"

# 5. Collecte des fichiers statiques (si applicable)
echo -e "${GREEN}[5/7] Collecte des fichiers statiques...${NC}"
if [ ! -d "static_collected" ]; then
    mkdir -p static_collected
fi
cp -r app/static/* static_collected/
echo -e "${GREEN}Fichiers statiques collectés.${NC}"

# 6. Configuration des sauvegardes automatiques
echo -e "${GREEN}[6/7] Configuration des sauvegardes automatiques...${NC}"
bash scripts/configure_backup_cron.sh

# 7. Configuration des permissions et sécurité
echo -e "${GREEN}[7/7] Configuration des permissions et sécurité...${NC}"
chmod -R 750 "$PROJECT_DIR"
chmod -R 770 "$PROJECT_DIR/logs"
chmod -R 770 "$PROJECT_DIR/backups"
chmod 440 "$PROJECT_DIR/config.py"

echo -e "${GREEN}=== Déploiement terminé avec succès ===${NC}"
echo -e "${YELLOW}Pour lancer l'application en production:${NC}"
echo "    export FLASK_CONFIG=production"
echo "    gunicorn -w 4 -b 0.0.0.0:5000 app:create_app() --access-logfile logs/access.log --error-logfile logs/error.log"
echo -e "${YELLOW}N'oubliez pas de configurer un reverse proxy (Nginx/Apache) en production${NC}"
