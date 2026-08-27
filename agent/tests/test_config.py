import importlib
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest
from pytest import MonkeyPatch


@contextmanager
def import_config(
    monkeypatch: MonkeyPatch,
) -> Iterator[tuple[ModuleType, MagicMock, MagicMock]]:
    monkeypatch.setenv("OPENROUTER_API_KEY", "openrouter-key")
    monkeypatch.setenv("API_HOST", "0.0.0.0")
    monkeypatch.setenv("PORT", "8000")
    monkeypatch.setenv("API_RELOAD", "false")
    monkeypatch.setenv("MAX_TOKENS", "1000")
    sys.modules.pop("config", None)

    with (
        patch("dotenv.load_dotenv") as load_dotenv,
        patch("openai.AsyncOpenAI") as openai_client,
        patch("agents.set_default_openai_api"),
        patch("agents.set_default_openai_client"),
        patch("agents.set_tracing_disabled"),
    ):
        module = importlib.import_module("config")
        yield module, openai_client, load_dotenv

    sys.modules.pop("config", None)


def test_configures_openrouter_without_overriding_runtime_environment(
    monkeypatch: MonkeyPatch,
) -> None:
    with import_config(monkeypatch) as (config, openai_client, load_dotenv):
        load_dotenv.assert_called_once_with(config.env_path, override=False)
        openai_client.assert_called_once_with(
            api_key="openrouter-key",
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://empower-plant.com",
                "X-OpenRouter-Title": "Empower Plant Agent",
            },
        )


def test_does_not_fall_back_to_an_openai_key(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("API_HOST", "0.0.0.0")
    monkeypatch.setenv("PORT", "8000")
    monkeypatch.setenv("API_RELOAD", "false")
    monkeypatch.setenv("MAX_TOKENS", "1000")
    sys.modules.pop("config", None)

    with (
        patch("dotenv.load_dotenv"),
        patch("openai.AsyncOpenAI"),
        patch("agents.set_default_openai_api"),
        patch("agents.set_default_openai_client"),
        patch("agents.set_tracing_disabled"),
        pytest.raises(RuntimeError, match="Set OPENROUTER_API_KEY"),
    ):
        importlib.import_module("config")

    sys.modules.pop("config", None)
