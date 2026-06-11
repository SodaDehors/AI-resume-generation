"""Abstract base class for LLM clients."""

from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    """Abstract interface for LLM API clients.

    All LLM providers (Claude, OpenAI) and the rule-based fallback
    must implement this interface.
    """

    def __init__(self, api_key: str = ''):
        self.api_key = api_key

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.4,
        max_tokens: int = 2000,
    ) -> str:
        """Generate text from the LLM.

        Args:
            system_prompt: System-level instruction for the model.
            user_prompt: User input / task description.
            temperature: Creativity level (0.0-1.0).
            max_tokens: Maximum output tokens.

        Returns:
            Raw text response from the model.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the client can make API calls.

        Returns:
            True if the client is properly configured and ready.
        """
        pass
