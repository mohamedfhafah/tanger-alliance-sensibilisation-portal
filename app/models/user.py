from app import db, login_manager, bcrypt
from flask_login import UserMixin
from datetime import datetime, timezone, timedelta
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    firstname = db.Column(db.String(50), nullable=True)
    lastname = db.Column(db.String(50), nullable=True)
    # Stocke le hash du mot de passe ; 128 caractères pour accommodate PBKDF2 & autres algos
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    department = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime, nullable=True)
    last_security_training = db.Column(db.DateTime, nullable=True, comment="Date de la dernière formation de sécurité suivie")
    profile_picture = db.Column(db.String(100), nullable=True, default='default_profile.jpg')
    
    # Relationships
    progress = db.relationship('UserProgress', backref='user', lazy=True)
    badges = db.relationship('Badge', secondary='user_badge', backref=db.backref('users', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return f"User('{self.email}', '{self.role}', '{self.department}')"
    
    def update_last_login(self):
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()
    
    def is_admin(self):
        return self.role == 'admin'

    def get_reset_token(self, expires_sec=1800):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expires_sec)
            user_id = data.get('user_id')
        except Exception:
            return None
        from app import db
        return db.session.get(User, user_id)

    # -------- Gestion des mots de passe --------
    def set_password(self, plain_password: str):
        """Hash le mot de passe avec Bcrypt et le stocke."""
        self.password = bcrypt.generate_password_hash(plain_password).decode('utf-8')

    def check_password(self, plain_password: str) -> bool:
        """Vérifie la correspondance mot de passe/hash."""
        return bcrypt.check_password_hash(self.password, plain_password)
