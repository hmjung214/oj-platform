from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, create_engine
from alembic import context
from app.db.base import Base
import sys
import os
from dotenv import load_dotenv
from app import models  # ensure all models are loaded

print("=== DEBUG Board in metadata ===")
print(Base.metadata.tables.keys())
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 환경 변수 로딩
load_dotenv()

# SQLAlchemy metadata
from app.models.base import Base
from app import models  # ensure all models are loaded
target_metadata = Base.metadata

# Alembic config
config = context.config

# Logging 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

sync_url = os.getenv("SYNC_DATABASE_URL")

def run_migrations_offline() -> None:
    """오프라인 마이그레이션"""
    context.configure(
        url=sync_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """온라인 마이그레이션"""
    connectable = create_engine(
        sync_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
