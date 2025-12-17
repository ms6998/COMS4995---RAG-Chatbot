"""
LLM interface module for generating responses.
Supports OpenAI and Anthropic models.
"""

from typing import List, Dict, Any, Optional
import logging
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


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


class OpenAIInterface(LLMInterface):
    """Interface for OpenAI models."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize OpenAI interface.
        
        Args:
            api_key: OpenAI API key
            model: Model name (e.g., "gpt-4", "gpt-3.5-turbo")
        """
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.model = model
            logger.info(f"Initialized OpenAI interface with model: {model}")
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate a response using OpenAI API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error: {str(e)}"


class AnthropicInterface(LLMInterface):
    """Interface for Anthropic Claude models."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        """
        Initialize Anthropic interface.
        
        Args:
            api_key: Anthropic API key
            model: Model name
        """
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key)
            self.model = model
            logger.info(f"Initialized Anthropic interface with model: {model}")
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate a response using Anthropic API.
        
        Args:
            messages: List of message dicts (OpenAI format)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated text
        """
        try:
            # Convert OpenAI format to Anthropic format
            system_message = None
            conversation = []
            
            for msg in messages:
                if msg['role'] == 'system':
                    system_message = msg['content']
                else:
                    conversation.append({
                        'role': msg['role'],
                        'content': msg['content']
                    })
            
            response = self.client.messages.create(
                model=self.model,
                system=system_message or "",
                messages=conversation,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error: {str(e)}"


class PromptTemplate:
    """Template for building prompts."""
    
    DEGREE_QA_SYSTEM = """You are PathWise, an intelligent academic advisor specializing in engineering degree programs.

Your role is to help students understand degree requirements, course options, and academic planning.

Guidelines:
1. Answer questions accurately based ONLY on the provided context
2. Always cite your sources using the format [Source: program, document]
3. If information is not in the context, clearly state "I don't have that information" and suggest contacting the official academic advisor
4. Be concise but thorough
5. Use bullet points for clarity when listing requirements
6. Never make up or assume requirements

Remember: You are a helpful tool, not a replacement for official advising. Always include a disclaimer when appropriate."""

    PLANNING_SYSTEM = """You are PathWise, an intelligent degree planning assistant.

Your role is to create personalized academic roadmaps for students.

Guidelines:
1. Use the provided degree requirements and user profile to create a realistic plan
2. Respect all prerequisites and course sequencing
3. When professor ratings are available, prefer higher-rated professors
4. Balance course load across semesters (typically 9-12 credits for MS students)
5. Include explanatory notes about your planning decisions
6. Output your plan in both natural language AND structured JSON format
7. Always note assumptions (e.g., "assuming you pass all courses")

JSON Format:
{
  "semesters": [
    {
      "name": "Fall 2024",
      "courses": [
        {
          "course_code": "COMS 4111",
          "course_name": "Database Systems",
          "credits": 3,
          "prof": "Smith",
          "rating": 4.8,
          "category": "core"
        }
      ]
    }
  ],
  "notes": ["List of planning notes and assumptions"]
}

Always provide actionable, safe recommendations."""

    @staticmethod
    def build_qa_prompt(
        query: str,
        context: str,
        user_profile: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """
        Build a Q&A prompt.
        
        Args:
            query: User question
            context: Retrieved context
            user_profile: Optional user profile
            
        Returns:
            List of messages for LLM
        """
        user_info = ""
        if user_profile:
            user_info = f"\nUser Profile:\n"
            user_info += f"- Program: {user_profile.get('program', 'Not specified')}\n"
            user_info += f"- Catalog Year: {user_profile.get('catalog_year', 'Not specified')}\n"
        
        user_message = f"""Context from degree requirements:
{context}
{user_info}
Question: {query}

Please answer the question using only the information provided in the context above. Include source citations."""
        
        return [
            {"role": "system", "content": PromptTemplate.DEGREE_QA_SYSTEM},
            {"role": "user", "content": user_message}
        ]
    
    @staticmethod
    def build_planning_prompt(
        user_profile: Dict[str, Any],
        requirements_context: str,
        professor_info: str
    ) -> List[Dict[str, str]]:
        """
        Build a planning prompt.
        
        Args:
            user_profile: User profile with program, courses taken, etc.
            requirements_context: Retrieved requirements
            professor_info: Professor ratings information
            
        Returns:
            List of messages for LLM
        """
        user_message = f"""User Profile:
- Program: {user_profile.get('program')}
- Catalog Year: {user_profile.get('catalog_year')}
- Target Graduation: {user_profile.get('target_graduation')}
- Completed Courses: {', '.join(user_profile.get('completed_courses', []))}
- Preferences: {user_profile.get('preference', 'balanced')}

Degree Requirements:
{requirements_context}

Professor Ratings:
{professor_info}

Task:
Create a semester-by-semester course plan for this student. Select the best-rated professors when possible.
Provide your response in two parts:
1. Natural language explanation of your plan
2. JSON structure with the detailed plan

Ensure the plan satisfies all degree requirements."""
        
        return [
            {"role": "system", "content": PromptTemplate.PLANNING_SYSTEM},
            {"role": "user", "content": user_message}
        ]


def create_llm_interface(
    provider: str,
    api_key: str,
    model: Optional[str] = None
) -> LLMInterface:
    """
    Factory function to create an LLM interface.
    
    Args:
        provider: Provider name ('openai' or 'anthropic')
        api_key: API key
        model: Optional model name
        
    Returns:
        LLMInterface instance
    """
    if provider.lower() == 'openai':
        model = model or "gpt-4"
        return OpenAIInterface(api_key, model)
    elif provider.lower() == 'anthropic':
        model = model or "claude-3-sonnet-20240229"
        return AnthropicInterface(api_key, model)
    else:
        raise ValueError(f"Unknown provider: {provider}")


if __name__ == "__main__":
    # Example usage
    print("Example prompt template:")
    messages = PromptTemplate.build_qa_prompt(
        query="What are the core courses for MS in Computer Science?",
        context="[Sample context about degree requirements]",
        user_profile={"program": "MS CS", "catalog_year": 2023}
    )
    
    for msg in messages:
        print(f"\n{msg['role'].upper()}:")
        print(msg['content'][:200] + "...")



