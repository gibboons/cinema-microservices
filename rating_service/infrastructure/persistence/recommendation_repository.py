from domain.entities.recommendation import Recommendation
from infrastructure.persistence.models import RecommendationModel
from shared.logger import get_logger

logger = get_logger(__name__)

class RecommendationRepository:
    def __init__(self, db):
        self.db = db
        logger.info("RecommendationRepository.__init__()")

    def save(self, r: Recommendation) -> Recommendation:
        logger.info(f"RecommendationRepository.save() - {r.film_title}")
        m = RecommendationModel(film_title=r.film_title, reason=r.reason,
                                generated_at=r.generated_at)
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        r.id = m.id
        return r

    def find_all(self) -> list[Recommendation]:
        logger.info("RecommendationRepository.find_all()")
        return [Recommendation(id=m.id, film_title=m.film_title, reason=m.reason,
                               generated_at=m.generated_at)
                for m in self.db.query(RecommendationModel).all()]
