from fastapi import FastAPI, HTTPException, status, Depends
from sqlmodel import SQLModel, select
from sqlmodel import Session
from typing import Optional
import os
from dotenv import load_dotenv
from models.task import Task
from models.user import User
from utils.database import engine, get_session
from api.tasks import router as tasks_router
from api.users import router as users_router
from chat import router as chat_router
from utils.auth import SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta
from jose import jwt
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Todo Backend API", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you should specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(tasks_router)
app.include_router(users_router)
app.include_router(chat_router)

# Create database tables on startup
@app.on_event("startup")
async def on_startup():
    from models.user import User  # Import to ensure models are registered
    from models.task import Task  # Import to ensure models are registered
    SQLModel.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Welcome to the Todo Backend API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    user_id: str
    email: str = None


@app.post("/auth/login", response_model=Token)
async def login(request: LoginRequest, session: Session = Depends(get_session)):
    """
    Login endpoint that generates a JWT token for the user
    Creates user in the database if it doesn't exist
    """
    # Check if user exists, create if not
    existing_user = session.exec(select(User).where(User.id == request.user_id)).first()
    if not existing_user:
        # Create new user
        new_user = User(
            id=request.user_id,
            email=request.email or f"{request.user_id}@example.com",  # Use provided email or default
            name=request.user_id  # Use user_id as name if no name provided
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
    else:
        # Update user if email was provided
        if request.email:
            existing_user.email = request.email
            session.add(existing_user)
            session.commit()

    # Create JWT token
    expire = datetime.utcnow() + timedelta(days=30)  # Token valid for 30 days
    to_encode = {
        "sub": request.user_id,
        "email": request.email,
        "exp": expire.timestamp()
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": encoded_jwt,
        "token_type": "bearer"
    }


class SignupRequest(BaseModel):
    user_id: str
    email: str
    name: Optional[str] = None


@app.post("/auth/signup", response_model=Token)
async def signup(request: SignupRequest, session: Session = Depends(get_session)):
    """
    Signup endpoint that creates a new user and generates a JWT token
    """
    # Check if user already exists
    existing_user = session.exec(select(User).where(User.id == request.user_id)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )

    # Create new user
    new_user = User(
        id=request.user_id,
        email=request.email,
        name=request.name or request.user_id
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Create JWT token
    expire = datetime.utcnow() + timedelta(days=30)  # Token valid for 30 days
    to_encode = {
        "sub": request.user_id,
        "email": request.email,
        "exp": expire.timestamp()
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": encoded_jwt,
        "token_type": "bearer"
    }


# Get the BETTER_AUTH_SECRET from environment variables
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

if not BETTER_AUTH_SECRET:
    print("WARNING: BETTER_AUTH_SECRET not set. Using default secret for development.")
    BETTER_AUTH_SECRET = "tBkg75XLHG27HhzgEG2nSbtI1PSeVRb62YAEi6s3COkLig7Jv2Ne51qOQWumTGi3"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)