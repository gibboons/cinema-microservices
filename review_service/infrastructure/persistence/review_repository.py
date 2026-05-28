from domain.entities.review import Review
from infrastructure.persistence.models import ReviewModel
from shared.logger import get_logger

logger = get_logger(__name__)

class ReviewRepository:
    def __init__(self, db):
        self.db = db
        logger.info("ReviewRepository.__init__()")

    def save(self, r: Review) -> Review:
        logger.info(f"ReviewRepository.save() - {r.film_title}")
        m = ReviewModel(film_title=r.film_title, reviewer=r.reviewer,
                        review_text=r.review_text, submitted_at=r.submitted_at)
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        r.id = m.id
        return r

    def find_all(self) -> list[Review]:
        logger.info("ReviewRepository.find_all()")
        return [Review(id=m.id, film_title=m.film_title, reviewer=m.reviewer,
                       review_text=m.review_text, submitted_at=m.submitted_at)
                for m in self.db.query(ReviewModel).all()]

    def find_by_film(self, film_title: str) -> list[Review]:
        logger.info(f"ReviewRepository.find_by_film() - {film_title}")
        return [Review(id=m.id, film_title=m.film_title, reviewer=m.reviewer,
                       review_text=m.review_text, submitted_at=m.submitted_at)
                for m in self.db.query(ReviewModel)
                .filter(ReviewModel.film_title == film_title).all()]
