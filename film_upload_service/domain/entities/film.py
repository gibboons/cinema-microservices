from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Film:
    filename: str
    extension: str
    title: str
    studio: str
    id: int = None
    uploaded_at: datetime = field(default_factory=datetime.utcnow)
