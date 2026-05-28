from dataclasses import dataclass
from diator.requests import Request

@dataclass(frozen=True, kw_only=True)
class SubmitReviewCommand(Request):
    film_title: str
    reviewer: str
    review_text: str
