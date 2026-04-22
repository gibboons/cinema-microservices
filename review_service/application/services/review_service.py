from domain.entities.review import Review
from domain.repositories.review_repository_protocol import ReviewRepositoryProtocol
from shared.logger import get_logger

logger = get_logger(__name__)

class ReviewService:
    def __init__(self, repository: ReviewRepositoryProtocol, publisher):
        self.repository = repository
        self.publisher = publisher
        logger.info("ReviewService.__init__()")

    def submit_review(self, film_title: str, reviewer: str, review_text: str) -> Review:
        logger.info(f"ReviewService.submit_review() - title={film_title}, reviewer={reviewer}")
        r = Review(film_title=film_title, reviewer=reviewer, review_text=review_text)
        saved = self.repository.save(r)
        self.publisher.publish({
            "film_title": film_title, "reviewer": reviewer,
            "review": review_text, "timestamp": saved.submitted_at.isoformat()
        })
        return saved

    def get_all(self) -> list[Review]:
        logger.info("ReviewService.get_all()")
        return self.repository.find_all()

    def get_by_film(self, film_title: str) -> list[Review]:
        logger.info(f"ReviewService.get_by_film() - {film_title}")
        return self.repository.find_by_film(film_title)
