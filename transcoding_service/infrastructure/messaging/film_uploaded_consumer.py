import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from shared.messaging.base_consumer import BaseConsumer
from shared.logger import get_logger

logger = get_logger(__name__)

class FilmUploadedConsumer(BaseConsumer):
    def __init__(self, session_factory, service_factory):
        super().__init__("FilmUploadedEvent")
        self.session_factory = session_factory
        self.service_factory = service_factory
        logger.info("FilmUploadedConsumer.__init__()")

    def handle(self, data: dict):
        logger.info(f"FilmUploadedConsumer.handle() - creating job for: {data.get('title')}")
        db = self.session_factory()
        try:
            service = self.service_factory(db)
            service.create_job_from_event(data)
        finally:
            db.close()
            logger.info("FilmUploadedConsumer.handle() - session closed")
