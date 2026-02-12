from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from budget_app.application.ports.repositories import BudgetRepository, ClientBudgetLine, ClientBudgetView
from budget_app.domain.entities import BudgetRecord, Client
from budget_app.infrastructure.db.models import BudgetModel, ClientModel


class SqlAlchemyBudgetRepository(BudgetRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert_budget_records(self, records: list[BudgetRecord]) -> int:
        inserted = 0
        # Track which client_ids we've already staged for insert in this batch
        staged_clients: set[str] = set()
        for record in records:
            client = self._session.get(ClientModel, record.client_id)
            if not client and record.client_id not in staged_clients:
                client = ClientModel(id=record.client_id, name=record.client_name)
                self._session.add(client)
                staged_clients.add(record.client_id)
            elif client and client.name != record.client_name:
                client.name = record.client_name

            existing = self._session.execute(
                select(BudgetModel).where(BudgetModel.row_hash == record.row_hash)
            ).scalar_one_or_none()

            if existing:
                continue

            budget = BudgetModel(
                client_id=record.client_id,
                category=record.category,
                amount=record.amount,
                budget_date=record.budget_date,
                row_hash=record.row_hash,
            )
            self._session.add(budget)
            inserted += 1

        self._session.commit()
        return inserted

    def list_clients(self) -> list[Client]:
        rows = self._session.execute(select(ClientModel).order_by(ClientModel.name.asc())).scalars().all()
        return [Client(client_id=row.id, client_name=row.name) for row in rows]

    def get_client_budget(self, client_id: str) -> ClientBudgetView | None:
        client = self._session.get(ClientModel, client_id)
        if not client:
            return None

        budget_rows = self._session.execute(
            select(BudgetModel)
            .where(BudgetModel.client_id == client_id)
            .order_by(BudgetModel.budget_date.desc(), BudgetModel.category.asc())
        ).scalars().all()

        lines = [
            ClientBudgetLine(
                category=row.category,
                amount=Decimal(row.amount),
                budget_date=row.budget_date,
            )
            for row in budget_rows
        ]
        total = sum((line.amount for line in lines), Decimal("0"))

        return ClientBudgetView(
            client=Client(client_id=client.id, client_name=client.name),
            lines=lines,
            total_amount=total,
        )
