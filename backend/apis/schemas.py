import re
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
import uuid

# ---------------------------------------------------------
# API Responses (Change 6: Specific Response Schema)
# ---------------------------------------------------------
class MessageResponse(BaseModel):
    """Standardized response for simple messaging."""
    message: str

class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)

class LoginResponse(BaseModel):
    """Payload returned upon successful login."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ---------------------------------------------------------
# Authentication Payloads
# ---------------------------------------------------------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    # Change 3: Validate password strength at the API boundary
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str
