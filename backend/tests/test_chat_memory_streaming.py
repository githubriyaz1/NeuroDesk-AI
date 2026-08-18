import pytest
from httpx import AsyncClient
from uuid import uuid4

from app.core.llm.memory import (
    TokenBudgetManager,
    ConversationSummarizer,
    ContextWindowManager,
    MemoryManager,
)
from app.core.llm.streaming import cancellation_manager, stream_cache
from app.models.chat import Conversation, ChatMessage


def test_token_budget_manager():
    budget_mgr = TokenBudgetManager(max_context_tokens=1000, reserved_output_tokens=200)
    text = "Hello world! This is a test prompt."
    tokens = TokenBudgetManager.estimate_tokens(text)
    assert tokens > 0

    info = budget_mgr.calculate_prompt_budget(tokens)
    assert info["available_for_prompt"] == 800
    assert info["remaining_budget"] == 800 - tokens


def test_context_window_trimming():
    window_mgr = ContextWindowManager(TokenBudgetManager(max_context_tokens=100, reserved_output_tokens=20))
    messages = [
        ChatMessage(id=uuid4(), role="user", content="This is message " + str(i) * 20)
        for i in range(10)
    ]
    formatted, total_tokens = window_mgr.prepare_context_window(
        system_prompt="System prompt",
        summary="Executive summary",
        messages=messages,
        current_prompt="Latest user question?",
    )

    assert len(formatted) > 0
    assert formatted[0]["role"] == "system"
    assert total_tokens <= 100


def test_cancellation_and_stream_cache():
    stream_id = f"test-stream-{uuid4()}"
    cancellation_manager.request_cancellation(stream_id)
    assert cancellation_manager.is_cancelled(stream_id) is True

    cancellation_manager.clear(stream_id)
    assert cancellation_manager.is_cancelled(stream_id) is False


@pytest.mark.asyncio
async def test_llm_diagnostics_endpoint(async_client: AsyncClient, auth_headers: dict):
    res = await async_client.get("/api/v1/chat/diagnostics", headers=auth_headers)
    assert res.status_code == 200
    diag = res.json()
    assert diag["status"] == "healthy"
    assert diag["streaming_health"] == "operational"
    assert "total_token_usage" in diag


@pytest.mark.asyncio
async def test_chat_streaming_endpoint(async_client: AsyncClient, auth_headers: dict):
    res = await async_client.post(
        "/api/v1/chat/stream",
        headers=auth_headers,
        json={"prompt": "Stream a response please"},
    )
    assert res.status_code == 200
    assert "text/event-stream" in res.headers["content-type"]
