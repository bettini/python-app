import logging

from budget_app.application.ports.event_bus import EventBus


class NoOpEventBus(EventBus):
    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def publish(self, event_name: str, payload: dict) -> None:
        self._logger.info("event=%s payload=%s", event_name, payload)
