from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from models.user import User, UserCreate, UserRead
from utils.database import get_session
from utils.auth import get_current_user, verify_user_ownership
from utils.auth import TokenData

router = APIRouter(prefix="/api", tags=["users"])


@router.get("/users/{user_id}", response_model=UserRead)
def get_user(
    user_id: str,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific user by ID
    """
    # Verify that the user_id in the token matches the user_id in the URL
    if not verify_user_ownership(current_user.user_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user"
        )

    statement = session.exec(select(User).where(User.id == user_id))
    user = statement.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user