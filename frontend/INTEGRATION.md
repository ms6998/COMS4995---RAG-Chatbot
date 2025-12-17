# Backend Integration Guide

## Overview
This document explains how to connect the React frontend with your FastAPI backend.

## Backend Requirements

Your FastAPI backend should expose the following endpoints:

### 1. Question Answering Endpoint

```python
# In your FastAPI app (e.g., src/api/app.py)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str
    
class QuestionResponse(BaseModel):
    answer: str
    sources: list = []

@app.post("/api/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    # Your RAG logic here
    answer = your_rag_system.get_answer(request.question)
    sources = your_rag_system.get_sources()
    
    return QuestionResponse(
        answer=answer,
        sources=sources
    )
```

### 2. Degree Planning Endpoint (Future)

```python
class PlanRequest(BaseModel):
    program: str
    catalog_year: int
    target_graduation: str
    completed_courses: list = []
    
class PlanResponse(BaseModel):
    semesters: list
    notes: list

@app.post("/api/plan", response_model=PlanResponse)
async def create_plan(request: PlanRequest):
    # Your planning logic here
    plan = your_planning_system.generate_plan(request)
    return plan
```

## Starting Both Services

### Terminal 1 - Backend
```bash
cd COMS4995---RAG-Chatbot
python scripts/start_server.py
# Or: uvicorn src.api.app:app --reload --port 8000
```

### Terminal 2 - Frontend
```bash
cd pathwise-frontend
npm run dev
```

## Testing the Connection

1. Start both servers
2. Open http://localhost:3000 in your browser
3. Try asking: "What are the core courses for MS DS?"
4. Check the Network tab in browser DevTools to see the API call

## Common Issues

### CORS Errors
If you see CORS errors in the browser console:
- Ensure the backend has CORS middleware configured
- Check that `allow_origins` includes your frontend URL

### Connection Refused
- Verify backend is running on port 8000
- Check firewall settings
- Ensure both services are running

### API Response Format
The frontend expects this JSON structure:
```json
{
  "answer": "Your answer here...",
  "sources": ["source1", "source2"]
}
```

## Environment Variables

Create a `.env` file in the frontend directory (optional):
```
VITE_API_URL=http://localhost:8000
```

Then update `App.jsx` to use it:
```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const response = await fetch(`${API_URL}/api/ask`, {
  // ...
});
```

## Production Deployment

### Backend
- Deploy to a cloud service (AWS, GCP, Heroku, etc.)
- Get the production URL (e.g., https://api.yourapp.com)

### Frontend
1. Update API URL in frontend config
2. Build: `npm run build`
3. Deploy the `dist/` folder to Vercel, Netlify, etc.

### Update CORS
In production, update the backend CORS settings:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://yourapp.vercel.app",  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Next Steps

1. ✅ Set up basic Q&A endpoint
2. 🔄 Add error handling and validation
3. 🔄 Implement /plan endpoint
4. 🔄 Add authentication (if needed)
5. 🔄 Add rate limiting
6. 🔄 Set up logging and monitoring

## Questions?

Check the main README.md or open an issue on the project repository.
