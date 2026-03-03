from sqlalchemy.orm import Mapped, mapped_column

from constants import TableNames
from db_components.encrypted_text import EncryptedText
from db_components.models.base import Base
from db_components.models.id_mixin import IDMixin
from db_components.models.timestamp_mixin import TimestampMixin

class AnalysisHistory(Base, IDMixin, TimestampMixin):
    __tablename__ = TableNames.ANALYSIS_HISTORY
    thesis: Mapped[str] = mapped_column(EncryptedText, nullable=False)
