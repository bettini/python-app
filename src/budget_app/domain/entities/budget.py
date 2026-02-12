from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class BudgetRecord:
    client_id: str
    client_name: str
    category: str
    amount: Decimal
    budget_date: date
    row_hash: str
