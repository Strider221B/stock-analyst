# /backend/schemas.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict
import uuid

# ---------------------------------------------------------
# Authentication Payloads
# ---------------------------------------------------------
class UserCreate(BaseModel):
    """Payload for registering a new user."""
    # EmailStr strictly validates the format (e.g., no missing '@')
    email: EmailStr
    # Enforce minimum length at the API boundary, before it ever reaches the DB
    password: str = Field(min_length=8, max_length=128)

class UserLogin(BaseModel):
    """Payload for authenticating an existing user."""
    email: EmailStr
    password: str

# ---------------------------------------------------------
# API Responses
# ---------------------------------------------------------
class UserResponse(BaseModel):
    """Safe user data returned to the client (NO PASSWORDS)."""
    id: uuid.UUID
    email: EmailStr

    # This allows Pydantic to read the data directly from your SQLAlchemy User model
    model_config = ConfigDict(from_attributes=True)
