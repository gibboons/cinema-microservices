from diator.requests import RequestHandler
from diator.events import Event
from domain.repositories.film_repository_protocol import FilmRepositoryProtocol
from domain.queries.get_file_from_s3_query import GetFileFromS3Query
from shared.logger import get_logger

logger = get_logger(__name__)

class GetFileFromS3QueryHandler(RequestHandler[GetFileFromS3Query, str]):
    def __init__(self, repository: FilmRepositoryProtocol, s3_storage):
        self._repository = repository
        self._s3_storage = s3_storage
        self._events: list[Event] = []
        logger.info("GetFileFromS3QueryHandler.__init__()")

    @property
    def events(self) -> list[Event]:
        return self._events

    async def handle(self, request: GetFileFromS3Query) -> str:
        logger.info(f"GetFileFromS3QueryHandler.handle() - film_id={request.film_id}")
        film = self._repository.find_by_id(request.film_id)
        if not film:
            raise ValueError(f"Film {request.film_id} not found")
        url = self._s3_storage.get_presigned_url(film.s3_key)
        logger.info("GetFileFromS3QueryHandler.handle() - presigned url generated")
        return url
