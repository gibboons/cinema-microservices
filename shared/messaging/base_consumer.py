import json, threading
from shared.messaging.connection import get_connection
from shared.logger import get_logger

logger = get_logger(__name__)

class BaseConsumer:
    def __init__(self, exchange_name: str):
        self.exchange_name = exchange_name
        self.connection = get_connection()
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=exchange_name, exchange_type="fanout")
        result = self.channel.queue_declare(queue="", exclusive=True)
        self.queue_name = result.method.queue
        self.channel.queue_bind(exchange=exchange_name, queue=self.queue_name)
        logger.info(f"BaseConsumer.__init__() - bound to: {exchange_name}")

    def handle(self, data: dict):
        raise NotImplementedError

    def _callback(self, ch, method, properties, body):
        data = json.loads(body)
        logger.info(f"BaseConsumer._callback() - {self.exchange_name}: {data}")
        self.handle(data)

    def start_consuming(self):
        logger.info(f"BaseConsumer.start_consuming() - {self.exchange_name}")
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=self._callback, auto_ack=True
        )
        self.channel.start_consuming()

    def start_in_background(self):
        t = threading.Thread(target=self.start_consuming, daemon=True)
        t.start()
        return t
