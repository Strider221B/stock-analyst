import uuid
from datetime import datetime, timezone
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum as SQLEnum

from constants import ChatSender, RelNames, TableNames
from db_components.encrypted_text import EncryptedText
from db_components.models.base import Base
from db_components.models.id_mixin import IDMixin
from db_components import rls_utils

class ChatMessage(Base, IDMixin):
    __tablename__ = TableNames.CHAT_MESSAGES

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{TableNames.USERS}.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{TableNames.CHAT_SESSIONS}.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_type: Mapped[ChatSender] = mapped_column(
        SQLEnum(ChatSender, create_constraint=True, validate_strings=True, name="chat_sender_enum"),
        nullable=False
    )
    content: Mapped[str] = mapped_column(EncryptedText, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates=RelNames.MESSAGES)

rls_utils.attach_rls_to_model(ChatMessage)
