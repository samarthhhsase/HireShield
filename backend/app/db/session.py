from typing import Generator, Optional
from sqlalchemy.orm import sessionmaker, Session
from app.db.database import get_engine

SessionLocal: Optional[sessionmaker] = None


def get_session_factory() -> Optional[sessionmaker]:
    global SessionLocal
    if SessionLocal is None:
        eng = get_engine()
        if eng is not None:
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=eng)
    return SessionLocal


def get_db() -> Generator[Optional[Session], None, None]:
    """
    FastAPI dependency yielding an isolated SQLAlchemy database session.
    Yields None if database engine is not configured.
    """
    factory = get_session_factory()
    if factory is None:
        yield None
        return

    db = factory()
    try:
        yield db
    finally:
        db.close()
