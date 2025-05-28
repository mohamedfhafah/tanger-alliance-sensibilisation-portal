from app import db
from datetime import datetime

class Campaign(db.Model):
    """Modèle pour les campagnes de sensibilisation"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    phishing_simulations = db.relationship('PhishingSimulation', backref='campaign', lazy=True)
    
    def __repr__(self):
        return f"Campaign('{self.name}', status='{self.status}')"


class PhishingSimulation(db.Model):
    """Modèle pour les simulations de phishing"""
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    template = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    targets = db.relationship('PhishingTarget', backref='simulation', lazy=True)
    
    def __repr__(self):
        return f"PhishingSimulation('{self.title}', campaign_id={self.campaign_id})"


class PhishingTarget(db.Model):
    """Modèle pour les cibles d'une simulation de phishing"""
    id = db.Column(db.Integer, primary_key=True)
    simulation_id = db.Column(db.Integer, db.ForeignKey('phishing_simulation.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sent = db.Column(db.Boolean, default=False)
    opened = db.Column(db.Boolean, default=False)
    clicked = db.Column(db.Boolean, default=False)
    reported = db.Column(db.Boolean, default=False)
    opened_at = db.Column(db.DateTime, nullable=True)
    clicked_at = db.Column(db.DateTime, nullable=True)
    reported_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f"PhishingTarget(user_id={self.user_id}, simulation_id={self.simulation_id}, clicked={self.clicked})"


class Certificate(db.Model):
    """Modèle pour les certificats de réussite"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    issued_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime, nullable=True)
    certificate_id = db.Column(db.String(50), nullable=False, unique=True)
    
    def __repr__(self):
        return f"Certificate('{self.title}', user_id={self.user_id}, issued_at={self.issued_at})"
