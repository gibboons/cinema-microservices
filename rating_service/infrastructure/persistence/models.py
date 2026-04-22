from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from infrastructure.persistence.database import Base

class RatingModel(Base):
    __tablename__ = "ratings"
    id           = Column(Integer, primary_key=True, index=True)
    film_title   = Column(String, nullable=False)
    user         = Column(String, nullable=False)
    score        = Column(Float, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

class RecommendationModel(Base):
    __tablename__ = "recommendations"
    id           = Column(Integer, primary_key=True, index=True)
    film_title   = Column(String, nullable=False)
    reason       = Column(String, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
