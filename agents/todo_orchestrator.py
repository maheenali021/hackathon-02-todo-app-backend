"""
TodoChatOrchestrator agent for the AI-powered conversational todo chatbot.
Coordinates between specialized agents and MCP tools.
"""
import asyncio
from typing import Dict, Any, List
from openai import AsyncOpenAI
from mcp.server import mcp_server
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL
import httpx


class TodoChatOrchestrator:
    """
    Main orchestrator agent that processes natural language input and determines
    which tools to call based on user intent.
    """

    def __init__(self):
        # Create a custom HTTP client without proxy settings to avoid compatibility issues
        http_client = httpx.AsyncClient(
            timeout=30.0,  # Set a reasonable timeout
            # Explicitly avoid any proxy configuration
        )

        # Initialize AsyncOpenAI client with the custom HTTP client
        self.client = AsyncOpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            http_client=http_client
        )
        self.mcp_server = mcp_server

    async def process_message(self, user_id: str, message: str, conversation_context: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Process a natural language message and return the appropriate response.

        Args:
            user_id: The ID of the user
            message: The natural language message from the user
            conversation_context: Optional conversation history for context

        Returns:
            Dict containing the response and any tool calls made
        """
        if not conversation_context:
            conversation_context = []

        # Prepare the messages for the OpenAI API
        system_message = {
            "role": "system",
            "content": """You are a helpful todo list assistant. You can help users manage their tasks by adding, listing, updating, completing, or deleting tasks.
            Always use the available functions to perform these operations.
            Be concise and friendly in your responses."""
        }

        # Add conversation history if available
        messages = [system_message]
        for msg in conversation_context:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        # Add the current user message
        messages.append({
            "role": "user",
            "content": message
        })

        # Get the available tool schemas
        tools = self.mcp_server.get_all_tool_schemas()

        # Call the OpenRouter API with function calling
        response = await self.client.chat.completions.create(
            model="xiaomi/mimo-v2-flash",  # Free model from OpenRouter that supports function calling
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        tool_calls_made = []
        tool_results = []

        # Execute any tool calls
        if tool_calls:
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                import json
                function_args = json.loads(tool_call.function.arguments)

                # Ensure user_id is passed to all tools
                function_args["user_id"] = user_id

                # Execute the tool
                result = await self.mcp_server.execute_tool(function_name, **function_args)
                tool_results.append(result)
                tool_calls_made.append(function_name)

        # Get the final response from the model
        if response_message.content:
            final_response = response_message.content
        else:
            # Generate a response based on tool results
            if tool_results:
                # Create a friendly message based on the tool results
                success_results = [r for r in tool_results if r.get("success")]
                error_results = [r for r in tool_results if not r.get("success")]

                responses = []
                if success_results:
                    for result in success_results:
                        responses.append(result.get("message", "Operation completed successfully"))

                if error_results:
                    for result in error_results:
                        responses.append(f"Error: {result.get('message', 'Operation failed')}")

                final_response = " ".join(responses)
            else:
                final_response = "I've processed your request."

        return {
            "response": final_response,
            "tool_calls": tool_calls_made,
            "tool_results": tool_results
        }


# Global instance of the orchestrator (created lazily to avoid import-time errors)
_todo_orchestrator_instance = None


def get_todo_orchestrator():
    global _todo_orchestrator_instance
    if _todo_orchestrator_instance is None:
        _todo_orchestrator_instance = TodoChatOrchestrator()
    return _todo_orchestrator_instance


# For backward compatibility
todo_orchestrator = get_todo_orchestrator()