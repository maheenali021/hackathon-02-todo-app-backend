"""
Database session dependency for the AI-powered conversational todo chatbot.
Provides database session management for FastAPI endpoints.
"""
from sqlmodel import create_engine, Session
from typing import Generator
from config import DATABASE_URL

# Create the database engine
engine = create_engine(str(DATABASE_URL), echo=False)


def get_session() -> Generator[Session, None, None]:
    """
    Provides a database session for dependency injection in FastAPI endpoints.
    """
    with Session(engine) as session:
        yield session


def get_session_context():
    """
    Context manager for database sessions, used directly in non-FastAPI contexts.
    """
    return Session(engine)