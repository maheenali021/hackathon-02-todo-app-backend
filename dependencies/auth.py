"""
JWT authentication dependency for the AI-powered conversational todo chatbot.
Extends Phase II authentication with user_id validation for todo operations.
"""
from fastapi import Depends, HTTPException, status
from typing import Optional
from utils.auth import get_current_user, verify_user_ownership, TokenData

async def get_current_user_id(token_data: TokenData = Depends(get_current_user)) -> str:
    """
    Extracts and validates the current user's ID from the JWT token.
    This function ensures that all operations are scoped to the authenticated user.

    Args:
        token_data: The token data containing user information

    Returns:
        str: The authenticated user's ID
    """
    return token_data.user_id


def validate_user_access(user_id: str, requested_user_id: str) -> bool:
    """
    Validates that the current user has access to resources belonging to the requested user.
    Implements user isolation to ensure users can only access their own data.

    Args:
        user_id: The ID of the currently authenticated user
        requested_user_id: The ID of the user whose resources are being accessed

    Returns:
        bool: True if access is allowed, raises HTTPException if not
    """
    if user_id != requested_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own resources"
        )
    return True