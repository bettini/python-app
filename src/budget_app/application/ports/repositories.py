from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Protocol

from budget_app.domain.entities import BudgetRecord, Client


@dataclass(frozen=True)
class ClientBudgetLine:
    category: str
    amount: Decimal
    budget_date: date


@dataclass(frozen=True)
class ClientBudgetView:
    client: Client
    lines: list[ClientBudgetLine]
    total_amount: Decimal


class BudgetRepository(Protocol):
    def upsert_budget_records(self, records: list[BudgetRecord]) -> int:
        ...

    def list_clients(self) -> list[Client]:
        ...

    def get_client_budget(self, client_id: str) -> ClientBudgetView | None:
        ...
