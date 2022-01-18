"""add hidden column to item and category table

Revision ID: 1b284f077aac
Revises: 
Create Date: 2022-01-17 19:38:16.033315

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b284f077aac'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('category', sa.Column('hidden', sa.Boolean))
    op.add_column('item', sa.Column('hidden', sa.Boolean))

def downgrade():
    op.drop_column('category', 'hidden')
    op.drop_column('item', 'hidden')
