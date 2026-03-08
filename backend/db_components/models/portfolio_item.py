import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, String, UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from constants import RelNames, TableNames
from db_components.models.base import Base
from db_components.models.id_mixin import IDMixin
from db_components import rls_utils

class PortfolioItem(Base, IDMixin):
    __tablename__ = TableNames.PORTFOLIO_ITEMS

    # Denormalized user_id for high-performance RLS
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f"{TableNames.USERS}.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    ticker: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    added_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    portfolio: Mapped["Portfolio"] = relationship("Portfolio", back_populates=RelNames.ITEMS)

    __table_args__ = (
        # 1. Unique constraint: One ticker per portfolio
        UniqueConstraint('portfolio_id', 'ticker', name='uq_portfolio_ticker'),

        # 2. Composite FK: Ensures PortfolioItem.user_id matches Portfolio.user_id
        ForeignKeyConstraint(
            ['portfolio_id', 'user_id'],
            [f"{TableNames.PORTFOLIOS}.id", f"{TableNames.PORTFOLIOS}.user_id"],
            ondelete="CASCADE"
        ),
    )

rls_utils.attach_rls_to_model(PortfolioItem)
