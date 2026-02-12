
import csv
import hashlib
import io
import logging
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
        self._logger = logging.getLogger(__name__)

    def execute(self, csv_bytes: bytes) -> IngestResult:
        self._logger.info("Starting CSV ingestion")
        decoded = csv_bytes.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(decoded))
        if not reader.fieldnames:
            self._logger.error("CSV has no header")
            raise ValueError("CSV has no header")

        normalized_fields = {field.strip() for field in reader.fieldnames if field}
        missing = REQUIRED_COLUMNS - normalized_fields
        if missing:
            self._logger.error(f"CSV missing columns: {', '.join(sorted(missing))}")
            raise ValueError(f"CSV missing columns: {', '.join(sorted(missing))}")

        records: list[BudgetRecord] = []
        total_rows = 0

        for row in reader:
            total_rows += 1
            try:
                record = self._parse_row(row, total_rows)
                records.append(record)
            except Exception as exc:
                self._logger.error(f"Row %d skipped: %s", total_rows, exc)
                raise

        self._logger.info("Parsed %d rows, ingesting to repository", total_rows)
        ingested = self._repository.upsert_budget_records(records)
        self._logger.info("Ingested %d new records (out of %d)", ingested, total_rows)
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
            self._logger.error(f"Missing required value in row %d: %s", line_number, exc)
            raise ValueError(f"Missing required value in row {line_number}: {exc}") from exc
        except (InvalidOperation, ValueError) as exc:
            self._logger.error(f"Invalid data format in row %d: %s", line_number, exc)
            raise ValueError(f"Invalid data format in row {line_number}: {exc}") from exc

        if not client_id or not client_name or not category:
            self._logger.error(f"Empty required value in row %d", line_number)
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
