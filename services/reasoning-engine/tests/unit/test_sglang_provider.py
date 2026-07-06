"""Tests for SGLang provider configuration."""

from mctagents.services.model_gateway.config import SGLangConfig


def test_sglang_config_defaults():
    config = SGLangConfig()
    assert config.base_url == "http://localhost:30000"
    assert config.model == "Qwen/Qwen3-1.7B"
    assert config.context_length == 4096


def test_sglang_config_from_env(monkeypatch):
    monkeypatch.setenv("SGLANG_BASE_URL", "http://custom:9999")
    monkeypatch.setenv("SGLANG_MODEL", "custom-model")
    config = SGLangConfig.from_env()
    assert config.base_url == "http://custom:9999"
    assert config.model == "custom-model"
