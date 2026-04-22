from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Recommendation:
    film_title: str
    reason: str
    id: int = None
    generated_at: datetime = field(default_factory=datetime.utcnow)
