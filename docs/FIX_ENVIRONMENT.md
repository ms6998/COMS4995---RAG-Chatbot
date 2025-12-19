# Environment Repair Quick Guide

## 🔍 Problem Diagnosis

Your Anaconda environment has some corrupted libraries (torch, mkl).

## ✅ Recommended Solution: Create a New Environment (Fastest & Most Stable)

### Run these commands in your terminal:

```bash
# 1. Create a new clean environment
conda create -n pathwise python=3.9 -y

# 2. Activate the new environment
conda activate pathwise

# 3. Install dependencies (use conda, precompiled versions)
conda install -c pytorch -c conda-forge sentence-transformers faiss-cpu pandas -y

# 4. Install remaining dependencies (use pip)
pip install pypdf beautifulsoup4 lxml

# 5. Verify installation
python -c "import sentence_transformers, faiss, pandas; print('✅ Ready!')"

Then build the Vector Database:

cd /Users/mingjunsun/Desktop/COMS4995---RAG-Chatbot

# Build the index
python scripts/build_simple_index.py

# Test search
python scripts/test_simple_search.py

🎯 Why do this?
	•	✅ Avoid conflicts in the existing environment
	•	✅ Use precompiled packages (no compilation needed)
	•	✅ Clean start
	•	✅ Takes about 5 minutes

📋 Full Command (Copy & Paste)

# One-click create and install
conda create -n pathwise python=3.9 -y && \
conda activate pathwise && \
conda install -c pytorch -c conda-forge sentence-transformers faiss-cpu pandas -y && \
pip install pypdf beautifulsoup4 lxml && \
cd /Users/mingjunsun/Desktop/COMS4995---RAG-Chatbot && \
python scripts/build_simple_index.py

🔄 Future Use

Activate the environment before each use:

conda activate pathwise
cd /Users/mingjunsun/Desktop/COMS4995---RAG-Chatbot
python scripts/start_server.py

🆘 If It Still Doesn’t Work

Use Google Colab:
	1.	Upload Build_Vector_DB_Colab.ipynb to Colab
	2.	Build the vector database in the cloud
	3.	Download the built vector_db_simple.zip
	4.	Extract it into the project folder

⸻

Recommended to try the new environment solution first! It should resolve the issue quickly.

