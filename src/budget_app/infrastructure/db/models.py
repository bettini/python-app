from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from budget_app.infrastructure.db.base import Base


class ClientModel(Base):
    __tablename__ = "clients"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    budgets = relationship("BudgetModel", back_populates="client", cascade="all, delete-orphan")


class BudgetModel(Base):
    __tablename__ = "budgets"
    __table_args__ = (UniqueConstraint("row_hash", name="uq_budget_row_hash"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), index=True)
    category: Mapped[str] = mapped_column(String(128), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    budget_date: Mapped[date] = mapped_column(Date, nullable=False)
    row_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    client = relationship("ClientModel", back_populates="budgets")
