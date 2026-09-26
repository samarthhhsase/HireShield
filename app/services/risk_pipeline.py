"""
HireShield Unified Multi-Input Risk Analysis Pipeline.

Coordinates ingestion across:
1. Job URL
2. Job/Offer PDF
3. Google Form / Recruitment Form URL
4. Pasted Job Description / Recruitment Text

Passes all content through the exact same central risk-analysis engine,
generating explainable scores, categorized risks (Financial, Identity, Behavioral, Technical),
evidence-based natural language summaries, and practical safety recommendations.
"""

import re
import logging
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

from app.risk_engine.risk_engine import default_risk_engine
from app.risk_engine.domain.analyzer import analyze_domain, extract_domain_from_url
from app.services.technical import analyze_technical
from app.services.candidate_service import auto_save_scan
from app.db.database import SessionLocal

logger = logging.getLogger("hireshield.services.risk_pipeline")


def categorize_signals(signals: List[Dict[str, Any]], technical_available: bool) -> Dict[str, Any]:
    """
    Groups detected signals and scores into 4 clear risk categories:
    - Financial Risk (upfront fees, deposits, courier charges, crypto, fake check cashing)
    - Identity/Data Risk (Aadhaar, PAN, passport, bank details, net banking, OTP, passwords)
    - Behavioral Risk (urgency, guaranteed placement, off-platform chat, vague lures, salary anomalies)
    - Technical Risk (domain age, SSL, DNS, lookalike typosquatting, private IP)
    """
    financial_flags: List[str] = []
    identity_flags: List[str] = []
    behavioral_flags: List[str] = []
    technical_flags: List[str] = []

    financial_score_accum = 0
    identity_score_accum = 0
    behavioral_score_accum = 0
    technical_score_accum = 0

    for s in signals:
        cat = s.get("category", "").lower()
        title = s.get("title", "")
        desc = s.get("description", "")
        sev = s.get("severity", "medium").lower()
        score = s.get("score", 0) or (45 if sev == "critical" else (30 if sev == "high" else 15))

        title_lower = title.lower()

        # Financial categorization
        if any(term in cat or term in title_lower for term in ["payment", "fee", "deposit", "mule", "check", "crypto", "cash"]):
            financial_flags.append(title)
            financial_score_accum += score

        # Identity/Data categorization
        elif any(term in cat or term in title_lower for term in ["credential", "aadhaar", "pan", "passport", "bank", "otp", "password", "pin", "cvv", "credit_card", "government id", "identity", "upi"]):
            identity_flags.append(title)
            identity_score_accum += score

        # Technical/Domain categorization
        elif any(term in cat or term in title_lower for term in ["domain", "ssl", "dns", "impersonation", "whois", "lookalike", "ip"]):
            technical_flags.append(title)
            technical_score_accum += score

        # Behavioral categorization (urgency, chat, lure, salary, recruiter, etc.)
        else:
            behavioral_flags.append(title)
            behavioral_score_accum += score

    def calc_cat_level(sc: int) -> str:
        if sc >= 70:
            return "Critical"
        if sc >= 40:
            return "High"
        if sc >= 20:
            return "Medium"
        return "Low"

    fin_score = min(100, financial_score_accum)
    id_score = min(100, identity_score_accum)
    beh_score = min(100, behavioral_score_accum)
    tech_score = min(100, technical_score_accum) if technical_available else None

    categories = {
        "financial_risk": {
            "name": "Financial Risk",
            "score": fin_score,
            "level": calc_cat_level(fin_score),
            "status": "AVAILABLE",
            "flags": financial_flags,
            "reason": (
                f"{len(financial_flags)} payment or deposit indicator(s) detected."
                if financial_flags else "No upfront fees or deposit demands detected."
            )
        },
        "identity_risk": {
            "name": "Identity / Data Risk",
            "score": id_score,
            "level": calc_cat_level(id_score),
            "status": "AVAILABLE",
            "flags": identity_flags,
            "reason": (
                f"{len(identity_flags)} sensitive identity or credential solicitation(s) detected."
                if identity_flags else "No premature government ID or credential requests detected."
            )
        },
        "behavioral_risk": {
            "name": "Behavioral Risk",
            "score": beh_score,
            "level": calc_cat_level(beh_score),
            "status": "AVAILABLE",
            "flags": behavioral_flags,
            "reason": (
                f"{len(behavioral_flags)} behavioral anomaly indicator(s) identified."
                if behavioral_flags else "Recruitment process follows standard professional communication."
            )
        },
        "technical_risk": {
            "name": "Technical Risk",
            "score": tech_score,
            "level": calc_cat_level(tech_score) if technical_available else "Unavailable",
            "status": "AVAILABLE" if technical_available else "UNAVAILABLE",
            "flags": technical_flags if technical_available else [],
            "reason": (
                (f"{len(technical_flags)} network or domain anomaly indicator(s) found." if technical_flags else "Domain infrastructure appears established and secure.")
                if technical_available else "No external technical URL provided for infrastructure scanning."
            )
        },
    }

    return categories


