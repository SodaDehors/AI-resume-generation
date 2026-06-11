"""Anthropic Claude API client implementation."""

from ai_service.base import BaseLLMClient


class ClaudeClient(BaseLLMClient):
    """LLM client using Anthropic Claude API."""

    def __init__(self, api_key: str, model: str = 'claude-sonnet-4-20250514'):
        super().__init__(api_key)
        self.model = model
        self._client = None

    def _get_client(self):
        """Lazy-init the Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    '请先安装 anthropic 库: pip install anthropic'
                )
        return self._client

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.4,
        max_tokens: int = 2000,
    ) -> str:
        """Generate text using Claude API."""
        client = self._get_client()

        response = client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[
                {'role': 'user', 'content': user_prompt}
            ],
        )

        # Extract text from response
        content = response.content
        if content and len(content) > 0:
            return content[0].text
        return ''

    def is_available(self) -> bool:
        """Check if the Claude client can make API calls."""
        if not self.api_key:
            return False
        try:
            import anthropic  # noqa: F401
            return True
        except ImportError:
            return False
