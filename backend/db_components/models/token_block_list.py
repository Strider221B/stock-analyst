from datetime import datetime
from sqlalchemy.types import String
from sqlalchemy.orm import Mapped, mapped_column

from constants import TableNames
from db_components.models import Base, IDMixin

class TokenBlocklist(Base, IDMixin):
    __tablename__ = TableNames.TOKEN_BLOCK_LIST

    # The JWT ID (jti) is a standard UUID string
    jti: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)

    # We store the expiration so a background job can clean up this table later
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
