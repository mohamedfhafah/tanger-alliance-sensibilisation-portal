from app import db
from datetime import datetime, timezone

class SimulationRating(db.Model):
    __tablename__ = 'simulation_ratings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    simulation_slug = db.Column(db.String(64), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1 à 5
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'simulation_slug', name='uq_user_simulation_rating'),)

    def __repr__(self):
        return f'<SimulationRating user={self.user_id} sim={self.simulation_slug} rating={self.rating}>'
