"""
Database engine — Supabase PostgreSQL (postgresql+asyncpg://).
SQLite is kept as a local dev fallback only; production should always
have DATABASE_URL set to the Supabase transaction-pooler URL.
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from core.config import settings

logger = logging.getLogger("mediguard.db")


def _build_engine():
    if settings.is_sqlite:
        logger.warning(
            "⚠️  Using SQLite fallback — set DATABASE_URL to your Supabase "
            "postgresql+asyncpg:// connection string for production."
        )
        # aiosqlite needed only for local dev
        return create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            connect_args={"check_same_thread": False},
        )
    else:
        logger.info("✅  Using Supabase PostgreSQL")
        return create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            pool_recycle=300,       # recycle every 5 min — important for Supabase pooler
            pool_timeout=30,
            connect_args={
                "server_settings": {"application_name": "mediguard"},
                "statement_cache_size": 0,  # required for pgBouncer / Supabase pooler
            },
        )


engine = _build_engine()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """
    Create all SQLAlchemy-managed tables in Supabase (CREATE TABLE IF NOT EXISTS).
    Safe to call on every startup — idempotent.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅  Database tables verified / created.")
