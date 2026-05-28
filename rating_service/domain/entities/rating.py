from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Rating:
    film_title: str
    user: str
    score: float
    id: int = None
    submitted_at: datetime = field(default_factory=datetime.utcnow)
