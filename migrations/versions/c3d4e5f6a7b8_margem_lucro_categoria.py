"""margem de lucro na categoria

Revision ID: c3d4e5f6a7b8
Revises: b2c8e9a1d4f0
Create Date: 2026-03-29

"""
from alembic import op
import sqlalchemy as sa


revision = "c3d4e5f6a7b8"
down_revision = "b2c8e9a1d4f0"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "category",
        sa.Column(
            "margem_de_lucro",
            sa.Numeric(8, 2),
            nullable=False,
            server_default="1.10",
        ),
    )


def downgrade():
    with op.batch_alter_table("category", schema=None) as batch_op:
        batch_op.drop_column("margem_de_lucro")
