import re
from sqlalchemy import String, DDL, event
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship

from constants import RelNames, TableNames
from db_components.models.base import Base
from db_components.models.id_mixin import IDMixin
from db_components.models.timestamp_mixin import TimestampMixin
from db_components import rls_utils
from db_components.security import get_password_hash, verify_password

# Regex for basic email validation
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

class User(Base, IDMixin, TimestampMixin):
    __tablename__ = TableNames.USERS

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    _password_hash: Mapped[str] = mapped_column("password_hash", String(1024), nullable=False)

    # Relationships (Essential for ORM navigation and cascade deletes)
    portfolios: Mapped[list["Portfolio"]] = relationship(
        "Portfolio", back_populates=RelNames.USER, cascade="all, delete-orphan"
    )
    analysis_history: Mapped[list["AnalysisHistory"]] = relationship(
        "AnalysisHistory", back_populates=RelNames.USER, cascade="all, delete-orphan"
    )
    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        "ChatSession", back_populates=RelNames.USER, cascade="all, delete-orphan"
    )

    @hybrid_property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, plain_password: str):
        if not plain_password or len(plain_password.strip()) == 0:
            raise ValueError("Password cannot be empty")
        if len(plain_password) > 128:
            raise ValueError("Password too long")
        self._password_hash = get_password_hash(plain_password)

    def verify_password(self, password: str) -> bool:
        """Prevents timing attacks by ensuring a hashing operation occurs."""
        if not password:
            # Hash a dummy string to consume CPU time even on empty input
            verify_password("dummy_password", self._password_hash)
            return False
        return verify_password(password, self._password_hash)

    @validates("email")
    def validate_email(self, key, address):
        if not address:
            raise ValueError("Email address cannot be empty")

        normalized = address.strip().lower()
        if not EMAIL_REGEX.match(normalized):
            raise ValueError("Invalid email format")

        return normalized

# This is outside class because:
# The Table Object: SQLAlchemy doesn't fully finalize the __table__ object (which the helper needs) until the class body has finished executing.
# Clean Execution: Putting it outside ensures the User class is already in the global namespace so the event.listen can correctly reference User.__table__.
rls_utils.attach_rls_to_model(User, owner_column="id")
