from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column

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
