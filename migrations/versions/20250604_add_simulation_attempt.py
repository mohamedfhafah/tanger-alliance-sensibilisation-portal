"""
Migration : Ajout du modèle SimulationAttempt pour le tracking des simulations immersives.
"""
from alembic import op
import sqlalchemy as sa

# Alembic identifiers
revision = '20250604_add_simulation_attempt'
down_revision = '6de55fe79c1b'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'simulation_attempts',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), nullable=False),
        sa.Column('simulation_slug', sa.String(64), nullable=False),
        sa.Column('action', sa.String(32), nullable=False),
        sa.Column('success', sa.Boolean, nullable=False),
        sa.Column('feedback', sa.Text, nullable=True),
        sa.Column('timestamp', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table('simulation_attempts')
