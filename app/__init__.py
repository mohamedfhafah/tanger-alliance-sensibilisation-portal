from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from config import Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
admin = Admin(template_mode='bootstrap4')

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    admin.init_app(app)
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.routes.main import main
    from app.routes.auth import auth
    
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
