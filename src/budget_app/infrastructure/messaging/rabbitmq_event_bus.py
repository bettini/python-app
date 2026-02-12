import json

import pika

from budget_app.application.ports.event_bus import EventBus


class RabbitMqEventBus(EventBus):
    def __init__(self, rabbitmq_url: str) -> None:
        self._rabbitmq_url = rabbitmq_url

    def publish(self, event_name: str, payload: dict) -> None:
        params = pika.URLParameters(self._rabbitmq_url)
        connection = pika.BlockingConnection(params)
        try:
            channel = connection.channel()
            channel.queue_declare(queue=event_name, durable=True)
            channel.basic_publish(
                exchange="",
                routing_key=event_name,
                body=json.dumps(payload).encode("utf-8"),
                properties=pika.BasicProperties(delivery_mode=2),
            )
        finally:
            connection.close()
