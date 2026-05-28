from dataclasses import dataclass
from diator.requests import Request

@dataclass(frozen=True, kw_only=True)
class UploadFilmCommand(Request):
    filename: str
    title: str
    studio: str
    file_content: bytes
    content_type: str
    size: int
