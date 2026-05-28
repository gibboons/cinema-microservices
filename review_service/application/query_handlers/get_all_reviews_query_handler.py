from diator.requests import RequestHandler
from diator.events import Event
from domain.entities.review import Review
from domain.repositories.review_repository_protocol import ReviewRepositoryProtocol
from domain.queries.get_all_reviews_query import GetAllReviewsQuery
from shared.logger import get_logger

logger = get_logger(__name__)

class GetAllReviewsQueryHandler(RequestHandler[GetAllReviewsQuery, list[Review]]):
    def __init__(self, repository: ReviewRepositoryProtocol):
        self._repository = repository
        self._events: list[Event] = []
        logger.info("GetAllReviewsQueryHandler.__init__()")

    @property
    def events(self) -> list[Event]:
        return self._events

    async def handle(self, request: GetAllReviewsQuery) -> list[Review]:
        logger.info("GetAllReviewsQueryHandler.handle()")
        return self._repository.find_all()
