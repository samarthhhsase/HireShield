"""
Salary Anomaly Engine for HireShield.

Extracts compensation ranges, currencies, payment frequencies, and experience levels.
Detects unrealistic income claims and role-to-compensation imbalances using configurable benchmarks.
"""

import re
from typing import Dict, Any, Optional, Tuple

from app.risk_engine.risk_config import ENTRY_LEVEL_MAX_ANNUAL_SALARY


def extract_salary_details(text_or_salary: str) -> Dict[str, Any]:
    """
    Extracts currency, numerical amounts, frequency, and role category.
    """
    res = {
        "raw_text": text_or_salary,
        "currency": "USD",
        "min_amount": None,
        "max_amount": None,
        "frequency": "annual",
        "role_category": "general",
        "experience_level": "mid",
        "annual_equivalent": None
    }

    if not text_or_salary:
        return res

    text = str(text_or_salary)

    # 1. Detect Currency
    if "₹" in text or re.search(r"\b(inr|rs\.?|rupees|lpa|lakhs?)\b", text, re.I):
        res["currency"] = "INR"
    elif "€" in text or re.search(r"\b(eur|euro)\b", text, re.I):
        res["currency"] = "EUR"
    elif "£" in text or re.search(r"\b(gbp|pound)\b", text, re.I):
        res["currency"] = "GBP"
    elif "$" in text or re.search(r"\b(usd|dollars?)\b", text, re.I):
        res["currency"] = "USD"

    # 2. Detect Frequency
    if re.search(r"\b(daily|per\s*day|a\s*day|\/day)\b", text, re.I):
        res["frequency"] = "daily"
    elif re.search(r"\b(hourly|per\s*hour|an\s*hour|\/hr|\/hour)\b", text, re.I):
        res["frequency"] = "hourly"
    elif re.search(r"\b(weekly|per\s*week|\/week)\b", text, re.I):
        res["frequency"] = "weekly"
    elif re.search(r"\b(monthly|per\s*month|\/month|\/mo)\b", text, re.I):
        res["frequency"] = "monthly"
    elif re.search(r"\b(yearly|annually|per\s*annum|annual|\/yr|\/year|lpa)\b", text, re.I):
        res["frequency"] = "annual"

    # 3. Detect Role Category
    if re.search(r"\b(data\s*entry|copy\s*paste|typing|typist|form\s*filling)\b", text, re.I):
        res["role_category"] = "data_entry"
    elif re.search(r"\b(customer\s*service|support\s*rep|chat\s*support)\b", text, re.I):
        res["role_category"] = "customer_service"
    elif re.search(r"\b(virtual\s*assistant|va)\b", text, re.I):
        res["role_category"] = "virtual_assistant"

    # 4. Detect Experience Level
    if re.search(r"\b(no\s+experience|fresher|freshers|entry\s*level|0\s*years?|students?)\b", text, re.I):
        res["experience_level"] = "entry"
    elif re.search(r"\b([5-9]|\d{2})\+?\s*years?\s+(of\s+)?experience\b", text, re.I):
        res["experience_level"] = "senior"

    # 5. Extract Numbers (Support Indian numbering / commas / Lakhs / K suffix)
    # Check for LPA (Lakhs Per Annum) e.g., "12 LPA", "5.5 Lakhs"
    lpa_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|to)?\s*(\d+(?:\.\d+)?)?\s*(?:lpa|lakhs?)", text, re.I)
    if lpa_match and res["currency"] == "INR":
        min_lakh = float(lpa_match.group(1))
        max_lakh = float(lpa_match.group(2)) if lpa_match.group(2) else min_lakh
        res["min_amount"] = int(min_lakh * 100000)
        res["max_amount"] = int(max_lakh * 100000)
        res["frequency"] = "annual"
    else:
        # Standard digits
        numbers = re.findall(r"\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b", text)
        clean_nums = []
        for n in numbers:
            try:
                clean_nums.append(float(n.replace(",", "")))
            except ValueError:
                continue

        # Filter out numbers that look like years (e.g., 2024, 2025, 2026) if lone
        salary_candidates = [n for n in clean_nums if n not in (2023, 2024, 2025, 2026)]
        if salary_candidates:
            res["min_amount"] = min(salary_candidates)
            res["max_amount"] = max(salary_candidates)

    # 6. Normalize to Annual Equivalent
    amt = res["max_amount"] or res["min_amount"]
    if amt:
        freq = res["frequency"]
        if freq == "hourly":
            res["annual_equivalent"] = amt * 2000
        elif freq == "daily":
            res["annual_equivalent"] = amt * 250
        elif freq == "weekly":
            res["annual_equivalent"] = amt * 52
        elif freq == "monthly":
            res["annual_equivalent"] = amt * 12
        else:
            res["annual_equivalent"] = amt

    return res


