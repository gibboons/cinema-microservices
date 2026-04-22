from pydantic import BaseModel
from datetime import datetime

class SubmitRatingRequest(BaseModel):
    film_title: str
    user: str
    score: float

class RatingResponse(BaseModel):
    id: int
    film_title: str
    user: str
    score: float
    submitted_at: datetime

    model_config = {"from_attributes": True}

class RecommendationResponse(BaseModel):
    id: int
    film_title: str
    reason: str
    generated_at: datetime

    model_config = {"from_attributes": True}
