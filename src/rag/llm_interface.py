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
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-pro"):
        """
        Initialize Gemini interface.
        """
        try:
            from google import genai
            # The new SDK uses a Client object
            self.client = genai.Client(api_key=api_key)
            self.model_id = model
            logger.info(f"Initialized Gemini interface with model: {model}")
        except ImportError:
            raise ImportError("google-genai package not installed. Run: pip install google-genai")
        
    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1, # Lower temperature for more consistent JSON
        max_tokens: int = 3000
    ) -> str:
        try:
            from google.genai import types
            
            # ... (history and system_instruction logic stays the same)

            # Update the config to enforce JSON
            system_instruction = None 
            history = []
        
            for msg in messages:
                if msg['role'] == 'system':
                    system_instruction = msg['content']
                else:
                    role = 'user' if msg['role'] == 'user' else 'model'
                    history.append(types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg['content'])]
                    ))

            # Now this will not crash because system_instruction is defined
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
                max_output_tokens=max_tokens,
                response_mime_type="application/json" # Add this to prevent the "Chatty" response
            )
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=history,
                config=config
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}")
            return f"Error: {str(e)}"
    '''
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
                if msg['role'] == 'system':
                    system_instruction = msg['content']
                else:
                    # The new SDK expects role to be 'user' or 'model'
                    role = 'user' if msg['role'] == 'user' else 'model'
                    history.append(types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg['content'])]
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
            return f"Error: {str(e)}"
'''
class PromptTemplate:
    """Template for building prompts."""
    
    DEGREE_QA_SYSTEM = """You are ColumbiaCourse AI, graduation requirements query assistant...""" # Rest of the string
    PLANNING_SYSTEM = """
    You are PathWise AI, a degree planning assistant.
    Based on the provided Degree Requirements and Professor Ratings, create a semester-by-semester plan.

    CRITICAL: You must return ONLY a JSON object. Do not include any introductory text, markdown formatting like ```json, or conversational filler.

    The JSON structure must be:
    {
    "semesters": [
        {
        "name": "Fall 2024",
        "courses": [
            {"code": "COMS 4721", "name": "Machine Learning", "credits": 3, "description": "...", "professor_recommendation": "..."}
        ],
        "total_credits": 3
        }
    ],
    "notes": ["Note 1", "Note 2"],
    "explanation": "Brief overview of the strategy used for this plan."
    }
    """

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
            return f"Error: {str(e)}"
    
    
# AnthropicInterface and PromptTemplate remain largely the same, 
# but ensure you use the logic above for the factory.

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
        return GeminiInterface(api_key, model or "gemini-1.5-pro")
    elif p == 'anthropic':
        from anthropic_interface import AnthropicInterface # Assuming it's in a separate file or defined
        return AnthropicInterface(api_key, model or "claude-3-5-sonnet-latest")
    else:
        raise ValueError(f"Unknown provider: {provider}")

if __name__ == "__main__":
    # Example health check
    from prompt_template import PromptTemplate # Assuming PromptTemplate is available
    print("Building test prompt...")
    test_messages = PromptTemplate.build_qa_prompt(
        query="What is the CS core?",
        context="The CS core consists of Algorithms and OS.",
        user_profile={"program": "MS CS"}
    )
    print("Prompt built successfully.")