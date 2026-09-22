import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import List, Optional, Dict
from fastapi import Depends
from sqlalchemy.orm import Session

from app.schemas.candidate import CandidateCreate, CandidateUpdate, CandidateResponse
from app.schemas.analysis import AnalysisResponse
from app.schemas.risk import RiskSignal, ScoreBreakdown, RiskLevel, RiskCategory
from app.models.candidate import Candidate
from app.models.analysis import Analysis
from app.models.risk_signal import RiskSignalModel
from app.db.session import get_db


class BaseCandidateRepository(ABC):
    """Abstract repository interface for candidate persistence."""

    @abstractmethod
    def create(self, candidate_in: CandidateCreate) -> CandidateResponse:
        pass

    @abstractmethod
    def get_by_id(self, candidate_id: str) -> Optional[CandidateResponse]:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[CandidateResponse]:
        pass

    @abstractmethod
    def list_all(self, skip: int = 0, limit: int = 100) -> List[CandidateResponse]:
        pass

    @abstractmethod
    def update(self, candidate_id: str, candidate_in: CandidateUpdate) -> Optional[CandidateResponse]:
        pass

    @abstractmethod
    def delete(self, candidate_id: str) -> bool:
        pass

    @abstractmethod
    def count(self) -> int:
        pass


class BaseAnalysisRepository(ABC):
    """Abstract repository interface for analysis results persistence."""

    @abstractmethod
    def save(self, analysis: AnalysisResponse) -> AnalysisResponse:
        pass

    @abstractmethod
    def get_by_id(self, analysis_id: str) -> Optional[AnalysisResponse]:
        pass

    @abstractmethod
    def get_by_candidate_id(self, candidate_id: str) -> List[AnalysisResponse]:
        pass

    @abstractmethod
    def list_all(self, skip: int = 0, limit: int = 100) -> List[AnalysisResponse]:
        pass

    @abstractmethod
    def count(self) -> int:
        pass


