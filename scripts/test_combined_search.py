#!/usr/bin/env python3
"""
Test combined search across both vector databases.
"""

import os
import sys
import pickle
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sentence_transformers import SentenceTransformer

def search_index(query, index_dir, k=3):
    """Search a vector index."""
    embeddings = np.load(index_dir / "embeddings.npy")
    with open(index_dir / "texts.pkl", 'rb') as f:
        texts = pickle.load(f)
    with open(index_dir / "metadata.pkl", 'rb') as f:
        metadatas = pickle.load(f)
    
    # Load model (reuse if possible)
    if not hasattr(search_index, 'model'):
        search_index.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    model = search_index.model
    
    # Encode query
    query_embedding = model.encode(query)
    
    # Compute similarities
    query_norm = query_embedding / np.linalg.norm(query_embedding)
    doc_norms = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    similarities = np.dot(doc_norms, query_norm)
    
    # Get top-k
    top_indices = np.argsort(similarities)[::-1][:k]
    
    results = []
    for idx in top_indices:
        results.append({
            'text': texts[idx],
            'metadata': metadatas[idx],
            'similarity': float(similarities[idx])
        })
    
    return results

def main():
    """Test combined searches."""
    print("="*60)
    print("PathWise Combined Search Test")
    print("="*60)
    
    # Test professor queries
    print("\n🎓 TEST 1: Professor Queries")
    print("-"*60)
    
    prof_queries = [
        "Best rated professors",
        "Professors with 5.0 rating",
        "Highly rated teachers"
    ]
    
    for query in prof_queries:
        print(f"\nQuery: '{query}'")
        results = search_index(query, Path("vector_db_simple"), k=3)
        for i, r in enumerate(results, 1):
            prof = r['metadata']['professor_name']
            rating = r['metadata']['rating']
            print(f"  {i}. {prof}: {rating:.2f}/5.0 (similarity: {r['similarity']:.3f})")
    
    # Test program queries
    print("\n\n📚 TEST 2: Program Requirement Queries")
    print("-"*60)
    
    program_queries = [
        "What are the requirements for Computer Science?",
        "Master's degree in Data Science",
        "Engineering programs available"
    ]
    
    for query in program_queries:
        print(f"\nQuery: '{query}'")
        results = search_index(query, Path("vector_db_programs"), k=2)
        for i, r in enumerate(results, 1):
            program = r['metadata']['program']
            source = r['metadata']['source']
            text_preview = r['text'][:100].replace('\n', ' ')
            print(f"  {i}. {program}")
            print(f"     Source: {source}")
            print(f"     Text: {text_preview}...")
            print(f"     Similarity: {r['similarity']:.3f}")
    
    print("\n" + "="*60)
    print("✅ Combined search test complete!")
    print("="*60)
    
    print("\n📊 System Summary:")
    print(f"  • Professor Database: 295 professors")
    print(f"  • Programs Database: 110 text chunks from 50 programs")
    print(f"  • Embedding Model: all-MiniLM-L6-v2 (384 dim)")
    print(f"  • Search Method: Cosine similarity")

if __name__ == "__main__":
    main()


