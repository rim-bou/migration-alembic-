"""add nb_enfants, quotient_caf and client_sensitive

Revision ID: 0002
Revises: 0001
Create Date: 2025-12-24
"""

from alembic import op
import sqlalchemy as sa

# NOTE: for a real repo, set proper revision hashes.
revision = "0002"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add columns to existing clients table (safe: nullable)
    with op.batch_alter_table("clients") as batch:
        batch.add_column(sa.Column("nb_enfants", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("quotient_caf", sa.Float(), nullable=True))

    # Create new sensitive table (1-1 via unique constraint)
    op.create_table(
        "client_sensitive",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("orientation_sexuelle", sa.String(length=50), nullable=True),
        sa.UniqueConstraint("client_id", name="uq_client_sensitive_client_id"),
    )

def downgrade() -> None:
    op.drop_table("client_sensitive")
    with op.batch_alter_table("clients") as batch:
        batch.drop_column("quotient_caf")
        batch.drop_column("nb_enfants")
