"""
MCP tools implementation for the AI-powered conversational todo chatbot.
Contains the 5 required tools: add_task, list_tasks, complete_task, delete_task, update_task.
"""
from typing import Dict, Any, List
from sqlmodel import Session, select
from models.task import Task, TaskCreate, TaskUpdate
from models.conversation import Conversation
from models.message import Message
from dependencies.db import get_session


async def add_task(user_id: str, title: str) -> Dict[str, Any]:
    """
    Add a new task to the user's todo list.

    Args:
        user_id: The ID of the user
        title: The title of the task to add

    Returns:
        Dict containing success status, task ID, and message
    """
    try:
        # Use the local database session
        from dependencies.db import get_session_context
        with get_session_context() as session:
            # Create the task
            task = Task(
                title=title,
                status="pending",
                user_id=user_id
            )

            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "success": True,
                "task_id": task.id,
                "message": f"Successfully added task '{title}'"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error adding task: {str(e)}"
        }


async def list_tasks(user_id: str, status_filter: str = "all") -> Dict[str, Any]:
    """
    List tasks from the user's todo list with optional filtering.

    Args:
        user_id: The ID of the user
        status_filter: Filter tasks by status (pending, completed, all)

    Returns:
        Dict containing success status, tasks list, and count
    """
    try:
        from dependencies.db import get_session_context
        with get_session_context() as session:
            # Build the query based on the status filter
            query = select(Task).where(Task.user_id == user_id)

            if status_filter == "pending":
                query = query.where(Task.status == "pending")
            elif status_filter == "completed":
                query = query.where(Task.status == "completed")
            # For "all", no additional filter is needed

            # Execute the query
            tasks = session.exec(query).all()

            # Format the tasks for the response
            formatted_tasks = []
            for task in tasks:
                formatted_tasks.append({
                    "id": task.id,
                    "title": task.title,
                    "status": task.status
                })

            return {
                "success": True,
                "tasks": formatted_tasks,
                "count": len(formatted_tasks)
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error listing tasks: {str(e)}"
        }


async def complete_task(user_id: str, task_id: int) -> Dict[str, Any]:
    """
    Mark a task as completed.

    Args:
        user_id: The ID of the user
        task_id: The ID of the task to complete

    Returns:
        Dict containing success status and message
    """
    try:
        from dependencies.db import get_session_context
        with get_session_context() as session:
            # Get the task
            task = session.get(Task, task_id)

            # Check if task exists and belongs to the user
            if not task:
                return {
                    "success": False,
                    "message": f"Task with ID {task_id} not found"
                }

            if task.user_id != user_id:
                return {
                    "success": False,
                    "message": "Access denied: You can only modify your own tasks"
                }

            # Update the task status and completion timestamp
            task.status = "completed"
            from datetime import datetime
            task.completed_at = datetime.utcnow()

            session.add(task)
            session.commit()

            return {
                "success": True,
                "message": f"Successfully marked task '{task.title}' as completed"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error completing task: {str(e)}"
        }


async def delete_task(user_id: str, task_id: int) -> Dict[str, Any]:
    """
    Delete a task from the user's todo list.

    Args:
        user_id: The ID of the user
        task_id: The ID of the task to delete

    Returns:
        Dict containing success status and message
    """
    try:
        from dependencies.db import get_session_context
        with get_session_context() as session:
            # Get the task
            task = session.get(Task, task_id)

            # Check if task exists and belongs to the user
            if not task:
                return {
                    "success": False,
                    "message": f"Task with ID {task_id} not found"
                }

            if task.user_id != user_id:
                return {
                    "success": False,
                    "message": "Access denied: You can only delete your own tasks"
                }

            # Delete the task
            session.delete(task)
            session.commit()

            return {
                "success": True,
                "message": f"Successfully deleted task '{task.title}'"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error deleting task: {str(e)}"
        }


async def update_task(user_id: str, task_id: int, title: str) -> Dict[str, Any]:
    """
    Update the title of a task in the user's todo list.

    Args:
        user_id: The ID of the user
        task_id: The ID of the task to update
        title: The new title for the task

    Returns:
        Dict containing success status and message
    """
    try:
        from dependencies.db import get_session_context
        with get_session_context() as session:
            # Get the task
            task = session.get(Task, task_id)

            # Check if task exists and belongs to the user
            if not task:
                return {
                    "success": False,
                    "message": f"Task with ID {task_id} not found"
                }

            if task.user_id != user_id:
                return {
                    "success": False,
                    "message": "Access denied: You can only modify your own tasks"
                }

            # Update the task title
            task.title = title

            session.add(task)
            session.commit()

            return {
                "success": True,
                "message": f"Successfully updated task to '{title}'"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error updating task: {str(e)}"
        }