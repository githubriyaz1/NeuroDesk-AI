from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List, Optional
from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ProviderCapabilities(BaseModel):
    supports_streaming: bool = True
    supports_vision: bool = False
    supports_tool_calling: bool = False
    supports_system_prompt: bool = True
    max_context_window: int = 128000


class ConversationContext(BaseModel):
    conversation_id: str
    system_prompt: Optional[str] = "You are NeuroDesk AI, an enterprise intelligent workspace assistant."
    history: List[Dict[str, Any]] = Field(default_factory=list)
    attached_asset_ids: List[str] = Field(default_factory=list)


class ProviderRequest(BaseModel):
    prompt: str
    context: Optional[ConversationContext] = None
    model: str = "neurodesk-mock-v1"
    temperature: float = 0.7
    max_tokens: int = 4096
    stream: bool = False
    extra_params: Dict[str, Any] = Field(default_factory=dict)


class StreamingChunk(BaseModel):
    delta: str
    finish_reason: Optional[str] = None
    token_usage: Optional[TokenUsage] = None


class ProviderResponse(BaseModel):
    content: str
    markdown_content: Optional[str] = None
    model: str
    provider_name: str
    token_usage: TokenUsage
    latency_ms: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseLLMProvider(ABC):
    """Abstract Base Class for Provider-Agnostic LLM Integrations."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the unique name identifier of the provider."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        """Returns capabilities metadata for this provider."""
        pass

    @abstractmethod
    async def generate_response(self, request: ProviderRequest) -> ProviderResponse:
        """Generates a complete non-streaming response."""
        pass

    @abstractmethod
    async def stream_response(self, request: ProviderRequest) -> AsyncGenerator[StreamingChunk, None]:
        """Yields streaming response chunks."""
        pass
