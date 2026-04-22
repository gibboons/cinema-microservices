from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from infrastructure.persistence.database import Base

class ReviewModel(Base):
    __tablename__ = "reviews"
    id           = Column(Integer, primary_key=True, index=True)
    film_title   = Column(String, nullable=False)
    reviewer     = Column(String, nullable=False)
    review_text  = Column(String, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)
