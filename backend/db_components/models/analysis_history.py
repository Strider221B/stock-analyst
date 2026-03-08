import uuid
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum

from constants import AnalysisRating, RelNames, TableNames
from db_components.encrypted_text import EncryptedText
from db_components.models.base import Base
from db_components.models.id_mixin import IDMixin
from db_components.models.timestamp_mixin import TimestampMixin

class AnalysisHistory(Base, IDMixin, TimestampMixin):
    __tablename__ = TableNames.ANALYSIS_HISTORY

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{TableNames.USERS}.id", ondelete="CASCADE"), nullable=False)
    ticker: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    rating: Mapped[AnalysisRating] = mapped_column(
            Enum(AnalysisRating, create_constraint=True, validate_strings=True, name="analysis_rating_enum"),
            nullable=False
        )
    confidence: Mapped[int] = mapped_column(Integer, nullable=False)
    thesis: Mapped[str] = mapped_column(EncryptedText, nullable=False)
    user: Mapped["User"] = relationship("User", back_populates=RelNames.ANALYSIS_HISTORY)
