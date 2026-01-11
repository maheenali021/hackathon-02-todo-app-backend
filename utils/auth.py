from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
import os
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Initialize security scheme
security = HTTPBearer()

# Secret key for JWT
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", "your-super-secret-jwt-key-here")
ALGORITHM = "HS256"

class TokenData(BaseModel):
    user_id: str
    email: Optional[str] = None


def verify_token(token: str) -> TokenData:
    """
    Verify JWT token and return user data
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_data = TokenData(user_id=user_id, email=email)
        return token_data
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """
    Dependency to get current user from JWT token
    """
    token_data = verify_token(credentials.credentials)
    return token_data


def verify_user_ownership(user_id_from_token: str, user_id_from_url: str) -> bool:
    """
    Verify that the user_id in the token matches the user_id in the URL
    """
    return user_id_from_token == user_id_from_url