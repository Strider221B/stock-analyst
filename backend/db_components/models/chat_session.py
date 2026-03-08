import uuid
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from constants import RelNames, TableNames
from db_components.models.base import Base
from db_components.models.id_mixin import IDMixin
from db_components.models.timestamp_mixin import TimestampMixin

class ChatSession(Base, IDMixin, TimestampMixin):
    __tablename__ = TableNames.CHAT_SESSIONS

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{TableNames.USERS}.id", ondelete="CASCADE"), nullable=False)
    context_ticker: Mapped[str | None] = mapped_column(String(20), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates=RelNames.CHAT_SESSIONS)
    messages: Mapped[list["ChatMessage"]] = relationship("ChatMessage", back_populates=RelNames.SESSION, cascade="all, delete-orphan", order_by="ChatMessage.created_at")
