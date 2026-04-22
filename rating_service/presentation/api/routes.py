from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from infrastructure.persistence.database import get_db
from infrastructure.persistence.rating_repository import RatingRepository
from infrastructure.persistence.recommendation_repository import RecommendationRepository
from infrastructure.messaging.rating_publisher import RatingSubmittedPublisher
from infrastructure.messaging.recommendation_publisher import RecommendationGeneratedPublisher
from application.services.rating_service import RatingService
from presentation.api.schemas import SubmitRatingRequest, RatingResponse, RecommendationResponse
from shared.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["ratings"])

def get_service(db: Session = Depends(get_db)):
    return RatingService(
        RatingRepository(db), RecommendationRepository(db),
        RatingSubmittedPublisher(), RecommendationGeneratedPublisher()
    )

@router.post("/ratings", response_model=RatingResponse, status_code=201)
def submit_rating(body: SubmitRatingRequest, service: RatingService = Depends(get_service)):
    logger.info(f"routes.submit_rating() - film={body.film_title}, score={body.score}")
    r = service.submit_rating(body.film_title, body.user, body.score)
    return RatingResponse(id=r.id, film_title=r.film_title, user=r.user,
                          score=r.score, submitted_at=r.submitted_at)

@router.get("/ratings", response_model=List[RatingResponse])
def list_ratings(service: RatingService = Depends(get_service)):
    logger.info("routes.list_ratings()")
    return [RatingResponse(id=r.id, film_title=r.film_title, user=r.user,
                           score=r.score, submitted_at=r.submitted_at)
            for r in service.get_all_ratings()]

@router.get("/recommendations", response_model=List[RecommendationResponse])
def list_recommendations(service: RatingService = Depends(get_service)):
    logger.info("routes.list_recommendations()")
    return [RecommendationResponse(id=r.id, film_title=r.film_title, reason=r.reason,
                                   generated_at=r.generated_at)
            for r in service.get_all_recommendations()]
