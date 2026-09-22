"""
HireShield Advanced Heuristic NLP & Behavioral Intelligence Service.

Evaluates visible recruitment content across comprehensive threat vectors:
1. Behavioral Fraud Vectors:
   - Upfront fees, registration/training charges, mandatory equipment deposits
   - Sensitive identity/PII solicitation (pre-interview Aadhaar, PAN, SSN, banking credentials, OTP)
   - Fake check cashing, equipment overpayment, money mule & package reshipping schemes
2. Linguistic Vectors:
   - High-pressure urgency & artificial scarcity
   - Unrealistic compensation & placement guarantees
   - Direct interview-bypassing & fake offer promises
   - Low-quality scam job categories (CAPTCHA entry, copy-paste, ad clicking, MLM)
3. Structural & Channel Vectors:
   - Informal messaging channels (Telegram, WhatsApp direct chat, Instagram DM)
   - Obfuscated contact patterns & link shorteners
   - Corporate impersonation using free email services (@gmail, @yahoo, @outlook)
4. Legitimacy (Green Flags) Engine:
   - Anti-scam employer disclaimers ("We never charge fees...")
   - Equal Opportunity Employer (EEO) statements
   - Structured corporate benefits (401k, PF/ESI, health insurance, PTO, equity)
   - Formal multi-stage hiring lifecycle & clear technical qualifications
   - Verified ATS / corporate platform signatures

Designed strictly to prevent false positives on legitimate corporate recruitment vocabulary
(e.g., 'urgent requirement', 'competitive salary', 'apply now', 'contact us', 'healthcare').
"""

import re
import os
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger("hireshield.ai")

# ==============================================================================
# 1. Behavioral Patterns — High-Severity Fraud Indicators
# ==============================================================================

GOV_IDENTITY_PATTERNS = [
    r"\b(aadhaar|aadhar|pan\s*card)\b",
    r"\b(social\s*security\s*number|ssn)\b",
    r"\b(passport\s*copy|driver('s)?\s*license\s*(photo|scan))\b",
]

BANKING_CREDENTIAL_PATTERNS = [
    r"\b(bank\s*(account|details)|account\s*number|ifsc(\s*code)?)\b",
    r"\b(debit\s*card|credit\s*card|cvv|cancelled\s*cheque)\b",
]

AUTH_PASSWORD_OTP_PATTERNS = [
    r"\b(atm\s*pin|upi\s*pin|otp)\b",
    r"\b(net\s*banking\s*password|login\s*credentials|share\s*screen|anydesk|teamviewer)\b",
]

SENSITIVE_IDENTITY_PATTERNS = (
    GOV_IDENTITY_PATTERNS + BANKING_CREDENTIAL_PATTERNS + AUTH_PASSWORD_OTP_PATTERNS
)

UPFRONT_PAYMENT_PATTERNS = [
    r"\b(registration|processing|verification|security|training|application|kit|uniform|laptop)\s*fee(s)?\b",
    r"\b(security\s*deposit|refundable\s*deposit|advance\s*deposit)\b",
    r"\bpay\s*(₹|rs\.?|inr|\$)\s*\d+",
    r"\b(payment|fee)\s*(is\s*)?(required|mandatory)\s*(before|prior|for)\b",
    r"\b(onboarding|background\s*check|documentation|badge)\s*fee(s)?\b",
    r"\b(send|transfer)\s*(money|funds|crypto|bitcoin|usdt)\b",
]

CHECK_CASHING_OVERPAYMENT_PATTERNS = [
    r"\b(cashier('s)?\s*check|certified\s*check|send\s*(you\s*)?a\s*check)\b",
    r"\b(purchase|buy)\s*(home\s*office\s*)?(equipment|supplies|materials|laptop)\s*(from\s*our|via\s*our)\s*(certified|authorized|approved|specified)\s*vendor\b",
    r"\b(package\s*(forwarding|reshipping)|reship(ping)?\s*(packages|parcels)|parcel\s*mule)\b",
    r"\b(crypto\s*transfer|bitcoin\s*deposit|usdt\s*payout|receive\s*funds\s*and\s*transfer)\b",
]

# ==============================================================================
# 2. Linguistic Patterns — Coercion, Scarcity & Unrealistic Claims
# Explicitly avoids overfitting generic terms like "urgent requirement", "apply now", "contact us"
# ==============================================================================

