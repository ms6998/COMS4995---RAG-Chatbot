# Backend (FastAPI)

This folder contains a **lightweight FastAPI backend scaffold** used to support
and test the React frontend during early development.

## Purpose
- Provide a working `/api/ask` endpoint for frontend integration
- Enable end-to-end testing of the chatbot UI
- Serve as a placeholder for future RAG / LLM logic

## Current Status
- Implements `/api/ask`
- Returns a simple echo response for testing
- No retrieval or LLM logic yet

## How to Run
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
