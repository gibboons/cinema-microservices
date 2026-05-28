import json
from shared.messaging.connection import get_connection
from shared.logger import get_logger

logger = get_logger(__name__)

class BasePublisher:
    def __init__(self, exchange_name: str):
        self.exchange_name = exchange_name
        self.connection = get_connection()
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=exchange_name, exchange_type="fanout")
        logger.info(f"BasePublisher.__init__() - exchange: {exchange_name}")

    def publish(self, data: dict):
        logger.info(f"BasePublisher.publish() - {self.exchange_name}: {data}")
        self.channel.basic_publish(
            exchange=self.exchange_name, routing_key="", body=json.dumps(data)
        )
