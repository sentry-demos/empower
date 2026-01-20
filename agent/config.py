"""Configuration management for the AI Agent application."""

import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""

    # API settings
    api_host: str = os.environ["API_HOST"]
    api_port: int = int(os.environ["PORT"])
    api_reload: bool = os.environ["API_RELOAD"].lower() == "true"

    # OpenAI settings
    agent_model: str = "gpt-5-mini"
    light_model: str = "gpt-5-nano"

    # Agent Configuration
    agent_name: str = "EmpowerPlantAgent"
    agent_description: str = "An AI agent for plant empowerment tasks"
    
    max_tokens: int = int(os.getenv("MAX_TOKENS", "1000"))
    temperature: float = 0.7

    class Config:
        env_file = ".env"
        case_sensitive = False


# Instantiate settings
settings = Settings()
