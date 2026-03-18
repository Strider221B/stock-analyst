from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# Imported the new MessageResponse schema
from apis.schemas import UserCreate, UserLogin, LoginResponse, MessageResponse
from db_components.security import create_refresh_token, create_access_token, check_needs_rehash, DUMMY_HASH, verify_password
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

@router.post("/login", response_model=LoginResponse)
async def login(user_in: UserLogin, response: Response, db: Session = Depends(get_db)):
    """Authenticates a user, sets the refresh cookie, and returns an access token."""

    # 1. Fetch the user by email
    user = db.query(User).filter(User.email == user_in.email).first()

    # 2. Timing Attack Mitigation
    is_authenticated = False
    if user:
        # User exists, do the real math
        is_authenticated = user.verify_password_match(user_in.password)
    else:
        # User does NOT exist. Do the fake math to stall the response time.
        verify_password(user_in.password, DUMMY_HASH)

    if not is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. The "Pro Move": Check if the Argon2 hash needs an upgrade
    # What was a "strong" password hash five years ago might be "weak" today because computers got faster
    # or researchers found a better way to crack them.
    # Without this, your old users' accounts stay protected by "yesterday's security."
    # With this, your database self-heals and gets stronger every time a user logs in.
    try:
        if check_needs_rehash(user.get_password_hash()):
            user.password = user_in.password
            db.commit()
            db.refresh(user) # Refresh to ensure the object is fully synced
    except SQLAlchemyError:
        # If the rehash fails (e.g., DB connection drop), rollback the transaction
        # so it doesn't poison the session, but ALLOW the login to proceed.
        db.rollback()

    # 4. Generate both tokens
    token_data = {"sub": str(user.id)}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # 5. Set the secure HttpOnly cookie
    is_production = settings.environment == Environment.PRODUCTION
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_production,
        samesite="strict",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60
    )

    # 6. Return the typed response
    return LoginResponse(
        access_token=access_token,
        user=user
    )
