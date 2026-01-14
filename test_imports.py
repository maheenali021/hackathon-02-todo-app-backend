#!/usr/bin/env python3
"""
Minimal test to check if the backend can start without errors
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

try:
    print("Testing imports...")

    # Test importing main components
    from chat import router as chat_router
    print("Chat router imported successfully")

    from agents.todo_orchestrator import todo_orchestrator
    print("Todo orchestrator imported successfully")

    from mcp.server import mcp_server
    print("MCP server imported successfully")

    from mcp.tools import add_task, list_tasks, complete_task, delete_task, update_task
    print("MCP tools imported successfully")

    from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL
    print("Config imported successfully")

    print("\nAll imports successful! The backend should be able to start.")

except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Other error: {e}")
    sys.exit(1)