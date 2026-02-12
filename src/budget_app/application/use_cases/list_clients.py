from budget_app.application.ports.repositories import BudgetRepository
from budget_app.domain.entities import Client


class ListClientsUseCase:
    def __init__(self, repository: BudgetRepository) -> None:
        self._repository = repository

    def execute(self) -> list[Client]:
        return self._repository.list_clients()