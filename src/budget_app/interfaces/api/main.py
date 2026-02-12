import logging

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile

from budget_app.application.use_cases.get_client_budget import GetClientBudgetUseCase
from budget_app.application.use_cases.ingest_budget_csv import IngestBudgetCsvUseCase
from budget_app.application.use_cases.list_clients import ListClientsUseCase
from budget_app.config import get_settings
from budget_app.infrastructure.logging.config import configure_logging
from budget_app.interfaces.api.deps import get_client_budget_use_case, get_ingest_use_case, get_list_clients_use_case
from budget_app.interfaces.api.schemas import (
    BudgetLineResponse,
    ClientBudgetResponse,
    ClientResponse,
    IngestResponse,
)

settings = get_settings()
app = FastAPI(title=settings.app_name)
logger = logging.getLogger(__name__)


@app.on_event("startup")
def startup_event() -> None:
    configure_logging()
    logger.info("API startup complete")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/budgets/upload-csv", response_model=IngestResponse)
async def upload_budget_csv(
    file: UploadFile = File(...),
    use_case: IngestBudgetCsvUseCase = Depends(get_ingest_use_case),
) -> IngestResponse:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    payload = await file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="File is empty")

    try:
        result = use_case.execute(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return IngestResponse(ingested_records=result.ingested_records, total_rows=result.total_rows)


@app.get("/clients", response_model=list[ClientResponse])
def list_clients(use_case: ListClientsUseCase = Depends(get_list_clients_use_case)) -> list[ClientResponse]:
    clients = use_case.execute()
    return [ClientResponse(client_id=client.client_id, client_name=client.client_name) for client in clients]


@app.get("/clients/{client_id}/budget", response_model=ClientBudgetResponse)
def get_client_budget(
    client_id: str,
    use_case: GetClientBudgetUseCase = Depends(get_client_budget_use_case),
) -> ClientBudgetResponse:
    budget_view = use_case.execute(client_id)
    if not budget_view:
        raise HTTPException(status_code=404, detail="Client not found")

    return ClientBudgetResponse(
        client_id=budget_view.client.client_id,
        client_name=budget_view.client.client_name,
        total_amount=budget_view.total_amount,
        lines=[
            BudgetLineResponse(category=line.category, amount=line.amount, date=line.budget_date)
            for line in budget_view.lines
        ],
    )
