from typing import Protocol


class EventBus(Protocol):
    def publish(self, event_name: str, payload: dict) -> None:
        ...
