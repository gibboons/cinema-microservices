from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from infrastructure.persistence.database import get_db
from infrastructure.persistence.film_repository import FilmRepository
from infrastructure.messaging.film_publisher import FilmUploadedPublisher
from application.services.film_service import FilmService
from presentation.api.schemas import FilmUploadResponse
from shared.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/films", tags=["films"])

def get_service(db: Session = Depends(get_db)):
    return FilmService(FilmRepository(db), FilmUploadedPublisher())

@router.post("/upload", response_model=FilmUploadResponse, status_code=201)
async def upload_film(
    file: UploadFile = File(...),
    title: str = Form(...),
    studio: str = Form(...),
    service: FilmService = Depends(get_service)
):
    logger.info(f"routes.upload_film() - file={file.filename}, title={title}, studio={studio}")
    film = service.upload_film(filename=file.filename, title=title, studio=studio)
    return FilmUploadResponse(id=film.id, filename=film.filename, extension=film.extension,
                              title=film.title, studio=film.studio, uploaded_at=film.uploaded_at)

@router.get("/", response_model=List[FilmUploadResponse])
def list_films(service: FilmService = Depends(get_service)):
    logger.info("routes.list_films()")
    return [FilmUploadResponse(id=f.id, filename=f.filename, extension=f.extension,
                               title=f.title, studio=f.studio, uploaded_at=f.uploaded_at)
            for f in service.get_all()]
