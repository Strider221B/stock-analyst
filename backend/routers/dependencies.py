from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from db_components.database import get_db as basic_get_db
from db_components.models import User
from db_components.rls_utils import current_user_id_ctx_var
from db_components.security import verify_token

# This automatically extracts the token from the "Authorization: Bearer <token>" header.
# The tokenUrl is strictly for FastAPI's auto-generated Swagger UI documentation.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# 1. First: Extract Token and Lock RLS
async def get_rls_user_id(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = verify_token(token, "access")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate credentials",
                                headers={"WWW-Authenticate": "Bearer"})
        # LOCK THE KEY: This ensures the 'checkout' listener in database.py
        # sees the user_id immediately.
        current_user_id_ctx_var.set(user_id)
        return user_id
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

# 2. Second: Get the DB (Forced to run AFTER get_rls_user_id)
async def get_db_with_rls(user_id: str = Depends(get_rls_user_id), db: Session = Depends(basic_get_db)):
    """
    This wrapper ensures that get_db only runs AFTER the user_id is set.
    """
    return db

# 3. Third: Get the User Object
async def get_current_user(
    db: Session = Depends(get_db_with_rls),
    user_id: str = Depends(get_rls_user_id)
) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user
