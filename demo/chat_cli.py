#!/usr/bin/env python3
"""
Simple command-line chatbot demo.
Run this to test the chatbot without a web interface.
"""

import requests
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

API_URL = "http://localhost:8000"

def chat():
    """Run interactive chatbot."""
    print("=" * 60)
    print("PathWay Chatbot Demo")
    print("=" * 60)
    print("\nType your questions about MS programs.")
    print("Commands: 'quit' to exit, 'help' for examples\n")

    # User profile (optional)
    profile = {
        "program": "MS Computer Science",
        "catalog_year": 2023
    }

    while True:
        try:
            question = input("\n🎓 You: ").strip()

            if not question:
                continue

            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye! 👋")
                break

            if question.lower() == 'help':
                print_help()
                continue

            # Send to chatbot
            print("🤖 Bot: ", end="", flush=True)

            response = requests.post(
                f"{API_URL}/ask",
                json={
                    "question": question,
                    "user_profile": profile
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                print(data['answer'])

                # Show sources
                if data.get('sources'):
                    print(f"\n   📚 Sources: {len(data['sources'])} documents")
            else:
                print(f"Error: {response.status_code}")
                print(response.text)

        except requests.exceptions.ConnectionError:
            print("\n❌ Error: Cannot connect to chatbot backend!")
            print("   Make sure the server is running:")
            print("   python scripts/start_server.py")
            break
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def print_help():
    """Print example questions."""
    print("\n" + "=" * 60)
    print("Example Questions:")
    print("=" * 60)
    print("1. What are the core courses for MS in Computer Science?")
    print("2. How many credits do I need to graduate?")
    print("3. Can I transfer credits from another university?")
    print("4. What is the GPA requirement?")
    print("5. What are the elective options?")
    print("=" * 60)


def test_connection():
    """Test if the server is running."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server Status: {data['status']}")
            print(f"   Embedder: {'✅' if data['embedder_loaded'] else '❌'}")
            print(f"   Vector Store: {'✅' if data['vector_store_connected'] else '❌'}")
            return True
        return False
    except:
        return False


def main():
    """Main function."""
    print("Checking server connection...")

    if not test_connection():
        print("\n❌ Cannot connect to chatbot backend!")
        print("\nPlease start the server first:")
        print("  python scripts/start_server.py")
        print("\nThen run this script again.")
        sys.exit(1)

    print()
    chat()


if __name__ == "__main__":
    main()
