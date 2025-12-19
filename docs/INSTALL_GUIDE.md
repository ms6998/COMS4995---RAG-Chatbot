# Dependency Installation Guide

## 🔧 Problem Diagnosis

The previous error occurred because `grpcio` needed to be compiled, but `Python.h` was missing.

## 🎯 Solutions (choose one)

### Option 1: Use FAISS (simplest, recommended) ✅

FAISS is lighter-weight, does not require grpcio, and installs quickly:

```bash
cd /Users/mingjunsun/Desktop/COMS4995---RAG-Chatbot

# Install core dependencies
pip install sentence-transformers faiss-cpu beautifulsoup4 lxml

# Modify config to use FAISS

Then edit data/full_index_config.json:

"vector_db": {
  "type": "faiss",  // change to faiss
  "persist_directory": "./vector_db"
}

Option 2: Use precompiled ChromaDB

pip install chromadb==0.4.15 --no-build-isolation

If that still fails, try:

pip install chromadb --only-binary :all:

Option 3: Use Conda (most stable)

# Create a new environment (optional but recommended)
conda create -n pathwise python=3.9
conda activate pathwise

# Install dependencies
conda install -c conda-forge sentence-transformers chromadb
conda install -c conda-forge beautifulsoup4 lxml pypdf pandas

Option 4: Minimal install (for testing)

Install only the necessary packages and temporarily skip the vector DB:

pip install pandas numpy sentence-transformers beautifulsoup4 lxml pypdf

Process the data first, then install the vector DB later when needed.

✅ Verify Installation

Run this to check which packages are installed:

cd /Users/mingjunsun/Desktop/COMS4995---RAG-Chatbot
python << 'EOF'
import sys
packages = {
    'sentence_transformers': 'Embeddings',
    'chromadb': 'ChromaDB (optional)',
    'faiss': 'FAISS (optional)',
    'pandas': 'Data processing',
    'pypdf': 'PDF processing',
    'bs4': 'HTML processing'
}

print("Package Status Check:")
print("=" * 60)
for package, desc in packages.items():
    try:
        __import__(package)
        print(f"✅ {package:20s} - {desc}")
    except ImportError:
        print(f"❌ {package:20s} - {desc} (NOT INSTALLED)")
print("=" * 60)
EOF

🚀 My Recommended Workflow

Step 1: Install base packages (fast)

pip install pandas numpy beautifulsoup4 lxml pypdf tqdm

Step 2: Install embeddings (may take a few minutes)

pip install sentence-transformers

Step 3: Choose a Vector DB

Option A – FAISS (recommended, fast):

pip install faiss-cpu

Option B – ChromaDB (more features):

# Try this first
pip install chromadb --only-binary :all:

# If it fails, use conda
conda install -c conda-forge chromadb

🐛 Common Issues

Q1: sentence-transformers installs very slowly

# Use Tsinghua mirror for faster installs
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple sentence-transformers

Q2: grpcio compilation fails

# Skip ChromaDB and use FAISS
pip install faiss-cpu

# Or install precompiled grpcio
pip install grpcio --only-binary :all:

Q3: Permission errors

pip install --user sentence-transformers faiss-cpu

Q4: Dependency conflicts

# Create a new conda environment
conda create -n pathwise python=3.9
conda activate pathwise
pip install -r requirements.txt

📦 Full Dependency List (requirements-minimal.txt)

If you want a minimal install, here is a slimmed-down version:

# Save this as requirements-minimal.txt
pandas>=1.4.0
numpy>=1.21.0
sentence-transformers>=2.2.0
faiss-cpu>=1.7.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
pypdf>=3.0.0
tqdm>=4.62.0

Install:

pip install -r requirements-minimal.txt

🎯 Quick Start (skip API)

If you only want to test core RAG functionality without FastAPI:

# Install only RAG core dependencies
pip install sentence-transformers faiss-cpu pandas pypdf beautifulsoup4 lxml

# Test data processing
python scripts/process_culpa_data.py documents/culpa_ratings.csv

# Test document indexing
python scripts/index_programs.py

✅ Success Indicator

After successful installation, this command should run:

python -c "from sentence_transformers import SentenceTransformer; print('✅ Ready to build RAG system!')"

🆘 If Nothing Works

Last resort — use Docker:

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EOF

# Build and run
docker build -t pathwise .
docker run -it pathwise bash


⸻

Recommended Order of Execution
	1.	Try Option 1 (FAISS) first — fastest and simplest
	2.	If you need ChromaDB features, try Option 2
	3.	If both fail, use Option 3 (Conda)
	4.	As a fallback, use Option 4 to test data processing first

After choosing an option, tell me and I can help you continue!

