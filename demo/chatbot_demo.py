#!/usr/bin/env python3
"""
Interactive chatbot demo using LangChain RAG.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.langchain_rag import create_pathwise_rag


def main():
    """Run interactive chatbot."""
    print("="*60)
    print("PathWise Chatbot - LangChain RAG Demo")
    print("="*60)
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n❌ OpenAI API key not found!")
        print("\nPlease set your API key:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("\nOr create config.py with your key")
        sys.exit(1)
    
    # Initialize RAG
    print("\nInitializing RAG system...")
    try:
        rag = create_pathwise_rag(api_key, model_name="gpt-3.5-turbo")
    except Exception as e:
        print(f"❌ Error initializing RAG: {e}")
        sys.exit(1)
    
    print("\n✅ Chatbot ready!")
    print("\nType your questions (or 'quit' to exit, 'help' for examples)")
    print("="*60)
    
    while True:
        try:
            print("\n🎓 You: ", end="")
            question = input().strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye! 👋")
                break
            
            if question.lower() == 'help':
                print_examples()
                continue
            
            # Detect query type
            if any(word in question.lower() for word in ['professor', 'teacher', 'instructor', 'rating']):
                query_type = "professor"
            elif any(word in question.lower() for word in ['requirement', 'course', 'program', 'degree', 'credit']):
                query_type = "program"
            else:
                query_type = "general"
            
            # Get answer
            print("\n🤖 PathWise: ", end="", flush=True)
            
            result = rag.answer_question(question, query_type=query_type)
            print(result['answer'])
            
            # Show sources
            if result.get('sources'):
                print(f"\n   📚 {result['num_sources']} sources used")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def print_examples():
    """Print example questions."""
    print("\n" + "="*60)
    print("Example Questions:")
    print("="*60)
    print("\n📚 Program Requirements:")
    print("  • What are the core courses for MS in Computer Science?")
    print("  • How many credits do I need for Data Science?")
    print("  • What are the elective options?")
    print("\n🎓 Professor Queries:")
    print("  • Who are the best-rated professors?")
    print("  • Show me professors with 5.0 ratings")
    print("  • Which professors teach databases?")
    print("\n📅 Planning:")
    print("  • Help me plan my MS CS degree")
    print("  • What courses should I take in my first semester?")
    print("="*60)


if __name__ == "__main__":
    main()


