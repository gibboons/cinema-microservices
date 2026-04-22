from domain.entities.film import Film
from infrastructure.persistence.models import FilmModel
from shared.logger import get_logger

logger = get_logger(__name__)

class FilmRepository:
    def __init__(self, db):
        self.db = db
        logger.info("FilmRepository.__init__()")

    def save(self, film: Film) -> Film:
        logger.info(f"FilmRepository.save() - {film.filename}")
        m = FilmModel(filename=film.filename, extension=film.extension,
                      title=film.title, studio=film.studio, uploaded_at=film.uploaded_at)
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        film.id = m.id
        return film

    def find_all(self) -> list[Film]:
        logger.info("FilmRepository.find_all()")
        return [
            Film(id=m.id, filename=m.filename, extension=m.extension,
                 title=m.title, studio=m.studio, uploaded_at=m.uploaded_at)
            for m in self.db.query(FilmModel).all()
        ]
