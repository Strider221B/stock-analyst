from sqlalchemy.orm import Mapped, mapped_column

from constants import TableNames
from db_components.encrypted_text import EncryptedText
from db_components.models.base import Base
from db_components.models.id_mixin import IDMixin

class ChatMessage(Base, IDMixin):
    __tablename__ = TableNames.CHAT_MESSAGES
    content: Mapped[str] = mapped_column(EncryptedText, nullable=False)
