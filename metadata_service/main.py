import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from contextlib import asynccontextmanager
from infrastructure.persistence.database import engine, Base, SessionLocal
from infrastructure.persistence.metadata_repository import MetadataRepository
from infrastructure.messaging.film_uploaded_consumer import FilmUploadedConsumer
from application.services.metadata_service import MetadataService
from shared.logger import get_logger

logger = get_logger("metadata_service")

def service_factory(db):
    return MetadataService(MetadataRepository(db))

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("MetadataService starting consumer...")
    consumer = FilmUploadedConsumer(SessionLocal, service_factory)
    consumer.start_in_background()
    yield

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Metadata Service", version="1.0", lifespan=lifespan)
logger.info("MetadataService initialized on port 8002")
