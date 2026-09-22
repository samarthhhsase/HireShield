# HireShield — AI-Powered Candidate Risk Intelligence Platform



> **"Hire with confidence. Detect recruitment fraud and employment scams before they strike."**

HireShield is an enterprise-grade AI risk intelligence platform engineered to evaluate recruitment postings, job offer vectors, and candidate references. By combining multimodal behavioral heuristics, linguistic urgency detection, network security telemetry, and an explainable risk calculation engine, HireShield detects employment fraud, advance-fee scams, credential harvesting fronts, and impersonation campaigns in real time.

---

## Complete Project Structure

```
Hireshield/
├── .gitignore                                # Git ignore configurations
├── conftest.py                               # Pytest configuration and shared fixtures
├── hireshield.db                             # SQLite persistent database (candidates, users, scans)
├── naukri_raw.html                           # Sample recruitment HTML fixture for offline testing
├── requirements.txt                          # Python dependencies specification
├── test_naukri.py                            # Standalone test runner for job parsing verification
├── README.md                                 # Comprehensive platform documentation & architectural guide
│
├── app/                                      # Main FastAPI Backend Application
│   ├── __init__.py                           # Python package initialization
│   ├── database.py                           # Legacy database session compatibility bridge
│   ├── main.py                               # FastAPI application entry point, middleware, routes, lifespans
│   │
│   ├── api/                                  # API Router Controllers
│   │   ├── __init__.py                       # Package initializer
│   │   ├── auth.py                           # Authentication routes (register, login, me)
│   │   ├── candidates.py                     # Candidate & job dossier persistence CRUD endpoints
│   │   └── risk.py                           # Risk calculation and fallback analysis routes
│   │
│   ├── db/                                   # Database Engine & Session Management
│   │   ├── __init__.py                       # Package initializer
│   │   └── database.py                       # SQLAlchemy engine, session maker, Base declarative model
│   │
│   ├── models/                               # SQLAlchemy Database Models
│   │   ├── __init__.py                       # Package initializer
│   │   ├── candidate.py                      # Candidate and Scan event ORM definitions
│   │   └── user.py                           # Security analyst user ORM model
│   │
│   ├── risk_engine/                          # Modular Sub-Engine Scoring & Rule Heuristics
│   │   ├── __init__.py                       # Package initializer
│   │   ├── confidence.py                     # Algorithmic confidence scoring for assessments
│   │   ├── explanations.py                   # Plain-English security audit explanations & rationale
│   │   ├── risk_config.py                    # Risk weights, severity thresholds, penalty parameters
│   │   ├── risk_engine.py                    # Core multi-layer risk synthesizer & critical overrides
│   │   ├── scoring.py                        # Score normalization and tier classification
│   │   │
│   │   ├── company/                          # Company Validation Modules
│   │   │   ├── __init__.py                   # Package initializer
│   │   │   ├── careers_check.py              # Official career portal existence checker
│   │   │   └── verifier.py                   # Corporate registry and legitimate entity verification
│   │   │
│   │   ├── domain/                           # Layer A Infrastructure & Network Analysis
│   │   │   ├── __init__.py                   # Package initializer
│   │   │   ├── analyzer.py                   # Unified domain risk analyzer
│   │   │   ├── dns.py                        # DNS records resolution & MX validation
│   │   │   ├── reputation.py                 # Domain reputation & blacklist checks
│   │   │   ├── ssl.py                        # SSL/TLS certificate validity & issuer verification
│   │   │   └── whois.py                      # WHOIS registration age & registrar analysis
│   │   │
│   │   ├── impersonation/                    # Brand & Identity Spoofing Detection
│   │   │   ├── __init__.py                   # Package initializer
│   │   │   └── detector.py                   # Typo-squatting, lookalike domains, brand spoofing
│   │   │
│   │   ├── nlp/                              # Layer B Linguistic & Content NLP Heuristics
│   │   │   ├── __init__.py                   # Package initializer
│   │   │   ├── analyzer.py                   # Master NLP text scanner and keyword pipeline
│   │   │   ├── credential_detection.py       # PII / sensitive identity document harvesting checks
│   │   │   ├── payment_detection.py          # Advance fees, deposits, processing charge alerts
│   │   │   ├── scam_patterns.py              # Known employment scam phrase dictionaries
│   │   │   └── urgency.py                    # Artificial urgency & pressure language detection
│   │   │
│   │   ├── recruiter/                        # Recruiter Identity Screening
│   │   │   ├── __init__.py                   # Package initializer
│   │   │   └── analyzer.py                   # Recruiter email domain, contact channels, anonymity
│   │   │
│   │   └── salary/                           # Compensation Anomaly Detection
│   │       ├── __init__.py                   # Package initializer
│   │       └── analyzer.py                   # Unrealistic salary guarantees & wage anomaly heuristics
│   │
│   ├── schemas/                              # Pydantic Request & Response Data Schemas
│   │   ├── __init__.py                       # Package initializer
│   │   ├── auth.py                           # Auth request/response models & token schemas
│   │   └── candidate.py                      # Candidate dossier schemas & scan payload validation
│   │
│   └── services/                             # Core Business Logic & External Integrations
│       ├── __init__.py                       # Package initializer
│       ├── ai_client.py                      # NLP parser, heuristic extraction, green/red flag generator
│       ├── auth_service.py                   # Password hashing (SHA-256 + salt), JWT tokens, seeding
│       ├── candidate_service.py              # DB operations for dossiers, scan persistence, seed records
│       ├── risk_engine.py                    # Multi-layer score aggregator and verdict classifier
│       ├── scraper.py                        # HTTPX page fetcher, WAF/403 classifier, HTML extractor
│       └── technical.py                      # Network socket, SSL handshake, DNS, domain age engine
│
├── frontend/                                 # Enterprise React + Vite Single Page Application
│   ├── index.html                            # Application HTML template
│   ├── package.json                          # Node.js dependencies & build scripts
│   ├── postcss.config.js                     # PostCSS configuration for Tailwind CSS
│   ├── tailwind.config.js                    # Custom dark cyber-security theme design tokens
│   ├── vite.config.js                        # Vite bundler configuration & local dev server setup
│   │
│   ├── public/                               # Static public web assets
│   │
│   └── src/                                  # Frontend Application Source Code
│       ├── App.jsx                           # Root application component & protected route hierarchy
│       ├── index.css                         # Global CSS styles, Tailwind layers, glassmorphism utilities
│       ├── main.jsx                          # React DOM application mounting point
│       │
│       ├── api/                              # Backend HTTP Client & API Integrations
│       │   ├── analysis.js                   # Live threat scan & browser fallback API calls
│       │   ├── auth.js                       # JWT authentication, login/signup API, session storage
│       │   ├── candidates.js                 # Candidate dossier API & offline fallback mock store
│       │   └── client.js                     # Centralized Axios instance with latency tracking
│       │
│       ├── components/                       # Reusable Cyber-Security UI Components
│       │   ├── CandidateCard/
│       │   │   └── CandidateCard.jsx         # Card view for candidate dossiers with risk badges
│       │   ├── CandidateTable/
│       │   │   └── CandidateTable.jsx        # Tabular data grid with filtering and sort options
│       │   ├── Common/
│       │   │   ├── BackendStatusBadge.jsx    # Real-time backend liveness and latency indicator
│       │   │   ├── MissingEndpointBadge.jsx  # Graceful UI fallback for offline microservices
│       │   │   └── ProtectedRoute.jsx        # Route guard ensuring valid security analyst tokens
│       │   ├── Navbar/
│       │   │   └── Navbar.jsx                # Top global navigation bar with analyst profile & status
│       │   ├── RiskAnalysis/
│       │   │   ├── AITerminal.jsx            # Live scanning terminal stream with syntax coloration
│       │   │   ├── BrowserFallbackModal.jsx  # Interactive modal for submitting WAF-blocked job text
│       │   │   ├── GreenFlagsList.jsx        # Legitimacy trust indicators and positive signals
│       │   │   ├── RedFlagsList.jsx          # Threat alert list categorized by severity
│       │   │   ├── TechnicalChecks.jsx       # Layer A network telemetry cards (SSL, DNS, WHOIS)
│       │   │   └── VerificationAudit.jsx     # Deep audit breakdown explaining why job is real or fake
│       │   ├── RiskBreakdown/
│       │   │   └── RiskBreakdownBars.jsx     # 4-tier horizontal risk factor contribution bars
│       │   ├── RiskScore/
│       │   │   └── RadialScoreGauge.jsx      # Animated SVG circular risk gauge (0 to 100)
│       │   ├── ShieldAnimation/
│       │   │   └── ShieldHero.jsx            # Interactive cyber-shield hero visualizer with scanning laser
│       │   └── Sidebar/
│       │       └── Sidebar.jsx               # Workspace sidebar navigation with active route highlights
│       │
│       ├── layouts/                          # Page Wrapper Layouts
│       │   ├── DashboardLayout.jsx           # Authenticated layout with sidebar, navbar, and status
│       │   └── PublicLayout.jsx              # Unauthenticated layout for marketing and landing pages
│       │
│       ├── pages/                            # Top-Level Workspace Views
│       │   ├── Activity.jsx                  # Security audit logs & engine event activity stream
│       │   ├── CandidateDetails.jsx          # Individual candidate/job dossier deep-dive view
│       │   ├── Candidates.jsx                # Candidate & target job intelligence registry
│       │   ├── Dashboard.jsx                 # Executive threat dashboard with KPIs and trend analytics
│       │   ├── Landing.jsx                   # Public marketing landing page with interactive scanner
│       │   ├── Login.jsx                     # Security analyst sign-in with 1-click demo access
│       │   ├── Register.jsx                  # Alias registration view
│       │   ├── Reports.jsx                   # Security Intelligence Reports with PDF download
│       │   ├── RiskAnalysis.jsx              # Main threat analysis workbench with live scan & fallback
│       │   └── Signup.jsx                    # Enterprise analyst registration portal
│       │
│       └── utils/                            # Frontend Utility Functions
│           └── generatePdfReport.js          # jsPDF + jspdf-autotable client-side PDF dossier generator
│
├── hireshield extension/                     # Chrome Extension (Manifest V3)
│   ├── background.js                         # Service worker for background extension lifecycle
│   ├── content.js                            # In-page DOM text extraction and scam indicator highlighting
│   ├── manifest.json                         # Extension Manifest V3 configuration and permissions
│   ├── popup.css                             # Cyber-security dark theme styling for extension popup
│   ├── popup.html                            # Popup interface layout for in-browser threat scanner
│   ├── popup.js                              # Extension popup controller, sync with webapp backend
│   └── icons/                                # Extension icons in standard resolutions (16, 48, 128px)
│
├── tests/                                    # Automated Test Suite (Pytest)
│   ├── test_auth_api.py                      # Authentication endpoints & JWT token verification
│   ├── test_auth_production.py               # Password hashing, salting, and user persistence
│   ├── test_browser_fallback.py              # WAF fallback ingestion and Layer B synthesis tests
│   ├── test_candidates_api.py                # Candidate persistence CRUD API tests
│   ├── test_extension_to_webapp_sync.py      # Chrome extension to backend synchronization tests
│   ├── test_fake_vs_real_detection.py        # Benchmark tests distinguishing real jobs from scams
│   ├── test_hybrid_risk_engine.py            # Multi-layer score weighting and override rules
│   ├── test_risk_engine.py                   # Baseline unit tests for the core risk engine
│   └── test_scanner_fetch_statuses.py        # HTTP status handling (403, 404, 429, timeout, network)
│
└── backend/                                  # Microservice Backend Variant (Independent Module)
    ├── .env                                  # Environment variables
    ├── requirements.txt                      # Requirements for standalone microservice variant
    ├── hireshield.db                         # Local SQLite database
    ├── app/                                  # Core app modules for standalone microservice
    └── tests/                                # Tests for backend module
```

