from typing import Dict, Type
from app.core.llm.base import BaseLLMProvider
from app.core.llm.mock_provider import MockProvider
from app.core.logging import logger


class ProviderRegistry:
    """Registry maintaining active and registered LLM Provider instances."""

    _providers: Dict[str, BaseLLMProvider] = {}

    @classmethod
    def register(cls, provider: BaseLLMProvider) -> None:
        name = provider.provider_name.lower()
        cls._providers[name] = provider
        logger.info(f"Registered LLM Provider: '{name}'")

    @classmethod
    def get(cls, name: str = "mock") -> BaseLLMProvider:
        name_lower = name.lower()
        if name_lower not in cls._providers:
            logger.warning(f"Provider '{name}' not found. Falling back to 'mock' provider.")
            return cls._providers.get("mock", MockProvider())
        return cls._providers[name_lower]

    @classmethod
    def list_providers(cls) -> Dict[str, str]:
        return {name: p.__class__.__name__ for name, p in cls._providers.items()}


# Initialize Factory with default MockProvider
ProviderRegistry.register(MockProvider())


class LLMProviderFactory:
    """Factory helper resolving LLM Provider instances by name."""

    @staticmethod
    def get_provider(provider_name: str = "mock") -> BaseLLMProvider:
        return ProviderRegistry.get(provider_name)
