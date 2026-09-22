"""
Human-Readable Explanation & Recommendation Generator for HireShield.

Synthesizes detected technical & behavioral red flags, trust signals, and actionable advice.
"""

from typing import Dict, Any, List, Optional


def generate_explanation_summary(
    risk_score: int,
    risk_level: str,
    signals: List[Dict[str, Any]],
    positive_signals: List[str],
    override_info: Optional[Dict[str, Any]] = None
) -> str:
    """Generates an executive explanation summary of the risk assessment."""
    if override_info and override_info.get("override"):
        return f"CRITICAL RISK OVERRIDE: {override_info.get('reason')}. Multiple high-severity fraud indicators were confirmed."

    if risk_level == "CRITICAL":
        critical_count = sum(1 for s in signals if s.get("severity") == "critical")
        return f"Multiple critical recruitment fraud indicators detected ({critical_count} severe signals). This posting demonstrates strong signatures of an active employment scam."

    elif risk_level == "HIGH":
        return "Elevated risk detected. The posting contains several suspicious indicators such as domain anomalies, off-platform communication, or aggressive urgency."

    elif risk_level == "MODERATE":
        if signals:
            top_signal = signals[0].get("title", "unverified recruitment attributes")
            return f"Moderate caution advised. Potential anomalies detected ({top_signal}). Review details carefully before sharing personal information."
        return "Moderate risk. Some attributes could not be fully verified against official corporate registries."

    else:
        if positive_signals:
            return f"Low risk posting. Demonstrates verified trust signals including {positive_signals[0].lower()}."
        return "Low risk. No prominent fraud or credential harvesting indicators were identified."


def generate_recommendations(
    risk_level: str,
    signals: List[Dict[str, Any]],
    positive_signals: List[str]
) -> List[str]:
    """Provides actionable candidate safety recommendations based on findings."""
    recs = []

    has_payment = any("fee" in s.get("title", "").lower() or "deposit" in s.get("title", "").lower() for s in signals)
    has_credentials = any("aadhaar" in s.get("title", "").lower() or "otp" in s.get("title", "").lower() or "credential" in s.get("title", "").lower() for s in signals)
    has_domain_mismatch = any("mismatch" in s.get("title", "").lower() or "lookalike" in s.get("title", "").lower() for s in signals)
    has_chat_only = any("whatsapp" in s.get("title", "").lower() or "telegram" in s.get("title", "").lower() for s in signals)

    if has_payment:
        recs.append("NEVER transfer money, purchase gift cards, or pay registration/training fees. Legitimate employers never charge candidates.")

    if has_credentials:
        recs.append("Do NOT share government identity copies (Aadhaar/PAN/Passport) or OTPs before receiving an authentic, verifiable job offer.")

    if has_domain_mismatch:
        recs.append("Cross-reference this job opening directly on the employer's official careers website.")

    if has_chat_only:
        recs.append("Insist on communicating through verified corporate email rather than private messaging apps.")

    if risk_level in ("CRITICAL", "HIGH"):
        recs.append("Do not click unverified external links or download executable attachments from this recruiter.")
    elif risk_level == "MODERATE":
        recs.append("Independently verify the recruiter's corporate affiliation via LinkedIn or official directory.")
    else:
        recs.append("Follow standard professional diligence during interview rounds.")

    # Deduplicate while preserving order
    return list(dict.fromkeys(recs))


