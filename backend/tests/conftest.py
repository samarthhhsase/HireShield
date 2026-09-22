import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_db
from app.db.session import get_session_factory
from app.models.candidate import Candidate
from app.models.analysis import Analysis
from app.models.risk_signal import RiskSignalModel
from app.db.repository import candidate_repo, analysis_repo


@pytest.fixture(autouse=True)
def setup_and_reset_db():
    """Ensure tables exist and clear test state before/after each test."""
    init_db()
    candidate_repo._storage.clear()
    analysis_repo._storage.clear()

    factory = get_session_factory()
    if factory is not None:
        db = factory()
        try:
            db.query(RiskSignalModel).delete()
            db.query(Analysis).delete()
            db.query(Candidate).delete()
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()

    yield

    candidate_repo._storage.clear()
    analysis_repo._storage.clear()
    if factory is not None:
        db = factory()
        try:
            db.query(RiskSignalModel).delete()
            db.query(Analysis).delete()
            db.query(Candidate).delete()
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as test_client:
        yield test_client
