"""
Urgency and Pressure Tactics Analyzer for HireShield NLP Engine.

Evaluates high-pressure recruitment tactics, artificial scarcity, and time-sensitive
coercion while distinguishing standard business hiring announcements.
"""

import re
from typing import Dict, Any, List

# Predatory Urgency Patterns (artificial scarcity, high pressure)
PREDATORY_URGENCY_PATTERNS = [
    (re.compile(r"\b(act\s+now|today\s+only|immediate\s+joining\s+today)\b", re.I), "extreme_time_pressure", 20, "high"),
    (re.compile(r"\b(only\s+\d+\s+(seats?|vacancies|spots?)\s*(left|remaining))\b", re.I), "artificial_scarcity", 20, "high"),
    (re.compile(r"\b(offer\s+valid\s+(for\s+today|for\s+next\s+\d+\s+hours?|until\s+midnight))\b", re.I), "exploding_offer_pressure", 25, "high"),
    (re.compile(r"\b(hurry\s+up|don['’]?t\s+miss\s+this\s+golden\s+opportunity)\b", re.I), "emotional_fomo_lure", 15, "medium"),
    (re.compile(r"\b(selected\s+candidates?\s+must\s+(pay|confirm\s+immediately))\b", re.I), "coercive_selection", 30, "critical"),
    (re.compile(r"\b(apply\s+immediately\s+or\s+lose\s+(your\s+)?(spot|job))\b", re.I), "threat_based_pressure", 25, "high"),
]

# Standard Hiring Expressions (mild urgency, normal corporate language)
STANDARD_URGENCY_PATTERNS = [
    (re.compile(r"\b(urgently\s+hiring|urgent\s+(opening|requirement|hire))\b", re.I), "standard_urgent_hiring", 5, "low"),
    (re.compile(r"\bapply\s+(now|today|online)\b", re.I), "standard_call_to_action", 0, "none"),
    (re.compile(r"\bimmediate\s+joiners?\s+preferred\b", re.I), "immediate_joiner_preference", 3, "low"),
]

def analyze_urgency(text: str) -> Dict[str, Any]:
    """
    Analyzes urgency language in job posting text.
    Returns score (0-100), detected features, and evidence snippets.
    """
    if not text:
        return {"urgency_score": 0, "features": [], "evidence": [], "is_predatory": False}

    features = []
    evidence = []
    predatory_matches = 0
    total_score = 0

    for pattern, name, score, severity in PREDATORY_URGENCY_PATTERNS:
        match = pattern.search(text)
        if match:
            predatory_matches += 1
            snippet = match.group(0)
            features.append({
                "feature": name,
                "severity": severity,
                "evidence": snippet,
                "score": score
            })
            evidence.append(snippet)
            total_score += score

    # Check mild / standard urgency
    has_standard = False
    for pattern, name, score, severity in STANDARD_URGENCY_PATTERNS:
        match = pattern.search(text)
        if match and score > 0:
            has_standard = True
            # Only record mild score if predatory score is low
            if predatory_matches == 0:
                features.append({
                    "feature": name,
                    "severity": severity,
                    "evidence": match.group(0),
                    "score": score
                })
                total_score += score

    # Cap urgency score to 100
    urgency_score = min(100, total_score)
    is_predatory = predatory_matches >= 1

    return {
        "urgency_score": urgency_score,
        "features": features,
        "evidence": evidence,
        "is_predatory": is_predatory
    }
