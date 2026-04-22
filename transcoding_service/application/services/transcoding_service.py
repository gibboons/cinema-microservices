from domain.entities.transcoding_job import TranscodingJob
from domain.repositories.transcoding_repository_protocol import TranscodingRepositoryProtocol
from shared.logger import get_logger

logger = get_logger(__name__)

class TranscodingService:
    def __init__(self, repository: TranscodingRepositoryProtocol):
        self.repository = repository
        logger.info("TranscodingService.__init__()")

    def create_job_from_event(self, data: dict) -> TranscodingJob:
        logger.info(f"TranscodingService.create_job_from_event() - title={data.get('title')}")
        job = TranscodingJob(film_title=data["title"], studio=data["studio"])
        return self.repository.save(job)

    def update_status(self, job_id: int, status: str) -> TranscodingJob | None:
        logger.info(f"TranscodingService.update_status() - id={job_id}, status={status}")
        return self.repository.update_status(job_id, status)

    def get_all(self) -> list[TranscodingJob]:
        logger.info("TranscodingService.get_all()")
        return self.repository.find_all()
