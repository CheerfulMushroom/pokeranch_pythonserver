"""create users table

Revision ID: 94c39cc88487
Revises: 
Create Date: 2019-12-05 16:17:03.677546

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94c39cc88487'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, unique=True),
        sa.Column('login', sa.String(64), nullable=False, unique=True),
        sa.Column('mail', sa.String(64), nullable=False, unique=True),
        sa.Column('password', sa.String(64), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('users')
