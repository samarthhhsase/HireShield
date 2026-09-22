"""
HireShield SQLite Database & Session Management.
Provides engine, SessionLocal, Base, and request-scoped dependency get_db.
"""
from app.db.database import (
    Base,
    engine,
    SessionLocal,
    get_db,
    DATABASE_URL,
)

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "DATABASE_URL",
]
