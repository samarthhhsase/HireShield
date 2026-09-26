import json
import logging
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app.models.candidate import Candidate, Scan
from app.schemas.candidate import CandidateCreate

logger = logging.getLogger("hireshield.services.candidate")

# Baseline reference profiles for initial database state
DEFAULT_SEEDS = [
    {
        "id": "HS-2026-00421",
        "candidate_name": "Alex Mercer (Lead Fullstack Architect)",
        "title": "Senior Distributed Systems Architect",
        "company": "Example Careers Cloud",
        "url": "https://example-careers.io/positions/lead-architect",
        "final_url": "https://example-careers.io/positions/lead-architect",
        "text_preview": "Seeking experienced architect with 8+ years in cloud infrastructure, Go, and Kubernetes. No upfront deposit required.",
        "risk_score": 11,
        "risk_level": "LOW",
        "verdict": "VERIFIED_LEGITIMATE",
        "legitimacy_score": 89,
        "fake_job_probability": 0.11,
        "scores": {
            "behavioral": 12,
            "linguistic": 8,
            "structural": 10,
            "technical": 15,
        },
        "red_flags": [],
        "green_flags": [
            {"type": "verification", "message": "Established domain registration (> 3 years old)."},
            {"type": "verification", "message": "Valid enterprise SSL certificate and verified DNS records."},
            {"type": "verification", "message": "No advance payment, deposit, or paid training solicitation detected."}
        ],
        "technical_checks": {
            "ssl_valid": True,
            "domain_age_days": 1420,
            "dns_exists": True,
            "ip": "198.51.100.42",
            "redirect_count": 0,
        },
        "verification_audit": {
            "verdict": "VERIFIED_LEGITIMATE",
            "checks_performed": [
                {"name": "Domain Age Verification", "passed": True, "category": "domain", "description": "Domain registered over 1400 days ago."},
                {"name": "SSL / TLS Encryption", "passed": True, "category": "security", "description": "Valid SSL certificate active."},
                {"name": "Payment Trap Detection", "passed": True, "category": "behavioral", "description": "No upfront deposit demands found."},
                {"name": "Credential Harvesting Check", "passed": True, "category": "behavioral", "description": "No sensitive government ID solicitations found."}
            ]
        },
        "explanation": "This job posting exhibits verified technical infrastructure, legitimate company credentials, and zero predatory upfront fee patterns.",
        "is_demo_data": True,
    },
    {
        "id": "HS-2026-00892",
        "candidate_name": "Elena Rostova (Cryptographic Engineer)",
        "title": "Immediate Remote Data Entry Specialist - Urgent Hiring",
        "company": "Telegram Quick Hire Network",
        "url": "https://telegram-quick-hire.vip/apply-urgent",
        "final_url": "https://redirect-node.net/portal/fee-collector",
        "text_preview": "Urgent vacancies! High salary guaranteed! Must pay ₹2500 refundable processing fee and provide Aadhaar Card and bank account details for verification.",
        "risk_score": 85,
        "risk_level": "CRITICAL",
        "verdict": "CONFIRMED_SCAM",
        "legitimacy_score": 15,
        "fake_job_probability": 0.85,
        "scores": {
            "behavioral": 90,
            "linguistic": 65,
            "structural": 60,
            "technical": 75,
        },
        "red_flags": [
            {
                "type": "behavioral",
                "severity": "critical",
                "message": "Sensitive identity or financial information is requested.",
            },
            {
                "type": "behavioral",
                "severity": "critical",
                "message": "A payment, fee, deposit, or paid verification is requested.",
            },
            {
                "type": "linguistic",
                "severity": "high",
                "message": "Urgency or pressure-based recruitment language detected.",
            },
            {
                "type": "structural",
                "severity": "medium",
                "message": "Recruitment appears to rely on informal messaging channels.",
            },
        ],
        "green_flags": [],
        "technical_checks": {
            "ssl_valid": False,
            "domain_age_days": 12,
            "dns_exists": True,
            "ip": "203.0.113.19",
            "redirect_count": 3,
        },
        "verification_audit": {
            "verdict": "CONFIRMED_SCAM",
            "checks_performed": [
                {"name": "Payment Trap Detection", "passed": False, "category": "behavioral", "description": "Demands ₹2,500 advance registration deposit."},
                {"name": "Credential Harvesting Check", "passed": False, "category": "behavioral", "description": "Demands Aadhaar and banking details."},
                {"name": "Domain Age Check", "passed": False, "category": "domain", "description": "Suspicious young domain (12 days old)."},
                {"name": "SSL Encryption", "passed": False, "category": "security", "description": "Invalid SSL certificate."}
            ]
        },
        "explanation": "Critical danger: Soliciting advance payment fees and sensitive Aadhaar identity details over an untrusted redirect proxy.",
        "is_demo_data": True,
    },
    {
        "id": "HS-2026-01044",
        "candidate_name": "Marcus Vance (Data Science Lead)",
        "title": "Machine Learning Research Engineer",
        "company": "Fast Talent Pipeline",
        "url": "https://fast-talent-pipeline.co/roles/ds",
        "final_url": "https://fast-talent-pipeline.co/roles/ds",
        "text_preview": "Position available immediately. No experience required for high salary. Send resume via WhatsApp recruiter.",
        "risk_score": 42,
        "risk_level": "MEDIUM",
        "verdict": "SUSPICIOUS_UNVERIFIED",
        "legitimacy_score": 58,
        "fake_job_probability": 0.42,
        "scores": {
            "behavioral": 0,
            "linguistic": 55,
            "structural": 40,
            "technical": 25,
        },
        "red_flags": [
            {
                "type": "linguistic",
                "severity": "high",
                "message": "Unusually strong job or income guarantees detected.",
            },
            {
                "type": "structural",
                "severity": "medium",
                "message": "Recruitment appears to rely on informal messaging channels.",
            },
        ],
        "green_flags": [
            {"type": "verification", "message": "Standard HTTPS transport layer active."},
            {"type": "verification", "message": "No direct payment solicitations detected."}
        ],
        "technical_checks": {
            "ssl_valid": True,
            "domain_age_days": 94,
            "dns_exists": True,
            "ip": "198.51.100.88",
            "redirect_count": 1,
        },
        "verification_audit": {
            "verdict": "SUSPICIOUS_UNVERIFIED",
            "checks_performed": [
                {"name": "Informal Channel Audit", "passed": False, "category": "structural", "description": "Redirects to informal WhatsApp recruiter."},
                {"name": "Guaranteed Income Check", "passed": False, "category": "linguistic", "description": "Unrealistic income guarantee with no experience requirement."}
            ]
        },
        "explanation": "Suspicious indicators detected: Reliance on WhatsApp recruiter and inflated compensation promises with low qualifications.",
        "is_demo_data": True,
    },
]


