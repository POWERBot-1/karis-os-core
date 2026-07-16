import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.config import config

# Create SQLAlchemy sync engine (can be pointed to PostgreSQL via DATABASE_URL e.g., postgresql://user:pass@localhost/karis_os)
# Defaulting to local sqlite for zero-dependency local workspace verification while fully supporting Postgres syntax via migrations.
DATABASE_URL = os.getenv("DATABASE_URL", config.DATABASE_URL)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI route handlers requiring SQL sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
