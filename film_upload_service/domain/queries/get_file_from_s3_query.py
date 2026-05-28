from dataclasses import dataclass
from diator.requests import Request

@dataclass(frozen=True, kw_only=True)
class GetFileFromS3Query(Request):
    film_id: int
