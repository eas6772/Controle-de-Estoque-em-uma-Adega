"""codigo de barras opcional no produto

Revision ID: b2c8e9a1d4f0
Revises: 4fb374ab16f8
Create Date: 2026-03-28

"""
from alembic import op
import sqlalchemy as sa


revision = "b2c8e9a1d4f0"
down_revision = "4fb374ab16f8"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("product", schema=None) as batch_op:
        batch_op.alter_column(
            "codigo_barras",
            existing_type=sa.String(length=30),
            nullable=True,
        )


def downgrade():
    conn = op.get_bind()
    conn.execute(
        sa.text("UPDATE product SET codigo_barras = 'LEGADO-' || CAST(id AS VARCHAR) WHERE codigo_barras IS NULL")
    )
    with op.batch_alter_table("product", schema=None) as batch_op:
        batch_op.alter_column(
            "codigo_barras",
            existing_type=sa.String(length=30),
            nullable=False,
        )