def build_evidence_based_summary(
    risk_score: int,
    risk_level: str,
    signals: List[Dict[str, Any]],
    positive_signals: List[str],
    input_type: str,
    override_info: Optional[Dict[str, Any]] = None
) -> str:
    """
    Constructs an evidence-grounded natural-language summary.
    Does not make unsupported defamatory claims; uses careful, objective language.
    """
    titles = [s.get("title", "") for s in signals]
    titles_lower = [t.lower() for t in titles]

    evidence_parts: List[str] = []

    if any("fee" in t or "payment" in t or "deposit" in t for t in titles_lower):
        evidence_parts.append("requests upfront payment or refundable registration fees before formal employment")

    if any("aadhaar" in t or "pan" in t or "passport" in t or "credential" in t for t in titles_lower):
        evidence_parts.append("prematurely requests sensitive government identity documents or banking credentials")

    if any("otp" in t or "password" in t or "pin" in t for t in titles_lower):
        evidence_parts.append("attempts to harvest authentication credentials or verification codes")

    if any("whatsapp" in t or "telegram" in t for t in titles_lower):
        evidence_parts.append("directs candidates toward informal, off-platform messaging channels")

    if any("urgency" in t or "immediate" in t for t in titles_lower):
        evidence_parts.append("employs artificial urgency or pressure tactics")

    if any("guaranteed" in t or "no interview" in t for t in titles_lower):
        evidence_parts.append("claims guaranteed employment or bypass of standard interview evaluation")

    if any("lookalike" in t or "impersonat" in t for t in titles_lower):
        evidence_parts.append("exhibits domain typographical similarity to a recognized brand")

    source_label = {
        "PDF": "The submitted document",
        "GOOGLE_FORM": "The analyzed recruitment form",
        "TEXT": "The submitted job description",
        "URL": "The target recruitment listing",
    }.get(input_type, "The evaluated recruitment target")

    if override_info and override_info.get("override"):
        core_reason = override_info.get("reason", "Critical recruitment fraud indicator detected")
        if evidence_parts:
            return (
                f"{source_label} triggered a high-risk security alert ({core_reason}). "
                f"Additionally, the content {', and '.join(evidence_parts)}. "
                "These signals significantly increase the potential risk to job applicants, and extreme caution is advised."
            )
        return (
            f"{source_label} triggered a high-risk security alert: {core_reason}. "
            "These indicators warrant comprehensive secondary verification before proceeding."
        )

    if risk_level == "CRITICAL":
        evidence_str = f"specifically because it {', and '.join(evidence_parts[:3])}" if evidence_parts else "exhibiting multiple severe recruitment anomalies"
        return (
            f"Multiple recruitment-fraud indicators were detected. {source_label} was flagged {evidence_str}. "
            "These high-risk signals strongly suggest potential employment fraud or credential harvesting. Do not transfer funds or share sensitive records."
        )

    if risk_level == "HIGH":
        evidence_str = f" The content {', and '.join(evidence_parts[:2])}." if evidence_parts else ""
        return (
            f"Elevated recruitment risk detected.{evidence_str} "
            "Several potentially suspicious indicators were identified. Further verification through official corporate channels is strongly recommended."
        )

    if risk_level in ("MEDIUM", "MODERATE"):
        top_name = titles[0] if titles else "unverified contact channels"
        return (
            f"Moderate risk indicators detected ({top_name}). "
            f"While not definitively fraudulent, {source_label.lower()} exhibits non-standard recruitment attributes. "
            "Independent verification of recruiter credentials is recommended before submitting confidential details."
        )

    # Low risk
    if positive_signals:
        top_pos = positive_signals[0].lower()
        return (
            f"{source_label} demonstrates legitimate corporate recruitment characteristics. "
            f"Verified trust indicators include {top_pos}. Standard professional hiring practices apply."
        )

    return (
        f"{source_label} appears consistent with standard employment postings. "
        "No upfront fee solicitations, credential harvesting, or prominent fraud indicators were identified."
    )


