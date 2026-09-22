import re
from typing import List, Optional
from app.schemas.risk import RiskCategory, RiskSignal

# Lexical indicators
SUSPICIOUS_GUARANTEE_PATTERNS = [
    r"\b100%\s*(guaranteed|placement|job)\b",
    r"\bguaranteed\s*(interview|offer|salary|visa)\b",
    r"\bno\s*experience\s*(needed|required)\s*high\s*salary\b",
    r"\bearn\s*(daily|unlimited|huge)\b",
]

SENSITIVE_FINANCIAL_PATTERNS = [
    r"\b(registration|processing|verification|security|training)\s*fee\b",
    r"\b(deposit|advance)\s*(required|money)\b",
    r"\b(bank\s*details|aadhaar|pan\s*card|debit\s*card|credit\s*card|otp)\b",
]

URGENT_PRESSURE_PATTERNS = [
    r"\b(urgent|immediate|limited\s*slots|last\s*chance|within\s*24\s*hours)\b",
    r"\b(hurry|act\s*now|rush)\b",
]

INFORMAL_CHANNEL_PATTERNS = [
    r"\b(whatsapp|telegram|direct\s*message|dm\s*me)\b",
]


class NLPService:
    """
    Deterministic NLP analysis service.
    Designed with a clean interface for seamless future LLM/AI model integration.
    """

    def analyze_text(
        self,
        resume_text: Optional[str] = None,
        job_description: Optional[str] = None,
        declared_skills: Optional[List[str]] = None,
    ) -> List[RiskSignal]:
        """
        Analyze candidate text content (resume, statements, role requirements)
        and extract potential risk signals.
        """
        signals: List[RiskSignal] = []

        combined_text = f"{resume_text or ''} {job_description or ''}".lower()
        if not combined_text.strip():
            # Flag missing resume/profile content as potential verification risk
            signals.append(
                RiskSignal(
                    signal_name="EMPTY_RESUME_TEXT",
                    category=RiskCategory.RESUME,
                    severity=35,
                    weight=0.25,
                    description="No detailed resume text or career narrative was provided for analysis.",
                    evidence="Resume text field is empty or unpopulated.",
                )
            )
            return signals

        # 1. Financial & Credential Demands
        for pattern in SENSITIVE_FINANCIAL_PATTERNS:
            matches = re.findall(pattern, combined_text)
            if matches:
                matched_sample = matches[0] if isinstance(matches[0], str) else matches[0][0]
                signals.append(
                    RiskSignal(
                        signal_name="FINANCIAL_OR_CREDENTIAL_SOLICITATION",
                        category=RiskCategory.NLP,
                        severity=85,
                        weight=0.45,
                        description="Potential solicitation of upfront fees, security deposits, or sensitive identity credentials.",
                        evidence=f"Matched trigger: '{matched_sample}' in profile context.",
                    )
                )
                break

        # 2. Unrealistic Guarantee Claims
        for pattern in SUSPICIOUS_GUARANTEE_PATTERNS:
            matches = re.findall(pattern, combined_text)
            if matches:
                signals.append(
                    RiskSignal(
                        signal_name="UNREALISTIC_GUARANTEE_LANGUAGE",
                        category=RiskCategory.NLP,
                        severity=60,
                        weight=0.35,
                        description="Unusually strong employment or salary guarantee statements detected.",
                        evidence="Contains promotional or high-assurance guarantee claims.",
                    )
                )
                break

        # 3. Urgency & Pressure Tactics
        urgency_matches = []
        for pattern in URGENT_PRESSURE_PATTERNS:
            found = re.findall(pattern, combined_text)
            if found:
                urgency_matches.extend(found)
        if len(urgency_matches) >= 2:
            signals.append(
                RiskSignal(
                    signal_name="EXCESSIVE_URGENCY_LANGUAGE",
                    category=RiskCategory.NLP,
                    severity=45,
                    weight=0.25,
                    description="High recurrence of artificial urgency or pressure-oriented phrasing.",
                    evidence=f"Multiple urgency phrases detected ({len(urgency_matches)} instances).",
                )
            )

        # 4. Informal Channel Reliance
        for pattern in INFORMAL_CHANNEL_PATTERNS:
            if re.search(pattern, combined_text):
                signals.append(
                    RiskSignal(
                        signal_name="INFORMAL_COMMUNICATION_VECTOR",
                        category=RiskCategory.CONSISTENCY,
                        severity=40,
                        weight=0.20,
                        description="Communication appears to route through personal/informal messaging apps.",
                        evidence="Mentions of WhatsApp or Telegram messaging channels.",
                    )
                )
                break

        # 5. Generic / Inflated Skill Buzzwords
        if resume_text and len(resume_text.split()) < 30 and (declared_skills and len(declared_skills) > 12):
            signals.append(
                RiskSignal(
                    signal_name="SKILL_LIST_INFLATION",
                    category=RiskCategory.RESUME,
                    severity=40,
                    weight=0.25,
                    description="High ratio of declared skills relative to minimal supporting resume text context.",
                    evidence=f"{len(declared_skills)} skills listed with under 30 words of explanatory work history.",
                )
            )

        return signals


nlp_service = NLPService()


def get_nlp_service() -> NLPService:
    return nlp_service
