from diator.requests import RequestHandler
from diator.events import Event
from domain.entities.review import Review
from domain.repositories.review_repository_protocol import ReviewRepositoryProtocol
from domain.queries.get_reviews_by_film_query import GetReviewsByFilmQuery
from shared.logger import get_logger

logger = get_logger(__name__)

class GetReviewsByFilmQueryHandler(RequestHandler[GetReviewsByFilmQuery, list[Review]]):
    def __init__(self, repository: ReviewRepositoryProtocol):
        self._repository = repository
        self._events: list[Event] = []
        logger.info("GetReviewsByFilmQueryHandler.__init__()")

    @property
    def events(self) -> list[Event]:
        return self._events

    async def handle(self, request: GetReviewsByFilmQuery) -> list[Review]:
        logger.info(f"GetReviewsByFilmQueryHandler.handle() - film={request.film_title}")
        return self._repository.find_by_film(request.film_title)
