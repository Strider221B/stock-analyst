import jwt
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.fernet import Fernet

from config import settings

_TOKEN_TYPE_ACCESS = 'access'
_TOKEN_TYPE_REFRESH = 'refresh'
_TOKEN_TYPE = 'type'

# ---------------------------------------------------------
# 1. Hashing & Encryption (Using direct argon2-cffi)
# ---------------------------------------------------------
ph = PasswordHasher()
cipher_suite = Fernet(settings.db_encryption_key.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Hashes a password using Argon2id."""
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a password against its hash."""
    try:
        return ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        # Argon2 raises an exception on failure; we catch it and return False
        return False

def check_needs_rehash(hashed_password: str) -> bool:
    """
    Checks if the password hash needs to be updated based on the
    current Argon2 parameters (e.g., if we increased memory/iterations later).
    """
    return ph.check_needs_rehash(hashed_password)

# ---------------------------------------------------------
# 2. JWT Generation & Verification
# ---------------------------------------------------------
def _create_token(data: dict, expires_delta: timedelta, token_type: str) -> str:
    """Internal helper to generate signed JWTs."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    # Inject the type claim to prevent token substitution attacks
    to_encode.update({
        "exp": expire,
        "type": token_type
    })

    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def create_access_token(data: dict) -> str:
    """Creates a short-lived access token for API authorization."""
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    return _create_token(data, expires_delta, _TOKEN_TYPE_ACCESS)

def create_refresh_token(data: dict) -> str:
    """Creates a long-lived refresh token to be stored in an HttpOnly cookie."""
    expires_delta = timedelta(days=settings.refresh_token_expire_days)
    return _create_token(data, expires_delta, _TOKEN_TYPE_REFRESH)

def verify_token(token: str,  expected_type: str) -> dict:
    """Decodes and verifies any JWT (Access or Refresh)."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

        if payload.get(_TOKEN_TYPE) != expected_type:
            raise ValueError(f"Invalid token type. Expected '{expected_type}'")

        return payload

    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
