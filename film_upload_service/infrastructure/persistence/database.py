from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker
from shared.config import get
from shared.logger import get_logger

logger = get_logger(__name__)

def _build_url() -> str:
    host     = get("FILM_UPLOAD_DB_HOST")
    port     = get("FILM_UPLOAD_DB_PORT", "5432")
    name     = get("FILM_UPLOAD_DB_NAME")
    user     = get("FILM_UPLOAD_DB_USER")
    password = get("FILM_UPLOAD_DB_PASSWORD")
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"

def _create_engine():
    url = _build_url()
    logger.info("FilmUploadDB - rozpoczynam połączenie z RDS PostgreSQL...")
    try:
        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("FilmUploadDB - połączenie z RDS PostgreSQL nawiązane pomyślnie")
        return engine
    except Exception as e:
        logger.error(f"FilmUploadDB - błąd połączenia z RDS PostgreSQL: {e}")
        raise

engine = _create_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
