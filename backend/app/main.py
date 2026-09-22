import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.db.init_db import init_db
from app.api.health import router as health_router
from app.api.candidates import router as candidates_router
from app.api.analysis import router as analysis_router
from app.api.dashboard import router as dashboard_router
from app.api.auth import router as auth_router
from app.services.auth_service import seed_default_analyst
from app.db.session import SessionLocal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("hireshield")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("==================================================")
    logger.info("HireShield Backend starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API Prefix: {settings.API_PREFIX}")
    logger.info(f"Allowed CORS Origins: {settings.cors_origins}")
    
    # Initialize database tables cleanly via db layer
    if settings.DATABASE_URL:
        logger.info(f"Database configured: {settings.DATABASE_URL.split('://')[0]}")
        init_db()
        if SessionLocal:
            with SessionLocal() as db:
                seed_default_analyst(db)
    else:
        logger.info("Database: InMemory fallback mode.")
    logger.info("==================================================")
    yield
    logger.info("HireShield Backend shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered hiring risk intelligence and candidate analysis platform backend.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# -------------------------------------------------------------
# CORS Middleware
# -------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------
# Global Clean Error Handlers
# -------------------------------------------------------------
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error.get("loc", []))
        errors.append({
            "field": field,
            "message": error.get("msg", "Invalid field"),
            "type": error.get("type", "value_error"),
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "status_code": 422,
            "message": "Input validation failed. Please inspect the request payload.",
            "details": errors,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "status_code": 500,
            "message": "An internal server error occurred while processing the request.",
        },
    )


# -------------------------------------------------------------
# Register Routers under /api
# -------------------------------------------------------------
app.include_router(health_router, prefix=settings.API_PREFIX)
app.include_router(candidates_router, prefix=settings.API_PREFIX)
app.include_router(analysis_router, prefix=settings.API_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_PREFIX)
app.include_router(auth_router, prefix=settings.API_PREFIX)

# Also expose direct /api/health and root info
@app.get("/", tags=["General"])
def root_info():
    return {
        "name": settings.APP_NAME,
        "status": "running",
        "docs_url": "/docs",
        "api_prefix": settings.API_PREFIX,
    }
