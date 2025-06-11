#!/usr/bin/env python
"""
Script de surveillance des sauvegardes de base de données.
Vérifie l'existence, l'âge et l'intégrité des fichiers de sauvegarde récents.
Envoie des alertes en cas de problème.

Usage:
    python monitor_backups.py --backup-dir <dossier_sauvegardes> --alert-email <email> [--max-age-hours <heures>]
"""

import os
import sys
import time
import logging
import argparse
import smtplib
import sqlite3
import configparser
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/backup_monitoring.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(description="Surveille les sauvegardes de la base de données.")
    parser.add_argument("--backup-dir", required=True, help="Répertoire des sauvegardes")
    parser.add_argument("--alert-email", required=True, help="Email à notifier en cas de problème")
    parser.add_argument("--max-age-hours", type=int, default=24, 
                        help="Âge maximum d'une sauvegarde valide en heures (défaut: 24)")
    parser.add_argument("--config", help="Chemin vers le fichier de configuration")
    parser.add_argument("--smtp-server", default="smtp.gmail.com", 
                        help="Serveur SMTP pour les alertes (défaut: smtp.gmail.com)")
    parser.add_argument("--smtp-port", type=int, default=587, 
                        help="Port SMTP (défaut: 587)")
    parser.add_argument("--smtp-user", help="Utilisateur SMTP")
    parser.add_argument("--smtp-password", help="Mot de passe SMTP")
    parser.add_argument("--from-email", help="Adresse d'expédition des alertes")
    
    return parser.parse_args()

def load_config(config_path):
    """
    Charge la configuration depuis un fichier .ini
    
    Args:
        config_path (str): Chemin vers le fichier de configuration
        
    Returns:
        dict: Configuration sous forme de dictionnaire
    """
    if not os.path.exists(config_path):
        logger.error(f"Fichier de configuration non trouvé: {config_path}")
        return {}
    
    try:
        config = configparser.ConfigParser()
        config.read(config_path)
        
        # Convertir en dictionnaire
        config_dict = {}
        if 'Monitoring' in config:
            for key, value in config['Monitoring'].items():
                if key == 'max_age_hours':
                    config_dict[key] = int(value)
                else:
                    config_dict[key] = value
        
        if 'Email' in config:
            for key, value in config['Email'].items():
                if key == 'smtp_port':
                    config_dict[key] = int(value)
                else:
                    config_dict[key] = value
                    
        logger.info(f"Configuration chargée depuis {config_path}")
        return config_dict
    except Exception as e:
        logger.error(f"Erreur de chargement de la configuration: {e}")
        return {}

def get_most_recent_backup(backup_dir):
    """
    Trouve la sauvegarde la plus récente dans le répertoire.
    
    Args:
        backup_dir (str): Répertoire des sauvegardes
        
    Returns:
        tuple: (chemin_fichier, date_modification) ou (None, None) si aucun fichier trouvé
    """
    if not os.path.exists(backup_dir) or not os.path.isdir(backup_dir):
        logger.error(f"Répertoire de sauvegarde invalide: {backup_dir}")
        return None, None
    
    # Rechercher les fichiers .bak
    backup_files = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) 
                    if f.endswith('.bak') and os.path.isfile(os.path.join(backup_dir, f))]
    
    if not backup_files:
        logger.warning(f"Aucun fichier de sauvegarde trouvé dans {backup_dir}")
        return None, None
    
    # Trier par date de modification (plus récent d'abord)
    backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    most_recent = backup_files[0]
    mod_time = datetime.fromtimestamp(os.path.getmtime(most_recent))
    
    return most_recent, mod_time

def verify_sqlite_backup(backup_file):
    """
    Vérifie si une sauvegarde SQLite est valide.
    
    Args:
        backup_file (str): Chemin du fichier de sauvegarde
        
    Returns:
        bool: True si la sauvegarde est valide, False sinon
    """
    if not os.path.exists(backup_file):
        logger.error(f"Fichier de sauvegarde introuvable: {backup_file}")
        return False
    
    try:
        # Tenter d'ouvrir la base SQLite
        conn = sqlite3.connect(backup_file)
        cursor = conn.cursor()
        
        # Vérifier qu'on peut au moins lire les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        conn.close()
        
        if not tables:
            logger.warning(f"La sauvegarde {backup_file} ne contient aucune table")
            return False
        
        logger.info(f"Sauvegarde SQLite valide: {backup_file} ({len(tables)} tables)")
        return True
        
    except sqlite3.Error as e:
        logger.error(f"Sauvegarde SQLite corrompue: {backup_file} - {e}")
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de {backup_file}: {e}")
        return False

