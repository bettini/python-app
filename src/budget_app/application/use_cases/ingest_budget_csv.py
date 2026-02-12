import csv
import hashlib
import io
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation

from budget_app.application.ports.event_bus import EventBus
from budget_app.application.ports.repositories import BudgetRepository
from budget_app.domain.entities import BudgetRecord

REQUIRED_COLUMNS = {"client_id", "client_name", "category", "amount", "date"}


@dataclass(frozen=True)
class IngestResult:
    ingested_records: int
    total_rows: int


class IngestBudgetCsvUseCase:
    def __init__(self, repository: BudgetRepository, event_bus: EventBus) -> None:
        self._repository = repository
        self._event_bus = event_bus

    def execute(self, csv_bytes: bytes) -> IngestResult:
        decoded = csv_bytes.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(decoded))
        if not reader.fieldnames:
            raise ValueError("CSV has no header")

        normalized_fields = {field.strip() for field in reader.fieldnames if field}
        missing = REQUIRED_COLUMNS - normalized_fields
        if missing:
            raise ValueError(f"CSV missing columns: {', '.join(sorted(missing))}")

        records: list[BudgetRecord] = []
        total_rows = 0

        for row in reader:
            total_rows += 1
            record = self._parse_row(row, total_rows)
            records.append(record)

        ingested = self._repository.upsert_budget_records(records)
        self._event_bus.publish(
            "budget.ingested",
            {
                "ingested_records": ingested,
                "total_rows": total_rows,
            },
        )
        return IngestResult(ingested_records=ingested, total_rows=total_rows)

    def _parse_row(self, row: dict[str, str], line_number: int) -> BudgetRecord:
        try:
            client_id = row["client_id"].strip()
            client_name = row["client_name"].strip()
            category = row["category"].strip()
            amount = Decimal(row["amount"].strip())
            budget_date = datetime.strptime(row["date"].strip(), "%Y-%m-%d").date()
        except KeyError as exc:
            raise ValueError(f"Missing required value in row {line_number}: {exc}") from exc
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"Invalid data format in row {line_number}: {exc}") from exc

        if not client_id or not client_name or not category:
            raise ValueError(f"Empty required value in row {line_number}")

        row_hash = self._build_row_hash(client_id, client_name, category, str(amount), str(budget_date))
        return BudgetRecord(
            client_id=client_id,
            client_name=client_name,
            category=category,
            amount=amount,
            budget_date=budget_date,
            row_hash=row_hash,
        )

    @staticmethod
    def _build_row_hash(*parts: str) -> str:
        payload = "|".join(parts)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
