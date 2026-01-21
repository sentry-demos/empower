"""Configuration management for the AI Agent application."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Allow extra env vars (OPENAI_API_KEY, AGENT_DSN, etc. used by other libs)
    )

    # API settings (read from environment / .env file)
    api_host: str = Field(alias="API_HOST")
    api_port: int = Field(alias="PORT")
    api_reload: bool = Field(alias="API_RELOAD")

    # OpenAI settings
    agent_model: str = "gpt-5-mini"
    light_model: str = "gpt-5-nano"

    # Agent Configuration
    agent_name: str = "EmpowerPlantAgent"
    agent_description: str = "An AI agent for plant empowerment tasks"
    
    max_tokens: int = Field(alias="MAX_TOKENS")
    temperature: float = 0.7


# Instantiate settings
settings = Settings()