---

## Architecture & Detection Pipeline

```
┌────────────────────────────────────────────────────────────────────────┐
│                   User Target Input (URL or Text)                      │
│      (Web Application Scanner / Chrome Extension / REST Client)        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                  HTTP POST /api/scan or /api/scan/content
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                       FastAPI Application Gateway                      │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
    ┌───────────────▼───────────────┐┌───────────────▼───────────────┐
    │  Layer A: Infrastructure      ││  Layer B: Content Heuristics  │
    │  (Network Security Engine)    ││  (NLP Threat Analyzer)        │
    ├───────────────────────────────┤├───────────────────────────────┤
    │ • Domain Age & WHOIS History  ││ • Upfront Fee / Deposit Alerts│
    │ • SSL / TLS Handshake Validity││ • Sensitive PII Harvesting    │
    │ • DNS A-Record & MX Validation││ • Pressure / Urgency Language │
    │ • Redirect Hop Counting       ││ • Telegram / WhatsApp Channels│
    │ • Typo-Squatting / Lookalikes ││ • Wage Guarantee Anomalies    │
    └───────────────┬───────────────┘└───────────────┬───────────────┘
                    │                                │
                    └───────────────┬────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                    Hybrid Risk Calculation Engine                      │
│                                                                        │
│   Weighted Base Formula:                                               │
│   Score = (0.40 * Behavioral) + (0.25 * Linguistic) +                  │
│           (0.20 * Structural) + (0.15 * Technical)                     │
│                                                                        │
│   Critical Safety Overrides:                                           │
│   • Advance Fee + Sensitive ID harvesting       => Force CRITICAL (>=85)│
│   • Unreachable DNS or Invalid SSL              => Elevate Risk Tier   │
│   • Remote Server WAF Block (HTTP 403)          => Zero Penalty Applied│
│     (Preserves Layer A, requests Layer B fallback)                     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                      Persistence & Reporting Layer                     │
│  • SQLite Storage: Automatic candidate dossier & scan event saving     │
│  • Client PDF Generator: Executive intelligence audit dossier export   │
│  • Security Verdicts: VERIFIED LEGITIMATE, SUSPICIOUS, CONFIRMED SCAM  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Core Capabilities & Features

### 1. Dual-Layer Threat Scanner
- **Layer A (Technical & Infrastructure)**: Evaluates network hygiene, protocol security (HTTPS), SSL certificate validity, domain registration age, DNS resolution, and redirect hops.
- **Layer B (Content & Heuristic NLP)**: Evaluates job spec vocabulary for upfront fee demands, requests for sensitive identification (Aadhaar, SSN, bank accounts), artificial deadline urgency, and informal recruitment channels (Telegram, WhatsApp).

### 2. Smart WAF / HTTP 403 Fallback Protection
- Protected career portals (such as Apple Careers, Workday, or Cloudflare-shielded corporate domains) often block server-side HTTP scrapers with HTTP 403 or 429.
- HireShield detects this access restriction, **applies zero fraud penalty** (since blocking scrapers is standard corporate security), preserves Layer A network checks, and provides an **interactive fallback modal** to submit the visible page text for instant Layer B heuristic synthesis.

### 3. Executive Security Reports & PDF Export
- Generate and download publication-quality PDF audit reports from:
  - The **Security Intelligence Reports** gallery (`/reports`)
  - The **Risk Analysis** page (`/risk-analysis`) upon scanning any job
  - The **Candidate Dossier** page (`/jobs/:id`)
- Built client-side using `jspdf` and `jspdf-autotable`, featuring risk gauge summaries, telemetry metrics, threat flag breakdowns, and candidate diligence advice.

### 4. Candidate Dossier Registry
- Persistent storage of evaluated job vectors and candidate profiles in SQLite.
- Search, filter by threat severity (LOW, MEDIUM, HIGH, CRITICAL), inspect detailed behavioral flags, and re-run live scans.

### 5. Analyst Authentication & Session Security
- SHA-256 password hashing with individual salt generation.
- JWT Bearer token authentication and route guarding for sensitive SecOps workspaces.
- One-click demo analyst login for fast evaluation.

### 6. Chrome Browser Extension (Manifest V3)
- Inspect job postings directly inside Chrome or Edge.
- Extracts DOM content, queries the HireShield backend, and displays instant threat scores in a cyber-security popup.

---

## Technology Stack Summary

| Domain | Technology | Description |
| :--- | :--- | :--- |
| **Frontend Framework** | React 18.3 + Vite 5.4 | High-performance single page application |
| **Routing** | React Router DOM 6.28 | Client-side routing with protected route guards |
| **Styling** | Tailwind CSS 3.4 | Custom cyber-security dark theme palette |
| **Icons** | Lucide React | Clean, scalable interface icons |
| **Data Visualization** | Recharts & SVG Gauges | Radial gauges, bar breakdowns, telemetry charts |
| **PDF Generation** | jsPDF 2.5 + jspdf-autotable 3.8 | Client-side executive security audit PDF exports |
| **HTTP Client** | Axios 1.7 | Centralized API client with latency measurement |
| **Backend Framework** | FastAPI 0.115+ | High-throughput asynchronous Python REST API |
| **ASGI Server** | Uvicorn 0.32+ | Production-ready ASGI server |
| **Database** | SQLite + SQLAlchemy 2.0 | Lightweight, persistent relational storage |
| **Scraper** | HTTPX + BeautifulSoup4 | Asynchronous web scraping and HTML parsing |
| **Network & Security** | Python socket, ssl, dnspython | Low-level SSL handshake and DNS inspection |
| **Browser Extension** | Manifest V3 | Chrome/Edge extension for in-browser evaluation |
| **Testing** | Pytest | Comprehensive test suite for APIs and risk engines |

---

## Quick Start Guide

### Prerequisites
- **Python**: 3.10, 3.11, 3.12, 3.13, or 3.14
- **Node.js**: v18+ or v20+ LTS (npm 9+)
- **OS**: Windows, macOS, or Linux

---

### Step 1: Clone and Set Up the Backend

1. Open your terminal in the project root (`d:\Hireshield`):
```powershell
# Create and activate a virtual environment (optional but recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1   # On Windows
# source venv/bin/activate     # On macOS/Linux

