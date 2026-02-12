"""initial

Revision ID: 20260212_0001
Revises: 
Create Date: 2026-02-12

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260212_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "clients",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "budgets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("client_id", sa.String(length=64), nullable=False),
        sa.Column("category", sa.String(length=128), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("budget_date", sa.Date(), nullable=False),
        sa.Column("row_hash", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("row_hash", name="uq_budget_row_hash"),
    )
    op.create_index("ix_budgets_client_id", "budgets", ["client_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_budgets_client_id", table_name="budgets")
    op.drop_table("budgets")
    op.drop_table("clients")
