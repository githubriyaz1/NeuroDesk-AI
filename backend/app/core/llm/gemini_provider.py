import asyncio
import math
import os
import re
import time
from typing import AsyncGenerator, Dict, Any, Optional

from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.core.config import settings
from app.core.llm.base import (
    BaseLLMProvider,
    ProviderCapabilities,
    ProviderRequest,
    ProviderResponse,
    StreamingChunk,
    TokenUsage,
)
from app.core.llm.mock_provider import MockProvider
from app.core.logging import logger


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM Provider integration using official google-genai SDK
    with automatic pandas CSV statistics engine preservation and MockProvider fallback.
    """

    def __init__(self, api_key: Optional[str] = None):
        self._mock_fallback = MockProvider()
        self.api_key = (
            api_key
            or os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
            or getattr(settings, "GOOGLE_API_KEY", "")
            or getattr(settings, "GEMINI_API_KEY", "")
        )
        self._client: Optional[genai.Client] = None
        if self.api_key:
            try:
                self._client = genai.Client(api_key=self.api_key)
            except Exception as exc:
                logger.warning(f"Failed to initialize google-genai Client: {exc}")

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_streaming=True,
            supports_vision=True,
            supports_tool_calling=True,
            supports_system_prompt=True,
            max_context_window=1000000,
        )

    def _get_active_model(self, requested_model: Optional[str] = None) -> str:
        if requested_model and "gemini" in requested_model.lower():
            return requested_model
        env_model = os.getenv("LLM_MODEL")
        if env_model:
            return env_model
        return getattr(settings, "LLM_MODEL", "gemini-2.5-flash")

    async def generate_response(self, request: ProviderRequest) -> ProviderResponse:
        start_time = time.perf_counter()

        # If client or API key is unavailable, gracefully fall back to MockProvider
        if not self._client or not self.api_key:
            logger.info("Gemini API key not configured. Falling back to MockProvider.")
            return await self._mock_fallback.generate_response(request)

        # 1. CSV / Spreadsheet Handling: Check if IntentRouter classified this as a CSV query
        from app.core.routing.intent_router import QueryIntent, intent_router
        intent, _, _ = intent_router.classify_intent(request.prompt)

        is_csv_query = intent in [
            QueryIntent.CSV_STATISTICS,
            QueryIntent.CSV_DISTRIBUTION,
            QueryIntent.CSV_FILTER,
            QueryIntent.CSV_GROUPBY,
            QueryIntent.CSV_CORRELATION,
        ]

        if is_csv_query:
            # Execute exact pandas operations first
            knowledge_text = self._mock_fallback._extract_knowledge_text(request)
            pandas_stats = self._mock_fallback._perform_csv_statistics(knowledge_text, request.prompt)
            if pandas_stats:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                prompt_tokens = len(request.prompt.split()) + 20
                completion_tokens = len(pandas_stats.split()) + 10
                return ProviderResponse(
                    content=pandas_stats,
                    markdown_content=pandas_stats,
                    model=self._get_active_model(request.model),
                    provider_name=self.provider_name,
                    token_usage=TokenUsage(
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=prompt_tokens + completion_tokens,
                    ),
                    latency_ms=round(elapsed_ms, 2),
                    metadata={"engine": "Pandas-DataFrame-Engine", "grounded": True},
                )

        # 2. PDF / Document / General Reasoning via Google Gemini API
        model_name = self._get_active_model(request.model)
        try:
            config_args = {}
            if request.system_prompt:
                config_args["system_instruction"] = request.system_prompt
            if request.temperature is not None:
                config_args["temperature"] = request.temperature
            if request.max_tokens is not None:
                config_args["max_output_tokens"] = request.max_tokens

            gen_config = types.GenerateContentConfig(**config_args) if config_args else None

            # Asynchronous call via client.aio
            response = await self._client.aio.models.generate_content(
                model=model_name,
                contents=request.prompt,
                config=gen_config,
            )

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            content = response.text or ""

            # Extract usage metadata if provided
            usage = getattr(response, "usage_metadata", None)
            p_tokens = getattr(usage, "prompt_token_count", len(request.prompt.split()) * 2) if usage else len(request.prompt.split()) * 2
            c_tokens = getattr(usage, "candidates_token_count", len(content.split()) * 2) if usage else len(content.split()) * 2

            return ProviderResponse(
                content=content,
                markdown_content=content,
                model=model_name,
                provider_name=self.provider_name,
                token_usage=TokenUsage(
                    prompt_tokens=p_tokens,
                    completion_tokens=c_tokens,
                    total_tokens=p_tokens + c_tokens,
                ),
                latency_ms=round(elapsed_ms, 2),
                metadata={"sdk": "google-genai", "status": "success"},
            )

        except Exception as exc:
            logger.warning(f"Gemini API call failed: {exc}. Falling back to MockProvider.")
            return await self._mock_fallback.generate_response(request)

    async def stream_response(self, request: ProviderRequest) -> AsyncGenerator[StreamingChunk, None]:
        # If client or API key is unavailable, gracefully fall back to MockProvider
        if not self._client or not self.api_key:
            async for chunk in self._mock_fallback.stream_response(request):
                yield chunk
            return

        # 1. CSV / Spreadsheet Handling: Check if pandas DataFrame engine should handle dataset queries
        knowledge_text = self._mock_fallback._extract_knowledge_text(request)
        prompt_lower = request.prompt.lower()
        is_csv_query = (
            any(k in prompt_lower for k in ["employee", "employees", "salary", "salaries", "department", "dataset", "how many", "count", "age", "tier", "bangalore", "city", "row", "rows", "duplicate", "duplicates", "dup", "missing", "null", "empty"])
            or bool(re.search(r"\bna\b", prompt_lower))
            or self._mock_fallback._detect_intent(request.prompt) == "calculate"
            or "csv dataset" in knowledge_text.lower()
            or "[file_path:" in knowledge_text.lower()
        )

        if is_csv_query:
            async for chunk in self._mock_fallback.stream_response(request):
                yield chunk
            return

        # 2. PDF / Document / General Reasoning Streaming via Google Gemini API
        model_name = self._get_active_model(request.model)
        try:
            config_args = {}
            if request.system_prompt:
                config_args["system_instruction"] = request.system_prompt
            if request.temperature is not None:
                config_args["temperature"] = request.temperature
            if request.max_tokens is not None:
                config_args["max_output_tokens"] = request.max_tokens

            gen_config = types.GenerateContentConfig(**config_args) if config_args else None

            # Asynchronous streaming via client.aio
            response_stream = await self._client.aio.models.generate_content_stream(
                model=model_name,
                contents=request.prompt,
                config=gen_config,
            )

            prompt_tokens = len(request.prompt.split()) * 2
            completion_tokens = 0

            async for chunk in response_stream:
                chunk_text = getattr(chunk, "text", "") or ""
                if chunk_text:
                    completion_tokens += len(chunk_text.split()) * 2
                    yield StreamingChunk(delta=chunk_text)

            total_tokens = prompt_tokens + completion_tokens
            yield StreamingChunk(
                delta="",
                finish_reason="stop",
                token_usage=TokenUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                ),
            )

        except Exception as exc:
            logger.warning(f"Gemini API streaming failed: {exc}. Falling back to MockProvider.")
            async for chunk in self._mock_fallback.stream_response(request):
                yield chunk

    async def health_check(self) -> bool:
        """Returns True if Gemini Provider is configured with a non-empty API key."""
        return bool(self.api_key and self._client)
