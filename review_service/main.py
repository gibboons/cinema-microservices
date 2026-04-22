import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from infrastructure.persistence.database import engine, Base
from presentation.api.routes import router
from shared.logger import get_logger

logger = get_logger("review_service")
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Review Service", version="1.0")
app.include_router(router)
logger.info("ReviewService initialized on port 8004")
