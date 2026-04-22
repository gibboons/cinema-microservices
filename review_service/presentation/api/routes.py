from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from infrastructure.persistence.database import get_db
from infrastructure.persistence.review_repository import ReviewRepository
from infrastructure.messaging.review_publisher import ReviewSubmittedPublisher
from application.services.review_service import ReviewService
from presentation.api.schemas import SubmitReviewRequest, ReviewResponse
from shared.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/reviews", tags=["reviews"])

def get_service(db: Session = Depends(get_db)):
    return ReviewService(ReviewRepository(db), ReviewSubmittedPublisher())

@router.post("/", response_model=ReviewResponse, status_code=201)
def submit_review(body: SubmitReviewRequest, service: ReviewService = Depends(get_service)):
    logger.info(f"routes.submit_review() - film={body.film_title}, reviewer={body.reviewer}")
    r = service.submit_review(body.film_title, body.reviewer, body.review_text)
    return ReviewResponse(id=r.id, film_title=r.film_title, reviewer=r.reviewer,
                          review_text=r.review_text, submitted_at=r.submitted_at)

@router.get("/", response_model=List[ReviewResponse])
def list_reviews(service: ReviewService = Depends(get_service)):
    logger.info("routes.list_reviews()")
    return [ReviewResponse(id=r.id, film_title=r.film_title, reviewer=r.reviewer,
                           review_text=r.review_text, submitted_at=r.submitted_at)
            for r in service.get_all()]

@router.get("/{film_title}", response_model=List[ReviewResponse])
def reviews_for_film(film_title: str, service: ReviewService = Depends(get_service)):
    logger.info(f"routes.reviews_for_film() - {film_title}")
    return [ReviewResponse(id=r.id, film_title=r.film_title, reviewer=r.reviewer,
                           review_text=r.review_text, submitted_at=r.submitted_at)
            for r in service.get_by_film(film_title)]
