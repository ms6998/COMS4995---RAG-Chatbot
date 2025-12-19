# PathWise - LLM-Powered Degree Advisor

PathWise is an intelligent academic advising system that uses Retrieval-Augmented Generation (RAG) to help engineering students navigate degree requirements, plan their academic path, and select courses taught by highly-rated professors.

## 🎯 Features

- **Degree Requirements Q&A**: Natural language interface to query degree requirements
- **Personalized Academic Planning**: Generate semester-by-semester course roadmaps
- **Professor-Aware Recommendations**: Automatically suggest highly-rated professors
- **Source Citations**: All answers include citations to official documents
- **Multi-Program Support**: Handles multiple programs (MS CS, MS Data Science, etc.)

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key (for LLM functionality)
- ~2GB disk space for models and vector database

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd COMS4995---RAG-Chatbot
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

```bash
cp config_example.py config.py
# Edit config.py and add your OpenAI API key
```

### 5. Build Vector Indices

```bash
python scripts/build_index.py data/sample/index_config.json
```

This will:
- Process degree requirement documents
- Generate embeddings
- Build vector database indices
- Index professor ratings

### 6. Start the API Server

```bash
python scripts/start_server.py
```

The server will start at `http://localhost:8000`

### 7. Test the System

In a new terminal:

```bash
python scripts/test_rag.py  # Test RAG components
python tests/test_api.py     # Test API endpoints
```

## 📚 API Documentation

Once the server is running, visit:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

### Key Endpoints

#### 1. Question Answering - `/ask`

Ask questions about degree requirements:

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the core courses for MS in Computer Science?",
    "user_profile": {
      "program": "MS Computer Science",
      "catalog_year": 2023
    }
  }'
```

#### 2. Degree Planning - `/plan`

Generate a personalized academic plan:

```bash
curl -X POST "http://localhost:8000/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "user_profile": {
      "program": "MS Computer Science",
      "catalog_year": 2023,
      "target_graduation": "Spring 2026",
      "completed_courses": ["COMS 4111"],
      "preference": "best_professors"
    },
    "num_semesters": 3
  }'
```

#### 3. Professor Ratings - `/professors`

Query professor ratings for specific courses:

```bash
curl -X POST "http://localhost:8000/professors" \
  -H "Content-Type: application/json" \
  -d '{
    "course_codes": ["COMS 4111", "COMS 4701"]
  }'
```

## 🏗️ Project Structure

```
COMS4995---RAG-Chatbot/
├── src/
│   ├── rag/                    # RAG system components
│   │   ├── document_processor.py   # Document extraction & chunking
│   │   ├── embeddings.py           # Embedding generation
│   │   ├── vector_store.py         # Vector database (Chroma)
│   │   ├── retriever.py            # Retrieval logic
│   │   ├── indexer.py              # Index building
│   │   └── llm_interface.py        # LLM integration
│   └── api/                    # FastAPI application
│       ├── app.py                  # Main API server
│       └── models.py               # Pydantic models
├── data/
│   ├── sample/                 # Sample data
│   │   ├── ms_cs_requirements.txt
│   │   ├── ms_ds_requirements.txt
│   │   ├── prof_ratings.csv
│   │   └── index_config.json
│   ├── raw/                    # Raw documents (PDFs, etc.)
│   └── processed/              # Processed data
├── scripts/
│   ├── build_index.py          # Build vector indices
│   ├── test_rag.py             # Test RAG components
│   └── start_server.py         # Start API server
├── tests/
│   └── test_api.py             # API endpoint tests
├── vector_db/                  # Vector database storage
├── requirements.txt
├── config_example.py
└── README.md
```

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Model Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "gpt-4"
LLM_TEMPERATURE = 0.3

# Vector Database
VECTOR_DB_TYPE = "chroma"
VECTOR_DB_PATH = "./vector_db"

# Retrieval
TOP_K_RETRIEVAL = 5
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100
```

## 📊 Adding Your Own Data

### Using Real CULPA Ratings (NEW!)

If you have real CULPA ratings data from Columbia:

```bash
# 1. Place culpa_ratings.csv in documents/ folder
# 2. Process the data
python scripts/process_culpa_data.py

# 3. Rebuild index with real ratings
python scripts/build_index.py data/culpa_index_config.json
```

See `INTEGRATION_GUIDE.md` for detailed instructions on integrating CULPA data and Spring semester courses.

