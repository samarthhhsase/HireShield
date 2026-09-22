from app.api.auth import router as auth_router
from app.api.risk import router as risk_router
from app.api.candidates import router as candidates_router

__all__ = ["auth_router", "risk_router", "candidates_router"]
