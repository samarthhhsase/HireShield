"""
Credential Harvesting & Sensitive PII Detector for HireShield NLP Engine.

Identifies premature requests for government identity documents, banking credentials,
passwords, and OTPs within job descriptions or preliminary application steps.
"""

import re
from typing import Dict, Any, List

# High-Risk Credential & Identity Demands
CREDENTIAL_PATTERNS = [
    (re.compile(r"\b(send|upload|provide|share|submit|attach|enter)\s+(?:your\s+)?.*?\b(aadhaar(?:\s*card|\s*number)?|pan\s*card|passport(?:\s*copy|\s*photo|\s*details)?)\b.*?\b(apply|registration|register|interview|joining|form)\b", re.I), "upfront_government_id_harvesting", 45, "critical"),
    (re.compile(r"\b(send|upload|enter|provide|share|attach|submit)\s+(?:your\s+)?(?:clear\s+copy\s+of\s+|copy\s+of\s+)?(aadhaar(?:\s*card|\s*number)?|pan(?:\s*card|\s*number)?|passport(?:\s*copy|\s*photo|\s*details)?)\b", re.I), "direct_government_id_harvesting", 40, "critical"),
    (re.compile(r"\b(aadhaar\s*(number|card)?|pan\s*card\s*details?)\s*(mandatory\s+for\s+application|required\s+to\s+register|mandatory\s+to\s+apply|mandatory\s+field)\b", re.I), "mandatory_id_registration", 35, "high"),
    (re.compile(r"\b(bank\s*account\s*(?:number|details)?|ifsc\s*code|net\s*banking|cancelled\s*cheque|bank\s*passbook)\b", re.I), "premature_banking_details", 45, "critical"),
    (re.compile(r"\b(otp|one[- ]time\s*password|verification\s*code)\b.*?\b(phone|mobile|sms|received|share|send|enter|provide)\b", re.I), "otp_harvesting_attempt", 50, "critical"),
    (re.compile(r"\b(net\s*banking\s*password|security\s*pin|account\s*password|portal\s*password|login\s*password|cvv)\b", re.I), "password_or_pin_harvesting", 50, "critical"),
    (re.compile(r"\b(password|pin|security\s*code|cvv)\s*(of\s+your\s+account|for\s+verification|to\s+activate)\b", re.I), "password_or_pin_harvesting", 50, "critical"),
    (re.compile(r"\b(credit\s*card\s*number|debit\s*card\s*details|card\s*expiry)\b", re.I), "credit_card_harvesting", 45, "critical"),
    (re.compile(r"\b(upi\s*id|gpay\s*number|phonepe\s*number|paytm\s*number|payment\s*screenshot|transaction\s*id\s*of\s*fee|utr\s*number)\b", re.I), "upi_payment_harvesting", 40, "critical"),
]

# Normal/Legitimate HR Background Check Mentions (post-offer standard practices)
NORMAL_BGV_PATTERNS = [
    re.compile(r"\b(upon\s+successful\s+offer|post[- ]offer|after\s+joining|during\s+formal\s+onboarding)\b", re.I),
    re.compile(r"\b(standard\s+background\s+verification|bgv\s+process\s+conducted\s+by)\b", re.I),
]

def analyze_credential_harvesting(text: str) -> Dict[str, Any]:
    """
    Evaluates whether job post prematurely harvests PII or financial credentials.
    """
    if not text:
        return {"credential_risk_score": 0, "features": [], "evidence": [], "is_critical_harvesting": False}

    features = []
    evidence = []
    total_score = 0

    for pattern, name, score, severity in CREDENTIAL_PATTERNS:
        match = pattern.search(text)
        if match:
            matched_str = match.group(0)
            start_pos = max(0, match.start() - 100)
            end_pos = min(len(text), match.end() + 100)
            surrounding = text[start_pos:end_pos]

            # If standard post-offer onboarding context is explicitly stated
            if any(p.search(surrounding) for p in NORMAL_BGV_PATTERNS):
                continue

            features.append({
                "feature": name,
                "severity": severity,
                "evidence": matched_str,
                "score": score
            })
            evidence.append(matched_str)
            total_score += score

    credential_risk_score = min(100, total_score)
    is_critical_harvesting = credential_risk_score >= 35

    return {
        "credential_risk_score": credential_risk_score,
        "features": features,
        "evidence": evidence,
        "is_critical_harvesting": is_critical_harvesting
    }
