from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
def get_health():
    """
    Service health probe.
    Returns: {"status": "ok", "service": "HireShield Backend"}
    """
    return {
        "status": "ok",
        "service": "HireShield Backend"
    }
