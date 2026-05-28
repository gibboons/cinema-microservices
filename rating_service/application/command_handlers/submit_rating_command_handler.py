from diator.requests import RequestHandler
from diator.events import Event
from domain.entities.rating import Rating
from domain.entities.recommendation import Recommendation
from domain.repositories.rating_repository_protocol import RatingRepositoryProtocol
from domain.repositories.recommendation_repository_protocol import RecommendationRepositoryProtocol
from domain.commands.submit_rating_command import SubmitRatingCommand
from shared.logger import get_logger

logger = get_logger(__name__)

class SubmitRatingCommandHandler(RequestHandler[SubmitRatingCommand, Rating]):
    def __init__(self, rating_repository: RatingRepositoryProtocol,
                 recommendation_repository: RecommendationRepositoryProtocol,
                 rating_publisher, recommendation_publisher):
        self._rating_repo         = rating_repository
        self._recommendation_repo = recommendation_repository
        self._rating_publisher    = rating_publisher
        self._recommendation_publisher = recommendation_publisher
        self._events: list[Event] = []
        logger.info("SubmitRatingCommandHandler.__init__()")

    @property
    def events(self) -> list[Event]:
        return self._events

    async def handle(self, request: SubmitRatingCommand) -> Rating:
        logger.info(f"SubmitRatingCommandHandler.handle() - film={request.film_title}, score={request.score}")
        r = Rating(film_title=request.film_title, user=request.user, score=request.score)
        saved = self._rating_repo.save(r)
        self._rating_publisher.publish({
            "film_title": request.film_title, "user": request.user,
            "score": request.score, "timestamp": saved.submitted_at.isoformat(),
        })
        reason = (f"Wysoko oceniony z wynikiem {request.score}"
                  if request.score >= 7.0
                  else f"Umiarkowanie oceniony z wynikiem {request.score}")
        rec = Recommendation(film_title=request.film_title, reason=reason)
        saved_rec = self._recommendation_repo.save(rec)
        self._recommendation_publisher.publish({
            "film_title": saved_rec.film_title, "reason": saved_rec.reason,
            "timestamp": saved_rec.generated_at.isoformat(),
        })
        logger.info("SubmitRatingCommandHandler.handle() - recommendation generated")
        return saved
