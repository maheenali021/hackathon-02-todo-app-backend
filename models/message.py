from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import json


class MessageBase(SQLModel):
    conversation_id: int = Field(index=True)
    role: str = Field(regex="^(user|assistant)$")  # Either "user" or "assistant"
    content: str = Field(min_length=1)
    tool_calls: Optional[str] = Field(default=None)  # JSON string of tool calls
    tool_responses: Optional[str] = Field(default=None)  # JSON string of tool responses


class Message(MessageBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)