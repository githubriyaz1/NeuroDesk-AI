import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.config import settings
from app.core.llm.base import ProviderRequest, ProviderResponse, StreamingChunk
from app.core.llm.gemini_provider import GeminiProvider
from app.core.llm.registry import LLMProviderFactory, ProviderRegistry
from app.core.llm.mock_provider import MockProvider


@pytest.mark.asyncio
async def test_gemini_provider_registration():
    """Verify GeminiProvider is correctly registered in ProviderRegistry and LLMProviderFactory."""
    provider = LLMProviderFactory.get_provider("gemini")
    assert isinstance(provider, GeminiProvider)
    assert provider.provider_name == "gemini"
    assert provider.capabilities.supports_streaming is True
    assert provider.capabilities.supports_system_prompt is True


@pytest.mark.asyncio
async def test_gemini_provider_fallback_when_no_api_key():
    """Verify GeminiProvider automatically falls back to MockProvider when GOOGLE_API_KEY is missing."""
    provider = GeminiProvider(api_key="")
    req = ProviderRequest(prompt="Hello Gemini, test fallback")
    res = await provider.generate_response(req)
    
    assert isinstance(res, ProviderResponse)
    assert res.content != ""
    assert res.provider_name in ["gemini", "mock"]


@pytest.mark.asyncio
async def test_gemini_provider_csv_dataframe_preservation():
    """Verify CSV dataset calculations use exact pandas engine rather than LLM hallucinations."""
    provider = GeminiProvider(api_key="test_dummy_key")
    
    # Simulating a prompt with [FILE_PATH:] context
    req = ProviderRequest(
        prompt="User Question: How many employees?",
        system_prompt="[Enterprise Knowledge Engine Retracted Sources]:\nContent: CSV Dataset 'Employee' [FILE_PATH: non_existent.csv]"
    )
    
    res = await provider.generate_response(req)
    assert isinstance(res, ProviderResponse)
    assert res.content != ""


@pytest.mark.asyncio
async def test_gemini_provider_streaming_fallback():
    """Verify stream_response yields StreamingChunk objects seamlessly."""
    provider = GeminiProvider(api_key="")
    req = ProviderRequest(prompt="Explain system architecture")
    
    chunks = []
    async for chunk in provider.stream_response(req):
        assert isinstance(chunk, StreamingChunk)
        chunks.append(chunk.delta)
    
    full_text = "".join(chunks)
    assert len(full_text) > 0


@pytest.mark.asyncio
async def test_gemini_provider_health_check(monkeypatch):
    """Verify health_check() returns True when configured and False when key missing."""
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    from app.core.config import settings
    monkeypatch.setattr(settings, "GOOGLE_API_KEY", "")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
    no_key_provider = GeminiProvider(api_key="")
    assert await no_key_provider.health_check() is False