# Install backend dependencies
pip install -r requirements.txt
```

2. Start the FastAPI backend server on port 8001:
```powershell
python -m uvicorn app.main:app --reload --port 8001
```

3. Verify backend connectivity:
- **API Status**: [http://127.0.0.1:8001/](http://127.0.0.1:8001/)
- **Health Check**: [http://127.0.0.1:8001/health](http://127.0.0.1:8001/health)
- **Interactive Swagger Documentation**: [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)

---

### Step 2: Set Up and Run the Frontend

1. In a second terminal window, navigate to the `frontend` folder:
```powershell
cd frontend
npm install
```

2. Start the Vite development server:
```powershell
npm run dev
```

3. Open the web application in your browser:
**[http://localhost:5173/](http://localhost:5173/)**

---

### Step 3: Default Security Analyst Credentials

To access protected workspace routes, log in with the seeded analyst account:
- **Email**: `analyst@hireshield.ai`
- **Password**: `Password123!`

*(Or simply click the **"Fill Analyst Credentials"** demo button on the login screen).*

---

### Step 4: Loading the Chrome Extension (Optional)

1. Open Google Chrome or Microsoft Edge and navigate to `chrome://extensions/`.
2. Enable **Developer mode** (toggle in the top-right corner).
3. Click **Load unpacked** and select the folder:
   `d:\Hireshield\hireshield extension`