def send_alert_email(recipient, subject, message, smtp_config):
    """
    Envoie un email d'alerte.
    
    Args:
        recipient (str): Destinataire de l'email
        subject (str): Sujet de l'email
        message (str): Corps de l'email
        smtp_config (dict): Configuration SMTP
        
    Returns:
        bool: True si l'envoi a réussi, False sinon
    """
    try:
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = smtp_config.get('from_email', 'backup-monitor@tangeralliance.com')
        msg['To'] = recipient
        
        server = smtplib.SMTP(smtp_config.get('smtp_server', 'smtp.gmail.com'), 
                              smtp_config.get('smtp_port', 587))
        
        if smtp_config.get('smtp_use_tls', True):
            server.starttls()
            
        if smtp_config.get('smtp_user') and smtp_config.get('smtp_password'):
            server.login(smtp_config.get('smtp_user'), smtp_config.get('smtp_password'))
            
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Alerte envoyée à {recipient}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur d'envoi d'alerte: {e}")
        return False

def main():
    """Fonction principale du script."""
    # S'assurer que le répertoire des logs existe
    os.makedirs("logs", exist_ok=True)
    
    # Analyser les arguments
    args = parse_args()
    
    # Charger la configuration depuis le fichier si spécifié
    config = {}
    if args.config and os.path.exists(args.config):
        config = load_config(args.config)
        
    # Les arguments de la ligne de commande ont priorité sur le fichier de configuration
    backup_dir = args.backup_dir
    alert_email = args.alert_email
    max_age_hours = args.max_age_hours or config.get('max_age_hours', 24)
    
    # Configuration SMTP
    smtp_config = {
        'smtp_server': args.smtp_server or config.get('smtp_server', 'smtp.gmail.com'),
        'smtp_port': args.smtp_port or config.get('smtp_port', 587),
        'smtp_user': args.smtp_user or config.get('smtp_user'),
        'smtp_password': args.smtp_password or config.get('smtp_password'),
        'from_email': args.from_email or config.get('from_email', 'backup-monitor@tangeralliance.com'),
        'smtp_use_tls': config.get('smtp_use_tls', True)
    }
    
    logger.info(f"Vérification des sauvegardes dans {backup_dir}")
    logger.info(f"Âge maximum autorisé: {max_age_hours} heures")
    
    # Trouver la sauvegarde la plus récente
    backup_file, mod_time = get_most_recent_backup(backup_dir)
    
    if not backup_file:
        # Aucune sauvegarde trouvée
        subject = "[ALERTE] Aucune sauvegarde trouvée - Portail Sécurité"
        message = f"""
ALERTE : Aucune sauvegarde n'a été trouvée dans le répertoire {backup_dir}.

Veuillez vérifier immédiatement le système de sauvegarde.

Date/heure de la vérification: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        send_alert_email(alert_email, subject, message, smtp_config)
        logger.critical(f"Aucune sauvegarde trouvée dans {backup_dir}")
        return 1
    
    # Vérifier l'âge de la sauvegarde la plus récente
    now = datetime.now()
    max_age = timedelta(hours=max_age_hours)
    
    if now - mod_time > max_age:
        # Sauvegarde trop ancienne
        age_hours = (now - mod_time).total_seconds() / 3600
        subject = "[ALERTE] Sauvegarde trop ancienne - Portail Sécurité"
        message = f"""
ALERTE : La sauvegarde la plus récente est trop ancienne.

Détails:
- Fichier: {os.path.basename(backup_file)}
- Date de modification: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}
- Âge: {age_hours:.2f} heures (maximum autorisé: {max_age_hours} heures)

Veuillez vérifier pourquoi les sauvegardes récentes ne sont pas créées correctement.

Date/heure de la vérification: {now.strftime('%Y-%m-%d %H:%M:%S')}
        """
        send_alert_email(alert_email, subject, message, smtp_config)
        logger.error(f"Sauvegarde trop ancienne: {backup_file} ({age_hours:.2f} heures)")
        return 2
    
    # Vérifier l'intégrité de la sauvegarde
    if backup_file.endswith('.bak') and not verify_sqlite_backup(backup_file):
        # Sauvegarde corrompue
        subject = "[ALERTE] Sauvegarde corrompue - Portail Sécurité"
        message = f"""
ALERTE : La sauvegarde la plus récente semble être corrompue ou invalide.

Détails:
- Fichier: {os.path.basename(backup_file)}
- Date de modification: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}

Veuillez vérifier le système de sauvegarde et restaurer une sauvegarde valide si nécessaire.

Date/heure de la vérification: {now.strftime('%Y-%m-%d %H:%M:%S')}
        """
        send_alert_email(alert_email, subject, message, smtp_config)
        logger.error(f"Sauvegarde corrompue: {backup_file}")
        return 3
    
    # Tout est OK
    logger.info(f"Vérification réussie: {backup_file} (modifié le {mod_time.strftime('%Y-%m-%d %H:%M:%S')})")
    return 0

if __name__ == "__main__":
    sys.exit(main())
