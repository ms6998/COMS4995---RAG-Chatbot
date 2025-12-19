"""Test if vector database has data"""
import numpy as np

# Check simple DB (professor ratings)
print("=" * 60)
print("Checking vector_db_simple (Professor Ratings)")
print("=" * 60)
try:
    embeddings = np.load('vector_db_simple/embeddings.npy')
    print(f"✅ Found {len(embeddings)} embeddings")
    print(f"   Embedding dimension: {embeddings.shape[1] if len(embeddings) > 0 else 0}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("Checking vector_db_programs (Program Requirements)")
print("=" * 60)
try:
    embeddings = np.load('vector_db_programs/embeddings.npy')
    print(f"✅ Found {len(embeddings)} embeddings")
    print(f"   Embedding dimension: {embeddings.shape[1] if len(embeddings) > 0 else 0}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("DIAGNOSIS")
print("=" * 60)
