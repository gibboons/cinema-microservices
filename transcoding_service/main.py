import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from contextlib import asynccontextmanager
from infrastructure.persistence.database import get_dynamodb_table
from infrastructure.persistence.transcoding_repository import TranscodingRepository
from infrastructure.messaging.film_uploaded_consumer import FilmUploadedConsumer
from shared.logger import get_logger

logger = get_logger("transcoding_service")

def repository_factory():
    table = get_dynamodb_table()
    return TranscodingRepository(table)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("TranscodingService starting consumer...")
    consumer = FilmUploadedConsumer(repository_factory)
    consumer.start_in_background()
    yield

app = FastAPI(title="Transcoding Service", version="3.0", lifespan=lifespan)
logger.info("TranscodingService initialized on port 8003")
