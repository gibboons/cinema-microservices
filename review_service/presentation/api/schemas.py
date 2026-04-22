from pydantic import BaseModel
from datetime import datetime

class SubmitReviewRequest(BaseModel):
    film_title: str
    reviewer: str
    review_text: str

class ReviewResponse(BaseModel):
    id: int
    film_title: str
    reviewer: str
    review_text: str
    submitted_at: datetime

    model_config = {"from_attributes": True}
