from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


def utc_now():
    return datetime.now(timezone.utc)


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(50), nullable=True)
    role = Column(String(150), nullable=False)
    resume_text = Column(Text, nullable=True)
    skills = Column(JSON, nullable=False, default=list)
    experience_years = Column(Float, nullable=True)
    education = Column(String(255), nullable=True)
    job_description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    analyses = relationship("Analysis", back_populates="candidate", cascade="all, delete-orphan")
