from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List
from diator.mediator import Mediator
from diator.requests import RequestMap
from diator.events import EventMap, EventEmitter

from infrastructure.persistence.database import get_db
from infrastructure.persistence.film_repository import FilmRepository
from infrastructure.messaging.film_publisher import FilmUploadedPublisher
from infrastructure.storage.s3_storage_service import S3StorageService
from application.command_handlers.upload_film_command_handler import UploadFilmCommandHandler
from application.query_handlers.get_all_films_query_handler import GetAllFilmsQueryHandler
from application.query_handlers.get_file_from_s3_query_handler import GetFileFromS3QueryHandler
from domain.commands.upload_film_command import UploadFilmCommand
from domain.queries.get_all_films_query import GetAllFilmsQuery
from domain.queries.get_file_from_s3_query import GetFileFromS3Query
from presentation.api.schemas import FilmUploadResponse, DownloadUrlResponse
from shared.container import SimpleContainer
from shared.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/films", tags=["films"])


def get_mediator(db: Session = Depends(get_db)) -> Mediator:
    repo      = FilmRepository(db)
    publisher = FilmUploadedPublisher()
    s3        = S3StorageService()

    container = SimpleContainer()
    container.register(UploadFilmCommandHandler,  lambda: UploadFilmCommandHandler(repo, publisher, s3))
    container.register(GetAllFilmsQueryHandler,   lambda: GetAllFilmsQueryHandler(repo))
    container.register(GetFileFromS3QueryHandler, lambda: GetFileFromS3QueryHandler(repo, s3))

    request_map = RequestMap()
    request_map.bind(UploadFilmCommand,  UploadFilmCommandHandler)
    request_map.bind(GetAllFilmsQuery,   GetAllFilmsQueryHandler)
    request_map.bind(GetFileFromS3Query, GetFileFromS3QueryHandler)

    event_emitter = EventEmitter(event_map=EventMap(), container=container, message_broker=None)
    return Mediator(request_map=request_map, event_emitter=event_emitter, container=container)


@router.post("/upload", response_model=FilmUploadResponse, status_code=201)
async def upload_film(
    file: UploadFile = File(...),
    title: str = Form(...),
    studio: str = Form(...),
    mediator: Mediator = Depends(get_mediator),
):
    logger.info(f"routes.upload_film() - file={file.filename}, title={title}")
    content = await file.read()
    film = await mediator.send(UploadFilmCommand(
        filename=file.filename, title=title, studio=studio,
        file_content=content,
        content_type=file.content_type or "application/octet-stream",
        size=len(content),
    ))
    return FilmUploadResponse(
        id=film.id, filename=film.filename, extension=film.extension,
        title=film.title, studio=film.studio, size=film.size,
        s3_key=film.s3_key, uploaded_at=film.uploaded_at,
    )


@router.get("/", response_model=List[FilmUploadResponse])
async def list_films(mediator: Mediator = Depends(get_mediator)):
    logger.info("routes.list_films()")
    films = await mediator.send(GetAllFilmsQuery())
    return [FilmUploadResponse(
        id=f.id, filename=f.filename, extension=f.extension,
        title=f.title, studio=f.studio, size=f.size,
        s3_key=f.s3_key, uploaded_at=f.uploaded_at,
    ) for f in films]


@router.get("/{film_id}/download", response_model=DownloadUrlResponse)
async def download_film(film_id: int, mediator: Mediator = Depends(get_mediator)):
    logger.info(f"routes.download_film() - film_id={film_id}")
    try:
        url = await mediator.send(GetFileFromS3Query(film_id=film_id))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return DownloadUrlResponse(film_id=film_id, presigned_url=url)
