import uuid
from datetime import datetime
from domain.entities.review import Review
from shared.logger import get_logger

logger = get_logger(__name__)

class ReviewRepository:
    def __init__(self, table):
        self.table = table
        logger.info("ReviewRepository.__init__()")

    def save(self, r: Review) -> Review:
        logger.info(f"ReviewRepository.save() - {r.film_title}")
        review_id = str(uuid.uuid4())
        item = {
            "id":          review_id,
            "film_title":  r.film_title,
            "reviewer":    r.reviewer,
            "review_text": r.review_text,
            "submitted_at": r.submitted_at.isoformat(),
        }
        self.table.put_item(Item=item)
        r.id = review_id
        return r

    def find_all(self) -> list[Review]:
        logger.info("ReviewRepository.find_all()")
        response = self.table.scan()
        return [
            Review(
                id=i["id"],
                film_title=i["film_title"],
                reviewer=i["reviewer"],
                review_text=i["review_text"],
                submitted_at=datetime.fromisoformat(i["submitted_at"]),
            )
            for i in response.get("Items", [])
        ]

    def find_by_film(self, film_title: str) -> list[Review]:
        logger.info(f"ReviewRepository.find_by_film() - {film_title}")
        response = self.table.scan(
            FilterExpression="film_title = :t",
            ExpressionAttributeValues={":t": film_title}
        )
        return [
            Review(
                id=i["id"],
                film_title=i["film_title"],
                reviewer=i["reviewer"],
                review_text=i["review_text"],
                submitted_at=datetime.fromisoformat(i["submitted_at"]),
            )
            for i in response.get("Items", [])
        ]
