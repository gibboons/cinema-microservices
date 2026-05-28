from diator.requests import RequestHandler
from diator.events import Event
from domain.entities.review import Review
from domain.repositories.review_repository_protocol import ReviewRepositoryProtocol
from domain.commands.submit_review_command import SubmitReviewCommand
from shared.logger import get_logger

logger = get_logger(__name__)

class SubmitReviewCommandHandler(RequestHandler[SubmitReviewCommand, Review]):
    def __init__(self, repository: ReviewRepositoryProtocol, publisher):
        self._repository = repository
        self._publisher  = publisher
        self._events: list[Event] = []
        logger.info("SubmitReviewCommandHandler.__init__()")

    @property
    def events(self) -> list[Event]:
        return self._events

    async def handle(self, request: SubmitReviewCommand) -> Review:
        logger.info(f"SubmitReviewCommandHandler.handle() - film={request.film_title}")
        r = Review(film_title=request.film_title, reviewer=request.reviewer,
                   review_text=request.review_text)
        saved = self._repository.save(r)
        self._publisher.publish({
            "film_title": request.film_title, "reviewer": request.reviewer,
            "review": request.review_text, "timestamp": saved.submitted_at.isoformat(),
        })
        return saved
