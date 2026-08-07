"""
Alembic environment configuration.

DATABASE_URL is read from the environment (via core.config.settings) so that
secrets never have to be committed to alembic.ini.

For offline / local generation run:
    alembic revision --autogenerate -m "initial_schema"

To apply to Supabase:
    alembic upgrade head
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ---------------------------------------------------------------------------
# Make sure the backend package is importable when running alembic from the
# backend/ directory.
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import settings so we can pull DATABASE_URL at runtime.
from core.config import settings  # noqa: E402

# Import every model so that Base.metadata is fully populated before
# autogenerate / compare_metadata runs.
import models  # noqa: E402, F401  (side-effect import)
from core.database import Base  # noqa: E402

# ---------------------------------------------------------------------------
# Alembic Config object — gives access to values in alembic.ini
# ---------------------------------------------------------------------------
config = context.config

# Wire up Python logging from the [loggers] section in alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override sqlalchemy.url with the real DATABASE_URL from the environment.
# asyncpg URLs must be rewritten to the synchronous psycopg2 dialect for
# Alembic (Alembic uses synchronous SQLAlchemy under the hood).
_db_url = settings.DATABASE_URL
if _db_url.startswith("postgresql+asyncpg://"):
    _db_url = _db_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
elif _db_url.startswith("sqlite+aiosqlite://"):
    _db_url = _db_url.replace("sqlite+aiosqlite://", "sqlite://", 1)

config.set_main_option("sqlalchemy.url", _db_url)

target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Offline migration (--sql flag / no live DB connection required)
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Generate SQL script without a live database connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online migration (live DB connection)
# ---------------------------------------------------------------------------
def run_migrations_online() -> None:
    """Apply migrations against a live database."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
