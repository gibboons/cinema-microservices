from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Film:
    filename: str
    extension: str
    title: str
    studio: str
    size: int = 0
    s3_key: str = ""
    id: int = None
    uploaded_at: datetime = field(default_factory=datetime.utcnow)
