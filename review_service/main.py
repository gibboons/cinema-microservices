import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from infrastructure.persistence.database import get_dynamodb_table
from infrastructure.persistence.review_repository import ReviewRepository
from presentation.api.routes import router
from shared.logger import get_logger

logger = get_logger("review_service")
app = FastAPI(title="Review Service", version="3.0")
app.include_router(router)
logger.info("ReviewService initialized on port 8004")
