#!/usr/bin/env python3
"""
Build vector index for program documents.
Uses simple numpy-based storage (no FAISS dependency).
"""

import os
import sys
import json
import pickle
from pathlib import Path
import pandas as pd
import numpy as np
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent.parent))

from sentence_transformers import SentenceTransformer

def read_text_file(file_path):
    """Read text from file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            print(f"  ⚠️  Error reading {file_path}: {e}")
            return ""

def clean_text(text):
    """Basic text cleaning."""
    import re
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_text(text, chunk_size=500, overlap=100):
    """Split text into chunks."""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if len(chunk) > 50:  # Minimum chunk size
            chunks.append(chunk)
    
    return chunks if chunks else [text]

def build_programs_index():
    """Build index from program documents."""
    print("\n" + "="*60)
    print("Building Programs Vector Index")
    print("="*60)
    
    programs_dir = Path("data/raw/programs")
    if not programs_dir.exists():
        print(f"\n❌ Programs folder not found: {programs_dir}")
        print("Please make sure the programs folder is extracted to data/raw/")
        return False
    
    # Find all text and HTML files
    files = list(programs_dir.glob("*.txt")) + list(programs_dir.glob("*.html"))
    print(f"\n1. Found {len(files)} program documents")
    
    # Process documents
    all_texts = []
    all_metadata = []
    
    print("\n2. Processing documents...")
    for file_path in tqdm(files[:50]):  # Limit to 50 for now
        text = read_text_file(file_path)
        if not text:
            continue
        
        text = clean_text(text)
        chunks = chunk_text(text, chunk_size=500, overlap=100)
        
        program_name = file_path.stem.replace('_', ' ').title()
        
        for i, chunk in enumerate(chunks):
            all_texts.append(chunk)
            all_metadata.append({
                'source': file_path.name,
                'program': program_name,
                'chunk_id': f"{file_path.stem}_{i}",
                'doc_type': 'degree_requirement'
            })
    
    print(f"   ✓ Created {len(all_texts)} text chunks")
    
    # Load model
    print("\n3. Loading embedding model...")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    print("   ✓ Model loaded")
    
    # Generate embeddings
    print(f"\n4. Generating embeddings...")
    embeddings = model.encode(all_texts, show_progress_bar=True, batch_size=32)
    print(f"   ✓ Generated {embeddings.shape} embeddings")
    
    # Save index
    output_dir = Path("vector_db_programs")
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n5. Saving index to {output_dir}")
    np.save(output_dir / "embeddings.npy", embeddings)
    
    with open(output_dir / "texts.pkl", 'wb') as f:
        pickle.dump(all_texts, f)
    
    with open(output_dir / "metadata.pkl", 'wb') as f:
        pickle.dump(all_metadata, f)
    
    info = {
        'model_name': 'sentence-transformers/all-MiniLM-L6-v2',
        'num_documents': len(all_texts),
        'embedding_dim': embeddings.shape[1],
        'index_type': 'simple_numpy'
    }
    
    with open(output_dir / "index_info.json", 'w') as f:
        json.dump(info, indent=2, fp=f)
    
    print("   ✓ Index saved")
    
    print("\n" + "="*60)
    print("✅ Programs Vector Index Built Successfully!")
    print("="*60)
    print(f"\nTotal chunks indexed: {len(all_texts)}")
    print(f"From {len(files[:50])} program documents")
    
    return True

if __name__ == "__main__":
    try:
        build_programs_index()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

