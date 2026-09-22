"""
Master Hybrid Job Scam Risk Engine for HireShield.

Coordinates NLP, Domain Intelligence, Lookalike Detection, Company Verification,
Recruiter Intelligence, and Salary Anomaly Analysis into an explainable risk score.
"""

from typing import Dict, Any, Optional, List

from app.risk_engine.nlp.analyzer import (
    analyze_job_text,
    detect_payment_request,
    detect_credential_harvesting,
)
from app.risk_engine.domain.analyzer import analyze_domain, extract_domain_from_url
from app.risk_engine.impersonation.detector import detect_lookalike_domain
from app.risk_engine.company.verifier import verify_company_entity
from app.risk_engine.recruiter.analyzer import analyze_recruiter
from app.risk_engine.salary.analyzer import analyze_salary_anomaly
from app.risk_engine.scoring import calculate_risk_score
from app.risk_engine.confidence import calculate_confidence
from app.risk_engine.explanations import (
    generate_explanation_summary,
    generate_recommendations,
    generate_verification_audit,
)


class RiskEngine:
    """Enterprise risk scoring orchestrator for recruitment postings and URLs."""

    def analyze_job(
        self,
        url: Optional[str] = None,
        job_text: Optional[str] = None,
        company_name: Optional[str] = None,
        recruiter_email: Optional[str] = None,
        salary: Optional[str] = None,
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes end-to-end multi-vector risk evaluation.
        """
        job_text = (job_text or "").strip()
        url = (url or "").strip()
        domain = extract_domain_from_url(url) if url else ""

        # 1. NLP & Language Features
        nlp_res = analyze_job_text(job_text)
        nlp_score = nlp_res["nlp_score"]
        nlp_features = nlp_res["features"]

        # 2. Domain Intelligence
        domain_res = analyze_domain(url) if url else {
            "domain": "",
            "domain_score": 0,
            "signals": [],
            "positive_signals": [],
            "details": {},
            "confidence": 0.1
        }
        domain_score = domain_res["domain_score"]
        domain_signals = domain_res["signals"]

        # 3. Lookalike / Impersonation Detection
        impersonation_res = detect_lookalike_domain(domain) if domain else {
            "is_lookalike": False,
            "matched_brand": None,
            "similarity": 0.0,
            "risk_score": 0,
            "evidence": "",
            "reason": ""
        }
        impersonation_score = impersonation_res["risk_score"]

        # 4. Company Verification
        company_res = verify_company_entity(company_name, domain, recruiter_email)
        company_score = company_res["company_score"]

        # 5. Recruiter & Contact Signals
        recruiter_res = analyze_recruiter(recruiter_email, company_name, domain, job_text)
        recruiter_score = recruiter_res["recruiter_score"]

        # 6. Payment & Credential Harvesting Sub-score
        payment_info = detect_payment_request(job_text)
        credential_info = detect_credential_harvesting(job_text)
        payment_credential_score = min(
            100,
            payment_info.get("payment_risk_score", 0) + credential_info.get("credential_risk_score", 0)
        )

        # 7. Salary Anomaly
        salary_res = analyze_salary_anomaly(salary, job_text)
        salary_score = salary_res["salary_anomaly_score"]

        # 8. Normalized Scoring & Critical Overrides
        final_score, risk_level, override_info = calculate_risk_score(
            nlp_score=nlp_score,
            domain_score=domain_score,
            company_score=company_score,
            recruiter_score=recruiter_score,
            payment_credential_score=payment_credential_score,
            salary_score=salary_score,
            impersonation_score=impersonation_score,
            nlp_features=nlp_features,
            domain_signals=domain_signals,
            impersonation_data=impersonation_res
        )

        # 9. Aggregate Signals & Positive Signals
        aggregated_signals: List[Dict[str, Any]] = []

        # Add NLP signals
        for f in nlp_features:
            cat = "payment" if "fee" in f.get("feature", "") or "deposit" in f.get("feature", "") else (
                "credential" if "aadhaar" in f.get("feature", "") or "otp" in f.get("feature", "") or "password" in f.get("feature", "") else "nlp"
            )
            aggregated_signals.append({
                "category": cat,
                "severity": f.get("severity", "medium"),
                "title": f.get("feature", "").replace("_", " ").title(),
                "description": f"Identified suspicious recruitment language: '{f.get('evidence', '')}'",
                "evidence": f.get("evidence", ""),
                "score": f.get("score", 0)
            })

        # Add Domain signals
        for s in domain_signals:
            aggregated_signals.append(s)

        # Add Impersonation signal if detected
        if impersonation_res.get("is_lookalike"):
            aggregated_signals.append({
                "category": "impersonation",
                "severity": "high" if impersonation_res.get("similarity", 0) < 0.9 else "critical",
                "title": f"Lookalike domain impersonating {impersonation_res.get('matched_brand')}",
                "description": impersonation_res.get("reason", "Suspicious typographical similarity"),
                "evidence": impersonation_res.get("evidence", ""),
                "score": impersonation_res.get("risk_score", 0)
            })

        # Add Company signals
        for s in company_res.get("signals", []):
            aggregated_signals.append(s)

        # Add Recruiter signals
        for s in recruiter_res.get("signals", []):
            aggregated_signals.append(s)

        # Add Salary signal if anomalous
        if salary_score > 0:
            aggregated_signals.append({
                "category": "salary",
                "severity": "high" if salary_score >= 40 else "medium",
                "title": "Salary compensation anomaly",
                "description": salary_res.get("reason", "Compensation significantly exceeds role benchmarks."),
                "score": salary_score
            })

        # Collect Positive Trust Signals
        all_positive_signals: List[str] = []
        all_positive_signals.extend(nlp_res.get("positive_signals", []))
        all_positive_signals.extend(domain_res.get("positive_signals", []))
        all_positive_signals.extend(company_res.get("positive_signals", []))
        all_positive_signals.extend(recruiter_res.get("positive_signals", []))
        all_positive_signals = list(dict.fromkeys(all_positive_signals))

        # 10. Confidence Calculation
        has_critical = (
            override_info is not None or
            any(s.get("severity") == "critical" for s in aggregated_signals)
        )
        confidence = calculate_confidence(
            job_text=job_text,
            domain_details=domain_res.get("details", {}),
            recruiter_email=recruiter_email,
            company_name=company_name,
            has_critical_indicators=has_critical
        )

        # 11. Explanations & Actionable Advice
        summary = generate_explanation_summary(
            risk_score=final_score,
            risk_level=risk_level,
            signals=aggregated_signals,
            positive_signals=all_positive_signals,
            override_info=override_info
        )
        recommendations = generate_recommendations(
            risk_level=risk_level,
            signals=aggregated_signals,
            positive_signals=all_positive_signals
        )

        analysis_data = {
            "nlp": {
                "score": nlp_score,
                "features": nlp_features,
                "evidence": nlp_res.get("evidence", [])
            },
            "domain": {
                "score": domain_score,
                "domain": domain,
                "details": domain_res.get("details", {})
            },
            "company": {
                "score": company_score,
                "is_verified": company_res.get("is_verified", False)
            },
            "recruiter": {
                "score": recruiter_score
            },
            "salary": {
                "score": salary_score,
                "details": salary_res.get("details", {})
            },
            "impersonation": {
                "score": impersonation_score,
                "is_lookalike": impersonation_res.get("is_lookalike", False),
                "matched_brand": impersonation_res.get("matched_brand")
            },
            "payment_credential": {
                "score": payment_credential_score
            }
        }

        verification_audit = generate_verification_audit(
            risk_score=final_score,
            risk_level=risk_level,
            signals=aggregated_signals,
            positive_signals=all_positive_signals,
            analysis=analysis_data,
            override_info=override_info
        )

        return {
            "success": True,
            "risk_score": final_score,
            "risk_level": risk_level,
            "confidence": confidence,
            "summary": summary,
            "signals": aggregated_signals,
            "positive_signals": all_positive_signals,
            "recommendations": recommendations,
            "verification_audit": verification_audit,
            "override": override_info,
            "analysis": analysis_data
        }


# Singleton engine instance for simple import
default_risk_engine = RiskEngine()


def analyze_job_risk(
    url: Optional[str] = None,
    job_text: Optional[str] = None,
    company_name: Optional[str] = None,
    recruiter_email: Optional[str] = None,
    salary: Optional[str] = None,
    source: Optional[str] = None
) -> Dict[str, Any]:
    """Helper functional interface for job risk analysis."""
    return default_risk_engine.analyze_job(
        url=url,
        job_text=job_text,
        company_name=company_name,
        recruiter_email=recruiter_email,
        salary=salary,
        source=source
    )
