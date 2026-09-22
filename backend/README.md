# HireShield Backend Service

> **AI-Powered Hiring Risk Intelligence & Threat Evaluation Platform**

The HireShield backend is a modular, production-ready RESTful service built with **FastAPI** and **Python 3.x**. It provides comprehensive candidate risk assessment, deterministic signal scoring, lexical NLP pattern detection, and technical qualification auditing.

The backend is architected with a strict repository abstraction pattern: currently running with an in-memory development repository, with complete SQLAlchemy models and schema design ready for upcoming PostgreSQL database integration.

---

## 1. Technology Stack

* **Language**: Python 3.10+ (Tested on Python 3.14)
* **Framework**: FastAPI
* **ASGI Server**: Uvicorn
* **Data Validation & Settings**: Pydantic v2 & Pydantic Settings
* **ORM & Database Ready**: SQLAlchemy 2.0 (Declarative Base & Models)
* **Database Migrations Ready**: Alembic
* **Configuration**: python-dotenv & Pydantic Settings
* **Testing**: pytest & HTTPX TestClient

---

## 2. Architecture & Design Principles

The backend enforces a clean 3-tier decoupling:

```text
       HTTP Client (React / cURL / Swagger)
                     │
                     ▼
           [API Routing Layer]
     (app/api/candidates, analysis, dashboard)
                     │
                     ▼
        [Business & Service Layer]
   (Risk Engine, NLP Service, Technical Analysis)
                     │
                     ▼
           [Data Access Layer]
      (Repository Interface / Abstract Base)
           ╱                         ╲
          ▼                           ▼
[InMemory Repository]      [SQLAlchemy Repository]
    (Active Prototype)        (Future: PostgreSQL)
```

1. **No Direct Route-to-Storage coupling**: API routes communicate solely through repository interfaces and orchestration services.
2. **Deterministic Risk Engine**: Explainable, mathematical scoring based on explicit weights and severities without ungrounded black-box claims.
3. **Database-Ready Isolation**: Adding PostgreSQL requires zero changes to the API schemas, route handlers, or business logic.

---

## 3. Directory Structure

```text
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py             # Health check endpoint (/api/health)
│   │   ├── candidates.py         # Candidate CRUD routes (/api/candidates)
│   │   ├── analysis.py           # Analysis orchestration routes (/api/analysis)
│   │   └── dashboard.py          # Dashboard analytics routes (/api/dashboard)
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # Pydantic Settings & environment variables
│   │   └── security.py           # Input sanitization and safety utilities
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py               # SQLAlchemy DeclarativeBase
│   │   ├── database.py           # Engine & connection initialization
│   │   ├── session.py            # Session factory & FastAPI dependency
│   │   └── repository.py         # Repository pattern (InMemory & Base contracts)
│   │
│   ├── models/
│   │   ├── __init__.py           # Model exports
│   │   ├── candidate.py          # SQLAlchemy Candidate table model
│   │   ├── analysis.py           # SQLAlchemy Analysis table model
│   │   └── risk_signal.py        # SQLAlchemy RiskSignal table model
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── candidate.py          # Pydantic request/response schemas
│   │   ├── risk.py               # RiskSignal, RiskAssessment, Enums
│   │   ├── analysis.py           # AnalysisResponse schema
│   │   └── dashboard.py          # Metrics & distribution schemas
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── risk_engine.py        # Deterministic weighted scoring engine
│   │   ├── nlp_service.py        # Lexical pattern & solicitation detector
│   │   ├── technical_analysis.py # Skill gap & experience verification
│   │   └── analysis_orchestrator.py # Multi-stage pipeline coordinator
│   │
│   └── main.py                   # Application factory, CORS, exception handlers
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # TestClient & repository isolation fixtures
│   ├── test_health.py            # Health endpoint test
│   ├── test_candidates.py        # Candidate CRUD & validation tests
│   ├── test_risk_engine.py       # Deterministic scoring & threshold tests
│   └── test_analysis.py          # End-to-end workflow & dashboard tests
│
├── .env.example                  # Environment configuration template
├── requirements.txt              # Production & development dependencies
└── README.md                     # Backend documentation
```

---

## 4. Getting Started (Local Setup)

### Prerequisites
* Python 3.10 or higher (Python 3.14 supported)
* `git`

### 1. Clone & Navigate to Backend
```powershell
cd backend
```

### 2. Create Virtual Environment
```powershell
python -m venv venv
```

### 3. Activate Virtual Environment
**Windows (PowerShell / Command Prompt):**
```powershell
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. Environment Configuration
Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```

Default `.env` contents:
```env
APP_NAME="HireShield Backend"
ENVIRONMENT="development"
FRONTEND_URL="http://localhost:5173"
DATABASE_URL="sqlite:///./hireshield.db"
```

---

## 5. Running the Backend Server

Start the Uvicorn development server:

```powershell
python -m uvicorn app.main:app --reload --port 8001
```

The server will be available at:
* **API Base URL**: `http://127.0.0.1:8001/api`
* **Health Check**: `http://127.0.0.1:8001/api/health`
* **Interactive OpenAPI Swagger Docs**: `http://127.0.0.1:8001/docs`
* **Alternative Redoc Documentation**: `http://127.0.0.1:8001/redoc`

On initial launch, SQLite database tables (`candidates`, `analyses`, `risk_signals`) are automatically verified and initialized in `hireshield.db`.

---

## 6. API Reference

All routes are mounted under the `/api` prefix.

### Health
| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Returns service health status and application metadata. |

