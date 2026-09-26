import logging
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.db.database import Base, engine, SessionLocal
from app.models.candidate import Candidate
from app.models.user import User
from sqlalchemy import or_, desc
from app.api.auth import router as auth_router
from app.api.risk import router as risk_router
from app.api.candidates import router as candidates_router
from app.api.scanner import router as scanner_router
from app.services.risk_pipeline import categorize_signals
from app.services.auth_service import seed_default_analyst, get_optional_current_user
from app.services.candidate_service import seed_default_candidates, auto_save_scan
from app.services.scraper import (
    extract_job_page,
    is_valid_url,
    FETCH_SUCCESS,
    FETCH_BLOCKED,
    FETCH_NOT_FOUND,
    FETCH_RATE_LIMITED,
    FETCH_SERVER_ERROR,
    FETCH_TIMEOUT,
    FETCH_NETWORK_ERROR,
    FETCH_INVALID_URL,
    BROWSER_PROVIDED,
    BROWSER_CONTENT_RECEIVED,
)
from app.services.technical import analyze_technical
from app.services.risk_engine import calculate_risk
from app.services.ai_client import analyze_with_ai

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("hireshield")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing HireShield SQLite database & tables...")
    try:
        # Verify candidates table schema compatibility
        try:
            with engine.connect() as conn:
                cols = [r[1] for r in conn.exec_driver_sql("PRAGMA table_info(candidates)").fetchall()]
                if cols and "candidate_name" not in cols:
                    logger.info("Migrating legacy candidates table schema...")
                    conn.exec_driver_sql("DROP TABLE candidates")
                    conn.commit()
        except Exception:
            pass

        Base.metadata.create_all(bind=engine)
        try:
            with engine.connect() as conn:
                cand_cols = [r[1] for r in conn.exec_driver_sql("PRAGMA table_info(candidates)").fetchall()]
                if cand_cols and "input_type" not in cand_cols:
                    logger.info("Adding input_type column to candidates table...")
                    conn.exec_driver_sql("ALTER TABLE candidates ADD COLUMN input_type VARCHAR(20) DEFAULT 'URL'")
                    conn.commit()
                scan_cols = [r[1] for r in conn.exec_driver_sql("PRAGMA table_info(scans)").fetchall()]
                if scan_cols and "input_type" not in scan_cols:
                    logger.info("Adding input_type column to scans table...")
                    conn.exec_driver_sql("ALTER TABLE scans ADD COLUMN input_type VARCHAR(20) DEFAULT 'URL'")
                    conn.commit()
        except Exception as mig_err:
            logger.warning(f"Schema check error: {mig_err}")

        with SessionLocal() as db:
            seed_default_analyst(db)
            seed_default_candidates(db)
        logger.info("Database initialized, default analyst and baseline job targets seeded successfully.")
    except Exception as exc:
        logger.error(f"Database initialization error: {exc}", exc_info=True)
    yield
    logger.info("HireShield backend shutting down.")