4. The HireShield Shield icon will appear in your browser toolbar, connected to your local backend.

---

## API Reference & Endpoints

### 1. Threat Scanner Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/scan` | Execute real-time Layer A network & Layer B NLP extraction against a URL |
| `POST` | `/api/scanner/analyze-content` | Analyze browser-supplied job text (WAF fallback handler) |
| `POST` | `/api/risk/analyze` | Direct risk engine analysis on provided scores and flag lists |

#### Sample `/api/scan` Payload:
```json
{
  "url": "https://example-careers.io/positions/software-engineer"
}
```

#### Sample Response:
```json
{
  "id": "HS-2026-00421",
  "url": "https://example-careers.io/positions/software-engineer",
  "final_url": "https://example-careers.io/positions/software-engineer",
  "fetch_status": "FETCH_SUCCESS",
  "content_analyzed": true,
  "job": {
    "title": "Senior Distributed Systems Architect",
    "company": "Example Careers",
    "text_preview": "Extracted text content..."
  },
  "risk_score": 11,
  "risk_level": "LOW",
  "verdict": "VERIFIED_LEGITIMATE",
  "fake_job_probability": 11,
  "scores": {
    "behavioral": 12,
    "linguistic": 8,
    "structural": 10,
    "technical": 15
  },
  "technical_checks": {
    "ssl_valid": true,
    "domain_age_days": 1420,
    "dns_exists": true,
    "ip": "198.51.100.42",
    "redirect_count": 0
  },
  "red_flags": [],
  "green_flags": [
    "Valid SSL/TLS certificate issued by trusted CA",
    "Well-established domain registration (>3 years)"
  ]
}
```

