from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from config import settings
from constants import Environment

# Create the SQLAlchemy Engine
# This manages the actual connection pool to the PostgreSQL container

connect_args = {}
if settings.environment == Environment.PRODUCTION:
    connect_args = {"sslmode": "require"}

engine = create_engine(
    settings.get_database_url(),
    # pool_pre_ping ensures connections aren't stale before using them
    pool_pre_ping=True,
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow,
    connect_args=connect_args,
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

def set_tenant_context(session, user_id: str):
    """
    Safely sets the Postgres session variable using parameterized binding
    to prevent SQL injection. The 'true' argument scopes it to the transaction.
    """
    session.execute(
        text("SELECT set_config('app.current_user_id', :user_id, true)"),
        {"user_id": str(user_id)}
    )

@event.listens_for(Engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """
    Runs when a connection is returned to the pool.
    'RESET ALL' safely drops the RLS tenant context (app.current_user_id)
    preventing data leakage, while preserving prepared statements
    and cached query plans for optimal performance.
    """
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("RESET ALL;")
    except Exception as e:
        # In the rare event the connection is completely broken,
        # SQLAlchemy will handle the invalidation automatically.
        pass
    finally:
        cursor.close()
