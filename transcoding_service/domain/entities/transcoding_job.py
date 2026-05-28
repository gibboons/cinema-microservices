from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class TranscodingJob:
    film_title: str
    studio: str
    status: str = "pending"
    id: int = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
