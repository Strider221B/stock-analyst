from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings
from constants import Environment

# Create the SQLAlchemy Engine
# This manages the actual connection pool to the PostgreSQL container
engine = create_engine(
    settings.get_database_url(),
    # pool_pre_ping ensures connections aren't stale before using them
    pool_pre_ping=True,
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow,
    echo=(settings.environment == Environment.DEVELOPMENT)
)

# Create a SessionLocal class
# Each instance of this class will be a distinct database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency Injection for database sessions.
    This ensures a database connection is opened when a request starts
    and securely closed when the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
