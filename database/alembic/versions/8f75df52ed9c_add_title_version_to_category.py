"""add title_version to category.

Revision ID: 8f75df52ed9c
Revises: 1b284f077aac
Create Date: 2022-01-17 20:03:15.047880

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8f75df52ed9c"
down_revision = "1b284f077aac"
branch_labels = None
depends_on = None


def upgrade():
    """Create title_version field for category records."""
    op.add_column("category", sa.Column("title_version", sa.Integer))


def downgrade():
    """Remove title_version field for category records."""
    op.drop_column("category", "title_version")
