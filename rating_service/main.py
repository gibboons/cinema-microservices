import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from contextlib import asynccontextmanager
from infrastructure.persistence.database import engine, Base, SessionLocal
from infrastructure.persistence.rating_repository import RatingRepository
from infrastructure.persistence.recommendation_repository import RecommendationRepository
from infrastructure.messaging.rating_consumer import RatingSubmittedConsumer
from infrastructure.messaging.rating_publisher import RatingSubmittedPublisher
from infrastructure.messaging.recommendation_publisher import RecommendationGeneratedPublisher
from application.services.rating_service import RatingService
from presentation.api.routes import router
from shared.logger import get_logger

logger = get_logger("rating_service")

def service_factory(db):
    return RatingService(
        RatingRepository(db),
        RecommendationRepository(db),
        RatingSubmittedPublisher(),
        RecommendationGeneratedPublisher()
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("RatingService starting consumer...")
    consumer = RatingSubmittedConsumer(SessionLocal, service_factory)
    consumer.start_in_background()
    yield

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Rating Service", version="1.0", lifespan=lifespan)
app.include_router(router)
logger.info("RatingService initialized on port 8005")
