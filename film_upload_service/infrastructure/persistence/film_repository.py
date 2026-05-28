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
                      title=film.title, studio=film.studio,
                      size=film.size, s3_key=film.s3_key,
                      uploaded_at=film.uploaded_at)
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        film.id = m.id
        return film

    def find_all(self) -> list[Film]:
        logger.info("FilmRepository.find_all()")
        return [Film(id=m.id, filename=m.filename, extension=m.extension,
                     title=m.title, studio=m.studio, size=m.size,
                     s3_key=m.s3_key, uploaded_at=m.uploaded_at)
                for m in self.db.query(FilmModel).all()]

    def find_by_id(self, film_id: int) -> Film | None:
        logger.info(f"FilmRepository.find_by_id() - {film_id}")
        m = self.db.query(FilmModel).filter(FilmModel.id == film_id).first()
        if not m:
            return None
        return Film(id=m.id, filename=m.filename, extension=m.extension,
                    title=m.title, studio=m.studio, size=m.size,
                    s3_key=m.s3_key, uploaded_at=m.uploaded_at)
