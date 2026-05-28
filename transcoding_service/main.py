import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from contextlib import asynccontextmanager
from infrastructure.persistence.database import engine, Base, SessionLocal
from infrastructure.persistence.transcoding_repository import TranscodingRepository
from infrastructure.messaging.film_uploaded_consumer import FilmUploadedConsumer
from shared.logger import get_logger

logger = get_logger("transcoding_service")

def repository_factory(db):
    return TranscodingRepository(db)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("TranscodingService starting consumer...")
    consumer = FilmUploadedConsumer(SessionLocal, repository_factory)
    consumer.start_in_background()
    yield

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Transcoding Service", version="2.0", lifespan=lifespan)
logger.info("TranscodingService initialized on port 8003")