HIGH_PRESSURE_URGENCY_PATTERNS = [
    r"\b(limited\s*slots|last\s*chance|within\s*24\s*hours|immediate\s*joining\s*without\s*interview|act\s*now\s*or\s*miss)\b",
    r"\bhurry\s*(up)?\s*(limited|few|last|slots)\b",
    r"\bonly\s*(1|2|3|few)\s*(slots?|openings?|seats?)\s*left\b",
]

INTERVIEW_BYPASS_PATTERNS = [
    r"\b(direct\s*selection\s*without\s*interview|offer\s*letter\s*(issued|ready)\s*(without|before)\s*interview|immediate\s*joining\s*without\s*(any\s*)?interview|no\s*interview\s*(needed|required))\b",
    r"\bdirect\s*(joining|selection)\s*no\s*(exam|test|interview)\b",
]

UNREALISTIC_GUARANTEE_PATTERNS = [
    r"\b100%\s*(job|placement|selection|guaranteed)\b",
    r"\bguaranteed\s*(job|placement|salary|income|interview)\b",
    r"\bno\s*experience\s*(needed|required)\s*high\s*salary\b",
    r"\bearn\s*(daily|weekly)\s*(₹|rs|\$)?\s*\d+\b",
    r"\bearn\s*(₹|rs|\$)\s*\d+\s*(daily|weekly|per\s*day|per\s*week)\b",
]

LURE_WORK_SCAM_PATTERNS = [
    r"\b(copy\s*paste\s*(work|job)|captcha\s*(typing|filling|entry|work)|sms\s*sending\s*job|ad\s*clicking|product\s*rating\s*job|video\s*liking\s*job)\b",
    r"\b(be\s*your\s*own\s*boss|unlimited\s*residual\s*income|downline\s*bonus|binary\s*plan|multi\s*level\s*marketing)\b",
]

# ==============================================================================
# 3. Structural Patterns — Unverified Informal Communication & Impersonation
# ==============================================================================

INFORMAL_CHANNEL_PATTERNS = [
    r"\b(whatsapp|telegram)\b",
    r"\bdm\s*(on|me)\s*(instagram|telegram|whatsapp)\b",
    r"\bmessage\s*(on|via)\s*(whatsapp|telegram)\b",
]

OBFUSCATED_CONTACT_PATTERNS = [
    r"\b(t\.me\/[a-zA-Z0-9_\-]+|wa\.me\/[0-9]+)\b",
    r"\b(bit\.ly|tinyurl\.com|cutt\.ly|is\.gd|rb\.gy)\/[a-zA-Z0-9_\-]+\b",
]

PROMINENT_CORPORATE_BRANDS = [
    "google", "amazon", "microsoft", "apple", "meta", "netflix",
    "tcs", "tata consultancy", "infosys", "wipro", "tata", "cognizant",
    "accenture", "deloitte", "ibm", "tesla", "adobe", "salesforce",
]

FREE_EMAIL_REGEX = re.compile(
    r"\b[\w\.-]+@(gmail|yahoo|hotmail|outlook|protonmail|rediffmail|live|aol|icloud)\.com\b",
    re.IGNORECASE,
)

# ==============================================================================
# 4. Legitimacy (Green Flags) Patterns — Hallmarks of Real Job Listings
# ==============================================================================

LEGITIMACY_DISCLAIMER_PATTERNS = [
    r"\b(we\s*(do\s*not|never)\s*charge\s*(any\s*)?(fee|money|deposit|payment)|recruitment\s*(fraud|scam)\s*alert|beware\s*of\s*(fraudulent|fake)\s*job|no\s*fee\s*is\s*charged\s*at\s*any\s*stage)\b",
]

LEGITIMACY_EEO_PATTERNS = [
    r"\b(equal\s*opportunity\s*employer|affirmative\s*action|without\s*regard\s*to\s*race,\s*color,\s*religion|eeo\s*employer|protected\s*veteran\s*status)\b",
]

LEGITIMACY_BENEFITS_PATTERNS = [
    r"\b(401\s*\(?k\)?|provident\s*fund|health\s*insurance|dental\s*(and|\&)\s*vision|paid\s*time\s*off|maternity\s*leave|paternity\s*leave|stock\s*options|equity\s*grant|esops?|health\s*savings\s*account)\b",
]

