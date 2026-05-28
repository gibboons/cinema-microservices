from diator.requests import RequestHandler
from diator.events import Event
from domain.entities.transcoding_job import TranscodingJob
from domain.repositories.transcoding_repository_protocol import TranscodingRepositoryProtocol
from domain.commands.create_transcoding_job_command import CreateTranscodingJobCommand
from shared.logger import get_logger

logger = get_logger(__name__)

class CreateTranscodingJobCommandHandler(RequestHandler[CreateTranscodingJobCommand, TranscodingJob]):
    def __init__(self, repository: TranscodingRepositoryProtocol):
        self._repository = repository
        self._events: list[Event] = []
        logger.info("CreateTranscodingJobCommandHandler.__init__()")

    @property
    def events(self) -> list[Event]:
        return self._events

    async def handle(self, request: CreateTranscodingJobCommand) -> TranscodingJob:
        logger.info(f"CreateTranscodingJobCommandHandler.handle() - title={request.title}")
        job = TranscodingJob(film_title=request.title, studio=request.studio)
        return self._repository.save(job)
