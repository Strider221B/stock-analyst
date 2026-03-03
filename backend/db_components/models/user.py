from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.types import String
from sqlalchemy.orm import Mapped, mapped_column, validates

from constants import TableNames
from db_components.models.base import Base
from db_components.models.id_mixin import IDMixin
from db_components.models.timestamp_mixin import TimestampMixin
from db_components.security import pwd_context

class User(Base, IDMixin, TimestampMixin):
    __tablename__ = TableNames.USERS

    # Task 4: Restrict email length to prevent buffer overflow probes
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    _password_hash: Mapped[str] = mapped_column(String(1024), nullable=False)

    @hybrid_property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, plain_password: str):
        # This runs automatically when you do user.password = "..."
        if not plain_password or len(plain_password.strip()) == 0:
            raise ValueError("Password cannot be empty or just whitespace")
        # Extremely long passwords (e.g., 10,000+ characters) can be used as a DoS (Denial of Service)
        # attack because hashing them consumes massive CPU cycles.
        if len(plain_password) > 128:
            raise ValueError("Password too long")
        self._password_hash = pwd_context.hash(plain_password)

    def verify_password(self, password: str) -> bool:
        if not password:
            return False
        return pwd_context.verify(password, self._password_hash)

    @validates("email")
    def validate_email(self, key, address):
        """
        Ensures emails are always stored in lowercase and whitespace is removed.
        This prevents 'duplicate' accounts like User@Example.com and user@example.com.
        """
        if not address:
            raise ValueError("Email address cannot be empty")
        return address.strip().lower()
