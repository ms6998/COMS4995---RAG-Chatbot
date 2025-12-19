#!/usr/bin/env python3
"""Convert numpy vector databases to ChromaDB format."""

import numpy as np
import pickle
from pathlib import Path
import chromadb
from chromadb.config import Settings

def convert_to_chroma(numpy_dir, chroma_dir, collection_name):
    """Convert numpy format to ChromaDB."""
    
    print(f"\n{'='*60}")
    print(f"Converting {numpy_dir} to ChromaDB")
    print(f"{'='*60}")
    
    # Load numpy data
    print(f"Loading data from {numpy_dir}...")
    embeddings = np.load(Path(numpy_dir) / "embeddings.npy")
    
    with open(Path(numpy_dir) / "texts.pkl", 'rb') as f:
        texts = pickle.load(f)
    
    with open(Path(numpy_dir) / "metadata.pkl", 'rb') as f:
        metadatas = pickle.load(f)
    
    print(f"✓ Loaded {len(embeddings)} documents")
    
    # Initialize ChromaDB
    print(f"Creating ChromaDB in {chroma_dir}...")
    Path(chroma_dir).mkdir(parents=True, exist_ok=True)
    
    client = chromadb.PersistentClient(
        path=chroma_dir,
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Delete collection if it exists
    try:
        client.delete_collection(collection_name)
        print(f"✓ Deleted existing collection: {collection_name}")
    except:
        pass
    
    # Create new collection
    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    print(f"✓ Created collection: {collection_name}")
    
    # Add documents in batches
    batch_size = 100
    total_batches = (len(texts) - 1) // batch_size + 1
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_embeddings = embeddings[i:i+batch_size].tolist()
        batch_metadata = metadatas[i:i+batch_size]
        batch_ids = [f"doc_{j}" for j in range(i, i+len(batch_texts))]
        
        collection.add(
            documents=batch_texts,
            embeddings=batch_embeddings,
            metadatas=batch_metadata,
            ids=batch_ids
        )
        
        batch_num = i // batch_size + 1
        print(f"  ✓ Added batch {batch_num}/{total_batches} ({len(batch_texts)} docs)")
    
    print(f"✅ Converted {len(texts)} documents to ChromaDB collection '{collection_name}'")
    return True

if __name__ == "__main__":
    print("\n🔄 Converting Vector Databases to ChromaDB Format\n")
    
    # Convert professors
    convert_to_chroma(
        numpy_dir="./vector_db_simple",
        chroma_dir="./vector_db",
        collection_name="professor_ratings"
    )
    
    # Convert programs
    convert_to_chroma(
        numpy_dir="./vector_db_programs",
        chroma_dir="./vector_db",
        collection_name="degree_requirements"
    )
    
    print(f"\n{'='*60}")
    print("✅ ALL DATA CONVERTED TO CHROMADB!")
    print(f"{'='*60}")
    print("\nYour backend is now ready to use ChromaDB.")
    print("Restart the server: python scripts/start_server.py")