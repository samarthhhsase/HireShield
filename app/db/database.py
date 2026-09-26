import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger("hireshield.db")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hireshield.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def ensure_schema():
    """Ensures SQLite tables have all required columns without dropping data."""
    try:
        with engine.connect() as conn:
            cand_cols = [r[1] for r in conn.exec_driver_sql("PRAGMA table_info(candidates)").fetchall()]
            if cand_cols and "input_type" not in cand_cols:
                conn.exec_driver_sql("ALTER TABLE candidates ADD COLUMN input_type VARCHAR(20) DEFAULT 'URL'")
                conn.commit()
            if cand_cols and "user_id" not in cand_cols:
                conn.exec_driver_sql("ALTER TABLE candidates ADD COLUMN user_id VARCHAR(36)")
                conn.commit()
            scan_cols = [r[1] for r in conn.exec_driver_sql("PRAGMA table_info(scans)").fetchall()]
            if scan_cols and "input_type" not in scan_cols:
                conn.exec_driver_sql("ALTER TABLE scans ADD COLUMN input_type VARCHAR(20) DEFAULT 'URL'")
                conn.commit()
            if scan_cols and "user_id" not in scan_cols:
                conn.exec_driver_sql("ALTER TABLE scans ADD COLUMN user_id VARCHAR(36)")
                conn.commit()
    except Exception as exc:
        logger.debug(f"Schema auto-migration check: {exc}")


# Run initial column compatibility check
ensure_schema()


def get_db():
    """FastAPI dependency for request-scoped database sessions."""
    ensure_schema()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

