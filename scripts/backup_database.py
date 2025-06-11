#!/usr/bin/env python
"""
Script de sauvegarde automatique de la base de données du portail de sécurité Tanger Alliance.
Crée une copie datée de la base de données SQLite ou exécute un dump PostgreSQL.

Utilisation:
    python backup_database.py --db-type [sqlite|postgres] --source [db_path_or_uri] --backup-dir [backup_directory]
"""

import argparse
import os
import sys
import subprocess
import shutil
import logging
import datetime
import configparser
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), "db_backup.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ajout du répertoire parent au path Python pour importer la configuration
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def parse_args():
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(description='Sauvegarde la base de données du portail.')
    parser.add_argument('--db-type', choices=['sqlite', 'postgres'], required=False, 
                       help='Type de base de données (sqlite ou postgres)')
    parser.add_argument('--source', required=False, 
                       help='Chemin vers le fichier SQLite ou URI PostgreSQL')
    parser.add_argument('--backup-dir', 
                       help='Répertoire de sauvegarde (par défaut: backups)')
    parser.add_argument('--retention', type=int, 
                       help='Nombre de jours de rétention des sauvegardes (par défaut: 30)')
    parser.add_argument('--config', 
                       help='Chemin vers le fichier de configuration')
    return parser.parse_args()

def create_backup_dir(backup_dir):
    """Crée le répertoire de sauvegarde s'il n'existe pas."""
    os.makedirs(backup_dir, exist_ok=True)
    logger.info(f"Répertoire de sauvegarde: {backup_dir}")

def backup_sqlite(db_path, backup_dir):
    """Crée une sauvegarde de la base de données SQLite."""
    if not os.path.isfile(db_path):
        logger.error(f"Base de données SQLite introuvable: {db_path}")
        return None
    
    # Création d'un nom de fichier avec timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    db_name = os.path.basename(db_path)
    backup_name = f"{db_name}_{timestamp}.bak"
    backup_path = os.path.join(backup_dir, backup_name)
    
    # Copie du fichier
    try:
        shutil.copy2(db_path, backup_path)
        logger.info(f"Sauvegarde SQLite créée: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde SQLite: {e}")
        return None

def parse_postgres_uri(postgres_uri):
    """Extrait les informations de connexion d'un URI PostgreSQL."""
    # Format: postgresql://user:pass@host:port/dbname
    if not postgres_uri.startswith('postgresql://'):
        logger.error("URI PostgreSQL invalide: doit commencer par 'postgresql://'")
        return None
    
    # Extraction des informations de connexion
    try:
        # Supprime 'postgresql://'
        uri = postgres_uri[13:]
        
        # Sépare les informations d'identification et le reste
        if '@' in uri:
            credentials, connection = uri.split('@', 1)
        else:
            credentials, connection = '', uri
        
        # Extrait l'utilisateur et le mot de passe
        if ':' in credentials:
            username, password = credentials.split(':', 1)
        else:
            username, password = credentials, ''
        
        # Extrait l'hôte, le port et le nom de la base
        if '/' in connection:
            host_port, dbname = connection.split('/', 1)
        else:
            host_port, dbname = connection, ''
        
        # Extrait l'hôte et le port
        if ':' in host_port:
            host, port = host_port.split(':', 1)
        else:
            host, port = host_port, '5432'
        
        return {
            'username': username,
            'password': password,
            'host': host,
            'port': port,
            'dbname': dbname
        }
    except Exception as e:
        logger.error(f"Erreur lors du parsing de l'URI PostgreSQL: {e}")
        return None

