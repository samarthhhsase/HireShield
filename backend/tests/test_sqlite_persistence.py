import os
from sqlalchemy import inspect
from app.core.config import settings
from app.db.database import get_engine
from app.db.session import get_session_factory
from app.db.repository import SQLAlchemyCandidateRepository, SQLAlchemyAnalysisRepository
from app.schemas.candidate import CandidateCreate, CandidateUpdate
from app.schemas.analysis import AnalysisResponse
from app.schemas.risk import RiskAssessment, RiskLevel, RiskSignal, RiskCategory, ScoreBreakdown
from datetime import datetime, timezone


def test_sqlite_engine_and_tables():
    """Verify SQLite engine is initialized and tables exist."""
    engine = get_engine()
    assert engine is not None
    assert "sqlite" in str(engine.url)

    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    assert "candidates" in table_names
    assert "analyses" in table_names
    assert "risk_signals" in table_names


def test_candidate_cross_session_persistence():
    """Verify candidate created in one session persists to SQLite and can be read by another session."""
    factory = get_session_factory()
    assert factory is not None

    # Session 1: Create candidate
    with factory() as db1:
        repo1 = SQLAlchemyCandidateRepository(db1)
        candidate_in = CandidateCreate(
            name="SQLite Test User",
            email="sqlite.test@example.com",
            role="Security Architect",
            skills=["Cryptography", "Python", "Linux"],
            experience_years=7.5,
            job_description="Looking for senior security architect with 5+ years cryptography.",
        )
        created = repo1.create(candidate_in)
        assert created.id.startswith("CAND-")
        cand_id = created.id

    # Session 2: Read candidate from independent connection
    with factory() as db2:
        repo2 = SQLAlchemyCandidateRepository(db2)
        retrieved = repo2.get_by_id(cand_id)
        assert retrieved is not None
        assert retrieved.name == "SQLite Test User"
        assert retrieved.email == "sqlite.test@example.com"
        assert "Cryptography" in retrieved.skills

        # Update in Session 2
        updated = repo2.update(cand_id, CandidateUpdate(phone="+1-555-SQLITE"))
        assert updated is not None
        assert updated.phone == "+1-555-SQLITE"

    # Session 3: Confirm update persisted
    with factory() as db3:
        repo3 = SQLAlchemyCandidateRepository(db3)
        retrieved3 = repo3.get_by_id(cand_id)
        assert retrieved3.phone == "+1-555-SQLITE"


def test_analysis_and_signals_persistence():
    """Verify analysis and child risk signals are stored and retrievable across sessions."""
    factory = get_session_factory()

    # Create candidate
    with factory() as db:
        c_repo = SQLAlchemyCandidateRepository(db)
        candidate = c_repo.create(CandidateCreate(
            name="Signal Test Candidate",
            email="signal.test@example.com",
            role="Backend Dev",
        ))
        cand_id = candidate.id

    # Save analysis with signals
    with factory() as db:
        a_repo = SQLAlchemyAnalysisRepository(db)
        signal1 = RiskSignal(
            signal_name="FINANCIAL_SOLICITATION",
            category=RiskCategory.NLP,
            severity=80,
            weight=0.4,
            description="Upfront registration fee demanded.",
            evidence="$500 required",
        )
        signal2 = RiskSignal(
            signal_name="MISSING_SKILL",
            category=RiskCategory.TECHNICAL,
            severity=40,
            weight=0.2,
            description="Lacks required Go experience.",
        )
        analysis = AnalysisResponse(
            id="ANL-SQLITE01",
            candidate_id=cand_id,
            candidate_name="Signal Test Candidate",
            risk_score=67,
            risk_level=RiskLevel.HIGH,
            signals=[signal1, signal2],
            explanation="High risk due to upfront fee demand.",
            breakdown=ScoreBreakdown(nlp=80, technical=40),
            analyzed_at=datetime.now(timezone.utc),
        )
        saved = a_repo.save(analysis)
        assert saved.id == "ANL-SQLITE01"

    # Read analysis in fresh session
    with factory() as db:
        a_repo2 = SQLAlchemyAnalysisRepository(db)
        fetched = a_repo2.get_by_id("ANL-SQLITE01")
        assert fetched is not None
        assert fetched.risk_score == 67
        assert fetched.risk_level == RiskLevel.HIGH
        assert len(fetched.signals) == 2
        sig_names = [s.signal_name for s in fetched.signals]
        assert "FINANCIAL_SOLICITATION" in sig_names
        assert "MISSING_SKILL" in sig_names

        # Also verify listing by candidate ID
        by_cand = a_repo2.get_by_candidate_id(cand_id)
        assert len(by_cand) == 1
        assert by_cand[0].id == "ANL-SQLITE01"
