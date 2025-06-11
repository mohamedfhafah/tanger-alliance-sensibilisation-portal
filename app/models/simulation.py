from app import db
from datetime import datetime, timezone

class SimulationAttempt(db.Model):
    __tablename__ = 'simulation_attempts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    simulation_slug = db.Column(db.String(64), nullable=False)
    action = db.Column(db.String(32), nullable=False)
    success = db.Column(db.Boolean, nullable=False)
    feedback = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f'<SimulationAttempt user={self.user_id} sim={self.simulation_slug} action={self.action} success={self.success}>'