### Candidates
| Method | Path | Description |
| :--- | :--- | :--- |
| `POST` | `/api/candidates` | Create a new candidate profile with validation. |
| `GET` | `/api/candidates` | Paginated listing of candidate profiles (`skip`, `limit`). |
| `GET` | `/api/candidates/{id}` | Retrieve candidate profile by unique identifier. |
| `PUT` | `/api/candidates/{id}` | Update candidate details (partial update supported). |
| `DELETE` | `/api/candidates/{id}` | Delete a candidate and cascade-delete associated analyses. |

### Analysis
| Method | Path | Description |
| :--- | :--- | :--- |
| `POST` | `/api/analysis/{candidate_id}` | Run full multi-stage risk analysis on a candidate. |
| `GET` | `/api/analysis/{analysis_id}` | Retrieve existing analysis record by analysis ID. |
| `GET` | `/api/analysis/candidate/{candidate_id}` | Retrieve all historical analyses for a specific candidate. |

### Dashboard
| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/api/dashboard/summary` | Summary counters (candidates, analyses, high-risk, avg score). |
| `GET` | `/api/dashboard/risk-distribution`| Risk breakdown by category tiers (LOW, MEDIUM, HIGH, CRITICAL). |
| `GET` | `/api/dashboard/recent` | Recent candidate analyses feed (`limit`). |

---

## 7. Risk Intelligence Engine

The Risk Engine (`app/services/risk_engine.py`) receives a collection of discrete, structured risk signals and computes a normalized score between **0 and 100**:

$$\text{Risk Score} = \text{round}\left( \frac{\sum (\text{severity}_i \times \text{weight}_i)}{\sum \text{weight}_i} \right)$$

### Risk Tiers
* **0–24**: `LOW` (Standard profile, minimal to no risk flags)
* **25–49**: `MEDIUM` (Minor inconsistencies or experience/skill discrepancies)
* **50–74**: `HIGH` (Significant skill gaps, unusual claims, or high-risk language)
* **75–100**: `CRITICAL` (Advance fee demands, credential solicitation, extreme claims)

### Explainability
The engine synthesizes an unambiguous explanation outlining the primary risk drivers ranked by severity and weight, alongside a categorical score breakdown (`RESUME`, `NLP`, `TECHNICAL`, `VERIFICATION`, `CONSISTENCY`).

---

## 8. NLP & Technical Analysis Services

### NLP Service (`app/services/nlp_service.py`)
Deterministic lexical analyzer scanning resume text, cover letters, and notes for:
* **Financial & Credential Solicitation**: Upfront fees, security deposits, OTP, bank account requests.
* **Unrealistic Guarantee Language**: 100% job placement guarantees, guaranteed offer letters, instant hiring claims.
* **High-Urgency & Pressure Phrasing**: Immediate payment demands, limited-time registration deadlines.
* **Unprofessional Communication Vectors**: Telegram/WhatsApp-only interview directives without official corporate correspondence.

### Technical Analysis Service (`app/services/technical_analysis.py`)
Validates technical attributes against the target job description:
* **Missing Required Skills**: Compares extracted/stated candidate skills against required keywords in the job description.
* **Seniority Inconsistency**: Compares declared experience years with senior job titles (e.g., "Senior Architect" claimed with < 3 years of experience).

---

## 9. Database Architecture & Persistence

### Current State (SQLite + SQLAlchemy)
* **Active Storage Engine**: SQLite file database at `backend/hireshield.db`.
* **ORM Implementation**: SQLAlchemy 2.0 declarative models (`Candidate`, `Analysis`, `RiskSignalModel`) located in `app/models/`.
* **Repository Layer**: `SQLAlchemyCandidateRepository` and `SQLAlchemyAnalysisRepository` in `app/db/repository.py` provide clean persistence and separation of concerns.
* **Automatic Table Creation**: Handled cleanly via `app/db/init_db.py` during FastAPI application lifespan startup.

### Transitioning to PostgreSQL (Future Production)
Because all database queries run through SQLAlchemy ORM and repository abstractions, migrating to PostgreSQL requires zero changes to API routes or business logic:
1. Start PostgreSQL:
   ```sql
   CREATE DATABASE hireshield;
   ```
2. Update the connection string in `backend/.env`:
   ```env
   DATABASE_URL=postgresql://postgres:password@localhost:5432/hireshield
   ```
3. Run Alembic migrations or startup table generation.

---

## 10. Running Tests

Run the complete test suite with verbose output:

```powershell
python -m pytest tests -v
```

All 19 unit and integration tests execute cleanly in isolated environments:
* `tests/test_health.py`: Healthcheck API contract.
* `tests/test_candidates.py`: Candidate creation, duplicate email rejection, validation errors, listing, and deletion.
* `tests/test_risk_engine.py`: Empty signals, low/medium/high/critical risk tiers, and multiple signal aggregation.
* `tests/test_analysis.py`: Clean candidates, flagged candidates, 404 handling, and dashboard analytics.
* `tests/test_sqlite_persistence.py`: SQLite engine verification, candidate cross-session persistence, analysis and child risk signals relational storage.

---

## 11. Current Limitations

* **Single-Node SQLite Concurrency**: SQLite is optimized for local development and single-instance deployments. For high-concurrency production or multi-replica clustering, PostgreSQL should be configured.
* **Lexical NLP Heuristics**: The current NLP service uses deterministic keyword and regex heuristics. External LLMs and vector embeddings can be added in future iterations.
