import uuid
from datetime import datetime
from domain.entities.transcoding_job import TranscodingJob
from domain.repositories.transcoding_repository_protocol import TranscodingRepositoryProtocol
from shared.logger import get_logger

logger = get_logger(__name__)

class TranscodingRepository:
    def __init__(self, table):
        self.table = table
        logger.info("TranscodingRepository.__init__()")

    def save(self, job: TranscodingJob) -> TranscodingJob:
        logger.info(f"TranscodingRepository.save() - {job.film_title}")
        job_id = str(uuid.uuid4())
        item = {
            "id":         job_id,
            "film_title": job.film_title,
            "studio":     job.studio,
            "status":     job.status,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat(),
        }
        self.table.put_item(Item=item)
        job.id = job_id
        return job

    def find_all(self) -> list[TranscodingJob]:
        logger.info("TranscodingRepository.find_all()")
        response = self.table.scan()
        return [
            TranscodingJob(
                id=i["id"],
                film_title=i["film_title"],
                studio=i["studio"],
                status=i["status"],
                created_at=datetime.fromisoformat(i["created_at"]),
                updated_at=datetime.fromisoformat(i["updated_at"]),
            )
            for i in response.get("Items", [])
        ]
