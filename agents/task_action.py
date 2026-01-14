"""
TaskActionAgent for the AI-powered conversational todo chatbot.
Handles add/update/delete/complete operations.
"""
from typing import Dict, Any
from backend.mcp.server import mcp_server


class TaskActionAgent:
    """
    Agent specialized in task modification operations: add, update, delete, and complete.
    """

    def __init__(self):
        self.mcp_server = mcp_server

    async def add_task(self, user_id: str, title: str) -> Dict[str, Any]:
        """
        Add a new task for the user.

        Args:
            user_id: The ID of the user
            title: The title of the task to add

        Returns:
            Dict containing the result of the operation
        """
        return await self.mcp_server.execute_tool("add_task", user_id=user_id, title=title)

    async def update_task(self, user_id: str, task_id: int, title: str) -> Dict[str, Any]:
        """
        Update the title of a task for the user.

        Args:
            user_id: The ID of the user
            task_id: The ID of the task to update
            title: The new title for the task

        Returns:
            Dict containing the result of the operation
        """
        return await self.mcp_server.execute_tool("update_task", user_id=user_id, task_id=task_id, title=title)

    async def delete_task(self, user_id: str, task_id: int) -> Dict[str, Any]:
        """
        Delete a task for the user.

        Args:
            user_id: The ID of the user
            task_id: The ID of the task to delete

        Returns:
            Dict containing the result of the operation
        """
        return await self.mcp_server.execute_tool("delete_task", user_id=user_id, task_id=task_id)

    async def complete_task(self, user_id: str, task_id: int) -> Dict[str, Any]:
        """
        Mark a task as completed for the user.

        Args:
            user_id: The ID of the user
            task_id: The ID of the task to complete

        Returns:
            Dict containing the result of the operation
        """
        return await self.mcp_server.execute_tool("complete_task", user_id=user_id, task_id=task_id)

    async def execute_action(self, action: str, user_id: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a specific task action based on the action type.

        Args:
            action: The type of action to execute (add, update, delete, complete)
            user_id: The ID of the user
            **kwargs: Additional arguments for the action

        Returns:
            Dict containing the result of the operation
        """
        action_map = {
            "add": self.add_task,
            "update": self.update_task,
            "delete": self.delete_task,
            "complete": self.complete_task
        }

        if action not in action_map:
            return {
                "success": False,
                "message": f"Action '{action}' not supported"
            }

        action_func = action_map[action]
        return await action_func(user_id=user_id, **kwargs)


# Global instance of the task action agent
task_action_agent = TaskActionAgent()