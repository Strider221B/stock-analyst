import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

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
