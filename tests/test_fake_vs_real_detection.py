import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ai_client import analyze_with_ai
from app.services.risk_engine import calculate_risk
from app.services.technical import analyze_technical

client = TestClient(app)


def test_detect_advance_fee_scam():
    """Verify that upfront registration/uniform/laptop fee scam is classified as CRITICAL."""
    payload = {
        "url": "https://fastjobs-careers.online/apply",
        "title": "Data Entry Specialist",
        "company": "Fast Data Operations",
        "content": (
            "We are hiring Data Entry Specialists. Immediate onboarding available. "
            "A mandatory registration fee and refundable laptop security deposit of ₹2,500 "
            "is required before you start training. Please pay via UPI to receive your credentials."
        ),
    }
    response = client.post("/api/scanner/analyze-content", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] >= 75
    assert data["risk_level"] == "CRITICAL"
    assert data["verdict"] == "CONFIRMED_SCAM"
    assert data["fake_job_probability"] >= 85
    assert data["scores"]["behavioral"] >= 45

    messages = " ".join(f["message"].lower() for f in data["red_flags"])
    assert "fee" in messages or "payment" in messages
    assert any("never transfer money" in rec.lower() for rec in data["recommendations"])


def test_detect_check_overpayment_scam():
    """Verify that fake check cashing / equipment vendor purchase scams are flagged as CRITICAL."""
    payload = {
        "url": "https://remote-work-portal.site/jobs/executive-assistant",
        "title": "Remote Executive Assistant",
        "company": "Apex Global Solutions",
        "content": (
            "We are seeking a Remote Executive Assistant. You will work from home 15 hours a week. "
            "Upon acceptance, we will send you a cashier's check to purchase home office equipment "
            "and materials from our certified vendor. Once you deposit the check, wire the remaining funds."
        ),
    }
    response = client.post("/api/scanner/analyze-content", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] >= 75
    assert data["risk_level"] == "CRITICAL"
    assert data["verdict"] == "CONFIRMED_SCAM"
    assert data["fake_job_probability"] >= 80

    messages = " ".join(f["message"].lower() for f in data["red_flags"])
    assert "check cashing" in messages or "vendor" in messages


def test_detect_identity_theft_scam():
    """Verify pre-interview Aadhaar/PAN/banking credentials demands trigger critical override."""
    payload = {
        "url": "https://careers-verify-now.xyz/form",
        "title": "Customer Service Representative",
        "company": "Quick Connect BPO",
        "content": (
            "Submit your job application now! To confirm your appointment, you must send your "
            "Aadhaar card number, PAN card copy, and bank account details with IFSC code "
            "along with net banking password or OTP for background authentication before the interview."
        ),
    }
    response = client.post("/api/scanner/analyze-content", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] >= 70
    assert data["scores"]["behavioral"] >= 45

    messages = " ".join(f["message"].lower() for f in data["red_flags"])
    assert "sensitive identity" in messages


