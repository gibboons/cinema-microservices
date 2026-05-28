from pydantic import BaseModel
from datetime import datetime

class FilmUploadResponse(BaseModel):
    id: int
    filename: str
    extension: str
    title: str
    studio: str
    size: int
    s3_key: str
    uploaded_at: datetime

    model_config = {"from_attributes": True}

class DownloadUrlResponse(BaseModel):
    film_id: int
    presigned_url: str
    expires_in_seconds: int = 3600
