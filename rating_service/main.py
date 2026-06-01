import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from infrastructure.persistence.database import engine, Base
from presentation.api.routes import router
from shared.logger import get_logger

logger = get_logger("rating_service")
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Rating Service", version="3.0")
app.include_router(router)
logger.info("RatingService initialized on port 8005")
