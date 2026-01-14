from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    status: str = Field(default="pending", regex="^(pending|completed)$")  # Either "pending" or "completed"


class TaskCreateBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    status: str = Field(default="pending", regex="^(pending|completed)$")


class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=255, index=True)  # Foreign key to user, indexed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)  # Optional timestamp when completed
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(TaskCreateBase):
    pass  # user_id will be added from the URL path in the service layer


class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    status: Optional[str] = Field(default=None, regex="^(pending|completed)$")


class TaskRead(TaskBase):
    id: int
    user_id: str
    created_at: datetime
    completed_at: Optional[datetime]
    updated_at: datetime