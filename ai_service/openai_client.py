"""OpenAI GPT API client implementation."""

from ai_service.base import BaseLLMClient


class OpenAIClient(BaseLLMClient):
    """LLM client using OpenAI GPT API."""

    def __init__(self, api_key: str, model: str = 'gpt-4o-mini'):
        super().__init__(api_key)
        self.model = model
        self._client = None

    def _get_client(self):
        """Lazy-init the OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
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
        """Generate text using OpenAI API."""
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

        # Extract text from response
        choice = response.choices[0]
        if choice and choice.message:
            return choice.message.content or ''
        return ''

    def is_available(self) -> bool:
        """Check if the OpenAI client can make API calls."""
        if not self.api_key:
            return False
        try:
            from openai import OpenAI  # noqa: F401
            return True
        except ImportError:
            return False
