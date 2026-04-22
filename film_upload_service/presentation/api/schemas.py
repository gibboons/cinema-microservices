from pydantic import BaseModel
from datetime import datetime

class FilmUploadResponse(BaseModel):
    id: int
    filename: str
    extension: str
    title: str
    studio: str
    uploaded_at: datetime

    model_config = {"from_attributes": True}
