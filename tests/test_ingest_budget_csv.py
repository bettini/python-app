from budget_app.application.use_cases.ingest_budget_csv import IngestBudgetCsvUseCase


class FakeRepository:
    def __init__(self) -> None:
        self.records = []

    def upsert_budget_records(self, records):
        self.records.extend(records)
        return len(records)

    def list_clients(self):
        return []

    def get_client_budget(self, client_id: str):
        return None


class FakeEventBus:
    def __init__(self) -> None:
        self.events = []

    def publish(self, event_name: str, payload: dict) -> None:
        self.events.append((event_name, payload))


def test_ingest_csv_success() -> None:
    csv_payload = b"client_id,client_name,category,amount,date\nC001,Acme,Marketing,100.50,2026-01-31\n"
    repo = FakeRepository()
    bus = FakeEventBus()

    result = IngestBudgetCsvUseCase(repo, bus).execute(csv_payload)

    assert result.total_rows == 1
    assert result.ingested_records == 1
    assert len(repo.records) == 1
    assert bus.events[0][0] == "budget.ingested"
