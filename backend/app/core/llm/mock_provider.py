import asyncio
import time
from typing import AsyncGenerator
from app.core.llm.base import (
    BaseLLMProvider,
    ProviderCapabilities,
    ProviderRequest,
    ProviderResponse,
    StreamingChunk,
    TokenUsage,
)


class MockProvider(BaseLLMProvider):
    """Production-grade Mock LLM Provider simulating contextual responses and token usage."""

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_streaming=True,
            supports_vision=True,
            supports_tool_calling=True,
            supports_system_prompt=True,
            max_context_window=128000,
        )

    async def generate_response(self, request: ProviderRequest) -> ProviderResponse:
        start_time = time.perf_counter()
        
        # Simulate intelligent response formatting with Markdown & code snippet if appropriate
        prompt_lower = request.prompt.lower()
        if "code" in prompt_lower or "python" in prompt_lower or "script" in prompt_lower:
            content = (
                f"Here is a clean Python solution for your request:\n\n"
                f"```python\n"
                f"# NeuroDesk AI Automated Analytics Snippet\n"
                f"def process_workspace_query(query_text: str):\n"
                f"    print(f'Processing query: {{query_text}}')\n"
                f"    return {{'status': 'success', 'confidence': 0.98}}\n"
                f"```\n\n"
                f"This code processes '{request.prompt}' within your secure enterprise environment."
            )
        elif "summary" in prompt_lower or "dataset" in prompt_lower:
            content = (
                f"### Dataset & Workspace Overview\n\n"
                f"Based on your query: **{request.prompt}**\n\n"
                f"- **Data Quality Score**: 98.5%\n"
                f"- **Records Analyzed**: 1,250 entries\n"
                f"- **Recommendation**: Proceed with pipeline execution."
            )
        else:
            content = (
                f"I have received your request: *'{request.prompt}'*.\n\n"
                f"As your NeuroDesk AI workspace assistant, I have analyzed your query within your active tenant context. "
                f"All systems are operational and ready for your next command."
            )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        # Calculate simulated token usage
        prompt_tokens = max(1, len(request.prompt.split()) * 2)
        completion_tokens = max(1, len(content.split()) * 2)
        total_tokens = prompt_tokens + completion_tokens

        return ProviderResponse(
            content=content,
            markdown_content=content,
            model=request.model,
            provider_name=self.provider_name,
            token_usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            ),
            latency_ms=round(elapsed_ms, 2),
            metadata={"simulated": True, "engine": "NeuroDesk-Mock-Engine-v1"},
        )

    async def stream_response(self, request: ProviderRequest) -> AsyncGenerator[StreamingChunk, None]:
        full_res = await self.generate_response(request)
        words = full_res.content.split(" ")
        for i, word in enumerate(words):
            delta = word + (" " if i < len(words) - 1 else "")
            yield StreamingChunk(delta=delta)
            await asyncio.sleep(0.02)
        
        yield StreamingChunk(delta="", finish_reason="stop", token_usage=full_res.token_usage)
