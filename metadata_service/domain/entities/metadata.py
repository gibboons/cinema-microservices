from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Metadata:
    film_title: str
    studio: str
    filename: str
    extension: str
    id: int = None
    received_at: datetime = field(default_factory=datetime.utcnow)