def seed_default_candidates(db: Session):
    """Seed baseline candidate/job targets in SQLite if database is empty."""
    count = db.query(Candidate).count()
    if count > 0:
        return

    logger.info("Seeding default candidate & job intelligence records in SQLite...")
    for seed in DEFAULT_SEEDS:
        cand = Candidate(
            id=seed["id"],
            candidate_name=seed["candidate_name"],
            title=seed["title"],
            company=seed["company"],
            url=seed["url"],
            final_url=seed["final_url"],
            text_preview=seed["text_preview"],
            risk_score=seed["risk_score"],
            risk_level=seed["risk_level"],
            verdict=seed.get("verdict"),
            legitimacy_score=seed.get("legitimacy_score"),
            fake_job_probability=seed.get("fake_job_probability"),
            explanation=seed.get("explanation"),
            is_demo_data=seed.get("is_demo_data", True),
            created_at=datetime.utcnow(),
            scanned_at=datetime.utcnow(),
        )
        cand.scores = seed.get("scores", {})
        cand.red_flags = seed.get("red_flags", [])
        cand.green_flags = seed.get("green_flags", [])
        cand.technical_checks = seed.get("technical_checks", {})
        cand.verification_audit = seed.get("verification_audit", {})
        db.add(cand)

    db.commit()
    logger.info("Successfully seeded 3 baseline candidate records.")


