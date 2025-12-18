
"""
Enhanced FastAPI backend scaffold for frontend integration testing.

PURPOSE (current):
- Provide a lightweight backend so the React frontend can be developed and tested
  without requiring any LLM API keys or vector databases.
- Match the request/response schema of the real RAG backend (see models.py)
  so frontend code does NOT need to change later.

DESIGN NOTES:
- This file intentionally returns MOCK responses.
- Endpoints and schemas mirror the real backend.


"""

from typing import List, Optional, Dict, Any
from fastapi import FastAPI
from pydantic import BaseModel, Field

# Initialize FastAPI app
app = FastAPI()


# -------------------------------------------------------------------
# Pydantic Models
# -------------------------------------------------------------------
# These models intentionally mirror the teammate's real backend
# (src/api/models.py). DO NOT change field names lightly, as the
# frontend depends on this schema.
# -------------------------------------------------------------------

class UserProfile(BaseModel):
    """User academic context passed from the frontend."""
    program: str
    catalog_year: int
    target_graduation: Optional[str] = None
    completed_courses: List[str] = Field(default_factory=list)
    preference: str = "balanced"


class QuestionRequest(BaseModel):
    """Request body for /ask endpoint."""
    question: str
    user_profile: Optional[UserProfile] = None
    top_k: Optional[int] = Field(5, ge=1, le=20)


class Source(BaseModel):
    """Citation/source object returned with each answer."""
    text: str
    source: str
    program: Optional[str] = None
    catalog_year: Optional[int] = None
    similarity: float


class QuestionResponse(BaseModel):
    """Response body for /ask endpoint."""
    question: str
    answer: str
    sources: List[Source]
    disclaimer: str = (
        "This information is for guidance only. Please verify with your official academic advisor."
    )


class PlanRequest(BaseModel):
    """Request body for degree planning endpoint."""
    user_profile: UserProfile
    num_semesters: int = Field(4, ge=1, le=8)


class PlanResponse(BaseModel):
    """Response body for degree planning endpoint."""
    user_profile: UserProfile
    semesters: List[Dict[str, Any]]
    notes: List[str]
    explanation: str
    disclaimer: str = (
        "This is an AI-generated plan. Please review with your academic advisor before making decisions."
    )


class ProfessorQueryRequest(BaseModel):
    """Request body for professor lookup endpoint."""
    course_codes: List[str]


class ProfessorQueryResponse(BaseModel):
    """Response body for professor lookup endpoint."""
    professors: Dict[str, List[Dict[str, Any]]]


# -------------------------------------------------------------------
# Mock Logic
# -------------------------------------------------------------------
# These functions simulate backend behavior.
# They are the ONLY places that should be replaced when connecting
# to the real RAG/LLM pipeline.
# -------------------------------------------------------------------

def mock_answer(req: QuestionRequest) -> QuestionResponse:
    """
    Mock implementation of the Q&A endpoint.

    FUTURE:
    - Replace this with real RAG retrieval + LLM generation.
    - Keep the return structure unchanged.
    """
    program = req.user_profile.program if req.user_profile else None
    year = req.user_profile.catalog_year if req.user_profile else None

    sources = [
        Source(
            text="(MOCK) Example snippet from requirements document.",
            source="mock_requirements_doc",
            program=program,
            catalog_year=year,
            similarity=0.88,
        )
    ]

    return QuestionResponse(
        question=req.question,
        answer=f"[MOCK] I received your question: {req.question}",
        sources=sources,
    )


def mock_plan(req: PlanRequest) -> PlanResponse:
    """
    Mock implementation of the degree planning endpoint.

    FUTURE:
    - Replace with prerequisite checking, semester balancing,
      and professor-aware planning logic.
    """
    semesters = [
        {"name": "Fall 2025", "courses": [{"course_code": "COMS 4995", "category": "elective"}]},
        {"name": "Spring 2026", "courses": [{"course_code": "COMS 4111", "category": "core"}]},
    ]

    return PlanResponse(
        user_profile=req.user_profile,
        semesters=semesters,
        notes=["(MOCK) Plan generated without prerequisite checks."],
        explanation="(MOCK) This is a placeholder plan for UI integration.",
    )


def mock_professors(req: ProfessorQueryRequest) -> ProfessorQueryResponse:
    """
    Mock implementation of professor lookup.

    FUTURE:
    - Replace with real professor ratings (CULPA / RMP / internal data).
    """
    professors = {
        code: [{"prof_name": "Mock Prof", "rating": 4.6, "tags": "clear, helpful"}]
        for code in req.course_codes
    }
    return ProfessorQueryResponse(professors=professors)


# -------------------------------------------------------------------
# API Routes
# -------------------------------------------------------------------
# Both /api/* and non-prefixed routes are supported so the frontend
# does not need to change when switching between mock and real backend.
# -------------------------------------------------------------------

@app.get("/health")
async def health():
    """Health check endpoint for frontend/server status."""
    return {"status": "ok", "version": "mock-api-0.1", "llm_enabled": False}


@app.post("/api/ask", response_model=QuestionResponse)
@app.post("/ask", response_model=QuestionResponse)
async def ask(req: QuestionRequest):
    return mock_answer(req)


@app.post("/api/plan", response_model=PlanResponse)
@app.post("/plan", response_model=PlanResponse)
async def plan(req: PlanRequest):
    return mock_plan(req)


@app.post("/api/professors", response_model=ProfessorQueryResponse)
@app.post("/professors", response_model=ProfessorQueryResponse)
async def professors(req: ProfessorQueryRequest):
    return mock_professors(req)
