"""
Scam Patterns and Linguistic Signature Definitions for HireShield NLP Engine.

Defines compiled patterns for guaranteed job promises, vague lure patterns,
suspicious contact methods, and formatting anomalies.
"""

import re
from typing import List, Dict, Any, Tuple

# Guaranteed Employment / Income Claims
GUARANTEED_JOB_PATTERNS = [
    (re.compile(r"\bguaranteed\s+(job|placement|income|employment|salary|earnings?)\b", re.I), "guaranteed_placement", 25, "high"),
    (re.compile(r"\b100%\s*(job\s*guarantee|placement\s*guarantee|money\s*back)\b", re.I), "guaranteed_placement_100", 25, "high"),
    (re.compile(r"\b(no\s+interview\s+required|direct\s+(joining|selection|appointment))\b", re.I), "direct_selection_no_interview", 30, "high"),
    (re.compile(r"\binstant\s+(offer\s*letter|appointment\s*letter)\b", re.I), "instant_offer_letter", 25, "high"),
    (re.compile(r"\bearn\s+(\$|₹|rs\.?|inr|usd)\s*\d+[\d,]*\s*(daily|per\s*day|per\s*hour)\b", re.I), "unrealistic_daily_earning", 20, "medium"),
]

# Suspicious Contact & Off-Platform Communication Methods
SUSPICIOUS_CONTACT_PATTERNS = [
    (re.compile(r"\b(contact|reach|message|apply|send\s+(?:resume|cv)|chat)\s*(?:us|me|recruiter|team)?\s*(?:only\s+)?(?:via|on|through)?\s*(?:only\s+)?(whats\s*app|wa\.me|telegram|t\.me|signal)\b", re.I), "off_platform_chat_only", 30, "high"),
    (re.compile(r"\b(whats\s*app|telegram|signal)\s+(?:only|recruiter\s*only|recruiter|contact|chat|messaging|interview|team)\b", re.I), "off_platform_chat_only", 30, "high"),
    (re.compile(r"\btelegram\s*(?:username|id|channel|handle)?\s*:\s*@?\w+", re.I), "telegram_contact", 25, "medium"),
    (re.compile(r"\b(whatsapp|wa\.me)\s*(?:number|contact|only)?\s*:\s*[\+\d\s\-\(\)]{8,}", re.I), "whatsapp_contact", 25, "medium"),
    (re.compile(r"\b(reach\s*out|dm\s*me)\s*on\s*hangouts\b", re.I), "hangouts_recruitment", 25, "high"),
]

# Vague Job Descriptions / Unrealistic Work Lures
VAGUE_LURE_PATTERNS = [
    (re.compile(r"\b(simple|easy)\s+copy[- ]paste\s+(work|job)\b", re.I), "copy_paste_lure", 20, "medium"),
    (re.compile(r"\bwork\s+(from\s+home\s+)?with\s+just\s+(a\s+)?(mobile|smartphone|phone)\b", re.I), "mobile_only_lure", 15, "medium"),
    (re.compile(r"\bno\s+(prior\s+)?experience\s+(needed|required|necessary)\b", re.I), "no_experience_required", 5, "low"),
    (re.compile(r"\b(unlimited\s+earning\s+potential|be\s+your\s+own\s+boss|financial\s+freedom)\b", re.I), "mlm_style_promise", 15, "medium"),
]

# Money Mule / Check Washing / Reshipping Fraud
MONEY_MULE_PATTERNS = [
    (re.compile(r"\b(receive\s+funds|transfer\s+money|forward\s+payments?|accept\s+payments?)\b", re.I), "payment_transfer_agent", 35, "critical"),
    (re.compile(r"\b(deposit\s+(a\s+)?(cashier['’]?s\s+)?check|reimburse\s+via\s+check)\b", re.I), "fake_check_deposit", 40, "critical"),
    (re.compile(r"\bpackage\s+(forwarding|reshipment|inspection)\s+agent\b", re.I), "reshipping_mule", 35, "critical"),
]

# Formatting Anomalies (excessive punctuation, capitalization)
def check_formatting_anomalies(text: str) -> List[Dict[str, Any]]:
    features = []
    if not text or len(text.strip()) < 40:
        return features

    # Excessive exclamation marks (e.g., "HURRY!!!" or multiple "!?!")
    excl_matches = re.findall(r"!{2,}|\?{2,}", text)
    if len(excl_matches) >= 3:
        features.append({
            "feature": "excessive_punctuation",
            "severity": "medium",
            "evidence": f"Found {len(excl_matches)} instances of stacked exclamation/question marks",
            "score": 10
        })

    # Excessive Capitalization (>40% uppercase letters in a reasonably sized description)
    letters = [c for c in text if c.isalpha()]
    if len(letters) > 80:
        upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
        if upper_ratio > 0.40:
            features.append({
                "feature": "excessive_capitalization",
                "severity": "medium",
                "evidence": f"{int(upper_ratio * 100)}% uppercase characters detected",
                "score": 12
            })

    return features
