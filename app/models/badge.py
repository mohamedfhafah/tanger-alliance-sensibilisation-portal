from app import db
from datetime import datetime, timezone

# Association table for User and Badge
user_badge_association = db.Table('user_badge',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('badge_id', db.Integer, db.ForeignKey('badge.id'), primary_key=True),
    db.Column('awarded_at', db.DateTime, default=lambda: datetime.now(timezone.utc))
)

class Badge(db.Model):
    """Modèle pour les badges obtenus par les utilisateurs."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    image_filename = db.Column(db.String(100), nullable=False, default='default_badge.png')
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False, unique=True) # Each module has one unique badge

    # Relationship to users who have earned this badge (many-to-many)
    # users = db.relationship('User', secondary=user_badge_association, back_populates='badges')
    # The back_populates will be defined in the User model

    def __repr__(self):
        return f"Badge('{self.name}', '{self.image_filename}')"
