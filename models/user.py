from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserRead(SQLModel):
    id: str
    email: str
    name: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UserCreate(SQLModel):
    email: str
    name: Optional[str] = None