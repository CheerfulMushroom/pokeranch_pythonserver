"""create_trainers_table

Revision ID: 72b750f82745
Revises: 9b5a775ee31a
Create Date: 2019-12-18 11:23:49.461245

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '72b750f82745'
down_revision = '9b5a775ee31a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'trainers',
        sa.Column('id', sa.Integer(), nullable=False, unique=True, primary_key=True, autoincrement=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(64), nullable=False),
    )


def downgrade():
    op.drop_table('trainers')