def backup_postgres(postgres_uri, backup_dir):
    """Crée une sauvegarde de la base de données PostgreSQL."""
    conn_info = parse_postgres_uri(postgres_uri)
    if not conn_info:
        return None
    
    # Création d'un nom de fichier avec timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{conn_info['dbname']}_{timestamp}.sql"
    backup_path = os.path.join(backup_dir, backup_name)
    
    # Configuration des variables d'environnement pour pg_dump
    env = os.environ.copy()
    if conn_info['username']:
        env['PGUSER'] = conn_info['username']
    if conn_info['password']:
        env['PGPASSWORD'] = conn_info['password']
    if conn_info['host']:
        env['PGHOST'] = conn_info['host']
    if conn_info['port']:
        env['PGPORT'] = conn_info['port']
    
    # Exécution de pg_dump
    try:
        with open(backup_path, 'w') as f:
            subprocess.run(
                ['pg_dump', '--clean', '--if-exists', conn_info['dbname']],
                stdout=f,
                env=env,
                check=True
            )
        logger.info(f"Sauvegarde PostgreSQL créée: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde PostgreSQL: {e}")
        return None

def cleanup_old_backups(backup_dir, retention_days):
    """Supprime les sauvegardes plus anciennes que retention_days."""
    now = datetime.datetime.now()
    cutoff_date = now - datetime.timedelta(days=retention_days)
    
    for filename in os.listdir(backup_dir):
        file_path = os.path.join(backup_dir, filename)
        if not os.path.isfile(file_path):
            continue
            
        file_stat = os.stat(file_path)
        file_date = datetime.datetime.fromtimestamp(file_stat.st_mtime)
        
        if file_date < cutoff_date:
            try:
                os.remove(file_path)
                logger.info(f"Ancienne sauvegarde supprimée: {filename}")
            except Exception as e:
                logger.error(f"Erreur lors de la suppression de {filename}: {e}")

def try_load_config(config_path=None):
    """Tente de charger la configuration depuis un fichier."""
    if not config_path:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'backup_config.ini')
    
    if os.path.exists(config_path):
        logger.info(f"Chargement de la configuration depuis {config_path}")
        config = configparser.ConfigParser()
        config.read(config_path)
        if 'backup' in config:
            return config['backup']
        else:
            logger.error(f"Section 'backup' non trouvée dans le fichier {config_path}")
    else:
        logger.error(f"Fichier de configuration {config_path} non trouvé")
    return {}

def main():
    """Fonction principale de sauvegarde."""
    # Parse les arguments de ligne de commande
    args = parse_args()
    
    # Essaie de charger la configuration depuis un fichier
    config_values = try_load_config(args.config if hasattr(args, 'config') and args.config else None)
    
    # Utiliser la configuration du fichier si les arguments ne sont pas spécifiés
    db_type = args.db_type if args.db_type else config_values.get('db_type')
    source = args.source if args.source else config_values.get('source')
    backup_dir_arg = args.backup_dir if args.backup_dir else config_values.get('backup_dir', 'backups')
    retention = int(args.retention if args.retention else config_values.get('retention', 30))
    
    # Vérifier que les paramètres obligatoires sont présents
    if not db_type:
        logger.error("Type de base de données (--db-type) non spécifié")
        return 1
    if not source:
        logger.error("Source de la base de données (--source) non spécifiée")
        return 1
    
    logger.info(f"Configuration: db_type={db_type}, source={source}, backup_dir={backup_dir_arg}, retention={retention}")
    
    # Le répertoire de sauvegarde peut être relatif au répertoire du script
    backup_dir = backup_dir_arg
    if not os.path.isabs(backup_dir):
        backup_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', backup_dir))
    
    # Création du répertoire de sauvegarde
    create_backup_dir(backup_dir)
    
    # Exécution de la sauvegarde
    backup_path = None
    if db_type == 'sqlite':
        backup_path = backup_sqlite(source, backup_dir)
    elif db_type == 'postgres':
        backup_path = backup_postgres(source, backup_dir)
    
    # Nettoyage des anciennes sauvegardes
    if backup_path:  # Seulement si la sauvegarde a réussi
        cleanup_old_backups(backup_dir, retention)
        return 0
    return 1

if __name__ == '__main__':
    sys.exit(main())
