import os
from datetime import timedelta

class Config:
    """
    Configuration de base commune à tous les environnements.
    Les valeurs spécifiques à l'environnement peuvent être remplacées 
    dans les classes dérivées.
    """
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_change_in_production')
    WTF_CSRF_ENABLED = True
    
    # Authentication
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    
    # Database - comportement général
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail server configuration (using environment variables)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)

    # Admin
    FLASK_ADMIN_SWATCH = 'cerulean'
    
    # Sauvegardes
    BACKUP_ENABLED = True
    BACKUP_RETENTION_DAYS = 30
    
    @staticmethod
    def init_app(app):
        """
        Initialisation de l'application avec cette configuration.
        Peut être étendu dans les classes dérivées.
        """
        pass


class DevelopmentConfig(Config):
    """
    Configuration de développement avec SQLite local.
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL', 'sqlite:///tanger_alliance.db')
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Afficher les requêtes SQL en développement
        import logging
        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class TestingConfig(Config):
    # Disable login checks and CSRF during testing
    LOGIN_DISABLED = True
    WTF_CSRF_ENABLED = False
    """
    Configuration de test avec une base de données SQLite en mémoire.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL', 'sqlite:///:memory:')
    # Mail : désactiver l'envoi réel mais fournir un sender par défaut pour les assertions Flask-Mail
    MAIL_SUPPRESS_SEND = True
    MAIL_DEFAULT_SENDER = 'test@example.com'

    # Désactiver les sauvegardes en test
    BACKUP_ENABLED = False


class ProductionConfig(Config):
    """
    Configuration de production avec PostgreSQL.
    """
    # PostgreSQL en production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:password@localhost:5432/portail_securite'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Journalisation des erreurs serveur vers fichier
        import logging
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler('logs/portail_securite.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler)
        
        # Notification des erreurs par email aux administrateurs
        if app.config.get('MAIL_USERNAME'):
            from logging.handlers import SMTPHandler
            credentials = None
            if app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'):
                credentials = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr=app.config['MAIL_DEFAULT_SENDER'],
                toaddrs=['admin@tangeralliance.com'],  # Adresse(s) à notifier
                subject='[Portail Sécurité] Erreur Application',
                credentials=credentials,
                secure=() if app.config['MAIL_USE_TLS'] else None
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)


class DockerConfig(ProductionConfig):
    """
    Configuration pour déploiement Docker.
    """
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        
        # Gestion des logs pour Docker
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


# Configuration par défaut selon l'environnement
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
}
