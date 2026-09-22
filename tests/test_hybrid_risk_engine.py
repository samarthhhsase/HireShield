"""
Automated Test Suite for HireShield Hybrid Job Scam Risk Engine.

Implements all 15 test scenarios required by Section 20 of specification:
1. Legitimate established company job
2. Fake job requesting registration fee
3. Fake job requesting Aadhaar/PAN
4. Unrealistic salary
5. New domain + valid SSL
6. Lookalike company domain
7. WhatsApp-only recruitment
8. Telegram recruitment
9. Urgency-heavy posting
10. Normal legitimate urgent hiring
11. Legitimate Gmail recruiter
12. Credential harvesting page
13. Legitimate startup with young domain
14. Multiple weak signals
15. Multiple strong signals
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.risk_engine import RiskEngine, analyze_job_risk

client = TestClient(app)
engine = RiskEngine()


def _print_test_summary(case_num: int, name: str, res: dict):
    """Helper to log individual feature scores, final score, risk level, confidence, explanation."""
    analysis = res.get("analysis", {})
    summary = str(res.get("summary", "")).encode("ascii", errors="replace").decode("ascii")
    print(f"\n==========================================")
    print(f"TEST CASE {case_num}: {name}")
    print(f"==========================================")
    print(f"Risk Score:   {res.get('risk_score')}/100")
    print(f"Risk Level:   {res.get('risk_level')}")
    print(f"Confidence:   {res.get('confidence')}")
    print(f"Summary:      {summary}")
    print(f"Scores breakdown:")
    for k, v in analysis.items():
        score = v.get("score") if isinstance(v, dict) else v
    red_flags_str = str(len(res.get('signals', [])))
    trust_signals_str = str(res.get('positive_signals', [])).encode("ascii", errors="replace").decode("ascii")
    override_str = str(res.get('override')).encode("ascii", errors="replace").decode("ascii")
    print(f"Red flags count:    {red_flags_str}")
    print(f"Trust signals:      {trust_signals_str}")
    print(f"Override:           {override_str}")


# --------------------------------------------------------------------------
# 1. Legitimate established company job
# --------------------------------------------------------------------------
def test_case_1_legitimate_established_company_job():
    res = engine.analyze_job(
        url="https://google.com/careers/software-engineer",
        company_name="Google",
        recruiter_email="recruiter@google.com",
        job_text="""
        Google is hiring a Senior Software Engineer in Mountain View.
        Requirements: Minimum 5 years of experience in distributed systems, Bachelor's degree in Computer Science.
        Structured technical round and system design interview required.
        Comprehensive benefits: health insurance, 401(k) matching, paid time off.
        Equal opportunity employer. Anti-fraud notice: We never charge any fee at any recruitment stage.
        """,
        salary="$160,000 - $210,000 / year",
        source="linkedin"
    )
    _print_test_summary(1, "Legitimate established company job", res)

    assert res["risk_score"] < 25, f"Expected LOW risk, got {res['risk_score']}"
    assert res["risk_level"] == "LOW"
    assert res["confidence"] >= 0.70
    assert len(res["positive_signals"]) > 0


# --------------------------------------------------------------------------
# 2. Fake job requesting registration fee
# --------------------------------------------------------------------------
def test_case_2_fake_job_requesting_registration_fee():
    res = engine.analyze_job(
        url="https://quickhire-portal.site/job/123",
        company_name="Global Fast Placements",
        job_text="""
        Congratulations! You have been selected for direct joining as a Back Office Assistant.
        A refundable registration fee of ₹1,500 is required before interview and appointment letter issuance.
        Pay now to book your seat.
        """,
        recruiter_email="hr@quickhire-portal.site",
        source="direct"
    )
    _print_test_summary(2, "Fake job requesting registration fee", res)

    assert res["risk_score"] >= 75, f"Expected CRITICAL risk, got {res['risk_score']}"
    assert res["risk_level"] == "CRITICAL"
    assert res["override"] is not None
    assert any("fee" in s["title"].lower() for s in res["signals"])


# --------------------------------------------------------------------------
# 3. Fake job requesting Aadhaar/PAN
# --------------------------------------------------------------------------
def test_case_3_fake_job_requesting_aadhaar_pan():
    res = engine.analyze_job(
        url="https://onlinejobs2024.xyz/apply",
        company_name="Quick Workforce",
        job_text="""
        Urgent recruitment for data typing work.
        Applicants must share your Aadhaar card and PAN card copy to apply before interview.
        Send scanned documents immediately to register.
        """,
        recruiter_email="hiring@onlinejobs2024.xyz"
    )
    _print_test_summary(3, "Fake job requesting Aadhaar/PAN", res)

    assert res["risk_score"] >= 50, f"Expected elevated risk, got {res['risk_score']}"
    assert res["risk_level"] in ("HIGH", "CRITICAL")
    assert any(s["category"] == "credential" or "id" in s["title"].lower() or "aadhaar" in s["title"].lower() for s in res["signals"])


# --------------------------------------------------------------------------
# 4. Unrealistic salary
# --------------------------------------------------------------------------
def test_case_4_unrealistic_salary():
    res = engine.analyze_job(
        url="https://entrylevel-typing.com",
        company_name="Global Data Services",
        job_text="""
        Simple copy paste work and data entry. Work from home with just a smartphone.
        No prior experience needed, freshers and students welcome.
        Guaranteed daily salary of ₹6,000 per day.
        """,
        salary="₹6,000 per day",
        recruiter_email="info@entrylevel-typing.com"
    )
    _print_test_summary(4, "Unrealistic salary", res)

    salary_score = res["analysis"]["salary"]["score"]
    assert salary_score >= 35, f"Expected high salary anomaly score, got {salary_score}"
    assert any("salary" in s["category"] or "salary" in s["title"].lower() for s in res["signals"])


# --------------------------------------------------------------------------
# 5. New domain + valid SSL
# --------------------------------------------------------------------------
def test_case_5_new_domain_with_valid_ssl(monkeypatch):
    # Mock WHOIS age to 14 days and SSL to valid
    from app.risk_engine.domain import analyzer as domain_analyzer
    
    def mock_query_whois(domain):
        return {
            "domain": domain,
            "creation_date": "2026-09-07T00:00:00Z",
            "age_days": 14,
            "is_recent": True,
            "whois_available": True,
            "registrar": "Namecheap Inc.",
            "error": None
        }

    def mock_check_ssl(domain, port=443, timeout=3.5):
        return {
            "domain": domain,
            "ssl_valid": True,
            "issuer": "Let's Encrypt",
            "expiry_date": "2026-12-07T00:00:00Z",
            "days_to_expiry": 77,
            "error": None,
            "is_free_automated_ca": True
        }

    monkeypatch.setattr("app.risk_engine.domain.analyzer.query_whois_info", mock_query_whois)
    monkeypatch.setattr("app.risk_engine.domain.analyzer.check_ssl_certificate", mock_check_ssl)

    res = engine.analyze_job(
        url="https://brandnew-consulting2026.com/job/1",
        company_name="Brand New Consulting",
        job_text="Hiring customer support executive. Basic computer skills needed."
    )
    _print_test_summary(5, "New domain + valid SSL", res)

    # Valid SSL certificate must NOT clear the domain; domain score must remain substantial
    assert res["analysis"]["domain"]["score"] >= 30
    assert any("30 days" in s.get("title", "").lower() or "recent" in s.get("title", "").lower() for s in res["signals"])
    assert any("https" in ps.lower() for ps in res["positive_signals"])


# --------------------------------------------------------------------------
# 6. Lookalike company domain
# --------------------------------------------------------------------------
def test_case_6_lookalike_company_domain():
    res = engine.analyze_job(
        url="https://micros0ft-careers.com/job/dev-lead",
        company_name="Microsoft",
        job_text="Leading cloud team. Apply now."
    )
    _print_test_summary(6, "Lookalike company domain", res)

    impersonation = res["analysis"]["impersonation"]
    assert impersonation["is_lookalike"] is True
    assert impersonation["matched_brand"] == "Microsoft"
    assert res["risk_score"] >= 75
    assert res["risk_level"] == "CRITICAL"


# --------------------------------------------------------------------------
# 7. WhatsApp-only recruitment
# --------------------------------------------------------------------------
def test_case_7_whatsapp_only_recruitment():
    res = engine.analyze_job(
        url="https://freelancegigs.in/job/987",
        company_name="Apex Marketing",
        job_text="""
        Immediate hiring for marketing coordinators.
        Do not apply on portal. Contact only via WhatsApp: +91 9988776655 to apply.
        Send your resume on WhatsApp to schedule interview.
        """
    )
    _print_test_summary(7, "WhatsApp-only recruitment", res)

    assert res["risk_score"] >= 25
    assert any("whatsapp" in s.get("title", "").lower() for s in res["signals"])


# --------------------------------------------------------------------------
# 8. Telegram recruitment
# --------------------------------------------------------------------------
def test_case_8_telegram_recruitment():
    res = engine.analyze_job(
        url="https://remotetasks.cc/job/1",
        company_name="CryptoGlobal Remote",
        job_text="""
        Work from anywhere worldwide.
        Contact recruiter on Telegram: @GlobalTaskHiring to start onboarding.
        """
    )
    _print_test_summary(8, "Telegram recruitment", res)

    assert any("telegram" in s.get("title", "").lower() for s in res["signals"])


# --------------------------------------------------------------------------
# 9. Urgency-heavy posting
# --------------------------------------------------------------------------
def test_case_9_urgency_heavy_posting():
    res = engine.analyze_job(
        url="https://dailyvacancies.in/apply",
        company_name="Immediate Placements",
        job_text="""
        Act now! Today only! Only 3 seats remaining!
        Hurry up, don't miss this golden opportunity.
        Selected candidates must pay immediate processing charges.
        Apply immediately or lose your spot!
        """
    )
    _print_test_summary(9, "Urgency-heavy posting", res)

    assert res["analysis"]["nlp"]["score"] >= 40
    assert any("urgency" in s.get("title", "").lower() or "scarcity" in s.get("title", "").lower() or "pressure" in s.get("title", "").lower() for s in res["signals"])


# --------------------------------------------------------------------------
# 10. Normal legitimate urgent hiring
# --------------------------------------------------------------------------
def test_case_10_normal_legitimate_urgent_hiring():
    res = engine.analyze_job(
        url="https://greenhouse.io/stripe/jobs/engineer",
        company_name="Stripe",
        recruiter_email="jobs@stripe.com",
        job_text="""
        We are urgently hiring a Principal Systems Engineer.
        Minimum 8+ years of experience with distributed payment infrastructure.
        Immediate joiner preferred to support Q4 roadmap.
        Panel interview rounds and coding assessment required.
        Equal opportunity employer. Comprehensive health insurance and equity package.
        """
    )
    _print_test_summary(10, "Normal legitimate urgent hiring", res)

    # Should NOT be heavily penalized for standard "urgently hiring" when on verified ATS with real requirements
    assert res["risk_score"] < 25
    assert res["risk_level"] == "LOW"


# --------------------------------------------------------------------------
# 11. Legitimate Gmail recruiter
# --------------------------------------------------------------------------
def test_case_11_legitimate_gmail_recruiter():
    res = engine.analyze_job(
        url="https://littlebistro.cafe/jobs",
        company_name="The Little Bistro",
        recruiter_email="thelittlebistro.jobs@gmail.com",
        job_text="""
        Looking for a friendly morning barista for our neighborhood cafe.
        Experience making espresso drinks preferred.
        Send your resume to thelittlebistro.jobs@gmail.com or visit in person.
        """
    )
    _print_test_summary(11, "Legitimate Gmail recruiter", res)

    # Gmail alone for small business should NOT cause CRITICAL or HIGH score
    assert res["risk_score"] < 50
    assert res["risk_level"] in ("LOW", "MODERATE")


# --------------------------------------------------------------------------
# 12. Credential harvesting page
# --------------------------------------------------------------------------
def test_case_12_credential_harvesting_page():
    res = engine.analyze_job(
        url="https://portal-verification-system.work/verify",
        company_name="National Banking Career Portal",
        job_text="""
        Candidate identity verification.
        Please provide your bank account number, net banking password, and security PIN
        along with the OTP received on your mobile phone to activate your pre-selected job offer.
        """
    )
    _print_test_summary(12, "Credential harvesting page", res)

    assert res["risk_score"] >= 75
    assert res["risk_level"] == "CRITICAL"
    assert res["override"] is not None
    assert any("otp" in s["title"].lower() or "credential" in s["title"].lower() for s in res["signals"])


# --------------------------------------------------------------------------
# 13. Legitimate startup with young domain
# --------------------------------------------------------------------------
def test_case_13_legitimate_startup_with_young_domain(monkeypatch):
    def mock_query_whois(domain):
        return {
            "domain": domain,
            "creation_date": "2026-07-01T00:00:00Z",
            "age_days": 80,
            "is_recent": True,
            "whois_available": True,
            "registrar": "Squarespace",
            "error": None
        }

    monkeypatch.setattr("app.risk_engine.domain.analyzer.query_whois_info", mock_query_whois)

    res = engine.analyze_job(
        url="https://neuroscale.ai/careers/founding-ai-engineer",
        company_name="NeuroScale AI",
        recruiter_email="founders@neuroscale.ai",
        job_text="""
        NeuroScale AI is an early-stage AI lab. We are seeking our Founding AI Engineer.
        Must have deep knowledge of PyTorch and Transformer architectures.
        Competitive salary ($140,000 - $180,000) and significant equity.
        Comprehensive benefits and remote flexibility.
        """
    )
    _print_test_summary(13, "Legitimate startup with young domain", res)

    # A young startup without scam language should not be marked as a scam
    assert res["risk_score"] < 50
    assert res["risk_level"] in ("LOW", "MODERATE")


# --------------------------------------------------------------------------
# 14. Multiple weak signals
# --------------------------------------------------------------------------
def test_case_14_multiple_weak_signals():
    res = engine.analyze_job(
        url="https://creative-agency-hiring.com/post/12",
        company_name="Apex Media",
        recruiter_email="recruiter.apexmedia@gmail.com",  # Weak: free webmail
        job_text="""
        Looking for a virtual assistant.
        Immediate joiners preferred.
        No prior experience required, on-the-job training provided.
        """
    )
    _print_test_summary(14, "Multiple weak signals", res)

    # Multiple weak signals should elevate to MODERATE, but not CRITICAL
    assert 20 <= res["risk_score"] <= 49
    assert res["risk_level"] == "MODERATE"


# --------------------------------------------------------------------------
# 15. Multiple strong signals
# --------------------------------------------------------------------------
def test_case_15_multiple_strong_signals():
    res = engine.analyze_job(
        url="https://tcs-careers-interview.xyz/apply",
        company_name="Tata Consultancy Services",
        recruiter_email="tcs-recruitment@tempmail.com",  # Disposable email!
        job_text="""
        TCS Direct Selection Walk-in. Guaranteed job placement with 100% money back guarantee.
        Deposit a security deposit of ₹3,000 before receiving appointment letter.
        Send your Aadhaar card and PAN card copy on WhatsApp to register immediately.
        """
    )
    _print_test_summary(15, "Multiple strong signals", res)

    assert res["risk_score"] >= 85
    assert res["risk_level"] == "CRITICAL"
    assert res["confidence"] >= 0.85
    assert len(res["signals"]) >= 3


# --------------------------------------------------------------------------
# 16. API Endpoint Integration Test (POST /api/risk/analyze)
# --------------------------------------------------------------------------
def test_api_risk_analyze_endpoint():
    payload = {
        "url": "https://fake-amazon-jobs.top/checkout",
        "company_name": "Amazon",
        "job_text": "Amazon Direct Hiring: pay registration fee of $50 and send Aadhaar copy.",
        "recruiter_email": "hr@fake-amazon-jobs.top",
        "source": "linkedin"
    }
    response = client.post("/api/risk/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["risk_score"] >= 75
    assert data["risk_level"] == "CRITICAL"
    assert "analysis" in data
    assert "verification_audit" in data
    audit = data["verification_audit"]
    assert audit["verdict"] == "FLAGGED_FAKE"
    assert "Why This Job Was Flagged" in audit["headline"]
    assert len(audit["checks_performed"]) >= 6


# --------------------------------------------------------------------------
# 17. Verification Audit: Why Real / What Checked / How Verified
# --------------------------------------------------------------------------
def test_case_17_verification_audit_real_job():
    res = engine.analyze_job(
        url="https://boards.greenhouse.io/stripe/jobs/4321000",
        company_name="Stripe",
        recruiter_email="talent-acquisition@stripe.com",
        job_text="""
        Stripe is looking for a Senior Backend Software Engineer to join our Payments Infrastructure team.
        Requirements: 5+ years experience with distributed systems, Ruby or Go.
        Competitive base salary $180,000 - $220,000 + equity + 401(k) matching.
        Stripe is an Equal Opportunity Employer. We do not charge application or processing fees.
        """
    )
    assert res["risk_level"] == "LOW"
    assert "verification_audit" in res
    audit = res["verification_audit"]
    assert audit["verdict"] == "VERIFIED_REAL"
    assert "Why This Job Appears REAL" in audit["headline"]
    assert "verdict_explanation" in audit
    assert len(audit["checks_performed"]) == 6
    
    # Check that each pillar has what_we_checked, how_verified, and finding
    for check in audit["checks_performed"]:
        assert "pillar" in check
        assert "status" in check
        assert check["status"] in ("PASSED", "CAUTION", "FAILED")
        assert "what_we_checked" in check and len(check["what_we_checked"]) > 10
        assert "how_verified" in check and len(check["how_verified"]) > 10
        assert "finding" in check and len(check["finding"]) > 5

    # In a legitimate job, upfront payment and identity theft checks must be PASSED
    pay_check = next(c for c in audit["checks_performed"] if "Payment" in c["pillar"])
    assert pay_check["status"] == "PASSED"
    assert "Zero upfront fees" in pay_check["finding"]


# --------------------------------------------------------------------------
# 18. Verification Audit: Why Fake / What Checked / How Verified
# --------------------------------------------------------------------------
def test_case_18_verification_audit_fake_job():
    res = engine.analyze_job(
        url="https://google-careers-portal.xyz/apply",
        company_name="Google",
        recruiter_email="google-recruiter@tempmail.com",
        job_text="""
        Google Remote Assistant. Immediate selection without interview.
        You must deposit ₹4,500 for training kit and laptop courier fee via UPI.
        Send Aadhaar and bank account details on WhatsApp to confirm registration.
        """
    )
    assert res["risk_level"] == "CRITICAL"
    assert "verification_audit" in res
    audit = res["verification_audit"]
    assert audit["verdict"] == "FLAGGED_FAKE"
    assert "Why This Job Was Flagged as FAKE" in audit["headline"]
    assert "checks_performed" in audit

    # Verify payment check failed
    pay_check = next(c for c in audit["checks_performed"] if "Payment" in c["pillar"])
    assert pay_check["status"] == "FAILED"
    assert "CRITICAL ALERT: Upfront payment" in pay_check["finding"]

