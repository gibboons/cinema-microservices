from domain.entities.rating import Rating
from domain.entities.recommendation import Recommendation
from domain.repositories.rating_repository_protocol import RatingRepositoryProtocol
from domain.repositories.recommendation_repository_protocol import RecommendationRepositoryProtocol
from shared.logger import get_logger

logger = get_logger(__name__)

class RatingService:
    def __init__(self, rating_repository: RatingRepositoryProtocol,
                 recommendation_repository: RecommendationRepositoryProtocol,
                 rating_publisher, recommendation_publisher):
        self.rating_repository = rating_repository
        self.recommendation_repository = recommendation_repository
        self.rating_publisher = rating_publisher
        self.recommendation_publisher = recommendation_publisher
        logger.info("RatingService.__init__()")

    def submit_rating(self, film_title: str, user: str, score: float) -> Rating:
        logger.info(f"RatingService.submit_rating() - title={film_title}, user={user}, score={score}")
        r = Rating(film_title=film_title, user=user, score=score)
        saved = self.rating_repository.save(r)
        self.rating_publisher.publish({
            "film_title": film_title, "user": user,
            "score": score, "timestamp": saved.submitted_at.isoformat()
        })
        return saved

    def generate_recommendation_from_event(self, data: dict) -> Recommendation:
        logger.info(f"RatingService.generate_recommendation_from_event() - {data}")
        score = data.get("score", 0)
        reason = f"Highly rated with score {score}" if score >= 7.0 else f"Moderately rated with score {score}"
        rec = Recommendation(film_title=data["film_title"], reason=reason)
        saved = self.recommendation_repository.save(rec)
        self.recommendation_publisher.publish({
            "film_title": saved.film_title, "reason": saved.reason,
            "timestamp": saved.generated_at.isoformat()
        })
        return saved

    def get_all_ratings(self) -> list[Rating]:
        logger.info("RatingService.get_all_ratings()")
        return self.rating_repository.find_all()

    def get_all_recommendations(self) -> list[Recommendation]:
        logger.info("RatingService.get_all_recommendations()")
        return self.recommendation_repository.find_all()
