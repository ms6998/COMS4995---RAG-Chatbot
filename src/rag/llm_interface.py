"""
LLM interface module for generating responses.
Updated for google-genai 1.x and modern LangChain standards.
"""

from typing import List, Dict, Any, Optional
import logging
from enum import Enum
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"


class LLMInterface:
    """Base interface for LLM interactions."""

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> str:
        """Generate a response from the LLM."""
        raise NotImplementedError


class GeminiInterface(LLMInterface):
    """Interface for Google Gemini models using the unified google-genai SDK."""

    def __init__(self, api_key: str, model: str = "models/gemini-2.5-pro"):
        """
        Initialize Gemini interface.
        """
        try:
            from google import genai

            # The new SDK uses a Client object
            self.client = genai.Client(api_key=api_key)

            # List available models
            logger.info("Available Gemini models:")
            for m in list(self.client.models.list()):
                logger.info(f"  {m.name}")

            self.model_id = model
            logger.info(f"Initialized Gemini interface with model: {model}")
        except ImportError:
            raise ImportError("google-genai package not installed. Run: pip install google-genai")

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate a response using Gemini API.
        """
        try:
            from google import genai
            from google.genai import types

            # Separate System message from User/Assistant history
            system_instruction = None
            history = []

            for msg in messages:
                if msg["role"] == "system":
                    system_instruction = msg["content"]
                else:
                    # The new SDK expects role to be "user" or "model"
                    role = "user" if msg["role"] == "user" else "model"
                    history.append(types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg["content"])]
                    ))

            # Modern configuration using GenerateContentConfig
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
                max_output_tokens=max_tokens,
            )

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=history,
                config=config
            )

            return response.text
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}")
            if os.environ["DEBUG"]:
                raise e
            return f"Error: {str(e)}"


class PromptTemplate:
    """Template for building prompts."""

    DEGREE_QA_SYSTEM = """You are PathWay, an academic advisor...""" # Rest of the string
    PLANNING_SYSTEM = """You are PathWay, a planning assistant...""" # Rest of the string

    @staticmethod
    def build_qa_prompt(query: str, context: str, user_profile: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        # ... (rest of the build_qa_prompt logic)
        return [
            {"role": "system", "content": PromptTemplate.DEGREE_QA_SYSTEM},
            {"role": "user", "content": f"Context: {context}\nQuestion: {query}"}
        ]

    @staticmethod
    def build_planning_prompt(user_profile: Dict[str, Any], requirements_context: str, professor_info: str) -> List[Dict[str, str]]:
        # ... (rest of the build_planning_prompt logic)
        return [
            {"role": "system", "content": PromptTemplate.PLANNING_SYSTEM},
            {"role": "user", "content": f"Task: Create a plan for {user_profile.get('program')}"}
        ]


class OpenAIInterface(LLMInterface):
    """Interface for OpenAI models."""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.model = model
            logger.info(f"Initialized OpenAI interface with model: {model}")
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

    def generate(self, messages, temperature=0.3, max_tokens=2000) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            if os.environ["DEBUG"]:
                raise e
            return f"Error: {str(e)}"


def create_llm_interface(
    provider: str,
    api_key: str,
    model: Optional[str] = None
) -> LLMInterface:
    p = provider.lower()
    if p == 'openai':
        return OpenAIInterface(api_key, model or "gpt-4o")

    elif p == 'gemini':
        # Removed the 'models/' prefix requirement as the SDK handles it
        return GeminiInterface(api_key, model or "models/gemini-2.5-pro")

    elif p == 'anthropic':
        from anthropic_interface import AnthropicInterface

        return AnthropicInterface(api_key, model or "claude-3-5-sonnet-latest")
    else:

        raise ValueError(f"Unknown provider: {provider}")


if __name__ == "__main__":
    # Example health check
    print("Building test prompt...")
    test_messages = PromptTemplate.build_qa_prompt(
        query="What is the CS core?",
        context="The CS core consists of Algorithms and OS.",
        user_profile={"program": "MS CS"}
    )
    print("Prompt built successfully.")
