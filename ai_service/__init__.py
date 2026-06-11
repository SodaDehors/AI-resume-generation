"""AI service factory — creates the appropriate LLM client."""

from ai_service.base import BaseLLMClient
from ai_service.claude_client import ClaudeClient
from ai_service.openai_client import OpenAIClient
from ai_service.deepseek_client import DeepSeekClient
from ai_service.fallback_client import FallbackClient


def create_llm_client(provider: str = 'claude',
                      api_key: str = '') -> BaseLLMClient:
    """Factory: create an LLM client based on provider and API key.

    Args:
        provider: 'claude', 'openai', or 'fallback'
        api_key: API key for the provider (empty = use fallback)

    Returns:
        An initialized BaseLLMClient instance.
    """
    if not api_key or not api_key.strip():
        return FallbackClient()

    provider = provider.lower().strip()

    if provider == 'claude':
        try:
            client = ClaudeClient(api_key)
            if client.is_available():
                return client
        except Exception:
            pass
        return FallbackClient()

    elif provider == 'openai':
        try:
            client = OpenAIClient(api_key)
            if client.is_available():
                return client
        except Exception:
            pass
        return FallbackClient()

    elif provider == 'deepseek':
        try:
            client = DeepSeekClient(api_key)
            if client.is_available():
                return client
        except Exception:
            pass
        return FallbackClient()

    else:
        return FallbackClient()


__all__ = ['BaseLLMClient', 'ClaudeClient', 'OpenAIClient',
           'DeepSeekClient', 'FallbackClient', 'create_llm_client']
