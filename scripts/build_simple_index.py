#!/usr/bin/env python3
"""
Simplified index builder that works with minimal dependencies.
Only needs: pandas, sentence-transformers (with no-mkl workaround)
"""

import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'  # Workaround for MKL issue

import sys
import json
import pickle
from pathlib import Path
import pandas as pd

print("Loading dependencies...")

try:
    from sentence_transformers import SentenceTransformer
    print("✅ sentence-transformers loaded")
except Exception as e:
    print(f"❌ Error loading sentence-transformers: {e}")
    sys.exit(1)

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def build_culpa_index_simple():
    """Build a simple index from CULPA ratings."""
    print("\n" + "="*60)
    print("Building Simple Vector Index")
    print("="*60)
    
    # Load CULPA data
    culpa_path = "data/processed/culpa_ratings_processed.csv"
    if not Path(culpa_path).exists():
        print(f"❌ Error: {culpa_path} not found")
        print("Run: python scripts/process_culpa_data.py first")
        return False
    
    print(f"\n1. Loading CULPA data from {culpa_path}")
    df = pd.read_csv(culpa_path)
    print(f"   ✓ Loaded {len(df)} professor ratings")
    
    # Create text for each professor
    texts = []
    metadatas = []
    
    for idx, row in df.iterrows():
        prof_name = row.get('prof_name') or row.get('professor_name', 'Unknown')
        rating = row['rating']
        course_code = row.get('course_code', '')
        tags = row.get('tags', '')
        
        # Create text representation
        text = f"Professor {prof_name}. "
        if course_code:
            text += f"Teaches {course_code}. "
        text += f"CULPA Rating: {rating}/5.0. "
        if tags:
            text += f"Student feedback: {tags}"
        
        texts.append(text)
        metadatas.append({
            'professor_name': prof_name,
            'rating': float(rating),
            'course_code': course_code,
            'doc_type': 'professor_rating'
        })
    
    # Load embedding model
    print("\n2. Loading embedding model...")
    print("   (This may download ~100MB on first run)")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    print("   ✓ Model loaded")
    
    # Generate embeddings
    print(f"\n3. Generating embeddings for {len(texts)} professors...")
    embeddings = model.encode(texts, show_progress_bar=True)
    print(f"   ✓ Generated {embeddings.shape} embeddings")
    
    # Save simple index
    output_dir = Path("vector_db_simple")
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n4. Saving index to {output_dir}")
    
    # Save embeddings
    import numpy as np
    np.save(output_dir / "embeddings.npy", embeddings)
    
    # Save texts and metadata
    with open(output_dir / "texts.pkl", 'wb') as f:
        pickle.dump(texts, f)
    
    with open(output_dir / "metadata.pkl", 'wb') as f:
        pickle.dump(metadatas, f)
    
    # Save model info
    info = {
        'model_name': 'sentence-transformers/all-MiniLM-L6-v2',
        'num_documents': len(texts),
        'embedding_dim': embeddings.shape[1],
        'index_type': 'simple_numpy'
    }
    
    with open(output_dir / "index_info.json", 'w') as f:
        json.dump(info, indent=2, fp=f)
    
    print("   ✓ Saved embeddings.npy")
    print("   ✓ Saved texts.pkl")
    print("   ✓ Saved metadata.pkl")
    print("   ✓ Saved index_info.json")
    
    print("\n" + "="*60)
    print("✅ Simple Vector Index Built Successfully!")
    print("="*60)
    print(f"\nIndex location: {output_dir}")
    print(f"Total documents: {len(texts)}")
    print(f"Embedding dimension: {embeddings.shape[1]}")
    
    print("\nNext steps:")
    print("  1. Test search: python scripts/test_simple_search.py")
    print("  2. Start API: python scripts/start_server.py")
    
    return True


def main():
    """Main function."""
    try:
        success = build_culpa_index_simple()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


