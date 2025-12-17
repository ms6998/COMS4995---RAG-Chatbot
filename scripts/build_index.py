#!/usr/bin/env python3
"""
Script to build vector indices from configuration file.
Usage: python scripts/build_index.py [config_file]
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.indexer import build_indices_from_config


def main():
    """Main function."""
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        # Use default config
        config_path = "data/sample/index_config.json"
    
    if not Path(config_path).exists():
        print(f"Error: Config file not found: {config_path}")
        print(f"\nUsage: python {sys.argv[0]} [config_file]")
        print(f"Example: python {sys.argv[0]} data/sample/index_config.json")
        sys.exit(1)
    
    print(f"Building indices from config: {config_path}")
    print("=" * 60)
    
    try:
        build_indices_from_config(config_path)
        print("\n" + "=" * 60)
        print("✓ Indices built successfully!")
        print("\nYou can now start the API server:")
        print("  python -m uvicorn src.api.app:app --reload")
    except Exception as e:
        print(f"\n✗ Error building indices: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