def analyze_salary_anomaly(
    salary_str: Optional[str] = None,
    job_text: Optional[str] = None,
    country: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluates salary credibility against role category, frequency, and experience level.
    """
    combined_text = f"{salary_str or ''} {job_text or ''}".strip()
    if not combined_text:
        return {
            "salary_anomaly_score": 0,
            "reason": "No compensation details found to analyze.",
            "confidence": 0.20,
            "details": {}
        }

    details = extract_salary_details(combined_text)
    curr = details["currency"]
    role = details["role_category"]
    exp = details["experience_level"]
    annual_val = details.get("annual_equivalent")

    score = 0
    reason = "Salary is within normal market parameters."
    confidence = 0.50

    # 1. Guaranteed income claims
    if re.search(r"\bguaranteed\s+(daily|weekly|monthly|annual)\s+(income|salary|earnings?)\b", combined_text, re.I):
        score = max(score, 35)
        reason = "Job claims guaranteed fixed income regardless of performance or hours worked."
        confidence = 0.85

    # 2. Daily / Hourly exorbitant claims for low-skill roles
    if details["frequency"] in ("daily", "hourly") and exp == "entry":
        if curr == "USD" and details["max_amount"] and details["max_amount"] > 100 and details["frequency"] == "hourly":
            score = max(score, 40)
            reason = f"Unrealistic hourly compensation of ${details['max_amount']}/hr claimed for entry-level work."
            confidence = 0.90
        elif curr == "USD" and details["max_amount"] and details["max_amount"] > 500 and details["frequency"] == "daily":
            score = max(score, 40)
            reason = f"Unrealistic daily compensation of ${details['max_amount']}/day claimed for entry-level work."
            confidence = 0.90
        elif curr == "INR" and details["max_amount"] and details["max_amount"] > 5000 and details["frequency"] == "daily":
            score = max(score, 40)
            reason = f"Unrealistic daily compensation of ₹{details['max_amount']}/day claimed for entry-level work."
            confidence = 0.90

    # 3. Benchmark Check for Entry-Level Roles
    benchmarks = ENTRY_LEVEL_MAX_ANNUAL_SALARY.get(curr, ENTRY_LEVEL_MAX_ANNUAL_SALARY["USD"])
    role_limit = benchmarks.get(role, benchmarks.get("general", 65000))

    if annual_val and exp == "entry":
        confidence = 0.80
        if annual_val > (role_limit * 2.5):
            score = max(score, 45)
            reason = (
                f"Severe compensation anomaly: Claimed annual equivalent ({curr} {int(annual_val):,}) "
                f"is over 2.5x the upper market benchmark ({curr} {int(role_limit):,}) for entry-level {role.replace('_', ' ')}."
            )
        elif annual_val > (role_limit * 1.5):
            score = max(score, 25)
            reason = (
                f"Elevated compensation: Claimed annual equivalent ({curr} {int(annual_val):,}) "
                f"significantly exceeds entry-level benchmark ({curr} {int(role_limit):,})."
            )

    return {
        "salary_anomaly_score": min(100, score),
        "reason": reason,
        "confidence": round(confidence, 2),
        "details": details
    }
