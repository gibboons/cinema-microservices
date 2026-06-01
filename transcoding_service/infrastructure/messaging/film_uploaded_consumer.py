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
    def __init__(self, repository_factory):
        super().__init__("FilmUploadedEvent")
        self.repository_factory = repository_factory
        logger.info("FilmUploadedConsumer.__init__()")

    def _build_mediator(self) -> Mediator:
        from domain.commands.create_transcoding_job_command import CreateTranscodingJobCommand
        from application.command_handlers.create_transcoding_job_command_handler import CreateTranscodingJobCommandHandler
        repo = self.repository_factory()

        container = SimpleContainer()
        container.register(CreateTranscodingJobCommandHandler,
                           lambda: CreateTranscodingJobCommandHandler(repo))
        request_map = RequestMap()
        request_map.bind(CreateTranscodingJobCommand, CreateTranscodingJobCommandHandler)
        event_emitter = EventEmitter(event_map=EventMap(), container=container, message_broker=None)
        return Mediator(request_map=request_map, event_emitter=event_emitter, container=container)

    def handle(self, data: dict):
        logger.info(f"FilmUploadedConsumer.handle() - title={data.get('title')}")
        from domain.commands.create_transcoding_job_command import CreateTranscodingJobCommand
        try:
            mediator = self._build_mediator()
            asyncio.run(mediator.send(CreateTranscodingJobCommand(
                title=data["title"], studio=data["studio"],
            )))
        except Exception as e:
            logger.error(f"FilmUploadedConsumer.handle() - error: {e}")
