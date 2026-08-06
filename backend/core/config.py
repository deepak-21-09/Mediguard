from pydantic_settings import BaseSettings
from typing import Optional

# Known weak/default keys that must never be used in production.
_KNOWN_DEFAULT_KEYS = {
    "change-me-in-production",
    "mediguard-local-dev-secret-key-2025",
    "your-super-secret-jwt-key-change-in-production",
    "",
}


class Settings(BaseSettings):
    # App
    APP_NAME: str = "MediGuard"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # ── Database ──────────────────────────────────────────────────────────────
    # Supabase Postgres (postgresql+asyncpg://...) or SQLite for local dev
    DATABASE_URL: str = "sqlite+aiosqlite:///./mediguard.db"

    # ── Supabase ──────────────────────────────────────────────────────────────
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_STORAGE_BUCKET_PRESCRIPTIONS: str = "prescriptions"
    SUPABASE_STORAGE_BUCKET_REPORTS: str = "reports"

    # ── Redis (optional) ──────────────────────────────────────────────────────
    REDIS_URL: str = ""

    # ── Qdrant (optional) ─────────────────────────────────────────────────────
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "mediguard_memory"
    QDRANT_ENABLED: bool = False

    # ── LLM Provider ─────────────────────────────────────────────────────────
    # Set LLM_PROVIDER to "groq" or "openai"
    LLM_PROVIDER: str = "openai"   # auto-detected if keys are set

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"

    # Groq  (key starts with gsk_)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"   # fast, free-tier available

    @property
    def effective_llm_provider(self) -> str:
        """Auto-detect provider based on which key is set."""
        if self.GROQ_API_KEY and self.GROQ_API_KEY.startswith("gsk_"):
            return "groq"
        if self.OPENAI_API_KEY and self.OPENAI_API_KEY.startswith("sk-"):
            return "openai"
        # Fall back to explicit setting
        return self.LLM_PROVIDER

    # ── Clerk Auth ────────────────────────────────────────────────────────────
    CLERK_SECRET_KEY: str = ""
    CLERK_PUBLISHABLE_KEY: str = ""

    # ── JWT fallback ──────────────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    @property
    def is_secret_key_safe(self) -> bool:
        """True only when SECRET_KEY is a real value (not blank or a known default)."""
        return self.SECRET_KEY.strip() not in _KNOWN_DEFAULT_KEYS

    @property
    def is_supabase_configured(self) -> bool:
        return bool(self.SUPABASE_URL and self.SUPABASE_SERVICE_ROLE_KEY)

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


def validate_production_secrets() -> None:
    """
    Hard-fail at startup if ENVIRONMENT=production and SECRET_KEY is weak.

    Generate a safe key with:
        python -c "import secrets; print(secrets.token_hex(32))"
    Then set SECRET_KEY=<result> in your production .env.
    """
    if settings.ENVIRONMENT != "production":
        return
    if not settings.is_secret_key_safe:
        raise RuntimeError(
            "\n\n"
            "╔══════════════════════════════════════════════════════════════╗\n"
            "║  STARTUP BLOCKED — INSECURE SECRET_KEY IN PRODUCTION        ║\n"
            "╠══════════════════════════════════════════════════════════════╣\n"
            "║  ENVIRONMENT=production requires a strong, random SECRET_KEY ║\n"
            "║  The current value is blank or a known default.              ║\n"
            "║                                                              ║\n"
            "║  Generate a safe key and add it to your production .env:     ║\n"
            "║    python -c \"import secrets; print(secrets.token_hex(32))\" ║\n"
            "║  Then set:  SECRET_KEY=<generated_value>                     ║\n"
            "╚══════════════════════════════════════════════════════════════╝\n"
        )
