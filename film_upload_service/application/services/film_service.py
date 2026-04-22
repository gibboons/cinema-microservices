from domain.entities.film import Film
from domain.repositories.film_repository_protocol import FilmRepositoryProtocol
from shared.logger import get_logger

logger = get_logger(__name__)

class FilmService:
    def __init__(self, repository: FilmRepositoryProtocol, publisher):
        self.repository = repository
        self.publisher = publisher
        logger.info("FilmService.__init__()")

    def upload_film(self, filename: str, title: str, studio: str) -> Film:
        logger.info(f"FilmService.upload_film() - filename={filename}, title={title}, studio={studio}")
        extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        logger.info(f"FilmService.upload_film() - detected extension: .{extension}")
        film = Film(filename=filename, extension=extension, title=title, studio=studio)
        saved = self.repository.save(film)
        self.publisher.publish({
            "title": title, "studio": studio,
            "filename": filename, "extension": extension,
            "timestamp": saved.uploaded_at.isoformat()
        })
        return saved

    def get_all(self) -> list[Film]:
        logger.info("FilmService.get_all()")
        return self.repository.find_all()