# =====================================================================
# SQLALCHEMY IMPLEMENTATION (For SQLite and PostgreSQL)
# =====================================================================
class SQLAlchemyCandidateRepository(BaseCandidateRepository):
    """Production-grade candidate repository backed by SQLAlchemy ORM."""

    def __init__(self, db: Session):
        self.db = db

    def _to_schema(self, model: Candidate) -> CandidateResponse:
        return CandidateResponse(
            id=model.id,
            name=model.name,
            email=model.email,
            phone=model.phone,
            role=model.role,
            resume_text=model.resume_text,
            skills=model.skills or [],
            experience_years=model.experience_years,
            education=model.education,
            job_description=model.job_description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def create(self, candidate_in: CandidateCreate) -> CandidateResponse:
        cand_id = f"CAND-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now(timezone.utc)
        
        record = Candidate(
            id=cand_id,
            name=candidate_in.name,
            email=candidate_in.email,
            phone=candidate_in.phone,
            role=candidate_in.role,
            resume_text=candidate_in.resume_text,
            skills=candidate_in.skills or [],
            experience_years=candidate_in.experience_years,
            education=candidate_in.education,
            job_description=candidate_in.job_description,
            created_at=now,
            updated_at=now,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return self._to_schema(record)

    def get_by_id(self, candidate_id: str) -> Optional[CandidateResponse]:
        model = self.db.query(Candidate).filter(Candidate.id == candidate_id).first()
        return self._to_schema(model) if model else None

    def get_by_email(self, email: str) -> Optional[CandidateResponse]:
        model = self.db.query(Candidate).filter(Candidate.email.ilike(email)).first()
        return self._to_schema(model) if model else None

    def list_all(self, skip: int = 0, limit: int = 100) -> List[CandidateResponse]:
        models = (
            self.db.query(Candidate)
            .order_by(Candidate.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_schema(m) for m in models]

    def update(self, candidate_id: str, candidate_in: CandidateUpdate) -> Optional[CandidateResponse]:
        model = self.db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not model:
            return None

        update_data = candidate_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(model, field, value)
        
        model.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(model)
        return self._to_schema(model)

    def delete(self, candidate_id: str) -> bool:
        model = self.db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not model:
            return False
        self.db.delete(model)
        self.db.commit()
        return True

    def count(self) -> int:
        return self.db.query(Candidate).count()


class SQLAlchemyAnalysisRepository(BaseAnalysisRepository):
    """Production-grade analysis repository backed by SQLAlchemy ORM."""

    def __init__(self, db: Session):
        self.db = db

    def _to_schema(self, model: Analysis) -> AnalysisResponse:
        signals = [
            RiskSignal(
                signal_name=s.signal_name,
                category=RiskCategory(s.category) if s.category in RiskCategory._value2member_map_ else s.category,
                severity=s.severity,
                weight=s.weight,
                description=s.description,
                evidence=s.evidence,
            )
            for s in model.signals
        ]
        breakdown_data = model.breakdown if isinstance(model.breakdown, dict) else {}
        return AnalysisResponse(
            id=model.id,
            candidate_id=model.candidate_id,
            candidate_name=model.candidate_name,
            risk_score=model.risk_score,
            risk_level=RiskLevel(model.risk_level) if model.risk_level in RiskLevel._value2member_map_ else model.risk_level,
            signals=signals,
            explanation=model.explanation,
            breakdown=ScoreBreakdown(**breakdown_data),
            analyzed_at=model.analyzed_at,
        )

    def save(self, analysis: AnalysisResponse) -> AnalysisResponse:
        existing = self.db.query(Analysis).filter(Analysis.id == analysis.id).first()
        if not existing:
            risk_level_str = analysis.risk_level.value if hasattr(analysis.risk_level, "value") else str(analysis.risk_level)
            breakdown_dict = analysis.breakdown.model_dump() if hasattr(analysis.breakdown, "model_dump") else dict(analysis.breakdown)
            
            record = Analysis(
                id=analysis.id,
                candidate_id=analysis.candidate_id,
                candidate_name=analysis.candidate_name,
                risk_score=analysis.risk_score,
                risk_level=risk_level_str,
                explanation=analysis.explanation,
                breakdown=breakdown_dict,
                analyzed_at=analysis.analyzed_at,
            )
            self.db.add(record)
            self.db.flush()

            for sig in analysis.signals:
                cat_str = sig.category.value if hasattr(sig.category, "value") else str(sig.category)
                sig_model = RiskSignalModel(
                    analysis_id=record.id,
                    signal_name=sig.signal_name,
                    category=cat_str,
                    severity=sig.severity,
                    weight=sig.weight,
                    description=sig.description,
                    evidence=sig.evidence,
                )
                self.db.add(sig_model)

            self.db.commit()
        return analysis

    def get_by_id(self, analysis_id: str) -> Optional[AnalysisResponse]:
        model = self.db.query(Analysis).filter(Analysis.id == analysis_id).first()
        return self._to_schema(model) if model else None

    def get_by_candidate_id(self, candidate_id: str) -> List[AnalysisResponse]:
        models = (
            self.db.query(Analysis)
            .filter(Analysis.candidate_id == candidate_id)
            .order_by(Analysis.analyzed_at.desc())
            .all()
        )
        return [self._to_schema(m) for m in models]

    def list_all(self, skip: int = 0, limit: int = 100) -> List[AnalysisResponse]:
        models = (
            self.db.query(Analysis)
            .order_by(Analysis.analyzed_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_schema(m) for m in models]

    def count(self) -> int:
        return self.db.query(Analysis).count()


# =====================================================================
# IN-MEMORY FALLBACK (Used only if database engine is unavailable)
# =====================================================================
class InMemoryCandidateRepository(BaseCandidateRepository):
    def __init__(self):
        self._storage: Dict[str, CandidateResponse] = {}

    def create(self, candidate_in: CandidateCreate) -> CandidateResponse:
        now = datetime.now(timezone.utc)
        cand_id = f"CAND-{uuid.uuid4().hex[:8].upper()}"
        record = CandidateResponse(
            id=cand_id,
            name=candidate_in.name,
            email=candidate_in.email,
            phone=candidate_in.phone,
            role=candidate_in.role,
            resume_text=candidate_in.resume_text,
            skills=candidate_in.skills or [],
            experience_years=candidate_in.experience_years,
            education=candidate_in.education,
            job_description=candidate_in.job_description,
            created_at=now,
            updated_at=now,
        )
        self._storage[cand_id] = record
        return record

    def get_by_id(self, candidate_id: str) -> Optional[CandidateResponse]:
        return self._storage.get(candidate_id)

    def get_by_email(self, email: str) -> Optional[CandidateResponse]:
        for candidate in self._storage.values():
            if candidate.email.lower() == email.lower():
                return candidate
        return None

    def list_all(self, skip: int = 0, limit: int = 100) -> List[CandidateResponse]:
        items = list(self._storage.values())
        items.sort(key=lambda x: x.created_at, reverse=True)
        return items[skip : skip + limit]

    def update(self, candidate_id: str, candidate_in: CandidateUpdate) -> Optional[CandidateResponse]:
        existing = self._storage.get(candidate_id)
        if not existing:
            return None
        update_data = candidate_in.model_dump(exclude_unset=True)
        current_data = existing.model_dump()
        current_data.update(update_data)
        current_data["updated_at"] = datetime.now(timezone.utc)
        updated_record = CandidateResponse(**current_data)
        self._storage[candidate_id] = updated_record
        return updated_record

    def delete(self, candidate_id: str) -> bool:
        if candidate_id in self._storage:
            del self._storage[candidate_id]
            return True
        return False

    def count(self) -> int:
        return len(self._storage)


class InMemoryAnalysisRepository(BaseAnalysisRepository):
    def __init__(self):
        self._storage: Dict[str, AnalysisResponse] = {}

    def save(self, analysis: AnalysisResponse) -> AnalysisResponse:
        self._storage[analysis.id] = analysis
        return analysis

    def get_by_id(self, analysis_id: str) -> Optional[AnalysisResponse]:
        return self._storage.get(analysis_id)

    def get_by_candidate_id(self, candidate_id: str) -> List[AnalysisResponse]:
        results = [a for a in self._storage.values() if a.candidate_id == candidate_id]
        results.sort(key=lambda x: x.analyzed_at, reverse=True)
        return results

    def list_all(self, skip: int = 0, limit: int = 100) -> List[AnalysisResponse]:
        items = list(self._storage.values())
        items.sort(key=lambda x: x.analyzed_at, reverse=True)
        return items[skip : skip + limit]

    def count(self) -> int:
        return len(self._storage)


# Global fallback instances
candidate_repo = InMemoryCandidateRepository()
analysis_repo = InMemoryAnalysisRepository()


def get_candidate_repository(db: Optional[Session] = Depends(get_db)) -> BaseCandidateRepository:
    """Dependency provider: returns SQLAlchemy repository if DB is active, else in-memory fallback."""
    if db is not None:
        return SQLAlchemyCandidateRepository(db)
    return candidate_repo


def get_analysis_repository(db: Optional[Session] = Depends(get_db)) -> BaseAnalysisRepository:
    """Dependency provider: returns SQLAlchemy repository if DB is active, else in-memory fallback."""
    if db is not None:
        return SQLAlchemyAnalysisRepository(db)
    return analysis_repo
