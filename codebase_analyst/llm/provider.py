"""
LLM Engine supporting both standard OpenAI and Azure OpenAI.
Provider is selected via LLM_PROVIDER setting.
"""
import logging
from typing import List, Dict, Any, Generator

from openai import OpenAI, AzureOpenAI

from ..config import settings

logger = logging.getLogger(__name__)


class LLMEngine:
    """Unified LLM client for OpenAI and Azure OpenAI."""

    def __init__(self):
        self._client = None
        self._model: str = settings.llm_model

    @property
    def client(self):
        if self._client is None:
            self._client = self._build_client()
        return self._client

    def _build_client(self):
        provider = settings.llm_provider.lower()
        if provider == "azure":
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required for Azure OpenAI")
            self._model = settings.azure_deployment or settings.llm_model
            return AzureOpenAI(
                api_key=settings.openai_api_key,
                api_version=settings.azure_api_version,
                azure_endpoint=settings.azure_endpoint,
            )
        else:
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required")
            return OpenAI(api_key=settings.openai_api_key)

    def chat(self, messages: List[Dict[str, str]], temperature: float = None) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature or settings.llm_temperature,
                max_tokens=settings.max_output_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("LLM chat error: %s", e)
            return f"Error: {e}"

    def chat_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        tool_choice: str = "auto",
        temperature: float = None,
    ) -> Any:
        try:
            response = self.client.chat.completions.create(
                model=self._model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                temperature=temperature or settings.llm_temperature,
                max_tokens=settings.max_output_tokens,
            )
            return response.choices[0].message
        except Exception as e:
            logger.error("LLM tool call error: %s", e)
            raise

    def stream_chat(
        self, messages: List[Dict[str, str]], temperature: float = None
    ) -> Generator[str, None, None]:
        try:
            stream = self.client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature or settings.llm_temperature,
                max_tokens=settings.max_output_tokens,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error: {e}"


def get_llm_engine() -> LLMEngine:
    """Factory that returns a lazily-initialized LLM engine."""
    return LLMEngine()
