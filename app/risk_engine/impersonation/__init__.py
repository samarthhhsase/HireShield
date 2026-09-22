"""
HireShield Impersonation & Lookalike Detection Package.
"""

from app.risk_engine.impersonation.detector import (
    detect_lookalike_domain,
    levenshtein_distance,
    normalized_similarity,
)

__all__ = [
    "detect_lookalike_domain",
    "levenshtein_distance",
    "normalized_similarity",
]