LEGITIMACY_QUALIFICATION_PATTERNS = [
    r"\b(bachelor('s)?\s*degree|master('s)?\s*degree|b\.?tech|m\.?tech|bs\s*in\s*computer\s*science|years\s*(of\s*)?experience|minimum\s*qualifications|preferred\s*qualifications)\b",
]

LEGITIMACY_INTERVIEW_PROCESS_PATTERNS = [
    r"\b(technical\s*interview|coding\s*(test|challenge)|system\s*design\s*interview|behavioral\s*interview|panel\s*interview|background\s*verification|take-home\s*(project|assignment))\b",
]

LEGITIMACY_ATS_SIGNATURE_PATTERNS = [
    r"\b(greenhouse\.io|lever\.co|myworkdayjobs|smartrecruiters|ashbyhq|taleo|icims|workday)\b",
]


def normalize_job_text(text: str) -> str:
    """Normalize whitespace, quotes, and punctuation for consistent NLP analysis."""
    if not text:
        return ""
    normalized = text.replace("“", '"').replace("”", '"').replace("’", "'").replace("–", "-")
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def extract_green_flags(text_lower: str) -> List[Dict[str, Any]]:
    """Identify positive hallmarks of legitimate corporate recruitment."""
    green_flags: List[Dict[str, Any]] = []

    # 1. Anti-Scam Recruiter Disclaimer
    for pattern in LEGITIMACY_DISCLAIMER_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            green_flags.append({
                "type": "anti_fraud_policy",
                "confidence": "high",
                "title": "Verified Anti-Fraud Disclaimer",
                "message": "Explicit recruiter disclaimer stating that no fees are ever charged for recruitment.",
                "evidence": f"Found: '{match.group(0)}'",
                "trust_bonus": +15,
            })
            break

    # 2. Equal Opportunity Employer (EEO) Compliance
    for pattern in LEGITIMACY_EEO_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            green_flags.append({
                "type": "eeo_compliance",
                "confidence": "high",
                "title": "EEO & Diversity Compliance",
                "message": "Contains standard Equal Opportunity Employer / affirmative action policy disclosure.",
                "evidence": f"Found: '{match.group(0)}'",
                "trust_bonus": +10,
            })
            break

    # 3. Comprehensive Corporate Benefits
    for pattern in LEGITIMACY_BENEFITS_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            green_flags.append({
                "type": "corporate_benefits",
                "confidence": "medium",
                "title": "Corporate Benefits Package",
                "message": "Lists legitimate employment benefits (e.g. 401k, health insurance, paid leave, or equity).",
                "evidence": f"Found: '{match.group(0)}'",
                "trust_bonus": +10,
            })
            break

    # 4. Structured Qualifications & Experience Requirements
    for pattern in LEGITIMACY_QUALIFICATION_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            green_flags.append({
                "type": "structured_qualifications",
                "confidence": "medium",
                "title": "Structured Qualifications Defined",
                "message": "Clearly specifies educational degrees, relevant work history, or formal qualifications.",
                "evidence": f"Found: '{match.group(0)}'",
                "trust_bonus": +10,
            })
            break

    # 5. Multi-Stage Hiring Lifecycle
    for pattern in LEGITIMACY_INTERVIEW_PROCESS_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            green_flags.append({
                "type": "hiring_process",
                "confidence": "medium",
                "title": "Defined Evaluation Process",
                "message": "Outlines formal interview stages, coding assessments, or reference checks.",
                "evidence": f"Found: '{match.group(0)}'",
                "trust_bonus": +10,
            })
            break

    # 6. Corporate ATS / Enterprise Platform Reference
    for pattern in LEGITIMACY_ATS_SIGNATURE_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            green_flags.append({
                "type": "enterprise_ats",
                "confidence": "high",
                "title": "Enterprise ATS Integration",
                "message": "References established applicant tracking system (e.g. Greenhouse, Workday, Lever).",
                "evidence": f"Found: '{match.group(0)}'",
                "trust_bonus": +15,
            })
            break

    return green_flags


