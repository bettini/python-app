from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class IngestResponse(BaseModel):
    ingested_records: int
    total_rows: int


class ClientResponse(BaseModel):
    client_id: str
    client_name: str


class BudgetLineResponse(BaseModel):
    category: str
    amount: Decimal
    date: date


class ClientBudgetResponse(BaseModel):
    client_id: str
    client_name: str
    total_amount: Decimal
    lines: list[BudgetLineResponse]