---

### 2. Candidate & Job Dossier Persistence Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/candidates` | List all saved candidate dossiers with threat level filtering |
| `GET` | `/api/candidates/{id}` | Retrieve single dossier by unique reference ID |
| `POST` | `/api/candidates` | Manually persist a new candidate/job record |
| `DELETE` | `/api/candidates/{id}` | Delete a dossier from persistent storage |

---

### 3. Authentication Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Register a new security analyst with salted password hashing |
| `POST` | `/api/auth/login` | Authenticate analyst and obtain signed JWT access token |
| `GET` | `/api/auth/me` | Retrieve profile of the currently authenticated analyst |

---

### 4. Health & Service Metadata

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Service identification, version, and route directory |
| `GET` | `/health` | Liveness health probe for uptime monitors |

---

## Running Automated Tests

HireShield includes a comprehensive pytest suite covering authentication, risk engines, WAF fallbacks, and real vs. fake job heuristics:

```powershell
# Run all automated tests
pytest tests/ -v

# Run specific test suites
pytest tests/test_hybrid_risk_engine.py -v
pytest tests/test_fake_vs_real_detection.py -v
pytest tests/test_browser_fallback.py -v
pytest tests/test_auth_api.py -v
```

---

## License & Security Advisory

HireShield is built for proactive recruitment threat detection, employment scam identification, and candidate vetting. When conducting risk assessments, always adhere to local regulations and utilize the tool to evaluate publicly accessible listings or authorized candidate submissions.
