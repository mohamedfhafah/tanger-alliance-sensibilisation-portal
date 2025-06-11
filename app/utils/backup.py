#!/usr/bin/env python
"""
Module utilitaire pour la configuration et gestion des sauvegardes automatiques
du Portail de Sécurité Tanger Alliance.
"""

import os
import sys
import logging
import smtplib
from email.mime.text import MIMEText
import subprocess
from datetime import datetime
from pathlib import Path
import traceback

logger = logging.getLogger(__name__)

def configure_backup(app):
    """
    Configure les sauvegardes automatiques selon la configuration de l'application.
    Cette fonction est appelée au démarrage de l'application en mode production.
    """
    app.logger.info("Configuration des sauvegardes automatiques...")
    
    # S'assurer que le répertoire de scripts existe
    scripts_dir = os.path.abspath(os.path.join(app.root_path, '..', 'scripts'))
    backup_script = os.path.join(scripts_dir, 'backup_database.py')
    
    if not os.path.exists(backup_script):
        app.logger.error(f"Script de sauvegarde non trouvé: {backup_script}")
        return
    
    # Vérifier que le script est exécutable
    try:
        os.chmod(backup_script, 0o755)  # rwxr-xr-x
    except Exception as e:
        app.logger.error(f"Impossible de rendre le script exécutable: {e}")
    
    # Enregistrer un gestionnaire d'événements pour les erreurs de sauvegarde
    app.backup_error_handler = BackupErrorHandler(app)


class BackupErrorHandler:
    """
    Gestionnaire pour les erreurs de sauvegarde.
    Envoie des alertes en cas d'échec des sauvegardes.
    """
    
    def __init__(self, app):
        self.app = app
        self.last_notification = None
        self.notification_threshold = 86400  # 24 heures en secondes
    
    def handle_backup_error(self, error_message, backup_file=None, exception=None):
        """
        Gère une erreur de sauvegarde en envoyant une notification
        et en enregistrant l'erreur dans les logs.
        """
        now = datetime.now()
        
        # Éviter d'envoyer trop de notifications
        if (self.last_notification is None or 
                (now - self.last_notification).total_seconds() > self.notification_threshold):
            
            self.app.logger.error(f"Erreur de sauvegarde: {error_message}")
            
            if exception:
                self.app.logger.error(f"Exception: {exception}")
                self.app.logger.error(traceback.format_exc())
            
            # Envoyer une alerte par email
            self._send_email_alert(error_message, backup_file, exception)
            
            # Mettre à jour l'horodatage de la dernière notification
            self.last_notification = now
    
    def _send_email_alert(self, error_message, backup_file=None, exception=None):
        """
        Envoie une alerte par email aux administrateurs.
        """
        if not self.app.config.get('MAIL_USERNAME'):
            self.app.logger.warning("Configuration email manquante, impossible d'envoyer l'alerte")
            return
        
        # Préparer le contenu de l'email
        subject = "[ALERTE] Échec de sauvegarde - Portail Sécurité Tanger Alliance"
        
        body = f"""
ALERTE: Échec de la sauvegarde de base de données

Détails:
- Date/heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Message d'erreur: {error_message}
- Fichier de sauvegarde: {backup_file or 'N/A'}
"""
        
        if exception:
            body += f"""
- Exception: {str(exception)}
- Traceback:
{traceback.format_exc()}
"""
        
        body += """
Veuillez vérifier le système de sauvegarde dès que possible.

Ce message est généré automatiquement par le système de surveillance des sauvegardes.
"""
        
        try:
            # Configurer l'email
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.app.config['MAIL_DEFAULT_SENDER']
            msg['To'] = 'admin@tangeralliance.com'  # Adresse à configurer
            
            # Envoyer l'email
            with smtplib.SMTP(self.app.config['MAIL_SERVER'], self.app.config['MAIL_PORT']) as server:
                if self.app.config['MAIL_USE_TLS']:
                    server.starttls()
                
                if self.app.config.get('MAIL_USERNAME') and self.app.config.get('MAIL_PASSWORD'):
                    server.login(self.app.config['MAIL_USERNAME'], self.app.config['MAIL_PASSWORD'])
                
                server.send_message(msg)
                
            self.app.logger.info("Alerte d'erreur de sauvegarde envoyée par email")
            
        except Exception as e:
            self.app.logger.error(f"Impossible d'envoyer l'alerte par email: {e}")


def run_backup(app, backup_config=None):
    """
    Exécute une sauvegarde manuelle avec les paramètres de l'application.
    
    Args:
        app: Instance de l'application Flask
        backup_config: Chemin vers un fichier de configuration spécifique
        
    Returns:
        bool: True si la sauvegarde a réussi, False sinon
    """
    try:
        # Chemin du script de sauvegarde
        scripts_dir = os.path.abspath(os.path.join(app.root_path, '..', 'scripts'))
        backup_script = os.path.join(scripts_dir, 'backup_database.py')
        
        # Configurer la commande
        cmd = [sys.executable, backup_script]
        
        if backup_config:
            cmd.extend(['--config', backup_config])
        else:
            # Utiliser les valeurs de l'application
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            
            if db_uri.startswith('sqlite:///'):
                db_type = 'sqlite'
                # Extraire le chemin du fichier SQLite
                db_path = db_uri.replace('sqlite:///', '')
                cmd.extend(['--db-type', db_type, '--source', db_path])
            elif db_uri.startswith('postgresql'):
                db_type = 'postgres'
                cmd.extend(['--db-type', db_type, '--source', db_uri])
            else:
                app.logger.error(f"Type de base de données non supporté pour sauvegarde: {db_uri}")
                return False
            
            # Ajout des paramètres de rétention
            retention_days = app.config.get('BACKUP_RETENTION_DAYS', 30)
            cmd.extend(['--retention', str(retention_days)])
        
        # Exécuter la sauvegarde
        app.logger.info(f"Exécution de la sauvegarde: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            app.logger.info("Sauvegarde réussie")
            app.logger.debug(result.stdout)
            return True
        else:
            app.logger.error(f"Échec de la sauvegarde (code {result.returncode})")
            app.logger.error(f"Sortie standard: {result.stdout}")
            app.logger.error(f"Erreur standard: {result.stderr}")
            
            # Envoyer une alerte
            if hasattr(app, 'backup_error_handler'):
                app.backup_error_handler.handle_backup_error(
                    f"Le script de sauvegarde a échoué avec le code de sortie {result.returncode}",
                    exception=result.stderr
                )
            return False
            
    except Exception as e:
        app.logger.error(f"Erreur lors de l'exécution de la sauvegarde: {e}")
        app.logger.error(traceback.format_exc())
        
        # Envoyer une alerte
        if hasattr(app, 'backup_error_handler'):
            app.backup_error_handler.handle_backup_error(
                "Exception lors de l'exécution de la sauvegarde",
                exception=e
            )
        return False
