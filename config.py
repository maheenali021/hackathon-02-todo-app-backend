"""
Configuration module for the AI-powered conversational todo chatbot.
Contains application settings and database configuration.
"""
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost/dbname")

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
if not OPENROUTER_API_KEY:
    print("Warning: OPENROUTER_API_KEY not set in environment variables")

# OpenRouter API base URL
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

# Better Auth configuration
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET", "fallback-secret-key")