"""
Configuration example file.
Copy this to config.py and fill in your actual values.
"""

# API Keys
OPENAI_API_KEY = "your_openai_api_key_here"
ANTHROPIC_API_KEY = "your_anthropic_api_key_here"

# Model Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "gpt-4"
LLM_TEMPERATURE = 0.3
MAX_TOKENS = 2000

# Vector Database
VECTOR_DB_TYPE = "chroma"  # or "faiss"
VECTOR_DB_PATH = "./vector_db"
COLLECTION_NAME_REQUIREMENTS = "degree_requirements"
COLLECTION_NAME_PROFESSORS = "professor_ratings"

# Chunking Configuration
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100

# Retrieval Configuration
TOP_K_RETRIEVAL = 5
SIMILARITY_THRESHOLD = 0.7

# Server Configuration
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True
