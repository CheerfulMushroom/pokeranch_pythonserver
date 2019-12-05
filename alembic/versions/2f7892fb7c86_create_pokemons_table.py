"""create pokemons table

Revision ID: 2f7892fb7c86
Revises: 94c39cc88487
Create Date: 2019-12-05 16:17:14.673838

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2f7892fb7c86'
down_revision = '94c39cc88487'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'pokemons',
        sa.Column('id', sa.Integer(), nullable=False, unique=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('power', sa.Integer, nullable=False),
        sa.Column('agility', sa.Integer(), nullable=False),
        sa.Column('loyalty', sa.Integer(), nullable=False),
        sa.Column('satiety', sa.Integer(), nullable=False),
        sa.Column('health', sa.Integer(), nullable=False),
        sa.Column('max_health', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('pokemons')
