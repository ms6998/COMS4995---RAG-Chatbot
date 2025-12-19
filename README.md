# PathWise - LLM-Powered Degree Advisor

PathWise is an intelligent academic advising system that uses Retrieval-
Augmented Generation (RAG) to help engineering students navigate degree
requirements, plan their academic path, and select courses taught by
highly-rated professors.

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

## 🚀 Quick Start with Docker

Using Docker is recommended. All you need to do is:

### 1. Clone Repo

```bash
git clone <repository-url>
cd COMS4995---RAG-Chatbot
```

### 2. Configure API Keys

```bash
cp config_example.py config.py
# Edit config.py and add your Gemini API key
```

### 3. Build and run the Backend Image

Building the image also builds the document index. In the future, these steps
would be separate, but, the corpus is small enough that it can be incorporated
into the running backend image

```bash
docker compose run --remove-orphans --build pathwise
```

Once indices are built, the server will be available at `http://localhost:8000`

### 4. Test the System

In a new terminal:

```bash
python scripts/test_rag.py  # Test RAG components
python tests/test_api.py    # Test API endpoints
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
      "catalog_year": 2026
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
      "catalog_year": 2026,
      "target_graduation": "Spring 2028",
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

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Model Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "gpt-4"
LLM_TEMPERATURE = 0.3

# Vector Database
VECTOR_DB_TYPE = "chroma"  # or "faiss"
VECTOR_DB_PATH = "./vector_db"

# Retrieval
TOP_K_RETRIEVAL = 5
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100
```

## Adding Data

The data in `data/` comes from a few sources:

- The Columbia University Directory of Classes <https://doc.search.columbia.edu/>
- The Columbia Engineering Program Finder <https://www.engineering.columbia.edu/academics/programs/program-finder>
- The Columbia Underground Library of Professor Assessments (CULPA) <https://culpa.info/about>

Some content was downloaded manually and parsed, and some content was
scraped programmatically. See `notebooks/colin/scratch.ipynb` for more
information. The data set corresponds to an index config at
`data/index_config.json` -- if the data is updated or augmented, be sure
to edit the index config and indexer code to incorprate additional data
correctly.

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

- Supports ChromaDB (default) and FAISS
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

## Limitations & Disclaimers

1. **Not Official Advising**: This tool is for guidance only. Always verify with official academic advisors.
2. **Data Currency**: Information is only as current as the indexed documents.
3. **LLM Limitations**: May occasionally hallucinate or misinterpret context.
4. **Professor Ratings**: Based on limited, potentially biased sample data.

## Future Enhancements

- [ ] Fine-tuning on domain-specific data
- [ ] Real-time professor rating integration
- [ ] Visual roadmap generation (Mermaid diagrams)
- [ ] Multi-turn conversation support
- [ ] Course prerequisite validation
- [ ] Frontend web interface (React/Streamlit)
- [ ] User authentication and saved plans
- [ ] Integration with university course catalog APIs

## 📄 License

MIT License - see LICENSE file for details.

## Contributors

- Mingjun Sun - RAG System Implementation
- Colin Payne-Rogers - Document retrieval, docker build and deploy to Google Cloud
- Byeolah Kwon - Frontend development and testing
- Yuxin Cai - Frontend design

## 📧 Contact

For questions or issues:

- Open a GitHub issue

---