def build_actionable_recommendations(
    risk_level: str,
    signals: List[Dict[str, Any]],
    positive_signals: List[str],
    input_type: str
) -> List[str]:
    """Provides targeted, practical safety advice ('What should you do?')."""
    recs: List[str] = []
    titles_lower = [s.get("title", "").lower() for s in signals]

    has_payment = any("fee" in t or "payment" in t or "deposit" in t for t in titles_lower)
    has_credentials = any("aadhaar" in t or "pan" in t or "passport" in t or "credential" in t for t in titles_lower)
    has_banking = any("bank" in t or "ifsc" in t or "cheque" in t or "upi" in t for t in titles_lower)
    has_otp = any("otp" in t or "password" in t or "pin" in t for t in titles_lower)
    has_chat = any("whatsapp" in t or "telegram" in t for t in titles_lower)
    has_urgency = any("urgency" in t or "immediate" in t for t in titles_lower)

    if has_payment:
        recs.append("Do not pay upfront recruitment, training, registration, or equipment fees under any circumstance.")

    if has_credentials:
        recs.append("Avoid sharing Aadhaar, PAN card, or passport copies until the employer's legitimacy is verified.")

    if has_banking:
        recs.append("Do not disclose bank account numbers, cancelled cheques, or UPI payment details during preliminary screening.")

    if has_otp:
        recs.append("Never share OTPs, portal passwords, or verification codes received on your phone or email.")

    if has_urgency:
        recs.append("Be cautious of urgent payment deadlines or pressure to accept offers without standard interviews.")

    if has_chat:
        recs.append("Insist on communicating through the organization's official corporate email domain rather than private messaging apps.")

    # Universal best practices
    recs.append("Verify the job posting independently by visiting the company's official careers portal.")
    recs.append("Contact the organization's human resources department using publicly listed telephone or email contacts.")

    # Deduplicate while preserving order
    return list(dict.fromkeys(recs))[:6]


