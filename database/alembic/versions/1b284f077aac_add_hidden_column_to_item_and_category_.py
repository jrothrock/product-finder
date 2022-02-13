"""add hidden column to item and category table.

Revision ID: 1b284f077aac
Revises:
Create Date: 2022-01-17 19:38:16.033315

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1b284f077aac"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create hidden fields for category and item records."""
    op.add_column("category", sa.Column("hidden", sa.Boolean))
    op.add_column("item", sa.Column("hidden", sa.Boolean))


def downgrade():
    """Remove hidden fields for category and item records."""
    op.drop_column("category", "hidden")
    op.drop_column("item", "hidden")
