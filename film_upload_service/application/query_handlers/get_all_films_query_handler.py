from diator.requests import RequestHandler
from diator.events import Event
from domain.entities.film import Film
from domain.repositories.film_repository_protocol import FilmRepositoryProtocol
from domain.queries.get_all_films_query import GetAllFilmsQuery
from shared.logger import get_logger

logger = get_logger(__name__)

class GetAllFilmsQueryHandler(RequestHandler[GetAllFilmsQuery, list[Film]]):
    def __init__(self, repository: FilmRepositoryProtocol):
        self._repository = repository
        self._events: list[Event] = []
        logger.info("GetAllFilmsQueryHandler.__init__()")

    @property
    def events(self) -> list[Event]:
        return self._events

    async def handle(self, request: GetAllFilmsQuery) -> list[Film]:
        logger.info("GetAllFilmsQueryHandler.handle()")
        return self._repository.find_all()
