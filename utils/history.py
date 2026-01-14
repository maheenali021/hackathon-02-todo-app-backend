"""
Conversation history utilities for the AI-powered conversational todo chatbot.
Provides helper functions for managing conversation context.
"""
from sqlmodel import Session, select
from typing import List, Dict, Any
from backend.models.message import Message


async def get_conversation_history(session: Session, conversation_id: int) -> List[Dict[str, Any]]:
    """
    Retrieve conversation history for a given conversation ID.

    Args:
        session: Database session
        conversation_id: ID of the conversation to retrieve history for

    Returns:
        List of messages in chronological order
    """
    # Get messages for the conversation, ordered by timestamp
    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.timestamp)
    ).all()

    # Format the messages for return
    formatted_messages = []
    for message in messages:
        formatted_message = {
            "id": message.id,
            "role": message.role,
            "content": message.content,
            "timestamp": message.timestamp.isoformat() if message.timestamp else None,
        }

        # Add tool information if present
        if message.tool_calls:
            try:
                import json
                formatted_message["tool_calls"] = json.loads(message.tool_calls)
            except:
                formatted_message["tool_calls"] = message.tool_calls

        if message.tool_responses:
            try:
                import json
                formatted_message["tool_responses"] = json.loads(message.tool_responses)
            except:
                formatted_message["tool_responses"] = message.tool_responses

        formatted_messages.append(formatted_message)

    return formatted_messages


def format_message_for_agent(message: Dict[str, Any]) -> Dict[str, str]:
    """
    Format a message for use with the AI agent.

    Args:
        message: Message dictionary

    Returns:
        Formatted message with role and content
    """
    return {
        "role": message.get("role", "user"),
        "content": message.get("content", "")
    }