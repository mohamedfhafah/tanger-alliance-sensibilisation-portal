from app import db
from datetime import datetime, timezone

class Setting(db.Model):
    """Modèle pour les paramètres de configuration de l'application"""
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True) # Utiliser Text pour permettre des valeurs plus longues
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Setting key='{self.key}' value='{self.value[:50]}'>"
