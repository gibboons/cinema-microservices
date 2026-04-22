from domain.entities.metadata import Metadata
from domain.repositories.metadata_repository_protocol import MetadataRepositoryProtocol
from shared.logger import get_logger

logger = get_logger(__name__)

class MetadataService:
    def __init__(self, repository: MetadataRepositoryProtocol):
        self.repository = repository
        logger.info("MetadataService.__init__()")

    def save_from_event(self, data: dict) -> Metadata:
        logger.info(f"MetadataService.save_from_event() - title={data.get('title')}")
        m = Metadata(
            film_title=data["title"], studio=data["studio"],
            filename=data.get("filename", ""), extension=data.get("extension", "")
        )
        return self.repository.save(m)

    def get_all(self) -> list[Metadata]:
        logger.info("MetadataService.get_all()")
        return self.repository.find_all()

    def get_by_title(self, title: str) -> Metadata | None:
        logger.info(f"MetadataService.get_by_title() - {title}")
        return self.repository.find_by_title(title)
