from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
from models.task import Task as DBTask, TaskCreate, TaskUpdate, TaskRead
from utils.database import get_session
from utils.auth import get_current_user, verify_user_ownership
from utils.auth import TokenData
from services.todo_service import TodoService

router = APIRouter(prefix="/api/{user_id}", tags=["tasks"])


@router.get("/tasks", response_model=List[TaskRead])
def get_tasks(
    user_id: str,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all tasks for a specific user
    """
    # Verify that the user_id in the token matches the user_id in the URL
    if not verify_user_ownership(current_user.user_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these tasks"
        )

    # Use the service layer to get tasks
    tasks = TodoService.get_tasks_by_user(session, user_id)
    return tasks


@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    user_id: str,
    task: TaskCreate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new task for a specific user
    """
    # Verify that the user_id in the token matches the user_id in the URL
    if not verify_user_ownership(current_user.user_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create tasks for this user"
        )

    # Use the service layer to create the task
    db_task = TodoService.create_task(session, user_id, task)
    return db_task


@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(
    user_id: str,
    task_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific task by ID for a specific user
    """
    # Verify that the user_id in the token matches the user_id in the URL
    if not verify_user_ownership(current_user.user_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these tasks"
        )

    # Use the service layer to get the specific task
    db_task = TodoService.get_task_by_id_and_user(session, user_id, task_id)

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return db_task


@router.put("/tasks/{task_id}", response_model=TaskRead)
def update_task(
    user_id: str,
    task_id: int,
    task_update: TaskUpdate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a specific task by ID for a specific user
    """
    # Verify that the user_id in the token matches the user_id in the URL
    if not verify_user_ownership(current_user.user_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these tasks"
        )

    # Use the service layer to update the task
    db_task = TodoService.update_task(session, user_id, task_id, task_update)

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return db_task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    user_id: str,
    task_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a specific task by ID for a specific user
    """
    # Verify that the user_id in the token matches the user_id in the URL
    if not verify_user_ownership(current_user.user_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these tasks"
        )

    # Use the service layer to delete the task
    success = TodoService.delete_task(session, user_id, task_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return


@router.patch("/tasks/{task_id}/complete", response_model=TaskRead)
def toggle_task_completion(
    user_id: str,
    task_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Toggle the completion status of a specific task by ID for a specific user
    """
    # Verify that the user_id in the token matches the user_id in the URL
    if not verify_user_ownership(current_user.user_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these tasks"
        )

    # Use the service layer to toggle task completion
    db_task = TodoService.toggle_task_completion(session, user_id, task_id)

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return db_task