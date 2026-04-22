from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Review:
    film_title: str
    reviewer: str
    review_text: str
    id: int = None
    submitted_at: datetime = field(default_factory=datetime.utcnow)
