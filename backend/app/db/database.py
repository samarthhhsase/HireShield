import logging
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from app.core.config import settings

logger = logging.getLogger("hireshield.db")

engine: Optional[Engine] = None

if settings.DATABASE_URL and settings.DATABASE_URL.strip():
    try:
        if settings.DATABASE_URL.startswith("sqlite"):
            engine = create_engine(
                settings.DATABASE_URL,
                connect_args={"check_same_thread": False},
                echo=settings.DEBUG,
            )
        else:
            engine = create_engine(
                settings.DATABASE_URL,
                pool_pre_ping=True,
                echo=settings.DEBUG,
            )
        logger.info(f"SQLAlchemy database engine initialized: {settings.DATABASE_URL.split('://')[0]}")
    except Exception as exc:
        logger.error(f"Failed to initialize database engine: {exc}")
        engine = None
else:
    logger.info("DATABASE_URL not configured. Running in fallback mode.")


def get_engine() -> Optional[Engine]:
    """Retrieve SQLAlchemy engine if configured."""
    return engine
