from typing import Optional, List
from models.task import Task, TaskCreate, TaskUpdate
from sqlmodel import Session, select
from datetime import datetime


class TodoService:
    """Service layer that implements the same functionality as the CLI app but with database persistence."""

    @staticmethod
    def get_tasks_by_user(session: Session, user_id: str) -> List[Task]:
        """Get all tasks for a specific user."""
        statement = select(Task).where(Task.user_id == user_id)
        tasks = session.exec(statement).all()
        return tasks

    @staticmethod
    def create_task(session: Session, user_id: str, task_create: TaskCreate) -> Task:
        """Create a new task for a user."""
        # Create a dictionary from the task_create object and add user_id
        task_data = task_create.model_dump()
        task_data['user_id'] = user_id
        task_data['completed'] = task_create.completed if task_create.completed is not None else False
        db_task = Task.model_validate(task_data)

        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task

    @staticmethod
    def get_task_by_id_and_user(session: Session, user_id: str, task_id: int) -> Optional[Task]:
        """Get a specific task by ID for a specific user."""
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        task = session.exec(statement).first()
        return task

    @staticmethod
    def update_task(session: Session, user_id: str, task_id: int, task_update: TaskUpdate) -> Optional[Task]:
        """Update a specific task for a user."""
        db_task = TodoService.get_task_by_id_and_user(session, user_id, task_id)
        if not db_task:
            return None

        # Update fields that are provided
        task_data = task_update.model_dump(exclude_unset=True)
        for field, value in task_data.items():
            setattr(db_task, field, value)

        db_task.updated_at = datetime.utcnow()

        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task

    @staticmethod
    def delete_task(session: Session, user_id: str, task_id: int) -> bool:
        """Delete a specific task for a user."""
        db_task = TodoService.get_task_by_id_and_user(session, user_id, task_id)
        if not db_task:
            return False

        session.delete(db_task)
        session.commit()
        return True

    @staticmethod
    def toggle_task_completion(session: Session, user_id: str, task_id: int) -> Optional[Task]:
        """Toggle the completion status of a specific task for a user."""
        db_task = TodoService.get_task_by_id_and_user(session, user_id, task_id)
        if not db_task:
            return None

        db_task.completed = not db_task.completed
        db_task.updated_at = datetime.utcnow()

        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task