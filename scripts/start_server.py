#!/usr/bin/env python3
"""
Script to start the FastAPI server.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn


def main():
    """Start the FastAPI server."""
    print("Starting PathWise API Server...")
    print("=" * 60)
    print("API Documentation will be available at:")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    print("\nEndpoints:")
    print("  - GET  /health - Health check")
    print("  - POST /ask - Answer degree requirement questions")
    print("  - POST /plan - Generate degree plans")
    print("  - POST /professors - Query professor ratings")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server\n")
    
    # Check if config exists
    config_path = Path("config.py")
    if not config_path.exists():
        print("⚠ Warning: config.py not found!")
        print("  Please copy config_example.py to config.py and fill in your API keys.")
        print("  The server will start but some features may not work without proper config.\n")
    
    # Check if vector DB exists
    vector_db_path = Path("./vector_db")
    if not vector_db_path.exists():
        print("⚠ Warning: Vector database not found!")
        print("  Please run 'python scripts/build_index.py' first to build the indices.")
        print("  The server will start but will not be able to answer questions.\n")
    
    # Start server
    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()



