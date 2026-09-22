"""
Unified NLP Risk Analyzer for HireShield.

Combines rule-based linguistic features, urgency detection, upfront fee analysis,
credential harvesting detection, and suspicious communication checks into an explainable score.
"""

import re
from typing import Dict, Any, List

from app.risk_engine.nlp.scam_patterns import (
    GUARANTEED_JOB_PATTERNS,
    SUSPICIOUS_CONTACT_PATTERNS,
    VAGUE_LURE_PATTERNS,
    MONEY_MULE_PATTERNS,
    check_formatting_anomalies,
)
from app.risk_engine.nlp.urgency import analyze_urgency
from app.risk_engine.nlp.payment_detection import analyze_payment_requests
from app.risk_engine.nlp.credential_detection import analyze_credential_harvesting

# Positive recruitment markers that indicate genuine corporate structure
POSITIVE_NLP_INDICATORS = [
    (re.compile(r"\b(equal\s+opportunity\s+employer|eeo\s+statement)\b", re.I), "Standard EEO / Diversity statement"),
    (re.compile(r"\b(comprehensive\s+benefits|health\s+insurance|401\(k\)|provident\s+fund|paid\s+time\s+off)\b", re.I), "Detailed corporate benefits package described"),
    (re.compile(r"\b(technical\s+round|coding\s+assessment|panel\s+interview|system\s+design)\b", re.I), "Structured multi-stage interview process defined"),
    (re.compile(r"\b(minimum\s+\d+\s+years?\s+of\s+experience|bachelor['’]?s\s+degree|master['’]?s\s+degree)\b", re.I), "Detailed qualifications and role requirements"),
    (re.compile(r"\b(anti[- ]fraud\s+notice|we\s+never\s+charge\s+any\s+fee)\b", re.I), "Corporate anti-fraud disclaimer present"),
]

def extract_linguistic_features(text: str) -> List[Dict[str, Any]]:
    """Extracts general linguistic scam indicators from job description text."""
    features = []
    if not text:
        return features

    # Check guaranteed job patterns
    for pattern, name, score, severity in GUARANTEED_JOB_PATTERNS:
        match = pattern.search(text)
        if match:
            features.append({
                "feature": name,
                "severity": severity,
                "evidence": match.group(0),
                "score": score
            })

    # Check vague lures
    for pattern, name, score, severity in VAGUE_LURE_PATTERNS:
        match = pattern.search(text)
        if match:
            features.append({
                "feature": name,
                "severity": severity,
                "evidence": match.group(0),
                "score": score
            })

    # Check money mule patterns
    for pattern, name, score, severity in MONEY_MULE_PATTERNS:
        match = pattern.search(text)
        if match:
            features.append({
                "feature": name,
                "severity": severity,
                "evidence": match.group(0),
                "score": score
            })

    # Check formatting anomalies (all-caps, excessive punctuation)
    features.extend(check_formatting_anomalies(text))

    return features

def detect_urgency(text: str) -> Dict[str, Any]:
    """Exposes standalone urgency detection."""
    return analyze_urgency(text)

def detect_payment_request(text: str) -> Dict[str, Any]:
    """Exposes standalone upfront payment analysis."""
    return analyze_payment_requests(text)

def detect_credential_harvesting(text: str) -> Dict[str, Any]:
    """Exposes standalone credential/PII harvesting detection."""
    return analyze_credential_harvesting(text)

def detect_unrealistic_salary(text: str) -> Dict[str, Any]:
    """Quick linguistic check for unrealistic salary phrases."""
    features = []
    evidence = []
    score = 0
    pattern = re.compile(r"\b(earn|make)\s+(\$|₹|rs\.?|inr|usd)?\s*\d+[\d,]*\s*(daily|per\s*day|every\s*day|hourly)\b", re.I)
    match = pattern.search(text)
    if match:
        matched_str = match.group(0)
        score = 25
        feat = {
            "feature": "unrealistic_daily_earning_claim",
            "severity": "high",
            "evidence": matched_str,
            "score": score
        }
        features.append(feat)
        evidence.append(matched_str)

    return {
        "unrealistic_salary_score": score,
        "features": features,
        "evidence": evidence
    }

