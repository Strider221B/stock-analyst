import uuid
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.types import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from constants import AccountType, RelNames, TableNames
from db_components.models.base import Base
from db_components.models.id_mixin import IDMixin
from db_components.models.timestamp_mixin import TimestampMixin
from db_components import rls_utils

class Portfolio(Base, IDMixin, TimestampMixin):
    __tablename__ = TableNames.PORTFOLIOS

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{TableNames.USERS}.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    account_type: Mapped[AccountType] = mapped_column(
        Enum(AccountType, create_constraint=True, validate_strings=True, name="account_type_enum"),
        nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates=RelNames.PORTFOLIOS)
    items: Mapped[list["PortfolioItem"]] = relationship("PortfolioItem", back_populates=RelNames.PORTFOLIO, cascade="all, delete-orphan")

    __table_args__ = (
        # Postgres needs this unique index to allow the
        # PortfolioItem composite FK to work!
        UniqueConstraint('id', 'user_id', name='uq_portfolio_id_user_id'),
    )

rls_utils.attach_rls_to_model(Portfolio)
