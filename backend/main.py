"""
MediGuard Backend — FastAPI entry point
"""
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings, validate_production_secrets
from core.database import create_tables
from core.redis_client import init_redis, close_redis

# Import all models so SQLAlchemy sees them before create_all
import models  # noqa: F401

from api.routes import (
    auth,
    profile,
    medications,
    symptoms,
    chat,
    appointments,
    reports,
    dashboard,
    reminders,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — hard-fail early if production secrets are misconfigured
    validate_production_secrets()
    await create_tables()
    await init_redis()
    yield
    # Shutdown
    await close_redis()


app = FastAPI(
    title="MediGuard API",
    description="AI-powered intelligent medication management platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — dev allows localhost; production locks to the actual domain.
# Set CORS_ORIGINS in .env (comma-separated) to override both defaults.
_raw_origins = os.getenv("CORS_ORIGINS", "")
if _raw_origins:
    _allow_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]
elif settings.ENVIRONMENT == "production":
    _allow_origins = ["https://mediguard.app"]
else:
    _allow_origins = ["http://localhost:3000", "http://localhost:3001"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(profile.router, prefix="/api/v1")
app.include_router(medications.router, prefix="/api/v1")
app.include_router(symptoms.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(appointments.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(reminders.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    # Keep internal topology out of unauthenticated responses.
    # Return only what a load-balancer or uptime monitor needs.
    return {"status": "ok", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    import logging

    provider = settings.effective_llm_provider
    db_type = "supabase_postgres" if not settings.is_sqlite else "sqlite"
    storage = "supabase" if settings.is_supabase_configured else "local"

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("mediguard")
    logger.info(f"🚀 MediGuard starting up")
    logger.info(f"   LLM provider : {provider}")
    logger.info(f"   Database     : {db_type}")
    logger.info(f"   Storage      : {storage}")
    logger.info(f"   Environment  : {settings.ENVIRONMENT}")
    logger.info(f"   Debug        : {settings.DEBUG}")
    logger.info(f"   CORS origins : {_allow_origins}")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
