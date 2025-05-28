from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    department = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    progress = db.relationship('UserProgress', backref='user', lazy=True)
    
    def __repr__(self):
        return f"User('{self.email}', '{self.role}', '{self.department}')"
    
    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def is_admin(self):
        return self.role == 'admin'
