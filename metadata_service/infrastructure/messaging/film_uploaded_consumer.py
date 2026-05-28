import sys, os, asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from diator.mediator import Mediator
from diator.requests import RequestMap
from diator.events import EventMap, EventEmitter
from shared.messaging.base_consumer import BaseConsumer
from shared.container import SimpleContainer
from shared.logger import get_logger

logger = get_logger(__name__)

class FilmUploadedConsumer(BaseConsumer):
    def __init__(self, session_factory, repository_factory):
        super().__init__("FilmUploadedEvent")
        self.session_factory    = session_factory
        self.repository_factory = repository_factory
        logger.info("FilmUploadedConsumer.__init__()")

    def _build_mediator(self, db) -> Mediator:
        from domain.commands.save_metadata_command import SaveMetadataCommand
        from application.command_handlers.save_metadata_command_handler import SaveMetadataCommandHandler
        repo = self.repository_factory(db)
        container = SimpleContainer()
        container.register(SaveMetadataCommandHandler, lambda: SaveMetadataCommandHandler(repo))
        request_map = RequestMap()
        request_map.bind(SaveMetadataCommand, SaveMetadataCommandHandler)
        event_emitter = EventEmitter(event_map=EventMap(), container=container, message_broker=None)
        return Mediator(request_map=request_map, event_emitter=event_emitter, container=container)

    def handle(self, data: dict):
        logger.info(f"FilmUploadedConsumer.handle() - {data}")
        from domain.commands.save_metadata_command import SaveMetadataCommand
        db = self.session_factory()
        try:
            mediator = self._build_mediator(db)
            asyncio.run(mediator.send(SaveMetadataCommand(
                title=data["title"], studio=data["studio"],
                filename=data.get("filename", ""), extension=data.get("extension", ""),
            )))
        finally:
            db.close()
            logger.info("FilmUploadedConsumer.handle() - session closed")
