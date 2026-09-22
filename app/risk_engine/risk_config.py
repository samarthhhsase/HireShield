"""
HireShield Risk Engine Configuration.

Defines configurable weights, tier thresholds, known brand databases,
suspicious TLDs, disposable email domains, and benchmark parameters.
"""

from typing import Dict, Any, List

# Core Feature Group Weights (Normalized to 1.0 / 100%)
WEIGHTS = {
    "nlp": 0.30,
    "domain": 0.20,
    "company": 0.15,
    "recruiter": 0.10,
    "payment_credential": 0.15,
    "salary": 0.05,
    "impersonation": 0.05,
}

# Configurable Risk Tier Boundaries
RISK_THRESHOLDS = {
    "LOW": (0, 24),
    "MODERATE": (25, 49),
    "HIGH": (50, 74),
    "CRITICAL": (75, 100),
}

# High-abuse disposable TLDs frequently utilized for recruitment fraud campaigns
SCAM_TLDS = {
    ".xyz", ".top", ".online", ".site", ".buzz", ".work", ".click",
    ".monster", ".fit", ".rest", ".space", ".cfd", ".sbs", ".cam", ".vip",
}

# Established applicant tracking systems and enterprise career portals
VERIFIED_ATS_PLATFORMS = {
    "greenhouse.io",
    "lever.co",
    "myworkdayjobs.com",
    "ashbyhq.com",
    "smartrecruiters.com",
    "taleo.net",
    "icims.com",
    "bamboohr.com",
    "linkedin.com",
    "indeed.com",
    "naukri.com",
    "wellfound.com",
    "handshake.com",
    "glassdoor.com",
    "apple.com",
    "google.com",
    "microsoft.com",
    "amazon.jobs",
    "meta.com",
}

# Free website builders commonly abused to host throwaway recruitment pages
FREE_HOSTING_DOMAINS = {
    "blogspot.com",
    "wixsite.com",
    "weebly.com",
    "wordpress.com",
    "sites.google.com",
    "carrd.co",
}

# Free public email providers (suspicious when used by major corporations)
FREE_EMAIL_PROVIDERS = {
    "gmail.com",
    "yahoo.com",
    "hotmail.com",
    "outlook.com",
    "protonmail.com",
    "rediffmail.com",
    "live.com",
    "aol.com",
    "icloud.com",
    "zoho.com",
}

# Known disposable/temporary email services
DISPOSABLE_EMAIL_DOMAINS = {
    "tempmail.com",
    "guerrillamail.com",
    "10minutemail.com",
    "mailinator.com",
    "throwawaymail.com",
    "yopmail.com",
    "sharklasers.com",
    "temp-mail.org",
}

# Known global brands for impersonation & lookalike analysis
KNOWN_COMPANY_DOMAINS: Dict[str, str] = {
    "microsoft": "microsoft.com",
    "google": "google.com",
    "amazon": "amazon.jobs",
    "apple": "apple.com",
    "meta": "meta.com",
    "netflix": "netflix.com",
    "tcs": "tcs.com",
    "tata consultancy services": "tcs.com",
    "infosys": "infosys.com",
    "wipro": "wipro.com",
    "deloitte": "deloitte.com",
    "accenture": "accenture.com",
    "ibm": "ibm.com",
    "salesforce": "salesforce.com",
    "tesla": "tesla.com",
    "oracle": "oracle.com",
    "cisco": "cisco.com",
    "adobe": "adobe.com",
}

# Configurable Salary Benchmarks (Upper reasonable limits by role & currency)
# Values represent max plausible annual salary for entry-level / no-experience
ENTRY_LEVEL_MAX_ANNUAL_SALARY = {
    "USD": {
        "data_entry": 55000,
        "customer_service": 50000,
        "virtual_assistant": 45000,
        "typist": 40000,
        "general": 65000,
    },
    "INR": {
        "data_entry": 400000,       # 4 LPA
        "customer_service": 450000, # 4.5 LPA
        "virtual_assistant": 350000,# 3.5 LPA
        "typist": 300000,          # 3 LPA
        "general": 600000,         # 6 LPA
    },
}
