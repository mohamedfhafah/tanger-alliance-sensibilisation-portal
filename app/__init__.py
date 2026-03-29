import os
import datetime
from flask import Flask, Response, request, jsonify, render_template, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_admin import Admin
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_migrate import Migrate
try:
    from flask_caching import Cache
except ImportError:
    # Dummy Cache if flask_caching is not installed
    class Cache:
        def __init__(self, *args, **kwargs):
            pass
        def init_app(self, app):
            pass
        def cached(self, *args, **kwargs):
            def decorator(f):
                return f
            return decorator
from config import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
admin = Admin(url='/flask-admin')
mail = Mail()
csrf = CSRFProtect()
migrate = Migrate()
# Initialize cache extension
cache = Cache()

def create_app(config_name=None):
    # Utiliser la configuration spécifiée ou détecter depuis l'environnement
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Configure cache: use RedisCache if REDIS_URL is defined, else SimpleCache
    if os.environ.get('REDIS_URL'):
        app.config['CACHE_TYPE'] = 'RedisCache'
        app.config['CACHE_REDIS_URL'] = os.environ['REDIS_URL']
    else:
        app.config['CACHE_TYPE'] = 'SimpleCache'
    cache.init_app(app)
    
    # Activer l'extension Jinja2 pour le tag {% do %}
    app.jinja_env.add_extension('jinja2.ext.do')
    
    # Créer le répertoire des logs si en production
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.routes.main import main
    from app.routes.auth import auth
    from app.routes.modules import modules
    from app.routes.admin import admin_bp
    from app.routes.security import security
    from app.routes.debug import debug
    from app.routes.quiz_sidebar import quiz_sidebar_bp
    from app.routes.quiz import quiz_bp
    from app.routes.phishing import phishing
    
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(modules, url_prefix='/modules')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(security, url_prefix='/security')
    app.register_blueprint(debug, url_prefix='/debug')
    app.register_blueprint(quiz_sidebar_bp, url_prefix='/quiz-sidebar')
    app.register_blueprint(quiz_bp)
    app.register_blueprint(phishing)

    @app.context_processor
    def inject_now():
        return {'now': datetime.datetime.now(datetime.timezone.utc)}
        
    # Désactiver le cache du navigateur pour éviter les problèmes de rechargement
    @app.after_request
    def add_cache_control_headers(response):
        if isinstance(response, Response):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '-1'
        return response
    
    # Create database tables
    with app.app_context():
        # Import models here to ensure they are registered with SQLAlchemy before create_all()
        from app.models.user import User
        from app.models.module import Module, Quiz, Question, Choice, UserProgress
        from app.models.campaign import Campaign, PhishingSimulation, PhishingTarget, Certificate # Corrected imports and added Certificate
        from app.models.settings import Setting
        from app.models.badge import Badge, user_badge_association # Added Badge and association table
        db.create_all()
        
        # Log l'URL de la base de données utilisée
        app.logger.info(f"Utilisation de la base de données: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Configure Flask-Admin with custom views
        from app.admin_views import (
            CustomAdminIndexView, UserAdminView, ModuleAdminView, 
            CampaignAdminView, SettingsAdminView, UserProgressAdminView,
            PhishingSimulationAdminView, CertificateAdminView,
            ReportingView, SystemConfigView
        )
        
        # Initialize admin with custom index view
        admin.init_app(app, index_view=CustomAdminIndexView())
        
        # Add model views
        admin.add_view(UserAdminView(User, db.session, name='Utilisateurs', category='Gestion'))
        admin.add_view(ModuleAdminView(Module, db.session, name='Modules', category='Contenu'))
        admin.add_view(CampaignAdminView(Campaign, db.session, name='Campagnes', category='Phishing'))
        admin.add_view(PhishingSimulationAdminView(PhishingSimulation, db.session, name='Simulations', category='Phishing'))
        admin.add_view(CertificateAdminView(Certificate, db.session, name='Certificats', category='Contenu'))
        admin.add_view(UserProgressAdminView(UserProgress, db.session, name='Progression', category='Rapports'))
        admin.add_view(SettingsAdminView(Setting, db.session, name='Paramètres', category='Système'))
        
        # Add custom views
        admin.add_view(ReportingView(name='Rapports', endpoint='reporting', category='Rapports'))
        admin.add_view(SystemConfigView(name='Configuration', endpoint='systemconfig', category='Système'))
        
        # Configuration des sauvegardes automatiques
        if app.config.get('BACKUP_ENABLED', False) and not app.testing:
            from app.utils.backup import configure_backup
            configure_backup(app)
    
    # Gestion des erreurs CSRF avec logging détaillé
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        # Log détaillé du contexte CSRF
        current_app.logger.warning(
            f"CSRF validation failed: {e.description}, Path: {request.path}, Method: {request.method}, "
            f"X-CSRFToken header: {request.headers.get('X-CSRFToken')}, "
            f"Cookies: {request.cookies}"
        )
        if request.path.startswith('/api/'):
            return jsonify({'status': 'error', 'message': 'CSRF token manquant ou invalide.'}), 400
        return render_template('errors/400_csrf.html', reason=e.description), 400

    # Expose cache for use in views
    app.cache = cache
    return app
