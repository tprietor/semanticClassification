"""Add the English text artifact path to documents.

Revision ID: f0a1b2c3d4e5
Revises: e9f0a1b2c3d4
"""

from alembic import op
import sqlalchemy as sa


revision = "f0a1b2c3d4e5"
down_revision = "e9f0a1b2c3d4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("english_path", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("documents", "english_path")
