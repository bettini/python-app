from budget_app.application.ports.repositories import BudgetRepository, ClientBudgetView


class GetClientBudgetUseCase:
    def __init__(self, repository: BudgetRepository) -> None:
        self._repository = repository

    def execute(self, client_id: str) -> ClientBudgetView | None:
        return self._repository.get_client_budget(client_id)