def get_candidates(
    db: Session,
    search: Optional[str] = None,
    risk_level: Optional[str] = None,
    user_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Query candidates with optional text search, threat level filtering, and user isolation."""
    query = db.query(Candidate)

    if user_id:
        query = query.filter(
            or_(
                Candidate.user_id == user_id,
                Candidate.is_demo_data == True,
            )
        )
    else:
        query = query.filter(
            or_(
                Candidate.user_id.is_(None),
                Candidate.is_demo_data == True,
            )
        )

    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Candidate.candidate_name.ilike(s),
                Candidate.title.ilike(s),
                Candidate.company.ilike(s),
                Candidate.url.ilike(s),
            )
        )

    if risk_level:
        query = query.filter(Candidate.risk_level == risk_level.upper())

    records = query.order_by(desc(Candidate.scanned_at)).offset(skip).limit(limit).all()
    return [c.to_dict() for c in records]


def get_candidate_by_id(
    db: Session,
    candidate_id: str,
    user_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single candidate by unique ID.
    Enforces authorization:
    - Demo data is publicly accessible.
    - User-created scans can only be accessed by their creator (returns {"_forbidden": True} if unauthorized).
    """
    record = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not record:
        return None

    if record.is_demo_data:
        return record.to_dict()

    if record.user_id:
        if not user_id or record.user_id != user_id:
            return {"_forbidden": True, "id": record.id}

    return record.to_dict()


def create_candidate(
    db: Session,
    payload: CandidateCreate,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Persist a new candidate/job scan dossier to SQLite associated with user_id."""
    resolved_id = payload.id or f"HS-2026-{uuid.uuid4().hex[:6].upper()}"
    
    # Check if ID already exists
    existing = db.query(Candidate).filter(Candidate.id == resolved_id).first()
    if existing:
        resolved_id = f"HS-2026-{uuid.uuid4().hex[:6].upper()}"

    resolved_name = (
        payload.candidateName
        or payload.candidate_name
        or payload.title
        or (payload.job.title if payload.job else None)
        or "Scanned Target Subject"
    )
    resolved_title = (
        payload.title
        or (payload.job.title if payload.job else None)
        or resolved_name
    )
    resolved_company = payload.company or (payload.job.company if payload.job else None)
    resolved_preview = payload.text_preview or (payload.job.text_preview if payload.job else None)
    effective_user_id = user_id or getattr(payload, "user_id", None)

    cand = Candidate(
        id=resolved_id,
        user_id=effective_user_id,
        candidate_name=resolved_name,
        title=resolved_title,
        company=resolved_company,
        url=payload.url,
        final_url=payload.final_url or payload.url,
        text_preview=resolved_preview,
        risk_score=payload.risk_score or 0,
        risk_level=(payload.risk_level or "LOW").upper(),
        verdict=payload.verdict,
        legitimacy_score=payload.legitimacy_score,
        fake_job_probability=payload.fake_job_probability,
        input_type=payload.input_type or "URL",
        explanation=payload.explanation,
        is_demo_data=bool(payload.is_demo_data or payload.isDemoData),
        created_at=datetime.utcnow(),
        scanned_at=datetime.utcnow(),
    )
    cand.scores = payload.scores or {}
    cand.red_flags = payload.red_flags or []
    cand.green_flags = payload.green_flags or []
    cand.technical_checks = payload.technical_checks or {}
    cand.verification_audit = payload.verification_audit or {}
    cand.recommendations = payload.recommendations or []

    db.add(cand)
    db.commit()
    db.refresh(cand)

    logger.info(f"Persisted candidate dossier: {cand.id} ({cand.candidate_name}) [user_id={effective_user_id}]")
    return cand.to_dict()


def auto_save_scan(
    db: Session,
    scan_result: Dict[str, Any],
    user_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Automatically persist live scan results into the candidate / job registry associated with user."""
    try:
        effective_user_id = user_id or scan_result.get("user_id")
        url = scan_result.get("url") or scan_result.get("final_url")
        input_type = scan_result.get("input_type") or scan_result.get("inputType") or "URL"
        job_info = scan_result.get("job") or {}
        title = job_info.get("title") or "Recruitment Target"
        company = job_info.get("company")
        text_preview = job_info.get("text_preview") or ""

        # Avoid spamming duplicate identical URLs within seconds for same user
        if url:
            query = db.query(Candidate).filter(Candidate.url == url)
            if effective_user_id:
                existing = query.filter(Candidate.user_id == effective_user_id).first()
            else:
                existing = query.filter(
                    or_(Candidate.user_id.is_(None), Candidate.is_demo_data == True)
                ).first()

            if existing:
                # Update existing record with newest analysis
                existing.risk_score = scan_result.get("risk_score", existing.risk_score)
                existing.risk_level = scan_result.get("risk_level", existing.risk_level)
                existing.verdict = scan_result.get("verdict", existing.verdict)
                existing.legitimacy_score = scan_result.get("legitimacy_score", existing.legitimacy_score)
                existing.fake_job_probability = scan_result.get("fake_job_probability", existing.fake_job_probability)
                existing.input_type = input_type
                existing.scores = scan_result.get("scores", existing.scores)
                existing.red_flags = scan_result.get("red_flags", existing.red_flags)
                existing.green_flags = scan_result.get("green_flags", existing.green_flags)
                existing.technical_checks = scan_result.get("technical_checks", existing.technical_checks)
                existing.verification_audit = scan_result.get("verification_audit", existing.verification_audit)
                existing.explanation = scan_result.get("explanation", existing.explanation)
                existing.scanned_at = datetime.utcnow()
                db.commit()
                db.refresh(existing)
                return existing.to_dict()

        # Also persist to Scans audit table for activity telemetry and user scan history
        try:
            scan_log = Scan(
                user_id=effective_user_id,
                target_url=url,
                final_url=scan_result.get("final_url") or url,
                title=title,
                company=company,
                risk_score=scan_result.get("risk_score", 0),
                risk_level=scan_result.get("risk_level", "LOW"),
                verdict=scan_result.get("verdict"),
                input_type=input_type,
                raw_payload_json=json.dumps(scan_result),
                scanned_at=datetime.utcnow(),
            )
            db.add(scan_log)
            db.commit()
        except Exception as scan_err:
            logger.warning(f"Could not persist scan log: {scan_err}")

        cand_create = CandidateCreate(
            candidate_name=title,
            title=title,
            company=company,
            url=url,
            final_url=scan_result.get("final_url") or url,
            text_preview=text_preview,
            risk_score=scan_result.get("risk_score", 0),
            risk_level=scan_result.get("risk_level", "LOW"),
            verdict=scan_result.get("verdict"),
            legitimacy_score=scan_result.get("legitimacy_score"),
            fake_job_probability=scan_result.get("fake_job_probability"),
            input_type=input_type,
            scores=scan_result.get("scores", {}),
            red_flags=scan_result.get("red_flags", []),
            green_flags=scan_result.get("green_flags", []),
            technical_checks=scan_result.get("technical_checks", {}),
            verification_audit=scan_result.get("verification_audit", {}),
            recommendations=scan_result.get("recommendations", []),
            explanation=scan_result.get("explanation"),
            is_demo_data=False,
        )
        return create_candidate(db, cand_create, user_id=effective_user_id)
    except Exception as exc:
        logger.warning(f"Could not auto-save scan as candidate: {exc}")
        return None


def get_user_scans(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Retrieve scans strictly belonging to the specified user."""
    scans = (
        db.query(Scan)
        .filter(Scan.user_id == user_id)
        .order_by(desc(Scan.scanned_at))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [s.to_dict() for s in scans]


def get_user_scan_by_id(
    db: Session,
    scan_id: str,
    user_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific scan by ID, enforcing strict ownership:
    - Returns None if scan does not exist
    - Returns {"_forbidden": True} if scan exists but belongs to a different user
    - Returns scan dictionary if owned by requesting user
    """
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        return None
    if scan.user_id != user_id:
        return {"_forbidden": True, "id": scan.id}
    return scan.to_dict()


def get_activity_log(db: Session, limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve live API scan telemetry and audit event records."""
    scans = db.query(Scan).order_by(desc(Scan.scanned_at)).limit(limit).all()
    if scans:
        return [
            {
                "id": s.id,
                "timestamp": s.scanned_at.isoformat() if s.scanned_at else datetime.utcnow().isoformat(),
                "method": "POST",
                "endpoint": "/api/scan",
                "target": s.target_url or s.final_url or s.title or "Scan Target",
                "status": 200,
                "riskScore": s.risk_score,
                "riskLevel": s.risk_level,
                "verdict": s.verdict,
                "inputType": getattr(s, "input_type", "URL") or "URL",
                "input_type": getattr(s, "input_type", "URL") or "URL",
            }
            for s in scans
        ]
    # Fallback to candidate entries if no dedicated scans recorded yet
    candidates = db.query(Candidate).order_by(desc(Candidate.scanned_at)).limit(limit).all()
    return [
        {
            "id": f"ACT-{c.id}",
            "timestamp": c.scanned_at.isoformat() if c.scanned_at else datetime.utcnow().isoformat(),
            "method": "POST",
            "endpoint": "/api/scan",
            "target": c.url or c.title or "Recruitment Target",
            "status": 200,
            "riskScore": c.risk_score,
            "riskLevel": c.risk_level,
            "verdict": c.verdict,
            "inputType": getattr(c, "input_type", "URL") or "URL",
            "input_type": getattr(c, "input_type", "URL") or "URL",
        }
        for c in candidates
    ]


def get_reports_list(db: Session, limit: int = 100) -> List[Dict[str, Any]]:
    """Retrieve compiled threat dossiers formatted for security intelligence reports."""
    candidates = get_candidates(db, limit=limit)
    return [
        {
            **c,
            "report_id": f"REP-{c['id']}",
            "generated_at": datetime.utcnow().isoformat(),
            "status": "COMPILED",
        }
        for c in candidates
    ]


def delete_candidate(db: Session, candidate_id: str, user_id: Optional[str] = None) -> Optional[bool]:
    """Delete a candidate dossier from database by ID with ownership enforcement."""
    record = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not record:
        return False
    if record.user_id and user_id and record.user_id != user_id:
        return None  # forbidden flag
    db.delete(record)
    db.commit()
    logger.info(f"Deleted candidate dossier: {candidate_id}")
    return True
