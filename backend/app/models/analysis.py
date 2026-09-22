from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


def utc_now():
    return datetime.now(timezone.utc)


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String(50), primary_key=True, index=True)
    candidate_id = Column(String(50), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_name = Column(String(150), nullable=False)
    risk_score = Column(Integer, nullable=False)
    risk_level = Column(String(20), nullable=False)
    explanation = Column(Text, nullable=False)
    breakdown = Column(JSON, nullable=False)
    analyzed_at = Column(DateTime, default=utc_now, nullable=False)

    candidate = relationship("Candidate", back_populates="analyses")
    signals = relationship("RiskSignalModel", back_populates="analysis", cascade="all, delete-orphan")
