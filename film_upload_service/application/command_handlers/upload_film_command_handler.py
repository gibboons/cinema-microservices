from diator.requests import RequestHandler
from diator.events import Event
from domain.entities.film import Film
from domain.repositories.film_repository_protocol import FilmRepositoryProtocol
from domain.commands.upload_film_command import UploadFilmCommand
from shared.logger import get_logger

logger = get_logger(__name__)

class UploadFilmCommandHandler(RequestHandler[UploadFilmCommand, Film]):
    def __init__(self, repository: FilmRepositoryProtocol, publisher, s3_storage):
        self._repository = repository
        self._publisher  = publisher
        self._s3_storage = s3_storage
        self._events: list[Event] = []
        logger.info("UploadFilmCommandHandler.__init__()")

    @property
    def events(self) -> list[Event]:
        return self._events

    async def handle(self, request: UploadFilmCommand) -> Film:
        logger.info(f"UploadFilmCommandHandler.handle() - filename={request.filename}")
        extension = request.filename.rsplit(".", 1)[-1].lower() if "." in request.filename else ""
        logger.info(f"UploadFilmCommandHandler.handle() - extension={extension}")

        s3_key = f"films/{request.title.replace(' ', '_')}/{request.filename}"
        self._s3_storage.upload_file(request.file_content, s3_key, request.content_type)

        film = Film(filename=request.filename, extension=extension,
                    title=request.title, studio=request.studio,
                    size=request.size, s3_key=s3_key)
        saved = self._repository.save(film)

        self._publisher.publish({
            "title": request.title, "studio": request.studio,
            "filename": request.filename, "extension": extension,
            "timestamp": saved.uploaded_at.isoformat(),
        })
        logger.info(f"UploadFilmCommandHandler.handle() - done, id={saved.id}")
        return saved
