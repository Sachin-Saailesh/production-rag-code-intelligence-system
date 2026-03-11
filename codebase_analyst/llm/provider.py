import os
import json
from typing import List, Dict, Any, Optional, Generator, Union
from openai import AzureOpenAI, APIError
from ..config import config

class LLMEngine:
    """
    Azure OpenAI LLM Engine.
    Singleton-ish behavior via shared config.
    """
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=config.openai_api_key or os.getenv("OPENAI_API_KEY"),
            api_version=config.api_version,
            azure_endpoint=config.azure_endpoint
        )
        self.model = config.deployment_name # Azure uses deployment name as model
        
        # Verify connection on init (optional, good for debugging)
        # try:
        #     self.client.models.list()
        # except Exception as e:
        #     print(f"Warning: LLM connection check failed: {e}")

    def chat(self, messages: List[Dict[str, str]], temperature: float = None) -> str:
        """Simple chat completion"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or config.temperature,
                max_tokens=config.max_output_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM Error: {e}")
            return f"Error: {e}"

    def chat_with_tools(
        self, 
        messages: List[Dict[str, str]], 
        tools: List[Dict[str, Any]],
        tool_choice: str = "auto",
        temperature: float = None
    ) -> Any:
        """Chat completion with tool calling support"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                temperature=temperature or config.temperature,
                max_tokens=config.max_output_tokens,
            )
            return response.choices[0].message
        except Exception as e:
            print(f"LLM Tool Error: {e}")
            raise e

    def stream_chat(self, messages: List[Dict[str, str]], temperature: float = None) -> Generator[str, None, None]:
        """Stream chat completion"""
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or config.temperature,
                max_tokens=config.max_output_tokens,
                stream=True
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error: {e}"

# Global instance
llm_engine = LLMEngine()
