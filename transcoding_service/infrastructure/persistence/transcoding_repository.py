from datetime import datetime
from domain.entities.transcoding_job import TranscodingJob
from infrastructure.persistence.models import TranscodingJobModel
from shared.logger import get_logger

logger = get_logger(__name__)

class TranscodingRepository:
    def __init__(self, db):
        self.db = db
        logger.info("TranscodingRepository.__init__()")

    def save(self, job: TranscodingJob) -> TranscodingJob:
        logger.info(f"TranscodingRepository.save() - {job.film_title}")
        m = TranscodingJobModel(film_title=job.film_title, studio=job.studio,
                                status=job.status, created_at=job.created_at,
                                updated_at=job.updated_at)
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        job.id = m.id
        return job

    def update_status(self, job_id: int, status: str) -> TranscodingJob | None:
        logger.info(f"TranscodingRepository.update_status() - id={job_id}, status={status}")
        m = self.db.query(TranscodingJobModel).filter(TranscodingJobModel.id == job_id).first()
        if not m:
            return None
        m.status = status
        m.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(m)
        return TranscodingJob(id=m.id, film_title=m.film_title, studio=m.studio,
                              status=m.status, created_at=m.created_at, updated_at=m.updated_at)

    def find_all(self) -> list[TranscodingJob]:
        logger.info("TranscodingRepository.find_all()")
        return [TranscodingJob(id=m.id, film_title=m.film_title, studio=m.studio,
                               status=m.status, created_at=m.created_at, updated_at=m.updated_at)
                for m in self.db.query(TranscodingJobModel).all()]
