import sys
import os

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# ==========================================
# 1. Import Dynamic Configuration & Metadata
# ==========================================

# Ensure the backend directory is on the Python path so absolute imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

from config import settings
from db_components.models.base import Base
# IMPORTANT: You MUST import your models here, or Alembic will generate an empty migration!
# Need to declare classes n
import db_components.models

# ==========================================
# Alembic Configuration Setup
# ==========================================
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 2. Point Alembic to your declarative base
target_metadata = Base.metadata

def get_url():
    """Extracts the secure, dynamically generated DB URL from Pydantic."""
    # Convert the SQLAlchemy URL object to a string for Alembic
    return str(settings.get_database_url())

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    # 3. Override the empty ini file config with our dynamic URL
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Ensure Alembic also detects changes to string lengths or Enum types
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
