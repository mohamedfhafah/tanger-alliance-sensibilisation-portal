import os
from datetime import timedelta

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_change_in_production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///tanger_alliance.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Authentication
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    
    # Admin
    FLASK_ADMIN_SWATCH = 'cerulean'
