import json
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text
from app.db.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String(50), primary_key=True, default=lambda: f"HS-2026-{uuid.uuid4().hex[:6].upper()}")
    candidate_name = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    url = Column(String(1000), nullable=True)
    final_url = Column(String(1000), nullable=True)
    text_preview = Column(Text, nullable=True)

    risk_score = Column(Integer, default=0)
    risk_level = Column(String(20), default="LOW")
    verdict = Column(String(50), nullable=True)
    legitimacy_score = Column(Integer, nullable=True)
    fake_job_probability = Column(Float, nullable=True)
    input_type = Column(String(20), default="URL")
    user_id = Column(String(36), nullable=True, index=True)

    # JSON stored as Text for foolproof SQLite compatibility
    scores_json = Column(Text, nullable=True, default="{}")
    red_flags_json = Column(Text, nullable=True, default="[]")
    green_flags_json = Column(Text, nullable=True, default="[]")
    technical_checks_json = Column(Text, nullable=True, default="{}")
    verification_audit_json = Column(Text, nullable=True, default="{}")
    recommendations_json = Column(Text, nullable=True, default="[]")
    explanation = Column(Text, nullable=True)

    is_demo_data = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    scanned_at = Column(DateTime, default=datetime.utcnow)

    @property
    def scores(self):
        try:
            return json.loads(self.scores_json or "{}")
        except Exception:
            return {}

    @scores.setter
    def scores(self, val):
        self.scores_json = json.dumps(val or {})

    @property
    def red_flags(self):
        try:
            return json.loads(self.red_flags_json or "[]")
        except Exception:
            return []

    @red_flags.setter
    def red_flags(self, val):
        self.red_flags_json = json.dumps(val or [])

    @property
    def green_flags(self):
        try:
            return json.loads(self.green_flags_json or "[]")
        except Exception:
            return []

    @green_flags.setter
    def green_flags(self, val):
        self.green_flags_json = json.dumps(val or [])

    @property
    def technical_checks(self):
        try:
            return json.loads(self.technical_checks_json or "{}")
        except Exception:
            return {}

    @technical_checks.setter
    def technical_checks(self, val):
        self.technical_checks_json = json.dumps(val or {})

    @property
    def verification_audit(self):
        try:
            return json.loads(self.verification_audit_json or "{}")
        except Exception:
            return {}

    @verification_audit.setter
    def verification_audit(self, val):
        self.verification_audit_json = json.dumps(val or {})

    @property
    def recommendations(self):
        try:
            return json.loads(self.recommendations_json or "[]")
        except Exception:
            return []

    @recommendations.setter
    def recommendations(self, val):
        self.recommendations_json = json.dumps(val or [])

    def to_dict(self):
        """Serialize candidate/job scan record to dictionary for API responses."""
        return {
            "id": self.id,
            "candidateName": self.candidate_name or self.title or "Target Subject",
            "candidate_name": self.candidate_name or self.title or "Target Subject",
            "title": self.title,
            "company": self.company,
            "url": self.url,
            "final_url": self.final_url or self.url,
            "job": {
                "title": self.title or self.candidate_name or "Job Posting",
                "company": self.company,
                "text_preview": self.text_preview or "",
            },
            "scores": self.scores,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "verdict": self.verdict,
            "legitimacy_score": self.legitimacy_score,
            "fake_job_probability": self.fake_job_probability,
            "red_flags": self.red_flags,
            "green_flags": self.green_flags,
            "technical_checks": self.technical_checks,
            "verification_audit": self.verification_audit,
            "recommendations": self.recommendations,
            "explanation": self.explanation,
            "content_analyzed": True,
            "fetch_status": "FETCH_SUCCESS",
            "input_type": self.input_type or "URL",
            "inputType": self.input_type or "URL",
            "user_id": self.user_id,
            "isDemoData": self.is_demo_data,
            "is_demo_data": self.is_demo_data,
            "scannedAt": self.scanned_at.isoformat() if self.scanned_at else (self.created_at.isoformat() if self.created_at else None),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Scan(Base):
    __tablename__ = "scans"

    id = Column(String(50), primary_key=True, default=lambda: f"SCAN-{uuid.uuid4().hex[:8].upper()}")
    user_id = Column(String(36), nullable=True, index=True)
    target_url = Column(String(1000), nullable=True)
    final_url = Column(String(1000), nullable=True)
    title = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    risk_score = Column(Integer, default=0)
    risk_level = Column(String(20), default="LOW")
    verdict = Column(String(50), nullable=True)
    input_type = Column(String(20), default="URL")
    raw_payload_json = Column(Text, nullable=True, default="{}")
    scanned_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        try:
            payload = json.loads(self.raw_payload_json or "{}")
        except Exception:
            payload = {}
        return {
            "id": self.id,
            "user_id": self.user_id,
            "url": self.target_url,
            "final_url": self.final_url,
            "title": self.title,
            "company": self.company,
            "input_type": self.input_type or "URL",
            "inputType": self.input_type or "URL",
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "verdict": self.verdict,
            "scanned_at": self.scanned_at.isoformat() if self.scanned_at else None,
            "payload": payload,
        }