def analyze_with_ai(title: str, text: str) -> Dict[str, Any]:
    """
    Execute multi-factor heuristic NLP analysis on recruitment posting text.
    Extracts behavioral, linguistic, structural risk signals, and green flags
    without overfitting standard recruitment keywords.
    """
    title_norm = normalize_job_text(title)
    text_norm = normalize_job_text(text)
    combined = f"{title_norm} {text_norm}".strip()
    low = combined.lower()

    red_flags: List[Dict[str, Any]] = []
    behavioral = 0
    linguistic = 0
    structural = 0

    # -------------------------------------------------------------------------
    # 1. Behavioral Check: Sensitive Credentials & PII
    # -------------------------------------------------------------------------
    matched_gov = None
    for pattern in GOV_IDENTITY_PATTERNS:
        match = re.search(pattern, low)
        if match:
            matched_gov = match.group(0)
            break

    matched_bank = None
    for pattern in BANKING_CREDENTIAL_PATTERNS:
        match = re.search(pattern, low)
        if match:
            matched_bank = match.group(0)
            break

    matched_auth = None
    for pattern in AUTH_PASSWORD_OTP_PATTERNS:
        match = re.search(pattern, low)
        if match:
            matched_auth = match.group(0)
            break

    if matched_gov:
        behavioral += 45
        red_flags.append({
            "type": "behavioral",
            "severity": "critical",
            "message": "Sensitive identity or financial information is requested.",
            "evidence": f"Detected: '{matched_gov}' in recruitment content.",
            "impact": "+45 Behavioral Risk",
        })

    if matched_bank:
        behavioral += 40
        red_flags.append({
            "type": "behavioral",
            "severity": "critical",
            "message": "Bank account details, card numbers, or financial identifiers solicited.",
            "evidence": f"Detected: '{matched_bank}' in recruitment content.",
            "impact": "+40 Behavioral Risk",
        })

    if matched_auth:
        behavioral += 50
        red_flags.append({
            "type": "behavioral",
            "severity": "critical",
            "message": "Critical authentication credentials (OTP, net banking password, or PIN) requested.",
            "evidence": f"Detected: '{matched_auth}' in recruitment content.",
            "impact": "+50 Behavioral Risk",
        })

    # -------------------------------------------------------------------------
    # 2. Behavioral Check: Upfront Payments & Deposits
    # -------------------------------------------------------------------------
    for pattern in UPFRONT_PAYMENT_PATTERNS:
        match = re.search(pattern, low)
        if match:
            behavioral += 45
            red_flags.append({
                "type": "behavioral",
                "severity": "critical",
                "message": "A payment, fee, deposit, or paid verification is requested.",
                "evidence": f"Detected: '{match.group(0)}' in recruitment content.",
                "impact": "+45 Behavioral Risk",
            })
            break

    # -------------------------------------------------------------------------
    # 3. Behavioral Check: Check Cashing / Equipment Overpayment Scam
    # -------------------------------------------------------------------------
    for pattern in CHECK_CASHING_OVERPAYMENT_PATTERNS:
        match = re.search(pattern, low)
        if match:
            behavioral += 40
            red_flags.append({
                "type": "behavioral",
                "severity": "critical",
                "message": "Check cashing, equipment vendor reimbursement, or parcel reshipping scheme detected.",
                "evidence": f"Detected: '{match.group(0)}' in recruitment content.",
                "impact": "+40 Behavioral Risk",
            })
            break

    # -------------------------------------------------------------------------
    # 4. Linguistic Check: High-Pressure Urgency
    # -------------------------------------------------------------------------
    for pattern in HIGH_PRESSURE_URGENCY_PATTERNS:
        match = re.search(pattern, low)
        if match:
            linguistic += 30
            red_flags.append({
                "type": "linguistic",
                "severity": "high",
                "message": "Urgency or pressure-based recruitment language detected.",
                "evidence": f"Detected artificial urgency: '{match.group(0)}'.",
                "impact": "+30 Linguistic Risk",
            })
            break

    # -------------------------------------------------------------------------
    # 5. Linguistic Check: Direct Interview Bypassing
    # -------------------------------------------------------------------------
    for pattern in INTERVIEW_BYPASS_PATTERNS:
        match = re.search(pattern, low)
        if match:
            linguistic += 30
            red_flags.append({
                "type": "linguistic",
                "severity": "high",
                "message": "Offer letter or direct selection promised without formal interview or screening.",
                "evidence": f"Detected interview bypass: '{match.group(0)}'.",
                "impact": "+30 Linguistic Risk",
            })
            break

    # -------------------------------------------------------------------------
    # 6. Linguistic Check: Unrealistic Guarantee Language
    # -------------------------------------------------------------------------
    for pattern in UNREALISTIC_GUARANTEE_PATTERNS:
        match = re.search(pattern, low)
        if match:
            linguistic += 25
            red_flags.append({
                "type": "linguistic",
                "severity": "high",
                "message": "Unusually strong job or income guarantees detected.",
                "evidence": f"Detected unrealistic claim: '{match.group(0)}'.",
                "impact": "+25 Linguistic Risk",
            })
            break

    # -------------------------------------------------------------------------
    # 7. Linguistic Check: Lure Work & High-Risk Scam Categories
    # -------------------------------------------------------------------------
    for pattern in LURE_WORK_SCAM_PATTERNS:
        match = re.search(pattern, low)
        if match:
            linguistic += 30
            red_flags.append({
                "type": "linguistic",
                "severity": "high",
                "message": "High-risk task lure or MLM/pyramid scheme keywords detected.",
                "evidence": f"Detected lure archetype: '{match.group(0)}'.",
                "impact": "+30 Linguistic Risk",
            })
            break

    # -------------------------------------------------------------------------
    # 8. Linguistic Check: Excessive Promotional Punctuation
    # -------------------------------------------------------------------------
    exclamations = combined.count("!")
    if exclamations >= 5:
        linguistic += 15
        red_flags.append({
            "type": "linguistic",
            "severity": "medium",
            "message": "Excessive promotional or urgent punctuation detected.",
            "evidence": f"Contains {exclamations} exclamation marks across the posting text.",
            "impact": "+15 Linguistic Risk",
        })

    # -------------------------------------------------------------------------
    # 9. Structural Check: Informal Messaging Channels
    # -------------------------------------------------------------------------
    for pattern in INFORMAL_CHANNEL_PATTERNS:
        match = re.search(pattern, low)
        if match:
            structural += 20
            red_flags.append({
                "type": "structural",
                "severity": "medium",
                "message": "Recruitment appears to rely on informal messaging channels.",
                "evidence": f"Informal channel detected: '{match.group(0)}'.",
                "impact": "+20 Structural Risk",
            })
            break

    # -------------------------------------------------------------------------
    # 10. Structural Check: Obfuscated Shortlinks & Direct Contact Links
    # -------------------------------------------------------------------------
    for pattern in OBFUSCATED_CONTACT_PATTERNS:
        match = re.search(pattern, low)
        if match:
            structural += 15
            red_flags.append({
                "type": "structural",
                "severity": "medium",
                "message": "Shortened link or direct chat redirect detected in job description.",
                "evidence": f"Detected redirect string: '{match.group(0)}'.",
                "impact": "+15 Structural Risk",
            })
            break

    # -------------------------------------------------------------------------
    # 11. Structural Check: Corporate Impersonation via Free Public Email
    # (e.g. MNC brand claimed, but contact address is @gmail.com or @yahoo.com)
    # -------------------------------------------------------------------------
    free_emails = FREE_EMAIL_REGEX.findall(combined)
    if free_emails:
        has_major_brand_claim = any(brand in low for brand in PROMINENT_CORPORATE_BRANDS)
        if has_major_brand_claim:
            structural += 30
            red_flags.append({
                "type": "structural",
                "severity": "high",
                "message": "Established corporate brand claimed alongside free, generic public email address.",
                "evidence": f"Detected free public email provider with corporate brand claim.",
                "impact": "+30 Structural Risk",
            })

    # -------------------------------------------------------------------------
    # 12. Green Flags (Legitimacy Signatures)
    # -------------------------------------------------------------------------
    green_flags = extract_green_flags(low)

    # Cap category scores at 100
    behavioral = min(100, behavioral)
    linguistic = min(100, linguistic)
    structural = min(100, structural)

    word_count = len(combined.split())

    # Calculate baseline legitimacy score from green flags (0 to 100)
    raw_trust = sum(flag.get("trust_bonus", 10) for flag in green_flags)
    legitimacy_score = min(100, max(0, raw_trust))

    return {
        "behavioral_score": behavioral,
        "linguistic_score": linguistic,
        "structural_score": structural,
        "red_flags": red_flags,
        "green_flags": green_flags,
        "legitimacy_score": legitimacy_score,
        "word_count": word_count,
    }
