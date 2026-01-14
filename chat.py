"""
Chat endpoint module for the AI-powered conversational todo chatbot.
Handles natural language processing and communication with the AI agent.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Optional, Dict, Any
from pydantic import BaseModel
from models.conversation import Conversation
from models.message import Message
from agents.todo_orchestrator import todo_orchestrator
from dependencies.auth import get_current_user_id
from dependencies.db import get_session


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: Optional[list[str]] = []


router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat_endpoint(
    user_id: str,
    request: ChatRequest,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Handle chat requests from OpenAI ChatKit frontend.
    Processes natural language input through AI agent with todo tools.
    """
    # Verify that the user_id in the token matches the user_id in the URL
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own chat"
        )

    # Get or create conversation
    conversation = None
    if request.conversation_id:
        # Try to get existing conversation
        conversation = session.get(Conversation, request.conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with ID {request.conversation_id} not found"
            )

        # Verify that the conversation belongs to the user
        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only access your own conversations"
            )
    else:
        # Create a new conversation
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    # Store the user's message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    session.add(user_message)
    session.commit()

    # Get conversation history for context
    from datetime import datetime
    conversation_history = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.timestamp)
    ).all()

    # Format history for the AI agent
    formatted_history = []
    for msg in conversation_history:
        formatted_history.append({
            "role": msg.role,
            "content": msg.content
        })

    # Process the message with the AI agent
    try:
        result = await todo_orchestrator.process_message(
            user_id=user_id,
            message=request.message,
            conversation_context=formatted_history[:-1]  # Exclude the current message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )

    # Store the assistant's response
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=result["response"],
        tool_calls=str(result["tool_calls"]) if result["tool_calls"] else None,
        tool_responses=str(result["tool_results"]) if "tool_results" in result else None
    )
    session.add(assistant_message)

    # Update the conversation's updated_at timestamp
    conversation.updated_at = datetime.now()
    session.add(conversation)

    session.commit()

    # Return the response
    return ChatResponse(
        conversation_id=conversation.id,
        response=result["response"],
        tool_calls=result["tool_calls"] if result["tool_calls"] else []
    )