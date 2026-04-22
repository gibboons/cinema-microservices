from domain.entities.metadata import Metadata
from infrastructure.persistence.models import MetadataModel
from shared.logger import get_logger

logger = get_logger(__name__)

class MetadataRepository:
    def __init__(self, db):
        self.db = db
        logger.info("MetadataRepository.__init__()")

    def save(self, m: Metadata) -> Metadata:
        logger.info(f"MetadataRepository.save() - {m.film_title}")
        model = MetadataModel(film_title=m.film_title, studio=m.studio,
                              filename=m.filename, extension=m.extension,
                              received_at=m.received_at)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        m.id = model.id
        return m

    def find_all(self) -> list[Metadata]:
        logger.info("MetadataRepository.find_all()")
        return [Metadata(id=r.id, film_title=r.film_title, studio=r.studio,
                         filename=r.filename, extension=r.extension, received_at=r.received_at)
                for r in self.db.query(MetadataModel).all()]

    def find_by_title(self, title: str) -> Metadata | None:
        logger.info(f"MetadataRepository.find_by_title() - {title}")
        r = self.db.query(MetadataModel).filter(MetadataModel.film_title == title).first()
        if not r:
            return None
        return Metadata(id=r.id, film_title=r.film_title, studio=r.studio,
                        filename=r.filename, extension=r.extension, received_at=r.received_at)
