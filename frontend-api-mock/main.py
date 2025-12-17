"""
FastAPI backend scaffold for frontend integration testing.

This file currently implements a minimal /api/ask endpoint
that returns an echo response. It is intended as a placeholder
for future RAG / LLM-based chatbot logic.
"""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class AskRequest(BaseModel):
    question: str

@app.post("/api/ask")
async def ask(req: AskRequest):
    # will replace this with real chatbot call
    return {
        "answer": f"I received your question: {req.question}",
        "sources": []
    }
