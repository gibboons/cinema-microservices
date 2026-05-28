from dataclasses import dataclass
from diator.requests import Request

@dataclass(frozen=True, kw_only=True)
class SubmitRatingCommand(Request):
    film_title: str
    user: str
    score: float
