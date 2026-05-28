from diator.requests import RequestHandler
from diator.events import Event
from domain.entities.recommendation import Recommendation
from domain.repositories.recommendation_repository_protocol import RecommendationRepositoryProtocol
from domain.queries.get_all_recommendations_query import GetAllRecommendationsQuery
from shared.logger import get_logger

logger = get_logger(__name__)

class GetAllRecommendationsQueryHandler(RequestHandler[GetAllRecommendationsQuery, list[Recommendation]]):
    def __init__(self, repository: RecommendationRepositoryProtocol):
        self._repository = repository
        self._events: list[Event] = []
        logger.info("GetAllRecommendationsQueryHandler.__init__()")

    @property
    def events(self) -> list[Event]:
        return self._events

    async def handle(self, request: GetAllRecommendationsQuery) -> list[Recommendation]:
        logger.info("GetAllRecommendationsQueryHandler.handle()")
        return self._repository.find_all()
