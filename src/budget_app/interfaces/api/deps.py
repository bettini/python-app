from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from budget_app.application.use_cases.get_client_budget import GetClientBudgetUseCase
from budget_app.application.use_cases.ingest_budget_csv import IngestBudgetCsvUseCase
from budget_app.application.use_cases.list_clients import ListClientsUseCase
from budget_app.infrastructure.db.session import SessionLocal
from budget_app.infrastructure.messaging import get_event_bus
from budget_app.infrastructure.repositories.sqlalchemy_budget_repository import SqlAlchemyBudgetRepository


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_ingest_use_case(db: Session = Depends(get_db)) -> IngestBudgetCsvUseCase:
    repository = SqlAlchemyBudgetRepository(db)
    event_bus = get_event_bus()
    return IngestBudgetCsvUseCase(repository, event_bus)


def get_client_budget_use_case(db: Session = Depends(get_db)) -> GetClientBudgetUseCase:
    repository = SqlAlchemyBudgetRepository(db)
    return GetClientBudgetUseCase(repository)


def get_list_clients_use_case(db: Session = Depends(get_db)) -> ListClientsUseCase:
    repository = SqlAlchemyBudgetRepository(db)
    return ListClientsUseCase(repository)