def run_central_risk_pipeline(
    input_type: str,
    text: str,
    url: Optional[str] = None,
    title: Optional[str] = None,
    company: Optional[str] = None,
    recruiter_email: Optional[str] = None,
    salary: Optional[str] = None,
    external_urls: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    auto_persist: bool = True
) -> Dict[str, Any]:
    """
    The Single Central Risk Engine Ingestion Pipeline.
    
    All scanner inputs (Job URL, PDF, Google Form, Pasted Text) must call this function.
    """
    clean_text = (text or "").strip()
    primary_url = (url or "").strip()
    input_type = (input_type or "URL").upper()

    # Discover target domain: either direct URL or first external URL extracted
    effective_url = primary_url
    if not effective_url and external_urls:
        effective_url = external_urls[0]

    technical_available = bool(effective_url)

    logger.info(
        f"Pipeline executing for input_type='{input_type}' "
        f"(URL: '{effective_url or 'None'}', Text Length: {len(clean_text)})"
    )

    # 1. Run Master Risk Engine
    engine_res = default_risk_engine.analyze_job(
        url=effective_url if technical_available else None,
        job_text=clean_text,
        company_name=company,
        recruiter_email=recruiter_email,
        salary=salary,
        source=input_type.lower()
    )

    final_score = engine_res.get("risk_score", 0)
    risk_level = engine_res.get("risk_level", "LOW")
    signals = engine_res.get("signals", [])
    positive_signals = engine_res.get("positive_signals", [])
    override_info = engine_res.get("override")
    confidence = engine_res.get("confidence", 0.8)

    # 2. Extract Layer A Technical Checks if URL was available
    if technical_available:
        try:
            tech_analysis = analyze_technical(effective_url, redirect_count=0)
            technical_checks = tech_analysis.get("checks", {})
            url_intel = tech_analysis.get("url_intelligence", {})
            technical_score = tech_analysis.get("technical_score", 0)
        except Exception as tech_err:
            logger.warning(f"Technical analysis error for {effective_url}: {tech_err}")
            technical_checks = {"analysis_available": False, "error": str(tech_err)}
            url_intel = {"domain": extract_domain_from_url(effective_url), "analysis_available": False}
            technical_score = 0
    else:
        technical_checks = {
            "ssl_valid": None,
            "domain_age_days": None,
            "dns_exists": None,
            "ip": None,
            "redirect_count": 0,
            "is_https": None,
            "suspicious_patterns": {"flagged": False},
            "analysis_available": False,
            "status": "UNAVAILABLE",
            "message": "Technical infrastructure checks unavailable (no domain URL present in document)."
        }
        url_intel = {
            "domain": "Not Provided",
            "is_https": None,
            "dns_exists": None,
            "ssl_valid": None,
            "domain_age_days": None,
            "ip": None,
            "analysis_available": False,
        }
        technical_score = 0

    # 3. Categorize Risk
    categories = categorize_signals(signals, technical_available)

    # 4. Generate Evidence-Based Summary & Recommendations
    summary = build_evidence_based_summary(
        risk_score=final_score,
        risk_level=risk_level,
        signals=signals,
        positive_signals=positive_signals,
        input_type=input_type,
        override_info=override_info
    )

    recommendations = build_actionable_recommendations(
        risk_level=risk_level,
        signals=signals,
        positive_signals=positive_signals,
        input_type=input_type
    )

    # 5. Formulate Verdict & Probability
    if final_score >= 75:
        verdict = "CONFIRMED_SCAM"
    elif final_score >= 50:
        verdict = "HIGH_RISK_FAKE"
    elif final_score >= 25:
        verdict = "SUSPICIOUS"
    else:
        verdict = "VERIFIED_LEGITIMATE"

    legitimacy_score = max(0, 100 - final_score)
    fake_job_prob = final_score

    # 6. Build Consistent Layer Breakdown
    nlp_sub = engine_res.get("analysis", {}).get("nlp", {}).get("score", 0)
    scores = {
        "behavioral": min(100, categories["behavioral_risk"]["score"]),
        "linguistic": min(100, nlp_sub),
        "structural": min(100, engine_res.get("analysis", {}).get("recruiter", {}).get("score", 0)),
        "technical": technical_score if technical_available else None,
    }

    job_title = title or company or (
        "Uploaded Recruitment Document" if input_type == "PDF" else (
            "Recruitment Application Form" if input_type == "GOOGLE_FORM" else "Evaluated Job Posting"
        )
    )

    job_info = {
        "title": job_title,
        "company": company or None,
        "text_preview": clean_text[:1000],
    }

    # Red flags with format expected by both UI and Extension
    red_flags: List[Dict[str, Any]] = []
    for s in signals:
        red_flags.append({
            "type": s.get("category", "nlp"),
            "category": s.get("category", "nlp"),
            "severity": s.get("severity", "medium"),
            "title": s.get("title", "Detected Threat"),
            "message": s.get("title", "Detected Threat"),
            "description": s.get("description", ""),
            "evidence": s.get("evidence", ""),
            "score": s.get("score", 0),
        })

    green_flags: List[Dict[str, Any]] = []
    for p in positive_signals:
        green_flags.append({
            "type": "verification",
            "message": p,
            "trust_bonus": 10,
        })

    layers = {
        "infrastructure": {
            "status": "AVAILABLE" if technical_available else "UNAVAILABLE",
            "description": "Layer A URL & Technical Infrastructure Analysis",
            "technical_score": technical_score if technical_available else None,
        },
        "content": {
            "status": "AVAILABLE",
            "description": f"Layer B {input_type} Content & NLP Heuristics",
            "source": input_type.lower(),
            "word_count": len(clean_text.split()),
        },
    }

    pipeline_stages = [
        "INPUT_RECEIVED",
        "CONTENT_EXTRACTED",
        "NORMALIZING_TEXT",
        "LINGUISTIC_ANALYSIS",
        "BEHAVIORAL_ANALYSIS",
        "SENSITIVE_INFO_DETECTION",
        "TECHNICAL_DOMAIN_CHECKS" if technical_available else "TECHNICAL_CHECKS_SKIPPED",
        "CENTRAL_RISK_ENGINE",
        "EXPLAINABLE_SYNTHESIS",
        "ANALYSIS_COMPLETE",
    ]

    response_payload = {
        # Core Consistent Fields
        "success": True,
        "status": "FETCH_SUCCESS",
        "score": final_score,
        "risk_score": final_score,
        "risk_level": risk_level,
        "verdict": verdict,
        "legitimacy_score": legitimacy_score,
        "fake_job_probability": fake_job_prob,
        "input_type": input_type,
        "inputType": input_type,
        "confidence": confidence,
        "summary": summary,
        "explanation": summary,
        "signals": signals,
        "red_flags": red_flags,
        "positive_signals": positive_signals,
        "green_flags": green_flags,
        "categories": categories,
        "recommendations": recommendations,
        "verification_audit": engine_res.get("verification_audit", {}),
        "job": job_info,
        "scores": scores,
        "layers": layers,
        "technical_checks": technical_checks,
        "url_intelligence": url_intel,
        "content_intelligence": {
            "status": "ANALYZED",
            "source": input_type.lower(),
            "word_count": len(clean_text.split()),
            "reason": None,
        },
        "content_analyzed": True,
        "fetch_status": "FETCH_SUCCESS",
        "http_status": 200,
        "message": f"{input_type} threat analysis completed successfully.",
        "url": primary_url or (external_urls[0] if external_urls else None),
        "final_url": primary_url or (external_urls[0] if external_urls else None),
        "pipeline_stages": pipeline_stages,
        "override": override_info,
        "analysis": engine_res.get("analysis", {}),
        "user_id": user_id,
    }

    # Auto-persist to SQLite
    if auto_persist:
        try:
            with SessionLocal() as db:
                saved = auto_save_scan(db, response_payload, user_id=user_id)
                if saved and "id" in saved:
                    response_payload["id"] = saved["id"]
                    response_payload["candidate_id"] = saved["id"]
        except Exception as db_exc:
            logger.warning(f"Error auto-persisting {input_type} scan: {db_exc}")

    return response_payload
