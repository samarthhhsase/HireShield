"""
Upfront Payment & Fee Request Detector for HireShield NLP Engine.

Identifies registration fees, training charges, security deposits, equipment fees,
and cryptocurrency/gift card payment demands, with intelligent fraud disclaimer suppression.
"""

import re
from typing import Dict, Any, List

# Legitimate anti-fraud disclaimers frequently present on official corporate careers pages
DISCLAIMER_PATTERNS = [
    re.compile(r"\b(never|does\s+not|do\s+not|will\s+never)\s+(charge|ask|request|demand|require|collect|solicit)\s+(any\s+)?([a-z\s]{0,30})?(fees?|money|payment|deposit|charges?)\b", re.I),
    re.compile(r"\b(we\s+do\s+not\s+collect|free\s+of\s+cost\s+recruitment|no\s+fees?\s+at\s+any\s+stage)\b", re.I),
    re.compile(r"\b(beware\s+of\s+(fake|fraudulent)|fraud\s+alert|anti[- ]fraud\s+notice)\b", re.I),
]

# Explicit upfront payment demands
PAYMENT_PATTERNS = [
    (re.compile(r"\b(registration|processing|application|onboarding|admin|joining)\s*fees?\s*(of\s*)?(\$|₹|rs\.?|inr|usd)?\s*\d*\b", re.I), "registration_fee_request", 40, "critical"),
    (re.compile(r"\b(security\s*deposit|refundable\s*deposit|caution\s*deposit)\s*(of\s*)?(\$|₹|rs\.?|inr|usd)?\s*\d*\b", re.I), "security_deposit_request", 40, "critical"),
    (re.compile(r"\b(training|course|certification|courier|delivery|kit|materials?|laptop)\s*fees?\s*(required|must\s+be\s+paid|applicable|of\s*(\$|₹|rs\.?|inr|usd)?\s*\d*|\b)", re.I), "mandatory_training_or_courier_fee", 35, "critical"),
    (re.compile(r"\b(pay|purchase|buy)\s+(your\s+own\s+)?(laptop|equipment|home\s+office\s+kit|software\s+license)\s*(first|in\s+advance|before)\b", re.I), "equipment_payment_scheme", 40, "critical"),
    (re.compile(r"\b(fee|charges?|amount)\s+(is\s+)?required\s+before\s+(interview|selection|joining|offer)\b", re.I), "pre_employment_fee_demand", 45, "critical"),
    (re.compile(r"\b(pay|deposit|transfer)\s+(\$|₹|rs\.?|inr|usd)?\s*\d+[\d,]*\s*(to|for|towards|as|before)\b", re.I), "direct_cash_to_apply", 45, "critical"),
    (re.compile(r"\b(bitcoin|crypto|usdt|eth|ethereum|gift\s*card|steam\s*card|apple\s*gift\s*card)\b", re.I), "cryptocurrency_or_giftcard_payment", 40, "critical"),
]

def analyze_payment_requests(text: str) -> Dict[str, Any]:
    """
    Evaluates whether job posting demands upfront money or deposits.
    Suppresses false alarms if the phrase appears inside an anti-scam corporate disclaimer.
    """
    if not text:
        return {"payment_risk_score": 0, "features": [], "evidence": [], "is_critical_payment": False}

    # Check for presence of legitimate anti-fraud disclaimer
    has_disclaimer = any(p.search(text) for p in DISCLAIMER_PATTERNS)

    features = []
    evidence = []
    total_score = 0

    for pattern, name, score, severity in PAYMENT_PATTERNS:
        matches = list(pattern.finditer(text))
        for m in matches:
            matched_str = m.group(0)
            start_pos = max(0, m.start() - 100)
            end_pos = min(len(text), m.end() + 100)
            surrounding_context = text[start_pos:end_pos]

            # If surrounding context has a negation (e.g. "We do not charge any registration fee")
            if any(p.search(surrounding_context) for p in DISCLAIMER_PATTERNS):
                continue

            features.append({
                "feature": name,
                "severity": severity,
                "evidence": matched_str,
                "score": score
            })
            evidence.append(matched_str)
            total_score += score
            break # Record once per pattern

    payment_risk_score = min(100, total_score)
    is_critical_payment = payment_risk_score >= 35

    return {
        "payment_risk_score": payment_risk_score,
        "features": features,
        "evidence": evidence,
        "is_critical_payment": is_critical_payment,
        "has_anti_fraud_disclaimer": has_disclaimer
    }
