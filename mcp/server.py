"""
MCP server skeleton for the AI-powered conversational todo chatbot.
Uses Official MCP SDK to expose 5 todo tools.
"""
import asyncio
from typing import Dict, Any, List
from .tools import add_task, list_tasks, complete_task, delete_task, update_task


class MCPServer:
    """
    MCP (Model Context Protocol) server that exposes todo operations as tools
    for the AI agent to use when processing natural language commands.
    """

    def __init__(self):
        self.tools = {
            "add_task": add_task,
            "list_tasks": list_tasks,
            "complete_task": complete_task,
            "delete_task": delete_task,
            "update_task": update_task
        }

    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a specific tool with the provided arguments.

        Args:
            tool_name: Name of the tool to execute
            **kwargs: Arguments to pass to the tool

        Returns:
            Dict containing the result of the tool execution
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "message": f"Tool '{tool_name}' not found"
            }

        try:
            # Get the tool function
            tool_func = self.tools[tool_name]

            # Execute the tool and return the result
            result = await tool_func(**kwargs) if asyncio.iscoroutinefunction(tool_func) else tool_func(**kwargs)
            return result
        except Exception as e:
            return {
                "success": False,
                "message": f"Error executing tool '{tool_name}': {str(e)}"
            }

    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """
        Get the schema for a specific tool (for function calling).

        Args:
            tool_name: Name of the tool

        Returns:
            Dict containing the tool's schema
        """
        schemas = {
            "add_task": {
                "name": "add_task",
                "description": "Add a new task to the user's todo list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The ID of the user"},
                        "title": {"type": "string", "description": "The title of the task to add"}
                    },
                    "required": ["user_id", "title"]
                }
            },
            "list_tasks": {
                "name": "list_tasks",
                "description": "List tasks from the user's todo list with optional filtering",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The ID of the user"},
                        "status_filter": {"type": "string", "enum": ["pending", "completed", "all"], "description": "Filter tasks by status"}
                    },
                    "required": ["user_id"]
                }
            },
            "complete_task": {
                "name": "complete_task",
                "description": "Mark a task as completed",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The ID of the user"},
                        "task_id": {"type": "integer", "description": "The ID of the task to complete"}
                    },
                    "required": ["user_id", "task_id"]
                }
            },
            "delete_task": {
                "name": "delete_task",
                "description": "Delete a task from the user's todo list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The ID of the user"},
                        "task_id": {"type": "integer", "description": "The ID of the task to delete"}
                    },
                    "required": ["user_id", "task_id"]
                }
            },
            "update_task": {
                "name": "update_task",
                "description": "Update the title of a task in the user's todo list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The ID of the user"},
                        "task_id": {"type": "integer", "description": "The ID of the task to update"},
                        "title": {"type": "string", "description": "The new title for the task"}
                    },
                    "required": ["user_id", "task_id", "title"]
                }
            }
        }

        return schemas.get(tool_name, {})

    def get_all_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Get schemas for all available tools.

        Returns:
            List of tool schemas
        """
        return [self.get_tool_schema(tool_name) for tool_name in self.tools.keys()]


# Global MCP server instance
mcp_server = MCPServer()