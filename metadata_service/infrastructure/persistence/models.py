from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from infrastructure.persistence.database import Base

class MetadataModel(Base):
    __tablename__ = "metadata"
    id          = Column(Integer, primary_key=True, index=True)
    film_title  = Column(String, nullable=False)
    studio      = Column(String, nullable=False)
    filename    = Column(String, nullable=False)
    extension   = Column(String, nullable=False)
    received_at = Column(DateTime, default=datetime.utcnow)
