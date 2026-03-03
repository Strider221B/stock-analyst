from sqlalchemy import DDL, event
from sqlalchemy.types import Enum
from sqlalchemy.orm import Mapped, mapped_column

from constants import AccountType, TableNames
from db_components.models.base import Base
from db_components.models.id_mixin import IDMixin
from db_components.models.timestamp_mixin import TimestampMixin

class Portfolio(Base, IDMixin, TimestampMixin):
    __tablename__ = TableNames.PORTFOLIOS

    account_type: Mapped[AccountType] = mapped_column(
        Enum(AccountType, create_constraint=True, validate_strings=True, name="account_type_enum"),
        nullable=False
    )

# Enable RLS on the Portfolios table
event.listen(
    Portfolio.__table__,
    'after_create',
    DDL(f"ALTER TABLE {TableNames.PORTFOLIOS} ENABLE ROW LEVEL SECURITY;")
)

# Create the policy restricting access to the current session user
event.listen(
    Portfolio.__table__,
    'after_create',
    DDL(f"CREATE POLICY tenant_isolation_policy ON {TableNames.PORTFOLIOS} USING (user_id = current_setting('app.current_user_id')::uuid);")
)
