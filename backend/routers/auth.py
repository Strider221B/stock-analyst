from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Imported the new MessageResponse schema
from apis.schemas import UserCreate, UserLogin, UserResponse, MessageResponse
from db_components.security import create_refresh_token
from config import settings
from constants import Environment
from db_components.models import User
from db_components.database import get_db

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

# Change 6: Use the explicit Pydantic response_model
@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=MessageResponse)
async def register(user_in: UserCreate, response: Response, db: Session = Depends(get_db)):
    """Registers a new user and sets the HttpOnly refresh token."""

    # Instantiate the new user
    new_user = User(
        email=user_in.email,
        password=user_in.password
    )

    # Change 1 & 5: Rely on the DB Unique Constraint via try/except
    try:
        db.add(new_user)
        db.commit()
        # Change 4: Ensure the DB-generated fields (like ID) are loaded into the Python object
        db.refresh(new_user)
    except IntegrityError as e:
        db.rollback()
        # The 'orig' attribute holds the underlying DBAPI error.
        # This catches standard PostgreSQL unique violation errors.
        error_msg = str(e.orig).lower()
        if "unique constraint" in error_msg or "duplicate key" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A database integrity error occurred."
        )

    # Generate the Long-Lived Refresh Token using the confirmed ID
    token_data = {"sub": str(new_user.id)}
    refresh_token = create_refresh_token(token_data)

    # Set the HttpOnly Cookie
    is_production = settings.environment == Environment.PRODUCTION
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_production,
        samesite="strict",  # Change 2: Upgraded to strict for maximum protection
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60
    )

    # Change 6: Return the typed Pydantic model
    return MessageResponse(message="User created successfully")
