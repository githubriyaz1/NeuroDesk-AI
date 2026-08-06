import asyncio
import time
from typing import Any, AsyncGenerator, Dict, List, Optional
from uuid import UUID

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.llm.base import BaseLLMProvider, ProviderRequest, ProviderResponse, TokenUsage
from app.core.llm.memory import memory_manager
from app.core.llm.registry import LLMProviderFactory
from app.core.llm.streaming import cancellation_manager, stream_cache, streaming_session_manager
from app.core.logging import logger
from app.models.chat import Conversation, ChatMessage
from app.schemas.chat import LLMDiagnosticsResponse


class LLMService:
    """Dedicated orchestrator for all LLM provider communication, memory management, retries, and streaming."""

    def __init__(self):
        self.memory_manager = memory_manager
        self.streaming_manager = streaming_session_manager
        self.cancellation = cancellation_manager
        self.cache = stream_cache
        self._latency_history: List[float] = []
        self._total_prompt_tokens = 0
        self._total_completion_tokens = 0

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, provider: str = "gemini") -> float:
        """Calculates estimated USD cost based on model pricing rules."""
        if provider == "gemini":
            cost = (prompt_tokens / 1000 * 0.000075) + (completion_tokens / 1000 * 0.0003)
        elif provider == "openai":
            cost = (prompt_tokens / 1000 * 0.005) + (completion_tokens / 1000 * 0.015)
        else:
            cost = (prompt_tokens / 1000 * 0.0001) + (completion_tokens / 1000 * 0.0004)
        return round(cost, 6)

    async def execute_provider_request(
        self,
        provider_name: str,
        request: ProviderRequest,
        max_retries: int = settings.MAX_RETRIES,
    ) -> ProviderResponse:
        """Executes LLM request with retry strategy and exponential backoff."""
        active_provider_name = provider_name or getattr(settings, "LLM_PROVIDER", "mock")
        provider = LLMProviderFactory.get_provider(active_provider_name)
        start_time = time.time()

        for attempt in range(1, max_retries + 1):
            try:
                response = await provider.generate_response(request)
                latency = round((time.time() - start_time) * 1000, 2)
                self._latency_history.append(latency)
                if len(self._latency_history) > 100:
                    self._latency_history.pop(0)

                self._total_prompt_tokens += response.token_usage.prompt_tokens
                self._total_completion_tokens += response.token_usage.completion_tokens

                return response

            except Exception as exc:
                logger.warning(f"Attempt {attempt}/{max_retries} failed for LLM Provider [{provider_name}]: {exc}")
                if attempt == max_retries:
                    logger.error(f"All {max_retries} retries exhausted for provider [{provider_name}]")
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"LLM Provider execution failed: {str(exc)}",
                    )
                await asyncio.sleep(2 ** (attempt - 1))

    async def generate_non_streaming(
        self,
        provider_name: str = "mock",
        model_name: str = settings.DEFAULT_MODEL,
        prompt: str = "",
        system_instruction: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Convenience method for non-streaming response generation used by WorkflowRunner."""
        req = ProviderRequest(
            prompt=prompt,
            system_prompt=system_instruction,
            model=model_name,
        )
        res = await self.execute_provider_request(provider_name, req)
        return {
            "text": res.content,
            "markdown_content": res.markdown_content,
            "token_usage": res.token_usage.model_dump(),
            "latency_ms": res.latency_ms,
        }

    async def stream_provider_response(
        self,
        conversation: Conversation,
        messages: List[ChatMessage],
        current_prompt: str,
        message_id: UUID,
        provider_name: str = "mock",
        stream_id: Optional[str] = None,
        knowledge_context: Optional[str] = None,
        citations: Optional[List[Dict[str, Any]]] = None,
    ) -> AsyncGenerator[str, None]:
        """Prepares memory context window and streams response chunks via SSE."""
        mem_context = self.memory_manager.prepare_memory_context(
            conversation=conversation,
            messages=messages,
            current_prompt=current_prompt,
            knowledge_context=knowledge_context,
            citations=citations,
        )

        formatted_msgs = mem_context.get("formatted_messages", [])
        system_prompts = [m["content"] for m in formatted_msgs if m.get("role") == "system"]
        sys_prompt_text = "\n\n".join(system_prompts) if system_prompts else conversation.settings_json.get("system_prompt")

        history_msgs = [m for m in formatted_msgs if m.get("role") in ["user", "assistant"]]
        if len(history_msgs) > 1:
            history_lines = []
            for h in history_msgs[:-1]:
                role_label = "User" if h.get("role") == "user" else "Assistant"
                history_lines.append(f"{role_label}: {h.get('content')}")
            full_prompt = "Conversation History:\n" + "\n".join(history_lines) + f"\n\nUser Question: {current_prompt}"
        else:
            full_prompt = current_prompt

        active_provider_name = provider_name or getattr(settings, "LLM_PROVIDER", "mock")
        provider = LLMProviderFactory.get_provider(active_provider_name)
        req = ProviderRequest(
            prompt=full_prompt,
            system_prompt=sys_prompt_text,
            model=conversation.settings_json.get("model", settings.DEFAULT_MODEL),
            temperature=conversation.settings_json.get("temperature", 0.7),
            max_tokens=conversation.settings_json.get("max_tokens", 4096),
        )

        chunk_stream = provider.stream_response(req)
        async for sse_frame in self.streaming_manager.stream_generator(
            conversation_id=conversation.id,
            message_id=message_id,
            chunk_stream=chunk_stream,
            stream_id=stream_id,
        ):
            yield sse_frame

    def get_diagnostics(self) -> LLMDiagnosticsResponse:
        avg_latency = (
            round(sum(self._latency_history) / len(self._latency_history), 2)
            if self._latency_history
            else 0.0
        )
        return LLMDiagnosticsResponse(
            status="healthy",
            active_provider=settings.DEFAULT_LLM_PROVIDER,
            streaming_health="operational",
            memory_health="operational",
            average_latency_ms=avg_latency,
            total_token_usage={
                "prompt_tokens": self._total_prompt_tokens,
                "completion_tokens": self._total_completion_tokens,
                "total_tokens": self._total_prompt_tokens + self._total_completion_tokens,
            },
            active_cancellation_count=len(self.cancellation._cancelled_streams),
            cache_stream_count=len(self.cache._cache),
        )


llm_service = LLMService()
