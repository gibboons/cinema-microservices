from domain.entities.rating import Rating
from infrastructure.persistence.models import RatingModel
from shared.logger import get_logger

logger = get_logger(__name__)

class RatingRepository:
    def __init__(self, db):
        self.db = db
        logger.info("RatingRepository.__init__()")

    def save(self, r: Rating) -> Rating:
        logger.info(f"RatingRepository.save() - {r.film_title} score={r.score}")
        m = RatingModel(film_title=r.film_title, user=r.user,
                        score=r.score, submitted_at=r.submitted_at)
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        r.id = m.id
        return r

    def find_all(self) -> list[Rating]:
        logger.info("RatingRepository.find_all()")
        return [Rating(id=m.id, film_title=m.film_title, user=m.user,
                       score=m.score, submitted_at=m.submitted_at)
                for m in self.db.query(RatingModel).all()]
