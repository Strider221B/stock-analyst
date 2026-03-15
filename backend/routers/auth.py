# /backend/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Response, status
from apis.schemas import UserCreate, UserLogin, UserResponse

# Create the router instance with a strict prefix
router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=dict)
async def register(user_in: UserCreate):
    """Registers a new user and sets the HttpOnly refresh token."""
    # Logic to be implemented in Task 2.3
    return {"message": "User created successfully"}

@router.post("/login", response_model=UserResponse)
async def login(user_in: UserLogin):
    """Authenticates a user and sets the HttpOnly refresh token."""
    # Logic to be implemented in Task 2.4
    return {"user": {"id": "...", "email": "..."}}

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout():
    """Clears the HttpOnly refresh token cookie."""
    # Logic to be implemented in Task 2.5
    return {"message": "Logged out"}
