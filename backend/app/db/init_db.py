import logging
from app.db.base import Base
from app.db.database import get_engine
# Import models to ensure they are registered with Base.metadata
import app.models  # noqa: F401

logger = logging.getLogger("hireshield.db")


def init_db() -> None:
    """Initialize database tables from SQLAlchemy declarative models."""
    engine = get_engine()
    if engine is not None:
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables verified and initialized successfully.")
        except Exception as exc:
            logger.error(f"Error initializing database tables: {exc}")
    else:
        logger.warning("Database engine unavailable. Tables not created.")
