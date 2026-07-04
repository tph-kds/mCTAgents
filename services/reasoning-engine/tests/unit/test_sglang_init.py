"""Tests for SGLang provider initialization and fallback logic."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest


class TestSGLangConfig:
    def test_sglang_config_defaults(self):
        from mctagents.services.model_gateway.config import SGLangConfig

        config = SGLangConfig()
        assert config.base_url == "http://localhost:30000"
        assert config.model == "Qwen/Qwen3-1.7B"
        assert config.context_length == 4096

    def test_sglang_config_from_env(self):
        with patch.dict("os.environ", {"SGLANG_BASE_URL": "http://test:30000"}):
            from mctagents.services.model_gateway.config import SGLangConfig

            config = SGLangConfig.from_env()
            assert config.base_url == "http://test:30000"

    def test_sglang_config_from_env_custom_model(self):
        with patch.dict(
            "os.environ",
            {"SGLANG_BASE_URL": "http://sglang:30000", "SGLANG_MODEL": "my-model"},
        ):
            from mctagents.services.model_gateway.config import SGLangConfig

            config = SGLangConfig.from_env()
            assert config.base_url == "http://sglang:30000"
            assert config.model == "my-model"

    def test_sglang_config_exportable(self):
        from mctagents.services.model_gateway import SGLangConfig

        config = SGLangConfig()
        assert config.base_url == "http://localhost:30000"


class TestSGLangFallback:
    def test_sglang_provider_is_openai_compatible(self):
        from mctagents.services.model_gateway.base import ModelProvider
        from mctagents.services.model_gateway.openai_compatible import (
            OpenAICompatibleProvider,
        )

        assert issubclass(OpenAICompatibleProvider, ModelProvider)

    def test_sglang_provider_init(self):
        from mctagents.services.model_gateway.openai_compatible import (
            OpenAICompatibleProvider,
        )

        provider = OpenAICompatibleProvider(
            base_url="http://sglang:30000", api_key="not-needed",
        )
        assert provider.base_url == "http://sglang:30000"

    @pytest.mark.asyncio
    async def test_sglang_health_check_success(self):
        from mctagents.services.model_gateway.openai_compatible import (
            OpenAICompatibleProvider,
        )

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"data": [{"id": "model-a"}]}

        provider = OpenAICompatibleProvider(
            base_url="http://sglang:30000", api_key="not-needed",
        )
        provider.client = AsyncMock()
        provider.client.get = AsyncMock(return_value=mock_response)

        health = await provider.health()
        assert health["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_sglang_health_check_failure(self):
        from mctagents.services.model_gateway.openai_compatible import (
            OpenAICompatibleProvider,
        )

        provider = OpenAICompatibleProvider(
            base_url="http://sglang:30000", api_key="not-needed",
        )
        provider.client = AsyncMock()
        provider.client.get = AsyncMock(
            side_effect=httpx.ConnectError("Connection refused"),
        )

        health = await provider.health()
        assert health["status"] == "unhealthy"

    def test_ollama_provider_init(self):
        from mctagents.services.model_gateway.ollama import OllamaProvider

        provider = OllamaProvider(base_url="http://localhost:11434")
        assert provider.base_url == "http://localhost:11434"
