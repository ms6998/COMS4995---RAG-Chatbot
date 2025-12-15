"""
FastAPI application for PathWise RAG system.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import json
import re
from typing import Optional

from .models import (
    QuestionRequest, QuestionResponse, Source,
    PlanRequest, PlanResponse, Semester, Course,
    ProfessorQueryRequest, ProfessorQueryResponse, ProfessorRating,
    HealthResponse, ErrorResponse
)
from ..rag.embeddings import EmbeddingGenerator
from ..rag.vector_store import create_vector_store
from ..rag.retriever import RAGRetriever, ProfessorRatingsRetriever
from ..rag.llm_interface import create_llm_interface, PromptTemplate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PathWise API",
    description="LLM-Powered Degree Advisor with RAG",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global components (initialized on startup)
embedder: Optional[EmbeddingGenerator] = None
requirements_retriever: Optional[RAGRetriever] = None
professor_retriever: Optional[ProfessorRatingsRetriever] = None
llm_interface = None


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global embedder, requirements_retriever, professor_retriever, llm_interface
    
    try:
        logger.info("Initializing PathWise RAG system...")
        
        # Load configuration (in production, use proper config management)
        try:
            from config import (
                EMBEDDING_MODEL, VECTOR_DB_TYPE, VECTOR_DB_PATH,
                COLLECTION_NAME_REQUIREMENTS, COLLECTION_NAME_PROFESSORS,
                TOP_K_RETRIEVAL, OPENAI_API_KEY, LLM_MODEL
            )
        except ImportError:
            logger.warning("Config file not found. Using defaults.")
            EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
            VECTOR_DB_TYPE = "chroma"
            VECTOR_DB_PATH = "./vector_db"
            COLLECTION_NAME_REQUIREMENTS = "degree_requirements"
            COLLECTION_NAME_PROFESSORS = "professor_ratings"
            TOP_K_RETRIEVAL = 5
            OPENAI_API_KEY = "your_key_here"
            LLM_MODEL = "gpt-4"
        
        # Initialize embedder
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        embedder = EmbeddingGenerator(EMBEDDING_MODEL)
        
        # Initialize vector stores
        logger.info("Connecting to vector stores...")
        requirements_store = create_vector_store(
            store_type=VECTOR_DB_TYPE,
            collection_name=COLLECTION_NAME_REQUIREMENTS,
            embedding_dim=embedder.embedding_dim,
            persist_directory=VECTOR_DB_PATH
        )
        
        professor_store = create_vector_store(
            store_type=VECTOR_DB_TYPE,
            collection_name=COLLECTION_NAME_PROFESSORS,
            embedding_dim=embedder.embedding_dim,
            persist_directory=VECTOR_DB_PATH
        )
        
        # Initialize retrievers
        requirements_retriever = RAGRetriever(
            embedder=embedder,
            vector_store=requirements_store,
            top_k=TOP_K_RETRIEVAL
        )
        
        professor_retriever = ProfessorRatingsRetriever(
            embedder=embedder,
            vector_store=professor_store
        )
        
        # Initialize LLM
        logger.info(f"Initializing LLM: {LLM_MODEL}")
        llm_interface = create_llm_interface(
            provider="openai",
            api_key=OPENAI_API_KEY,
            model=LLM_MODEL
        )
        
        logger.info("PathWise RAG system initialized successfully!")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        # Don't fail the startup, but log the error


@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to PathWise API",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "ask": "/ask",
            "plan": "/plan",
            "professors": "/professors"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if embedder and requirements_retriever else "initializing",
        version="0.1.0",
        embedder_loaded=embedder is not None,
        vector_store_connected=requirements_retriever is not None
    )


@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Answer a question about degree requirements.
    
    Args:
        request: Question request with user query and optional profile
        
    Returns:
        Answer with sources and citations
    """
    if not requirements_retriever or not llm_interface:
        raise HTTPException(
            status_code=503,
            detail="System is still initializing. Please try again in a moment."
        )
    
    try:
        logger.info(f"Received question: {request.question}")
        
        # Build user profile for filtering if provided
        user_profile_dict = None
        if request.user_profile:
            user_profile_dict = request.user_profile.dict()
        
        # Retrieve relevant documents
        retrieval_result = requirements_retriever.retrieve_with_context(
            query=request.question,
            user_profile=user_profile_dict,
            k=request.top_k
        )
        
        retrieved_docs = retrieval_result['results']
        
        if not retrieved_docs:
            return QuestionResponse(
                question=request.question,
                answer="I couldn't find relevant information in the knowledge base to answer your question. Please contact your academic advisor for assistance.",
                sources=[]
            )
        
        # Format context for LLM
        context = requirements_retriever.format_context_for_llm(retrieved_docs)
        
        # Build prompt
        messages = PromptTemplate.build_qa_prompt(
            query=request.question,
            context=context,
            user_profile=user_profile_dict
        )
        
        # Generate answer
        answer = llm_interface.generate(messages)
        
        # Format sources
        sources = [
            Source(
                text=doc['text'][:200] + "..." if len(doc['text']) > 200 else doc['text'],
                source=doc['metadata'].get('source', 'Unknown'),
                program=doc['metadata'].get('program'),
                catalog_year=doc['metadata'].get('catalog_year'),
                similarity=doc.get('similarity', 0)
            )
            for doc in retrieved_docs[:5]
        ]
        
        return QuestionResponse(
            question=request.question,
            answer=answer,
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/plan", response_model=PlanResponse)
async def create_plan(request: PlanRequest):
    """
    Create a personalized degree plan.
    
    Args:
        request: Planning request with user profile
        
    Returns:
        Semester-by-semester course plan with professor recommendations
    """
    if not requirements_retriever or not professor_retriever or not llm_interface:
        raise HTTPException(
            status_code=503,
            detail="System is still initializing. Please try again in a moment."
        )
    
    try:
        logger.info(f"Creating plan for: {request.user_profile.program}")
        
        user_profile_dict = request.user_profile.dict()
        
        # Retrieve degree requirements
        req_query = f"degree requirements and course list for {request.user_profile.program}"
        req_docs = requirements_retriever.retrieve(
            query=req_query,
            k=10,
            filter_dict={
                'program': request.user_profile.program,
                'catalog_year': request.user_profile.catalog_year
            }
        )
        
        requirements_context = requirements_retriever.format_context_for_llm(req_docs)
        
        # Get professor ratings for relevant courses
        # Extract course codes from requirements
        course_codes = set()
        for doc in req_docs:
            codes = doc['metadata'].get('course_codes', [])
            course_codes.update(codes)
        
        # Get professor info
        prof_info_parts = []
        for course_code in list(course_codes)[:20]:  # Limit to avoid too long context
            profs = professor_retriever.get_professors_for_course(course_code, k=3)
            if profs:
                prof_info_parts.append(f"\n{course_code}:")
                for prof in profs:
                    prof_info_parts.append(f"  - {professor_retriever.format_professor_info(prof)}")
        
        professor_info = "\n".join(prof_info_parts) if prof_info_parts else "No professor rating data available."
        
        # Build planning prompt
        messages = PromptTemplate.build_planning_prompt(
            user_profile=user_profile_dict,
            requirements_context=requirements_context,
            professor_info=professor_info
        )
        
        # Generate plan
        plan_text = llm_interface.generate(messages, max_tokens=3000)
        
        # Parse JSON from response
        semesters, notes, explanation = parse_planning_response(plan_text)
        
        return PlanResponse(
            user_profile=request.user_profile,
            semesters=semesters,
            notes=notes,
            explanation=explanation
        )
        
    except Exception as e:
        logger.error(f"Error creating plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/professors", response_model=ProfessorQueryResponse)
async def query_professors(request: ProfessorQueryRequest):
    """
    Query professor ratings for specific courses.
    
    Args:
        request: List of course codes
        
    Returns:
        Professor ratings for each course
    """
    if not professor_retriever:
        raise HTTPException(
            status_code=503,
            detail="Professor ratings system not initialized."
        )
    
    try:
        result = {}
        
        for course_code in request.course_codes:
            profs = professor_retriever.get_professors_for_course(course_code, k=5)
            
            result[course_code] = [
                ProfessorRating(
                    course_code=p['metadata']['course_code'],
                    prof_name=p['metadata']['prof_name'],
                    rating=p['metadata']['rating'],
                    tags=p['metadata'].get('tags', '')
                )
                for p in profs
            ]
        
        return ProfessorQueryResponse(professors=result)
        
    except Exception as e:
        logger.error(f"Error querying professors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def parse_planning_response(plan_text: str) -> tuple:
    """
    Parse LLM planning response to extract structured data.
    
    Args:
        plan_text: Raw LLM response
        
    Returns:
        Tuple of (semesters, notes, explanation)
    """
    # Try to extract JSON
    json_match = re.search(r'\{[\s\S]*"semesters"[\s\S]*\}', plan_text)
    
    if json_match:
        try:
            json_str = json_match.group(0)
            plan_data = json.loads(json_str)
            
            semesters = []
            for sem_data in plan_data.get('semesters', []):
                courses = [
                    Course(**course_data)
                    for course_data in sem_data.get('courses', [])
                ]
                semesters.append(Semester(
                    name=sem_data['name'],
                    courses=courses,
                    total_credits=sum(c.credits for c in courses)
                ))
            
            notes = plan_data.get('notes', [])
            
            # Extract explanation (text before JSON)
            explanation = plan_text[:json_match.start()].strip()
            
            return semesters, notes, explanation
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from planning response")
    
    # Fallback: return text only
    return [], ["Unable to generate structured plan. See explanation."], plan_text


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

