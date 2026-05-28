from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from diator.mediator import Mediator
from diator.requests import RequestMap
from diator.events import EventMap, EventEmitter

from infrastructure.persistence.database import get_db
from infrastructure.persistence.review_repository import ReviewRepository
from infrastructure.messaging.review_publisher import ReviewSubmittedPublisher
from application.command_handlers.submit_review_command_handler import SubmitReviewCommandHandler
from application.query_handlers.get_all_reviews_query_handler import GetAllReviewsQueryHandler
from application.query_handlers.get_reviews_by_film_query_handler import GetReviewsByFilmQueryHandler
from domain.commands.submit_review_command import SubmitReviewCommand
from domain.queries.get_all_reviews_query import GetAllReviewsQuery
from domain.queries.get_reviews_by_film_query import GetReviewsByFilmQuery
from presentation.api.schemas import SubmitReviewRequest, ReviewResponse
from shared.container import SimpleContainer
from shared.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/reviews", tags=["reviews"])


def get_mediator(db: Session = Depends(get_db)) -> Mediator:
    repo      = ReviewRepository(db)
    publisher = ReviewSubmittedPublisher()

    container = SimpleContainer()
    container.register(SubmitReviewCommandHandler,   lambda: SubmitReviewCommandHandler(repo, publisher))
    container.register(GetAllReviewsQueryHandler,    lambda: GetAllReviewsQueryHandler(repo))
    container.register(GetReviewsByFilmQueryHandler, lambda: GetReviewsByFilmQueryHandler(repo))

    request_map = RequestMap()
    request_map.bind(SubmitReviewCommand,   SubmitReviewCommandHandler)
    request_map.bind(GetAllReviewsQuery,    GetAllReviewsQueryHandler)
    request_map.bind(GetReviewsByFilmQuery, GetReviewsByFilmQueryHandler)

    event_emitter = EventEmitter(event_map=EventMap(), container=container, message_broker=None)
    return Mediator(request_map=request_map, event_emitter=event_emitter, container=container)


@router.post("/", response_model=ReviewResponse, status_code=201)
async def submit_review(body: SubmitReviewRequest, mediator: Mediator = Depends(get_mediator)):
    logger.info(f"routes.submit_review() - film={body.film_title}")
    r = await mediator.send(SubmitReviewCommand(
        film_title=body.film_title, reviewer=body.reviewer, review_text=body.review_text))
    return ReviewResponse(id=r.id, film_title=r.film_title, reviewer=r.reviewer,
                          review_text=r.review_text, submitted_at=r.submitted_at)


@router.get("/", response_model=List[ReviewResponse])
async def list_reviews(mediator: Mediator = Depends(get_mediator)):
    logger.info("routes.list_reviews()")
    reviews = await mediator.send(GetAllReviewsQuery())
    return [ReviewResponse(id=r.id, film_title=r.film_title, reviewer=r.reviewer,
                           review_text=r.review_text, submitted_at=r.submitted_at)
            for r in reviews]


@router.get("/{film_title}", response_model=List[ReviewResponse])
async def reviews_for_film(film_title: str, mediator: Mediator = Depends(get_mediator)):
    logger.info(f"routes.reviews_for_film() - {film_title}")
    reviews = await mediator.send(GetReviewsByFilmQuery(film_title=film_title))
    return [ReviewResponse(id=r.id, film_title=r.film_title, reviewer=r.reviewer,
                           review_text=r.review_text, submitted_at=r.submitted_at)
            for r in reviews]
