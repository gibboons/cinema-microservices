from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from diator.mediator import Mediator
from diator.requests import RequestMap
from diator.events import EventMap, EventEmitter

from infrastructure.persistence.database import get_db
from infrastructure.persistence.rating_repository import RatingRepository
from infrastructure.persistence.recommendation_repository import RecommendationRepository
from infrastructure.messaging.rating_publisher import RatingSubmittedPublisher
from infrastructure.messaging.recommendation_publisher import RecommendationGeneratedPublisher
from application.command_handlers.submit_rating_command_handler import SubmitRatingCommandHandler
from application.query_handlers.get_all_ratings_query_handler import GetAllRatingsQueryHandler
from application.query_handlers.get_all_recommendations_query_handler import GetAllRecommendationsQueryHandler
from domain.commands.submit_rating_command import SubmitRatingCommand
from domain.queries.get_all_ratings_query import GetAllRatingsQuery
from domain.queries.get_all_recommendations_query import GetAllRecommendationsQuery
from presentation.api.schemas import SubmitRatingRequest, RatingResponse, RecommendationResponse
from shared.container import SimpleContainer
from shared.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["ratings"])


def get_mediator(db: Session = Depends(get_db)) -> Mediator:
    rating_repo = RatingRepository(db)
    rec_repo    = RecommendationRepository(db)
    rat_pub     = RatingSubmittedPublisher()
    rec_pub     = RecommendationGeneratedPublisher()

    container = SimpleContainer()
    container.register(SubmitRatingCommandHandler,
        lambda: SubmitRatingCommandHandler(rating_repo, rec_repo, rat_pub, rec_pub))
    container.register(GetAllRatingsQueryHandler,
        lambda: GetAllRatingsQueryHandler(rating_repo))
    container.register(GetAllRecommendationsQueryHandler,
        lambda: GetAllRecommendationsQueryHandler(rec_repo))

    request_map = RequestMap()
    request_map.bind(SubmitRatingCommand,        SubmitRatingCommandHandler)
    request_map.bind(GetAllRatingsQuery,         GetAllRatingsQueryHandler)
    request_map.bind(GetAllRecommendationsQuery, GetAllRecommendationsQueryHandler)

    event_emitter = EventEmitter(event_map=EventMap(), container=container, message_broker=None)
    return Mediator(request_map=request_map, event_emitter=event_emitter, container=container)


@router.post("/ratings", response_model=RatingResponse, status_code=201)
async def submit_rating(body: SubmitRatingRequest, mediator: Mediator = Depends(get_mediator)):
    logger.info(f"routes.submit_rating() - film={body.film_title}, score={body.score}")
    r = await mediator.send(SubmitRatingCommand(
        film_title=body.film_title, user=body.user, score=body.score))
    return RatingResponse(id=r.id, film_title=r.film_title, user=r.user,
                          score=r.score, submitted_at=r.submitted_at)


@router.get("/ratings", response_model=List[RatingResponse])
async def list_ratings(mediator: Mediator = Depends(get_mediator)):
    logger.info("routes.list_ratings()")
    ratings = await mediator.send(GetAllRatingsQuery())
    return [RatingResponse(id=r.id, film_title=r.film_title, user=r.user,
                           score=r.score, submitted_at=r.submitted_at)
            for r in ratings]


@router.get("/recommendations", response_model=List[RecommendationResponse])
async def list_recommendations(mediator: Mediator = Depends(get_mediator)):
    logger.info("routes.list_recommendations()")
    recs = await mediator.send(GetAllRecommendationsQuery())
    return [RecommendationResponse(id=r.id, film_title=r.film_title,
                                   reason=r.reason, generated_at=r.generated_at)
            for r in recs]
