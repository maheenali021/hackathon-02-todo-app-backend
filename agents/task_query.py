"""
TaskQueryAgent for the AI-powered conversational todo chatbot.
Handles list operations and filtering.
"""
from typing import Dict, Any
from backend.mcp.server import mcp_server


class TaskQueryAgent:
    """
    Agent specialized in task querying operations: list and filter tasks.
    """

    def __init__(self):
        self.mcp_server = mcp_server

    async def list_tasks(self, user_id: str, status_filter: str = "all") -> Dict[str, Any]:
        """
        List tasks for the user with optional filtering.

        Args:
            user_id: The ID of the user
            status_filter: Filter tasks by status (pending, completed, all)

        Returns:
            Dict containing the list of tasks
        """
        return await self.mcp_server.execute_tool("list_tasks", user_id=user_id, status_filter=status_filter)

    async def get_pending_tasks(self, user_id: str) -> Dict[str, Any]:
        """
        Get only pending tasks for the user.

        Args:
            user_id: The ID of the user

        Returns:
            Dict containing the list of pending tasks
        """
        return await self.list_tasks(user_id=user_id, status_filter="pending")

    async def get_completed_tasks(self, user_id: str) -> Dict[str, Any]:
        """
        Get only completed tasks for the user.

        Args:
            user_id: The ID of the user

        Returns:
            Dict containing the list of completed tasks
        """
        return await self.list_tasks(user_id=user_id, status_filter="completed")

    async def get_all_tasks(self, user_id: str) -> Dict[str, Any]:
        """
        Get all tasks for the user (both pending and completed).

        Args:
            user_id: The ID of the user

        Returns:
            Dict containing the list of all tasks
        """
        return await self.list_tasks(user_id=user_id, status_filter="all")

    async def search_tasks(self, user_id: str, search_term: str, status_filter: str = "all") -> Dict[str, Any]:
        """
        Search tasks for the user by title with optional filtering.

        Args:
            user_id: The ID of the user
            search_term: Term to search for in task titles
            status_filter: Filter tasks by status (pending, completed, all)

        Returns:
            Dict containing the list of matching tasks
        """
        # First get the tasks based on status filter
        result = await self.list_tasks(user_id=user_id, status_filter=status_filter)

        if not result.get("success"):
            return result

        # Then filter by search term
        all_tasks = result.get("tasks", [])
        matching_tasks = [
            task for task in all_tasks
            if search_term.lower() in task.get("title", "").lower()
        ]

        return {
            "success": True,
            "tasks": matching_tasks,
            "count": len(matching_tasks)
        }


# Global instance of the task query agent
task_query_agent = TaskQueryAgent()