app = FastAPI(
    title="HireShield API",
    description="AI-powered candidate threat intelligence, job scam detection, and security analyst authentication backend.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(auth_router, prefix="/api")
app.include_router(risk_router, prefix="/api")
app.include_router(candidates_router, prefix="/api")
app.include_router(candidates_router)
app.include_router(scanner_router, prefix="/api")
app.include_router(scanner_router)


class ScanRequest(BaseModel):
    url: str


class ContentScanRequest(BaseModel):
    url: Optional[str] = ""
    title: Optional[str] = ""
    company: Optional[str] = ""
    content: str


@app.get("/")
def home():
    return {
        "name": "HireShield",
        "status": "running",
        "message": "Candidate risk intelligence & scam detection backend is ready",
        "scanner_endpoints": {
            "url_scan": "/api/scan",
            "pdf_scan": "/api/scanner/analyze-pdf",
            "form_scan": "/api/scanner/analyze-form",
            "text_scan": "/api/scanner/analyze-text",
            "content_fallback": "/api/scanner/analyze-content",
            "risk_engine": "/api/risk/analyze",
        },
        "candidate_endpoints": {
            "list": "/api/candidates",
            "get": "/api/candidates/{id}",
            "create": "/api/candidates",
            "delete": "/api/candidates/{id}",
        },
        "auth_endpoints": {
            "login": "/api/auth/login",
            "register": "/api/auth/register",
            "me": "/api/auth/me",
        },
    }


@app.get("/health")
@app.get("/api/health")
def health():
    return {"status": "healthy"}


@app.post("/api/scan")
def scan_job(
    request: ScanRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """
    Execute recruitment risk analysis on a target URL.
    Distinguishes server access limitations (e.g. HTTP 403) from fraud signals.
    """
    url = str(request.url).strip()
    logger.info(f"Scanner request received for: {url}")

    # 1. Fetch & extract page
    page = extract_job_page(url)
    fetch_status = page.get("fetch_status", FETCH_NETWORK_ERROR)
    final_url = page.get("final_url", url)

    # 2. Run Layer A: URL Intelligence & Technical checks (always executes)
    technical = analyze_technical(final_url, page.get("redirect_count", 0))

    # 3. Handle based on fetch status
    if fetch_status == FETCH_SUCCESS:
        logger.info(f"Page fetch succeeded for {url}, running Layer B NLP analysis")
        ai = analyze_with_ai(page.get("title", ""), page.get("text", ""))
        result = calculate_risk(
            behavioral=ai["behavioral_score"],
            linguistic=ai["linguistic_score"],
            structural=ai["structural_score"],
            technical=technical["technical_score"],
            red_flags=ai["red_flags"],
            green_flags=ai.get("green_flags", []),
            content_analyzed=True,
        )
        content_analyzed = True
        scores = {
            "behavioral": ai["behavioral_score"],
            "linguistic": ai["linguistic_score"],
            "structural": ai["structural_score"],
            "technical": technical["technical_score"],
        }
        red_flags = result["red_flags"]
        job_info = {
            "title": page.get("title", "Recruitment Posting"),
            "text_preview": page.get("text", "")[:1000],
        }
        content_intelligence = {
            "status": "ANALYZED",
            "source": "server_fetch",
            "word_count": ai.get("word_count", len(page.get("text", "").split())),
            "reason": None,
        }
        layers = {
            "infrastructure": {
                "status": "AVAILABLE",
                "description": "Layer A URL & Technical Infrastructure Analysis",
                "technical_score": technical["technical_score"],
            },
            "content": {
                "status": "AVAILABLE",
                "description": "Layer B Page Content & NLP Heuristics",
                "source": "server_fetch",
                "word_count": ai.get("word_count", len(page.get("text", "").split())),
            },
        }
    else:
        logger.info(f"Page fetch incomplete for {url} ({fetch_status}), skipping Layer B content analysis without risk penalty")
        result = calculate_risk(
            behavioral=0,
            linguistic=0,
            structural=0,
            technical=technical["technical_score"],
            red_flags=[],
            green_flags=[],
            content_analyzed=False,
        )
        content_analyzed = False
        scores = {
            "behavioral": None,
            "linguistic": None,
            "structural": None,
            "technical": technical["technical_score"],
        }
        red_flags = []
        job_info = {
            "title": page.get("title", "Access Restricted by Target Server"),
            "text_preview": page.get("message", "Automated access to target website was restricted. Page content was not analyzed."),
        }
        content_intelligence = {
            "status": "UNAVAILABLE",
            "source": None,
            "reason": page.get("message", "Target server access restriction."),
            "analyzed": False,
        }
        layers = {
            "infrastructure": {
                "status": "AVAILABLE",
                "description": "Layer A URL & Technical Infrastructure Analysis",
                "technical_score": technical["technical_score"],
            },
            "content": {
                "status": "UNAVAILABLE",
                "description": "Layer B Page Content & NLP Heuristics",
                "reason": page.get("message", "Target server access restriction."),
                "http_status": page.get("http_status"),
            },
        }

    scan_response = {
        "status": fetch_status,
        "fetch_status": fetch_status,
        "http_status": page.get("http_status"),
        "message": page.get("message", "Scan completed."),
        "risk_impact": 0 if not content_analyzed else None,
        "content_analyzed": content_analyzed,
        "risk_assessment_status": result["risk_assessment_status"],
        "fallback_available": page.get("fallback_available", False),
        "url": url,
        "final_url": final_url,
        "job": job_info,
        "scores": scores,
        "layers": layers,
        "risk_score": result["risk_score"],
        "score": result["risk_score"],
        "risk_level": result["risk_level"],
        "legitimacy_score": result.get("legitimacy_score"),
        "fake_job_probability": result.get("fake_job_probability"),
        "verdict": result.get("verdict"),
        "input_type": "URL",
        "inputType": "URL",
        "red_flags": red_flags,
        "signals": red_flags,
        "green_flags": result.get("green_flags", []),
        "positive_signals": [g.get("message", "") if isinstance(g, dict) else str(g) for g in result.get("green_flags", [])],
        "categories": categorize_signals(red_flags, technical_available=True),
        "recommendations": result.get("recommendations", []),
        "verification_audit": result.get("verification_audit"),
        "explanation": result.get("explanation"),
        "summary": result.get("explanation") or "URL recruitment scan completed.",
        "technical_checks": technical["checks"],
        "url_intelligence": technical["url_intelligence"],
        "content_intelligence": content_intelligence,
    }

    user_id = current_user.id if current_user else None
    scan_response["user_id"] = user_id

    try:
        with SessionLocal() as db:
            saved = auto_save_scan(db, scan_response, user_id=user_id)
            if saved and "id" in saved:
                scan_response["id"] = saved["id"]
    except Exception as exc:
        logger.warning(f"Error auto-persisting scan result to candidates db: {exc}")

    return scan_response


@app.post("/api/scanner/analyze-content")
@app.post("/api/scan/content")
def analyze_browser_content(
    request: ContentScanRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """
    Browser-content fallback endpoint:
    Processes page content supplied by the browser or browser extension through
    the exact same Risk Engine and Layer A URL intelligence.
    """
    raw_content = request.content
    if raw_content is None or not str(raw_content).strip():
        raise HTTPException(
            status_code=422,
            detail="Job description cannot be empty. Please paste the visible text from the job posting.",
        )

    content = str(raw_content).strip()
    if len(content) < 15:
        raise HTTPException(
            status_code=422,
            detail="Submitted content is too brief to evaluate. Please provide the full visible job description.",
        )

    if len(content) > 100000:
        raise HTTPException(
            status_code=422,
            detail="Submitted content exceeds the maximum limit of 100,000 characters.",
        )

    url = (request.url or "").strip()
    if url:
        if not is_valid_url(url):
            raise HTTPException(
                status_code=422,
                detail="The provided URL is invalid. Must be a valid HTTP or HTTPS URL.",
            )

    title = (request.title or "").strip()
    company = (request.company or "").strip()

    logger.info(f"Browser content analysis requested for URL: '{url}' (Title: '{title}', {len(content)} chars)")

    # 1. Run Layer A URL Intelligence if URL is provided
    if url:
        technical = analyze_technical(url, redirect_count=0)
    else:
        technical = {
            "technical_score": 0,
            "checks": {
                "ssl_valid": None,
                "domain_age_days": None,
                "dns_exists": None,
                "ip": None,
                "redirect_count": 0,
                "is_https": None,
                "suspicious_patterns": {"flagged": False},
            },
            "url_intelligence": {
                "domain": "Not Provided",
                "is_https": False,
                "dns_exists": False,
                "ssl_valid": False,
                "domain_age_days": None,
                "ip": None,
                "suspicious_url_patterns": False,
                "analysis_available": False,
            },
        }

    # 2. Run Layer B NLP Analysis on provided content
    combined_headline = f"{title} {company}".strip()
    ai = analyze_with_ai(combined_headline, content)

    # 3. Run Risk Engine combining both layers
    result = calculate_risk(
        behavioral=ai["behavioral_score"],
        linguistic=ai["linguistic_score"],
        structural=ai["structural_score"],
        technical=technical["technical_score"],
        red_flags=ai["red_flags"],
        green_flags=ai.get("green_flags", []),
        content_analyzed=True,
    )

    layers = {
        "infrastructure": {
            "status": "AVAILABLE" if url else "NOT_PROVIDED",
            "description": "Layer A URL & Technical Infrastructure Analysis",
            "technical_score": technical["technical_score"],
        },
        "content": {
            "status": "AVAILABLE",
            "description": "Layer B Page Content & NLP Heuristics",
            "source": "browser_fallback",
            "word_count": ai.get("word_count", len(content.split())),
        },
    }

    pipeline_stages = [
        "CONTENT_RECEIVED",
        "NORMALIZING_TEXT",
        "RUNNING_NLP",
        "ANALYZING_BEHAVIOR",
        "ANALYZING_LINGUISTICS",
        "ANALYZING_STRUCTURE",
        "CALCULATING_RISK",
        "ANALYSIS_COMPLETE",
    ]

    content_response = {
        "status": "FETCH_SUCCESS",
        "fetch_status": BROWSER_CONTENT_RECEIVED,
        "http_status": 200,
        "message": "Page content provided via browser fallback analyzed successfully.",
        "risk_impact": 0,
        "content_analyzed": True,
        "content_analysis_status": "CONTENT_ANALYSIS_AVAILABLE",
        "risk_assessment_status": "RISK_ASSESSMENT_COMPLETE",
        "fallback_available": False,
        "url": url,
        "final_url": url,
        "job": {
            "title": title or "Browser Extracted Job",
            "company": company or None,
            "text_preview": content[:1000],
        },
        "scores": {
            "behavioral": ai["behavioral_score"],
            "linguistic": ai["linguistic_score"],
            "structural": ai["structural_score"],
            "technical": technical["technical_score"],
        },
        "layers": layers,
        "risk_score": result["risk_score"],
        "score": result["risk_score"],
        "risk_level": result["risk_level"],
        "legitimacy_score": result.get("legitimacy_score"),
        "fake_job_probability": result.get("fake_job_probability"),
        "verdict": result.get("verdict"),
        "input_type": "TEXT" if not url else "URL",
        "inputType": "TEXT" if not url else "URL",
        "red_flags": result["red_flags"],
        "signals": result["red_flags"],
        "green_flags": result.get("green_flags", []),
        "positive_signals": [g.get("message", "") if isinstance(g, dict) else str(g) for g in result.get("green_flags", [])],
        "categories": categorize_signals(result["red_flags"], technical_available=bool(url)),
        "recommendations": result.get("recommendations", []),
        "verification_audit": result.get("verification_audit"),
        "explanation": result["explanation"],
        "summary": result["explanation"],
        "technical_checks": technical["checks"],
        "url_intelligence": technical["url_intelligence"],
        "pipeline_stages": pipeline_stages,
        "content_intelligence": {
            "status": "ANALYZED",
            "source": "browser_fallback",
            "word_count": ai.get("word_count", len(content.split())),
            "reason": None,
        },
    }

    user_id = current_user.id if current_user else None
    content_response["user_id"] = user_id

    try:
        with SessionLocal() as db:
            saved = auto_save_scan(db, content_response, user_id=user_id)
            if saved and "id" in saved:
                content_response["id"] = saved["id"]
    except Exception as exc:
        logger.warning(f"Error auto-persisting content scan result to candidates db: {exc}")

    return content_response
