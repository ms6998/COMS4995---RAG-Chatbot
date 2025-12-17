"""
Pydantic models for API request/response validation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """User profile information."""
    program: str = Field(..., description="Program name (e.g., 'MS Computer Science')")
    catalog_year: int = Field(..., description="Academic catalog year")
    target_graduation: Optional[str] = Field(None, description="Target graduation semester")
    completed_courses: List[str] = Field(default_factory=list, description="List of completed course codes")
    preference: str = Field(default="balanced", description="Planning preference: 'best_professors', 'balanced', or 'fast_track'")


class QuestionRequest(BaseModel):
    """Request model for Q&A endpoint."""
    question: str = Field(..., description="User's question about degree requirements")
    user_profile: Optional[UserProfile] = Field(None, description="Optional user profile for context")
    top_k: Optional[int] = Field(5, description="Number of documents to retrieve", ge=1, le=20)


class Source(BaseModel):
    """Source information for citations."""
    text: str = Field(..., description="Snippet of source text")
    source: str = Field(..., description="Source document identifier")
    program: Optional[str] = Field(None, description="Program name")
    catalog_year: Optional[int] = Field(None, description="Catalog year")
    similarity: float = Field(..., description="Relevance score")


class QuestionResponse(BaseModel):
    """Response model for Q&A endpoint."""
    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="Generated answer")
    sources: List[Source] = Field(..., description="List of sources used")
    disclaimer: str = Field(
        default="This information is for guidance only. Please verify with your official academic advisor.",
        description="Disclaimer text"
    )


class Course(BaseModel):
    """Course information."""
    course_code: str = Field(..., description="Course code (e.g., 'COMS 4111')")
    course_name: Optional[str] = Field(None, description="Course name")
    credits: int = Field(3, description="Number of credits")
    prof: Optional[str] = Field(None, description="Recommended professor")
    rating: Optional[float] = Field(None, description="Professor rating")
    category: str = Field(..., description="Course category (core, elective, etc.)")


class Semester(BaseModel):
    """Semester plan."""
    name: str = Field(..., description="Semester name (e.g., 'Fall 2024')")
    courses: List[Course] = Field(..., description="List of courses in this semester")
    total_credits: Optional[int] = Field(None, description="Total credits for semester")


class PlanRequest(BaseModel):
    """Request model for planning endpoint."""
    user_profile: UserProfile = Field(..., description="User profile")
    num_semesters: Optional[int] = Field(4, description="Number of semesters to plan", ge=1, le=8)


class PlanResponse(BaseModel):
    """Response model for planning endpoint."""
    user_profile: UserProfile = Field(..., description="User profile used")
    semesters: List[Semester] = Field(..., description="Planned semesters")
    notes: List[str] = Field(..., description="Planning notes and assumptions")
    explanation: str = Field(..., description="Natural language explanation of the plan")
    disclaimer: str = Field(
        default="This is an AI-generated plan. Please review with your academic advisor before making decisions.",
        description="Disclaimer text"
    )


class ProfessorRating(BaseModel):
    """Professor rating information."""
    course_code: str = Field(..., description="Course code")
    prof_name: str = Field(..., description="Professor name")
    rating: float = Field(..., description="Rating score (0-5)")
    tags: str = Field(default="", description="Tags or keywords")


class ProfessorQueryRequest(BaseModel):
    """Request for querying professor information."""
    course_codes: List[str] = Field(..., description="List of course codes to query")


class ProfessorQueryResponse(BaseModel):
    """Response with professor information."""
    professors: Dict[str, List[ProfessorRating]] = Field(
        ...,
        description="Dictionary mapping course codes to lists of professor ratings"
    )


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    embedder_loaded: bool = Field(..., description="Whether embedder is loaded")
    vector_store_connected: bool = Field(..., description="Whether vector store is connected")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")


