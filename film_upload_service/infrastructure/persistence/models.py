from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from infrastructure.persistence.database import Base

class FilmModel(Base):
    __tablename__ = "films"
    id          = Column(Integer, primary_key=True, index=True)
    filename    = Column(String, nullable=False)
    extension   = Column(String, nullable=False)
    title       = Column(String, nullable=False)
    studio      = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
