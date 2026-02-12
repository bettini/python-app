from budget_app.config import get_settings
from budget_app.infrastructure.messaging.noop_event_bus import NoOpEventBus
from budget_app.infrastructure.messaging.rabbitmq_event_bus import RabbitMqEventBus


def get_event_bus():
    settings = get_settings()
    if settings.rabbitmq_enabled:
        return RabbitMqEventBus(settings.rabbitmq_url)
    return NoOpEventBus()
