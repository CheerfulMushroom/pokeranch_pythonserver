"""create tokens table

Revision ID: 9b5a775ee31a
Revises: 2f7892fb7c86
Create Date: 2019-12-06 14:21:53.457261

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9b5a775ee31a'
down_revision = '2f7892fb7c86'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'tokens',
        sa.Column('user_id', sa.Integer(), nullable=False, unique=True),
        sa.Column('token', sa.String(50), nullable=False, unique=True),
        sa.PrimaryKeyConstraint('user_id'),
    )


def downgrade():
    op.drop_table('tokens')
