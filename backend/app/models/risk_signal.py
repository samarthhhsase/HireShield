from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class RiskSignalModel(Base):
    __tablename__ = "risk_signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String(50), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    signal_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    severity = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(Text, nullable=True)

    analysis = relationship("Analysis", back_populates="signals")
