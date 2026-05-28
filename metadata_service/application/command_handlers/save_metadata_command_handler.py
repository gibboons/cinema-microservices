from diator.requests import RequestHandler
from diator.events import Event
from domain.entities.metadata import Metadata
from domain.repositories.metadata_repository_protocol import MetadataRepositoryProtocol
from domain.commands.save_metadata_command import SaveMetadataCommand
from shared.logger import get_logger

logger = get_logger(__name__)

class SaveMetadataCommandHandler(RequestHandler[SaveMetadataCommand, Metadata]):
    def __init__(self, repository: MetadataRepositoryProtocol):
        self._repository = repository
        self._events: list[Event] = []
        logger.info("SaveMetadataCommandHandler.__init__()")

    @property
    def events(self) -> list[Event]:
        return self._events

    async def handle(self, request: SaveMetadataCommand) -> Metadata:
        logger.info(f"SaveMetadataCommandHandler.handle() - title={request.title}")
        m = Metadata(film_title=request.title, studio=request.studio,
                     filename=request.filename, extension=request.extension)
        return self._repository.save(m)