### 1. Prepare Documents

Add your degree requirement documents to `data/raw/`:
- PDFs, HTML, or TXT files
- Organized by program/year

### 2. Create Index Configuration

Create a JSON config file (see `data/sample/index_config.json`):

```json
{
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "degree_requirements": {
    "collection_name": "degree_requirements",
    "documents": [
      {
        "file_path": "data/raw/your_program.pdf",
        "program": "Your Program Name",
        "degree": "MS",
        "catalog_year": 2024
      }
    ]
  },
  "professor_ratings": {
    "collection_name": "professor_ratings",
    "ratings_file": "data/your_ratings.csv"
  }
}
```

### 3. Build Indices

```bash
python scripts/build_index.py path/to/your_config.json
```

## 🧪 RAG System Components

### Document Processing

- Extracts text from PDFs, HTML, and text files
- Chunks documents with overlapping windows (600 tokens, 100 overlap)
- Preserves metadata (program, year, source)
- Extracts course codes automatically

### Embeddings

- Uses sentence-transformers for local embedding generation
- Default model: `all-MiniLM-L6-v2` (384 dimensions)
- Supports OpenAI embeddings as alternative

### Vector Store

- Supports ChromaDB (default)
- Efficient similarity search with metadata filtering
- Persistent storage

### Retrieval

- Semantic search using cosine similarity
- Metadata filtering by program, year, etc.
- Context formatting for LLM prompts

### LLM Integration

- Supports OpenAI (GPT-4, GPT-3.5)
- Supports Anthropic Claude
- Structured prompts for Q&A and planning

## 📝 Example Use Cases

### 1. Check Degree Requirements

```text
Q: "What are the core courses for MS in Computer Science?"
A: Returns specific courses with citations to the bulletin.
```

### 2. Verify Course Eligibility

```text
Q: "Does COMS 4995 count as a technical elective?"
A: Checks requirements and provides official guidance.
```

### 3. Plan Your Degree

```text
Input: Program, year, completed courses, preferences
Output: 4-semester plan with best-rated professors
```

### 4. Find Best Professors

```text
Q: "Who are the top-rated professors for Database Systems?"
A: Ranked list with ratings and student feedback tags.
```

## 🔍 Testing

### Test RAG Components

```bash
python scripts/test_rag.py
```

Tests:
- Document retrieval accuracy
- Embedding quality
- Professor rating queries
- Context formatting

### Test API Endpoints
```bash
# Start server first
python scripts/start_server.py

# In another terminal
python tests/test_api.py
```

## 🎓 Academic Context

This project was developed for COMS 4995 - Applied Machine Learning at Columbia University.

### Key Concepts Demonstrated

- **RAG (Retrieval-Augmented Generation)**: Combines information retrieval with LLM generation
- **Semantic Search**: Uses embeddings for meaning-based retrieval
- **Prompt Engineering**: Structured prompts for accurate, safe responses
- **API Design**: RESTful API with proper validation and error handling

### Alignment with Course Trends

- Self-improving agents (LLM learns from retrieved context)
- RLAIF potential (AI-generated training data for fine-tuning)
- Multimodal capabilities (can extend to process diagrams, flowcharts)
- Parameter-efficient approaches (uses pre-trained models via API)

## ⚠️ Limitations & Disclaimers

1. **Not Official Advising**: This tool is for guidance only. Always verify with official academic advisors.
2. **Data Currency**: Information is only as current as the indexed documents.
3. **LLM Limitations**: May occasionally hallucinate or misinterpret context.
4. **Professor Ratings**: Based on limited, potentially biased sample data.

## 🚧 Future Enhancements

- [ ] Fine-tuning on domain-specific data
- [ ] Real-time professor rating integration (RateMyProfessors API)
- [ ] Visual roadmap generation (Mermaid diagrams)
- [ ] Multi-turn conversation support
- [ ] Course prerequisite validation
- [ ] Frontend web interface (React/Streamlit)
- [ ] User authentication and saved plans
- [ ] Integration with university course catalog APIs

## 📄 License

MIT License - see LICENSE file for details.

## 👥 Contributors

- Mingjun Sun - RAG System Implementation
- Colin Payne-Rogers - Document retrieval, backend integration, docker setup

## 📧 Contact

For questions or issues:

- Open a GitHub issue
- Contact: [ms6998@columbia.edu]

---

**Note**: Remember to add your actual API keys to `config.py` before running the system!
