import re
from typing import List, Optional, Set
from app.schemas.risk import RiskCategory, RiskSignal


class TechnicalAnalysisService:
    """
    Evaluates technical consistency, skill coverage, and experience alignment.
    """

    def analyze_technical(
        self,
        candidate_skills: List[str],
        job_description: Optional[str] = None,
        experience_years: Optional[float] = None,
        role: Optional[str] = None,
    ) -> List[RiskSignal]:
        """
        Compare declared candidate skills and experience against job expectations.
        Produces structured RiskSignal objects with TECHNICAL or CONSISTENCY categories.
        """
        signals: List[RiskSignal] = []
        c_skills_set = {s.strip().lower() for s in candidate_skills if s}

        # 1. Evaluate Skill Availability
        if not c_skills_set:
            signals.append(
                RiskSignal(
                    signal_name="NO_DECLARED_TECHNICAL_SKILLS",
                    category=RiskCategory.TECHNICAL,
                    severity=50,
                    weight=0.30,
                    description="Candidate profile contains no declared technical skills.",
                    evidence="Skills array is empty.",
                )
            )

        # 2. Extract Required Skills from Job Description
        if job_description:
            jd_lower = job_description.lower()
            # Common tech skills dictionary for comparison
            TECH_KEYWORDS = [
                "python", "javascript", "typescript", "react", "fastapi", "django",
                "sql", "postgresql", "docker", "kubernetes", "aws", "gcp", "azure",
                "node.js", "graphql", "java", "c++", "golang", "rust", "machine learning",
                "data science", "devops", "ci/cd", "rest api", "nosql", "redis",
            ]

            required_found = [kw for kw in TECH_KEYWORDS if kw in jd_lower]
            
            if required_found:
                matched = [kw for kw in required_found if kw in c_skills_set]
                missing = [kw for kw in required_found if kw not in c_skills_set]
                match_ratio = len(matched) / len(required_found)

                if match_ratio < 0.35 and len(required_found) >= 3:
                    signals.append(
                        RiskSignal(
                            signal_name="LOW_TECHNICAL_SKILL_ALIGNMENT",
                            category=RiskCategory.TECHNICAL,
                            severity=55,
                            weight=0.35,
                            description=f"Significant mismatch between target role requirements and candidate skill profile ({int(match_ratio * 100)}% match).",
                            evidence=f"Missing key requirements: {', '.join(missing[:4])}.",
                        )
                    )

        # 3. Experience vs Seniority Consistency Check
        if role and experience_years is not None:
            role_lower = role.lower()
            is_senior = any(title in role_lower for title in ["senior", "lead", "principal", "architect", "staff", "director"])
            
            if is_senior and experience_years < 2.0:
                signals.append(
                    RiskSignal(
                        signal_name="SENIORITY_EXPERIENCE_MISMATCH",
                        category=RiskCategory.CONSISTENCY,
                        severity=65,
                        weight=0.35,
                        description=f"Target role implies senior authority ('{role}'), but reported experience is only {experience_years} year(s).",
                        evidence=f"Experience ({experience_years} yrs) is significantly below typical seniority baseline for '{role}'.",
                    )
                )

        return signals


technical_analysis_service = TechnicalAnalysisService()


def get_technical_analysis_service() -> TechnicalAnalysisService:
    return technical_analysis_service