def test_detect_free_email_corporate_impersonation():
    """Verify claiming an MNC brand with a free public email (e.g. Google HR @gmail.com) is flagged."""
    payload = {
        "url": "https://careers-google-verify.online/listing",
        "title": "Google Cloud Support Specialist",
        "company": "Google",
        "content": (
            "Google is hiring Cloud Support Specialists in India. Excellent benefits and flexible hours. "
            "To apply for this Google role, send your resume directly to google.hiring.team2024@gmail.com. "
            "Do not apply on the main portal."
        ),
    }
    response = client.post("/api/scanner/analyze-content", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["scores"]["structural"] >= 30
    assert data["risk_score"] >= 50
    assert data["verdict"] in ("HIGH_RISK_FAKE", "SUSPICIOUS")

    messages = " ".join(f["message"].lower() for f in data["red_flags"])
    assert "free, generic public email" in messages or "corporate brand claimed" in messages


def test_detect_lure_work_captcha_scam():
    """Verify copy-paste/captcha typing high income trap is flagged."""
    payload = {
        "url": "https://work-from-home-easy.site/register",
        "title": "Part Time Online Typist",
        "company": "Easy Cash Jobs",
        "content": (
            "Simple copy paste work from home! Earn ₹50,000 monthly with no experience needed. "
            "Captcha typing work 2 hours daily with 100% guaranteed job placement and daily payout. "
            "Hurry up limited slots available!"
        ),
    }
    response = client.post("/api/scanner/analyze-content", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["scores"]["linguistic"] >= 40
    assert data["risk_score"] >= 50
    assert data["verdict"] in ("HIGH_RISK_FAKE", "CONFIRMED_SCAM")

    messages = " ".join(f["message"].lower() for f in data["red_flags"])
    assert "lure" in messages or "guarantee" in messages


def test_detect_whatsapp_no_interview_scam():
    """Verify direct selection without interview via WhatsApp is detected."""
    payload = {
        "url": "https://jobs-express-joining.xyz/apply",
        "title": "Office Assistant",
        "company": "Metro Direct",
        "content": (
            "Immediate joining without interview! Offer letter ready today. "
            "Direct selection without any exam. Message on WhatsApp +91-9988776655 "
            "within 24 hours to claim your position!"
        ),
    }
    response = client.post("/api/scanner/analyze-content", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] >= 60
    assert data["scores"]["linguistic"] >= 30
    assert data["scores"]["structural"] >= 20

    messages = " ".join(f["message"].lower() for f in data["red_flags"])
    assert "without formal interview" in messages or "offer letter" in messages
    assert "informal messaging" in messages


def test_legitimate_google_job_verified():
    """Verify that genuine corporate job vocabulary (urgent requirement, competitive salary) produces 0 false positives."""
    payload = {
        "url": "https://careers.google.com/jobs/results/98765",
        "title": "Staff Software Engineer, Distributed Systems",
        "company": "Google LLC",
        "content": (
            "Google is seeking a Staff Software Engineer to join our infrastructure group. "
            "In this role you will architect high-scale distributed systems and collaborate with cross-functional teams. "
            "We have an urgent requirement for experienced engineering leaders with 8+ years of experience. "
            "We offer a highly competitive salary, comprehensive health insurance, and equity packages. "
            "Please contact our recruitment team or apply directly through our official careers portal."
        ),
    }
    response = client.post("/api/scanner/analyze-content", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["scores"]["behavioral"] == 0
    assert data["scores"]["linguistic"] == 0
    assert data["scores"]["structural"] == 0
    assert data["risk_score"] <= 15
    assert data["risk_level"] == "LOW"
    assert data["verdict"] in ("VERIFIED_REAL", "LIKELY_REAL")
    assert len(data["red_flags"]) == 0
    assert data["legitimacy_score"] >= 80


def test_legitimate_job_with_eeo_and_benefits():
    """Verify that corporate hallmarks (EEO, 401k, health insurance, anti-scam disclaimer) are identified as green flags."""
    payload = {
        "url": "https://jobs.lever.co/enterprise-tech/12345",
        "title": "Senior Backend Engineer (Python / Go)",
        "company": "Enterprise Tech Solutions",
        "content": (
            "About the Role: We are looking for a Senior Backend Engineer. Minimum qualifications: "
            "Bachelor's degree in Computer Science and 5+ years of experience in distributed systems. "
            "Responsibilities include building scalable microservices and mentoring junior engineers. "
            "Our hiring process involves a technical interview, a take-home coding challenge, and a system design review. "
            "Benefits: We provide comprehensive health insurance, 401(k) matching, paid time off, and stock options. "
            "Equal Opportunity Employer: We evaluate qualified applicants without regard to race, color, religion, sex, or national origin. "
            "Recruitment Fraud Alert: We never charge any fee or deposit at any stage of our recruitment process."
        ),
    }
    response = client.post("/api/scanner/analyze-content", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] <= 10
    assert data["risk_level"] == "LOW"
    assert data["verdict"] == "VERIFIED_REAL"
    assert data["fake_job_probability"] <= 10
    assert data["legitimacy_score"] >= 85
    assert len(data["green_flags"]) >= 3

    green_types = [g["type"] for g in data["green_flags"]]
    assert "anti_fraud_policy" in green_types
    assert "eeo_compliance" in green_types
    assert "corporate_benefits" in green_types


def test_verified_ats_domain_identification():
    """Verify that recognized ATS platforms (Greenhouse, Lever, Workday) receive verified platform status."""
    tech_greenhouse = analyze_technical("https://boards.greenhouse.io/company/jobs/12345")
    assert tech_greenhouse["checks"]["is_verified_platform"] is True
    assert tech_greenhouse["technical_score"] <= 10

    tech_workday = analyze_technical("https://company.myworkdayjobs.com/careers/job/123")
    assert tech_workday["checks"]["is_verified_platform"] is True

    # High-risk scam TLD
    tech_scam = analyze_technical("https://recruitment-urgent-job.xyz/apply")
    assert tech_scam["checks"]["suspicious_patterns"]["has_scam_tld"] is True
    assert tech_scam["technical_score"] >= 25
