#!/usr/bin/env python3
"""
Script to build vector indices from configuration file.
Usage: python scripts/build_index.py [config_file]
"""
import sys
import traceback
from pathlib import Path

# Access FastAPI source code
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.indexer import build_indices_from_config


def main():
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        # Use default config
        config_path = "data/sample_config.json"

    if not Path(config_path).exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)

    print(f"Building indices from config: {config_path}")
    print("=" * 60)

    try:
        build_indices_from_config(config_path)
        print("\n" + "=" * 60)
        print("✓ Indices built successfully!")
    except Exception as e:
        print(f"\n✗ Error building indices: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
