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
        candidate = requested_model or os.getenv("LLM_MODEL") or getattr(settings, "LLM_MODEL", "gemini-flash-latest")
        if not candidate or "mock" in candidate.lower() or "2.5" in candidate or "1.5-flash" in candidate or "2.0-flash" in candidate:
            return "gemini-flash-latest"
        return candidate

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
        clean_prompt = request.prompt.split("User Question:")[-1].strip() if "User Question:" in request.prompt else request.prompt

        user_content_payload = clean_prompt
        if request.system_prompt and "[Enterprise Knowledge Engine Retracted Sources]:" in request.system_prompt:
            extracted_knowledge = request.system_prompt.split("[Enterprise Knowledge Engine Retracted Sources]:")[-1].strip()
            user_content_payload = f"WORKSPACE DOCUMENT CONTEXT:\n{extracted_knowledge}\n\nUSER QUESTION:\n{clean_prompt}"
        elif request.system_prompt and "Content:" in request.system_prompt:
            user_content_payload = f"WORKSPACE DOCUMENT CONTEXT:\n{request.system_prompt}\n\nUSER QUESTION:\n{clean_prompt}"

        try:
            config_args = {}
            if user_content_payload != clean_prompt:
                sys_instruction = (
                    "You are NeuroDesk AI, a document-grounded workspace assistant.\n"
                    "Answer the user's question using the supplied workspace document context.\n"
                    "Do not assume the document is an architecture specification.\n"
                    "Do not reuse information from previous documents.\n"
                    "Do not use conversation history as document content.\n"
                    "Do not fabricate facts.\n"
                    "For PDF questions:\n"
                    "- explain the actual retrieved content\n"
                    "- preserve important terminology\n"
                    "- mention relevant page numbers\n"
                    "- cite the source filename and page\n"
                    "- never use a canned PDF summary\n"
                )
            else:
                sys_instruction = (
                    "You are NeuroDesk AI, an intelligent AI workspace assistant.\n"
                    "Help the user with their questions, code generation, script writing, and data analysis tasks.\n"
                )
            config_args["system_instruction"] = sys_instruction

            if request.temperature is not None:
                config_args["temperature"] = request.temperature
            if request.max_tokens is not None:
                config_args["max_output_tokens"] = request.max_tokens

            gen_config = types.GenerateContentConfig(**config_args) if config_args else None

            # Asynchronous call via client.aio
            response = await self._client.aio.models.generate_content(
                model=model_name,
                contents=user_content_payload,
                config=gen_config,
            )

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            content = response.text or ""

            prompt_tokens = len(user_content_payload.split()) + 20
            completion_tokens = len(content.split()) + 10
            total_tokens = prompt_tokens + completion_tokens

            return ProviderResponse(
                content=content,
                markdown_content=content,
                model=model_name,
                provider_name=self.provider_name,
                token_usage=TokenUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                ),
                latency_ms=round(elapsed_ms, 2),
            )

        except Exception as exc:
            logger.warning(f"Gemini API generation failed: {exc}. Falling back to MockProvider.")
            return await self._mock_fallback.generate_response(request)

    async def stream_response(self, request: ProviderRequest) -> AsyncGenerator[StreamingChunk, None]:
        start_time = time.perf_counter()

        # If client or API key is unavailable, gracefully fall back to MockProvider
        if not self._client or not self.api_key:
            logger.info("Gemini API key not configured. Falling back to MockProvider.")
            async for chunk in self._mock_fallback.stream_response(request):
                yield chunk
            return

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
            async for chunk in self._mock_fallback.stream_response(request):
                yield chunk
            return

        # 2. PDF / Document / General Reasoning Streaming via Google Gemini API
        model_name = self._get_active_model(request.model)
        clean_prompt = request.prompt.split("User Question:")[-1].strip() if "User Question:" in request.prompt else request.prompt

        user_content_payload = clean_prompt
        if request.system_prompt and "[Enterprise Knowledge Engine Retracted Sources]:" in request.system_prompt:
            extracted_knowledge = request.system_prompt.split("[Enterprise Knowledge Engine Retracted Sources]:")[-1].strip()
            user_content_payload = f"WORKSPACE DOCUMENT CONTEXT:\n{extracted_knowledge}\n\nUSER QUESTION:\n{clean_prompt}"
        elif request.system_prompt and "Content:" in request.system_prompt:
            user_content_payload = f"WORKSPACE DOCUMENT CONTEXT:\n{request.system_prompt}\n\nUSER QUESTION:\n{clean_prompt}"

        try:
            config_args = {}
            if user_content_payload != clean_prompt:
                sys_instruction = (
                    "You are NeuroDesk AI, a document-grounded workspace assistant.\n"
                    "Answer the user's question using the supplied workspace document context.\n"
                    "Do not assume the document is an architecture specification.\n"
                    "Do not reuse information from previous documents.\n"
                    "Do not use conversation history as document content.\n"
                    "Do not fabricate facts.\n"
                    "For PDF questions:\n"
                    "- explain the actual retrieved content\n"
                    "- preserve important terminology\n"
                    "- mention relevant page numbers\n"
                    "- cite the source filename and page\n"
                    "- never use a canned PDF summary\n"
                )
            else:
                sys_instruction = (
                    "You are NeuroDesk AI, an intelligent AI workspace assistant.\n"
                    "Help the user with their questions, code generation, script writing, and data analysis tasks.\n"
                )
            config_args["system_instruction"] = sys_instruction

            if request.temperature is not None:
                config_args["temperature"] = request.temperature
            if request.max_tokens is not None:
                config_args["max_output_tokens"] = request.max_tokens

            gen_config = types.GenerateContentConfig(**config_args) if config_args else None

            # Asynchronous streaming via client.aio
            response_stream = await self._client.aio.models.generate_content_stream(
                model=model_name,
                contents=user_content_payload,
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
