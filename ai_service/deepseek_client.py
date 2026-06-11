"""DeepSeek API client implementation.

DeepSeek API is OpenAI-compatible, so we reuse the OpenAI SDK
with DeepSeek's base URL and models.
"""

from ai_service.base import BaseLLMClient


class DeepSeekClient(BaseLLMClient):
    """LLM client using DeepSeek API (OpenAI-compatible)."""

    # DeepSeek API endpoint and models
    BASE_URL = 'https://api.deepseek.com'
    DEFAULT_MODEL = 'deepseek-chat'  # DeepSeek-V3

    def __init__(self, api_key: str, model: str = None):
        super().__init__(api_key)
        self.model = model or self.DEFAULT_MODEL
        self._client = None

    def _get_client(self):
        """Lazy-init the OpenAI client pointed at DeepSeek."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.BASE_URL,
                )
            except ImportError:
                raise ImportError(
                    '请先安装 openai 库: pip install openai'
                )
        return self._client

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.4,
        max_tokens: int = 2000,
    ) -> str:
        """Generate text using DeepSeek API."""
        client = self._get_client()

        response = client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
        )

        choice = response.choices[0]
        if choice and choice.message:
            return choice.message.content or ''
        return ''

    def is_available(self) -> bool:
        """Check if the DeepSeek client can make API calls."""
        if not self.api_key:
            return False
        try:
            from openai import OpenAI  # noqa: F401
            return True
        except ImportError:
            return False
