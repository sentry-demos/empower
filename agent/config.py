"""Configuration management for the AI Agent application."""

import os
from pathlib import Path

from agents import (
    set_default_openai_api,
    set_default_openai_client,
    set_tracing_disabled,
)
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load local .env values without overriding runtime configuration such as
# Cloud Run environment variables and Secret Manager references.
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=False)

DEFAULT_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def configure_openrouter_client() -> None:
    """Point the OpenAI Agents SDK at OpenRouter instead of api.openai.com."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("Set OPENROUTER_API_KEY.")

    base_url = os.environ.get("OPENROUTER_BASE_URL")
    base_url = base_url or DEFAULT_OPENROUTER_BASE_URL
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
        default_headers={
            "HTTP-Referer": "https://empower-plant.com",
            "X-OpenRouter-Title": "Empower Plant Agent",
        },
    )
    # OpenRouter keys are not valid for OpenAI tracing uploads.
    set_default_openai_client(client, use_for_tracing=False)
    set_tracing_disabled(True)
    # OpenRouter only implements the Chat Completions API, not the Responses
    # API that the Agents SDK uses by default.
    set_default_openai_api("chat_completions")


configure_openrouter_client()


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Other libraries read these variables directly from the environment.
        extra="ignore",
    )

    # API settings (read from environment / .env file)
    api_host: str = Field(alias="API_HOST")
    api_port: int = Field(alias="PORT")
    api_reload: bool = Field(alias="API_RELOAD")

    # OpenRouter model ids (OpenAI-compatible provider/model slugs)
    agent_model: str = "openai/gpt-5-mini"
    light_model: str = "openai/gpt-5-nano"

    # Agent Configuration
    agent_name: str = "EmpowerPlantAgent"
    agent_description: str = "An AI agent for plant empowerment tasks"

    max_tokens: int = Field(alias="MAX_TOKENS")
    temperature: float = 0.7


# Instantiate settings
settings = Settings()  # type: ignore[call-arg]
