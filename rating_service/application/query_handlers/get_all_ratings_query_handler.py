from diator.requests import RequestHandler
from diator.events import Event
from domain.entities.rating import Rating
from domain.repositories.rating_repository_protocol import RatingRepositoryProtocol
from domain.queries.get_all_ratings_query import GetAllRatingsQuery
from shared.logger import get_logger

logger = get_logger(__name__)

class GetAllRatingsQueryHandler(RequestHandler[GetAllRatingsQuery, list[Rating]]):
    def __init__(self, repository: RatingRepositoryProtocol):
        self._repository = repository
        self._events: list[Event] = []
        logger.info("GetAllRatingsQueryHandler.__init__()")

    @property
    def events(self) -> list[Event]:
        return self._events

    async def handle(self, request: GetAllRatingsQuery) -> list[Rating]:
        logger.info("GetAllRatingsQueryHandler.handle()")
        return self._repository.find_all()