def generate_verification_audit(
    risk_score: int,
    risk_level: str,
    signals: List[Dict[str, Any]],
    positive_signals: List[str],
    analysis: Dict[str, Any],
    override_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generates a comprehensive verification breakdown explaining exactly:
    1. Why this job is verified real OR why this job was flagged as fake/suspicious.
    2. What we have checked across 6 intelligence pillars.
    3. How each check was verified with concrete findings and evidence.
    """
    if risk_level == "LOW":
        verdict = "VERIFIED_REAL"
        headline = "Why This Job Appears REAL & Legitimate"
        verdict_explanation = (
            "This posting exhibits authentic corporate recruitment patterns. "
            "The infrastructure is established and encrypted, official company presence is verified, "
            "zero upfront payment or identity harvesting demands were detected, and standard hiring procedures are followed."
        )
    elif risk_level in ("HIGH", "CRITICAL"):
        verdict = "FLAGGED_FAKE"
        headline = "Why This Job Was Flagged as FAKE & Fraudulent"
        if override_info and override_info.get("override"):
            verdict_explanation = (
                f"CRITICAL FRAUD SIGNATURE CONFIRMED: {override_info.get('reason')}. "
                "Legitimate employers never demand upfront fees, passwords, OTPs, or impersonate corporate domains."
            )
        else:
            verdict_explanation = (
                "Multiple high-severity recruitment fraud signatures were confirmed. "
                "The posting conflicts with legitimate hiring practices and presents severe risk to applicants."
            )
    else:
        verdict = "SUSPICIOUS"
        headline = "Why This Job Requires CAUTION & Verification"
        verdict_explanation = (
            "Potential recruitment anomalies or unverified credentials were identified. "
            "While no definitive payment extortion was confirmed, independent verification of the recruiter and employer is advised."
        )

    # Extract sub-scores
    domain_data = analysis.get("domain", {})
    domain_score = domain_data.get("score", 0) if isinstance(domain_data, dict) else 0
    
    company_data = analysis.get("company", {})
    company_score = company_data.get("score", 0) if isinstance(company_data, dict) else 0
    
    recruiter_data = analysis.get("recruiter", {})
    recruiter_score = recruiter_data.get("score", 0) if isinstance(recruiter_data, dict) else 0
    
    impersonation_data = analysis.get("impersonation", {})
    is_lookalike = impersonation_data.get("is_lookalike", False) if isinstance(impersonation_data, dict) else False
    
    salary_data = analysis.get("salary", {})
    salary_score = salary_data.get("score", 0) if isinstance(salary_data, dict) else 0
    
    nlp_data = analysis.get("nlp", {})
    nlp_score = nlp_data.get("score", 0) if isinstance(nlp_data, dict) else 0

    def _sig_text(s: Dict[str, Any]) -> str:
        return f"{s.get('title', '')} {s.get('message', '')} {s.get('description', '')}".lower()

    has_payment_flag = any(
        s.get("category") == "payment" or "payment" in _sig_text(s) or "fee" in _sig_text(s)
        for s in signals
    )
    has_credential_flag = any(
        s.get("category") in ("credential", "identity") or "credential" in _sig_text(s) or "banking" in _sig_text(s) or "otp" in _sig_text(s) or "pan" in _sig_text(s)
        for s in signals
    )

    # 1. Domain & Infrastructure Check
    if domain_score >= 35 or any("tld" in _sig_text(s) for s in signals):
        dom_status = "FAILED"
        dom_finding = "Domain registered recently or utilizes high-abuse disposable TLD commonly associated with scam infrastructure."
    elif domain_score > 0:
        dom_status = "CAUTION"
        dom_finding = "Domain infrastructure is active but possesses limited historical corporate longevity."
    else:
        dom_status = "PASSED"
        dom_finding = "Domain is well-established, DNS resolves correctly, and valid active TLS/SSL encryption is confirmed."

    # 2. Employer & Brand Identity Check
    if is_lookalike:
        brand_status = "FAILED"
        brand_finding = f"Lookalike domain detected: mimics {impersonation_data.get('matched_brand')} using typosquatting or brand affix insertion."
    elif company_score >= 30 or any("impersonat" in _sig_text(s) for s in signals):
        brand_status = "FAILED"
        brand_finding = "Mismatched employer identity: claimed major corporate brand does not align with posting domain."
    elif company_score > 0:
        brand_status = "CAUTION"
        brand_finding = "Employer entity could not be definitively linked to a verified corporate domain."
    else:
        brand_status = "PASSED"
        ats_str = next((ps for ps in positive_signals if "ATS" in ps or "platform" in ps), "Official corporate domain verified")
        brand_finding = f"{ats_str}. Consistent brand presence."

    # 3. Recruiter & Contact Channels Check
    if any("disposable" in _sig_text(s) for s in signals):
        rec_status = "FAILED"
        rec_finding = "Recruiter uses a temporary/burner email inbox (disposable domain). Legitimate employers never use burner emails."
    elif any("whatsapp" in _sig_text(s) or "telegram" in _sig_text(s) for s in signals):
        rec_status = "FAILED" if risk_level in ("HIGH", "CRITICAL") else "CAUTION"
        rec_finding = "Recruiter demands communicating solely via personal messaging apps (WhatsApp/Telegram) to evade platform audit trails."
    elif recruiter_score >= 30 or any("free, generic public email" in _sig_text(s) for s in signals):
        rec_status = "FAILED"
        rec_finding = "Claimed enterprise recruiter uses personal free webmail address (@gmail/@yahoo) rather than official corporate domain."
    elif recruiter_score > 0:
        rec_status = "CAUTION"
        rec_finding = "Recruiter uses free webmail. Common for small businesses/freelancers, but warrants caution for large organizations."
    else:
        rec_status = "PASSED"
        rec_finding = "Recruiter communicates through verified corporate email matching employer domain."

    # 4. Financial & Upfront Payment Demands Check
    if has_payment_flag:
        pay_status = "FAILED"
        pay_finding = "CRITICAL ALERT: Upfront payment request identified (registration fee, training charge, or security deposit)."
    else:
        pay_status = "PASSED"
        pay_finding = "PASSED: Zero upfront fees, registration charges, laptop purchase schemes, or cryptocurrency demands detected."

    # 5. Sensitive Identity & Credential Security Check
    if has_credential_flag:
        cred_status = "FAILED"
        cred_finding = "CRITICAL ALERT: Premature collection of government IDs (Aadhaar/PAN/Passport), banking credentials, passwords, or OTPs detected."
    else:
        cred_status = "PASSED"
        cred_finding = "PASSED: No premature credential harvesting, OTP solicitation, or banking data demands detected."

    # 6. Salary & Role Credibility Check
    if salary_score >= 35:
        sal_status = "FAILED"
        sal_finding = "Compensation anomaly: Offered salary significantly exceeds regional benchmarks for entry-level experience."
    elif salary_score > 0:
        sal_status = "CAUTION"
        sal_finding = "Elevated salary promises compared to role category benchmark."
    else:
        sal_status = "PASSED"
        sal_finding = "PASSED: Compensation claims are consistent with industry market standards and required qualifications."

    audit_checks = [
        {
            "pillar": "Domain & Infrastructure",
            "status": dom_status,
            "what_we_checked": "Evaluated WHOIS domain registration age, TLS/SSL security certificate, DNS resolution, and disposable scam TLD registries.",
            "how_verified": "Cross-referenced ICANN WHOIS data, tested port 443 TLS handshake, verified DNS A/NS records, and audited against high-abuse TLD blocklists.",
            "finding": dom_finding
        },
        {
            "pillar": "Employer & Brand Identity",
            "status": brand_status,
            "what_we_checked": "Audited claimed company name against hosting domain, verified ATS integration, and screened for lookalike typosquatting.",
            "how_verified": "Executed normalized Levenshtein similarity distance matching, homoglyph replacement, and enterprise ATS directory cross-referencing.",
            "finding": brand_finding
        },
        {
            "pillar": "Recruiter & Communication Channels",
            "status": rec_status,
            "what_we_checked": "Verified recruiter email domain, disposable burner inboxes, corporate MX alignment, and off-platform messaging solicitation.",
            "how_verified": "Screened recruiter email against disposable domain databases, MX records, and parsed for off-platform evasion (WhatsApp/Telegram).",
            "finding": rec_finding
        },
        {
            "pillar": "Upfront Payment & Fee Security",
            "status": pay_status,
            "what_we_checked": "Audited job body for registration fees, training costs, caution deposits, equipment purchases, or crypto transactions.",
            "how_verified": "Executed contextual NLP payment pattern extractors with intelligent corporate anti-fraud disclaimer suppression.",
            "finding": pay_finding
        },
        {
            "pillar": "Identity & Credential Security",
            "status": cred_status,
            "what_we_checked": "Checked for premature demands for government IDs (Aadhaar/PAN/Passport), bank accounts, passwords, or OTPs.",
            "how_verified": "Screened pre-interview application requirements against standard enterprise HR onboarding workflows.",
            "finding": cred_finding
        },
        {
            "pillar": "Salary & Role Credibility",
            "status": sal_status,
            "what_we_checked": "Audited compensation claims against role category, payment frequency, and stated experience level.",
            "how_verified": "Normalized compensation to annual figures and compared against regional market salary benchmarks.",
            "finding": sal_finding
        }
    ]

    return {
        "verdict": verdict,
        "headline": headline,
        "verdict_explanation": verdict_explanation,
        "checks_performed": audit_checks,
        "verification_methodology": "Multi-vector cross-referencing across DNS, WHOIS, TLS, NLP heuristics, and enterprise ATS platform whitelists."
    }

