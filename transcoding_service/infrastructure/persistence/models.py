from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from infrastructure.persistence.database import Base

class TranscodingJobModel(Base):
    __tablename__ = "transcoding_jobs"
    id         = Column(Integer, primary_key=True, index=True)
    film_title = Column(String, nullable=False)
    studio     = Column(String, nullable=False)
    status     = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
