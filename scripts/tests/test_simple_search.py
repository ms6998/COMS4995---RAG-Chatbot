#!/usr/bin/env python3
"""
Test the simple vector index.
"""

import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import sys
import pickle
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sentence_transformers import SentenceTransformer

def search(query, k=5):
    """Search the simple index."""
    print(f"\n🔍 Searching for: '{query}'")

    # Load index
    index_dir = Path("vector_db_simple")

    embeddings = np.load(index_dir / "embeddings.npy")
    with open(index_dir / "texts.pkl", 'rb') as f:
        texts = pickle.load(f)
    with open(index_dir / "metadata.pkl", 'rb') as f:
        metadatas = pickle.load(f)

    # Load model
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    # Encode query
    query_embedding = model.encode(query)

    # Compute similarities (cosine)
    query_norm = query_embedding / np.linalg.norm(query_embedding)
    doc_norms = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    similarities = np.dot(doc_norms, query_norm)

    # Get top-k
    top_indices = np.argsort(similarities)[::-1][:k]

    print(f"\n📊 Top {k} Results:")
    print("="*60)

    for i, idx in enumerate(top_indices, 1):
        print(f"\n{i}. Similarity: {similarities[idx]:.3f}")
        print(f"   {texts[idx][:150]}...")
        print(f"   Professor: {metadatas[idx]['professor_name']}")
        print(f"   Rating: {metadatas[idx]['rating']}/5.0")


def main():
    """Test searches."""
    print("="*60)
    print("PathWise Simple Search Test")
    print("="*60)

    # Check if index exists
    if not Path("vector_db_simple").exists():
        print("\n❌ Index not found!")
        print("Build it first: python scripts/build_simple_index.py")
        sys.exit(1)

    # Test queries
    queries = [
        "Who are the best professors?",
        "Highly rated teachers",
        "Professors with 5.0 rating"
    ]

    for query in queries:
        search(query, k=5)

    print("\n" + "="*60)
    print("✅ Search test complete!")
    print("="*60)


if __name__ == "__main__":
    main()
