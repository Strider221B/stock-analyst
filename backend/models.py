import uuid
from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# ==========================================
# The Declarative Base
# ==========================================
class Base(DeclarativeBase):
    """
    The master class that all SQLAlchemy models will inherit from.
    SQLAlchemy's metadata catalog is attached to this class.
    """
    pass

# ==========================================
# Object-Oriented Mixins
# ==========================================
class IDMixin:
    """
    Provides a standardized UUID primary key for tables.
    Using UUIDs instead of auto-incrementing integers prevents attackers
    from guessing database sizes or user IDs (IDOR vulnerabilities).
    """
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

class TimestampMixin:
    """
    Provides standardized audit timestamps for tables.
    Automatically records when a row is created and updated.
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(), # Use the Database clock for the initial insert
        onupdate=func.now() # Use the Database clock for all future updates
    )
