"""
HireShield Salary Anomaly Engine Package.
"""

from app.risk_engine.salary.analyzer import analyze_salary_anomaly, extract_salary_details

__all__ = ["analyze_salary_anomaly", "extract_salary_details"]
