from sqlmodel import create_engine, Session
from typing import Generator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_qiUMh84NJQcL@ep-winter-dream-a4gq17g2-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require")

# Create engine with proper Neon configuration
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,  # Verify connections before use
    pool_size=5,
    max_overflow=10,
    pool_recycle=300,  # Recycle connections after 5 minutes
)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session