def detect_suspicious_contact_methods(text: str) -> Dict[str, Any]:
    """Identifies off-platform contact attempts (WhatsApp/Telegram-only)."""
    features = []
    evidence = []
    score = 0

    for pattern, name, feat_score, severity in SUSPICIOUS_CONTACT_PATTERNS:
        match = pattern.search(text)
        if match:
            matched_str = match.group(0)
            score = max(score, feat_score)
            feat = {
                "feature": name,
                "severity": severity,
                "evidence": matched_str,
                "score": feat_score
            }
            features.append(feat)
            evidence.append(matched_str)

    return {
        "contact_risk_score": score,
        "features": features,
        "evidence": evidence
    }

def detect_impersonation_language(text: str) -> Dict[str, Any]:
    """Detects suspicious claims of association with top brands inside text."""
    features = []
    evidence = []
    score = 0

    partner_claim_pattern = re.compile(
        r"\b(authorized\s+hiring\s+partner\s+for|direct\s+vendor\s+for|recruiting\s+on\s+behalf\s+of)\s+(google|microsoft|amazon|apple|meta|tcs|infosys)\b",
        re.I
    )
    match = partner_claim_partner = partner_claim_pattern.search(text)
    if match:
        matched_str = match.group(0)
        score = 20
        feat = {
            "feature": "unverified_third_party_brand_claim",
            "severity": "medium",
            "evidence": matched_str,
            "score": score
        }
        features.append(feat)
        evidence.append(matched_str)

    return {
        "impersonation_language_score": score,
        "features": features,
        "evidence": evidence
    }

def analyze_job_text(text: str) -> Dict[str, Any]:
    """
    Main entry point for Job NLP Risk Analysis.
    Combines linguistic indicators, urgency, payment requests, credential harvesting,
    and returns a standardized response with score, features, evidence, and confidence.
    """
    if not text or len(text.strip()) == 0:
        return {
            "nlp_score": 0,
            "features": [],
            "evidence": [],
            "positive_signals": [],
            "confidence": 0.1
        }

    all_features = []
    all_evidence = []
    positive_signals = []

    # 1. Linguistic features
    ling_features = extract_linguistic_features(text)
    for f in ling_features:
        all_features.append(f)
        all_evidence.append(f["evidence"])

    # 2. Urgency
    urgency_res = analyze_urgency(text)
    for f in urgency_res["features"]:
        all_features.append(f)
        all_evidence.append(f["evidence"])

    # 3. Upfront Payment requests
    payment_res = analyze_payment_requests(text)
    for f in payment_res["features"]:
        all_features.append(f)
        all_evidence.append(f["evidence"])

    # 4. Credential Harvesting
    credential_res = analyze_credential_harvesting(text)
    for f in credential_res["features"]:
        all_features.append(f)
        all_evidence.append(f["evidence"])

    # 5. Suspicious Contact Methods
    contact_res = detect_suspicious_contact_methods(text)
    for f in contact_res["features"]:
        all_features.append(f)
        all_evidence.append(f["evidence"])

    # 6. Check for Positive Trust Signals
    for pattern, desc in POSITIVE_NLP_INDICATORS:
        if pattern.search(text):
            positive_signals.append(desc)

    # Calculate NLP Score
    # Deduplicate similar feature contributions and avoid simple linear accumulation exploding
    # Critical features (payment, credential harvesting) heavily drive score
    score_sum = sum(f.get("score", 0) for f in all_features)
    
    # Mitigation: If strong positive signals exist (e.g. detailed interview process, EEO statement)
    # and no critical payment/credential features are found, mitigate minor false-positive keywords
    has_critical = any(f.get("severity") == "critical" for f in all_features)
    if not has_critical and len(positive_signals) >= 2:
        score_sum = max(0, score_sum - (len(positive_signals) * 10))

    nlp_score = max(0, min(100, score_sum))

    # Calculate Confidence based on text length and feature density
    text_len = len(text.strip())
    if text_len < 100:
        base_confidence = 0.35
    elif text_len < 400:
        base_confidence = 0.60
    elif text_len < 1500:
        base_confidence = 0.85
    else:
        base_confidence = 0.95

    # If critical indicators are detected, boost confidence
    if has_critical:
        base_confidence = min(0.98, base_confidence + 0.15)

    return {
        "nlp_score": nlp_score,
        "features": all_features,
        "evidence": list(dict.fromkeys(all_evidence)),  # Unique preservation
        "positive_signals": positive_signals,
        "confidence": round(base_confidence, 2)
    }
