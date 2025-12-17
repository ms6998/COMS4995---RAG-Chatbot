#!/usr/bin/env python3
"""
Script to index all program documents from Colin's programs folder.
This will automatically scan the folder and index all documents.
"""

import sys
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def scan_programs_folder(programs_dir):
    """
    Scan the programs folder and create document list.
    
    Args:
        programs_dir: Path to programs folder
        
    Returns:
        List of document configurations
    """
    programs_path = Path(programs_dir)
    
    if not programs_path.exists():
        print(f"❌ Error: Programs folder not found: {programs_dir}")
        print("\nPlease download Colin's programs folder from Google Drive:")
        print("https://drive.google.com/drive/folders/1djwskyPBs211TZFumsCnimOkzkDZ-13G")
        print("\nAnd extract it to: data/raw/programs/")
        return []
    
    documents = []
    
    # Find all supported document files
    supported_extensions = ['.pdf', '.txt', '.html', '.htm']
    
    for ext in supported_extensions:
        for file_path in programs_path.rglob(f'*{ext}'):
            # Extract program name from path or filename
            relative_path = file_path.relative_to(programs_path)
            program_name = relative_path.parts[0] if len(relative_path.parts) > 1 else file_path.stem
            
            # Try to infer degree type from filename/path
            file_lower = str(file_path).lower()
            if 'master' in file_lower or 'ms' in file_lower:
                degree = 'MS'
            elif 'phd' in file_lower or 'doctor' in file_lower:
                degree = 'PhD'
            elif 'bachelor' in file_lower or 'bs' in file_lower:
                degree = 'BS'
            else:
                degree = 'MS'  # Default
            
            doc_config = {
                "file_path": str(file_path),
                "program": program_name.replace('_', ' ').title(),
                "degree": degree,
                "catalog_year": 2024,  # Current year
                "source_url": f"https://www.engineering.columbia.edu/academics/programs/{program_name}"
            }
            
            documents.append(doc_config)
    
    return documents


def create_full_index_config(programs_dir, output_file):
    """
    Create a complete index configuration including programs and CULPA data.
    
    Args:
        programs_dir: Path to programs folder
        output_file: Where to save the config
    """
    print("=" * 60)
    print("Creating Full Index Configuration")
    print("=" * 60)
    
    # Scan programs folder
    print(f"\nScanning programs folder: {programs_dir}")
    documents = scan_programs_folder(programs_dir)
    
    if not documents:
        print("\n❌ No documents found!")
        return False
    
    print(f"✓ Found {len(documents)} program documents")
    
    # Show program breakdown
    programs_found = set(doc['program'] for doc in documents)
    print(f"\nPrograms found: {len(programs_found)}")
    for program in sorted(programs_found)[:10]:
        print(f"  • {program}")
    if len(programs_found) > 10:
        print(f"  ... and {len(programs_found) - 10} more")
    
    # Create full config
    config = {
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "chunk_size": 600,
        "chunk_overlap": 100,
        "vector_db": {
            "type": "chroma",
            "persist_directory": "./vector_db"
        },
        "degree_requirements": {
            "collection_name": "degree_requirements",
            "documents": documents
        },
        "professor_ratings": {
            "collection_name": "culpa_professor_ratings",
            "ratings_file": "data/processed/culpa_ratings_processed.csv"
        }
    }
    
    # Save config
    with open(output_file, 'w') as f:
        json.dump(config, indent=2, fp=f)
    
    print(f"\n✓ Configuration saved to: {output_file}")
    print("\nNext steps:")
    print(f"  1. Install dependencies: pip install -r requirements.txt")
    print(f"  2. Build index: python scripts/build_index.py {output_file}")
    print(f"  3. Test system: python scripts/test_rag.py")
    
    return True


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Index program documents from Colin's programs folder"
    )
    parser.add_argument(
        '--programs-dir',
        default='data/raw/programs',
        help='Path to programs folder (default: data/raw/programs)'
    )
    parser.add_argument(
        '--output',
        default='data/full_index_config.json',
        help='Output config file (default: data/full_index_config.json)'
    )
    
    args = parser.parse_args()
    
    success = create_full_index_config(args.programs_dir, args.output)
    
    if not success:
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ Ready to build complete RAG system!")
    print("=" * 60)


if __name__ == "__main__":
    main()

