"""
LangChain RAG integration module.
Connects our vector databases with LangChain's RAG chain.
"""

import os
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional

from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser


class SimpleVectorStore:
    """Simple vector store wrapper for LangChain."""
    
    def __init__(self, index_dir: str):
        """
        Load a simple numpy-based vector index.
        
        Args:
            index_dir: Directory containing the vector index
        """
        index_path = Path(index_dir)
        
        self.embeddings = np.load(index_path / "embeddings.npy")
        
        with open(index_path / "texts.pkl", 'rb') as f:
            self.texts = pickle.load(f)
        
        with open(index_path / "metadata.pkl", 'rb') as f:
            self.metadatas = pickle.load(f)
        
        print(f"✅ Loaded vector store from {index_dir}")
        print(f"   Documents: {len(self.texts)}")
        print(f"   Embedding dim: {self.embeddings.shape[1]}")
    
    def similarity_search(
        self,
        query_embedding: np.ndarray,
        k: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> List[Document]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results
            filter_dict: Optional metadata filters
            
        Returns:
            List of LangChain Document objects
        """
        # Compute cosine similarities
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        doc_norms = self.embeddings / np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        similarities = np.dot(doc_norms, query_norm)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1]
        
        # Apply filters if provided
        results = []
        for idx in top_indices:
            metadata = self.metadatas[idx]
            
            # Check filters
            if filter_dict:
                match = all(metadata.get(k) == v for k, v in filter_dict.items())
                if not match:
                    continue
            
            # Create LangChain Document
            doc = Document(
                page_content=self.texts[idx],
                metadata={
                    **metadata,
                    'similarity': float(similarities[idx])
                }
            )
            results.append(doc)
            
            if len(results) >= k:
                break
        
        return results


class PathWiseRAG:
    """
    PathWise RAG system using LangChain.
    """
    
    def __init__(
        self,
        openai_api_key: str,
        professor_db_path: str = "vector_db_simple",
        programs_db_path: str = "vector_db_programs",
        model_name: str = "gpt-4",
        temperature: float = 0.3
    ):
        """
        Initialize PathWise RAG system.
        
        Args:
            openai_api_key: OpenAI API key
            professor_db_path: Path to professor vector database
            programs_db_path: Path to programs vector database
            model_name: LLM model name
            temperature: LLM temperature
        """
        print("Initializing PathWise RAG with LangChain...")
        
        # Set API key
        os.environ['OPENAI_API_KEY'] = openai_api_key
        
        # Load vector stores
        self.prof_store = SimpleVectorStore(professor_db_path)
        self.programs_store = SimpleVectorStore(programs_db_path)
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=openai_api_key
        )
        
        # Initialize embeddings (for queries)
        from sentence_transformers import SentenceTransformer
        self.embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        print("✅ PathWise RAG initialized")
    
    def retrieve_context(
        self,
        query: str,
        query_type: str = "general",
        k: int = 5
    ) -> List[Document]:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: User query
            query_type: 'professor', 'program', or 'general'
            k: Number of documents to retrieve
            
        Returns:
            List of relevant documents
        """
        # Generate query embedding
        query_embedding = self.embedder.encode(query)
        
        # Choose appropriate database
        if query_type == "professor":
            docs = self.prof_store.similarity_search(query_embedding, k=k)
        elif query_type == "program":
            docs = self.programs_store.similarity_search(query_embedding, k=k)
        else:
            # Search both and combine
            prof_docs = self.prof_store.similarity_search(query_embedding, k=k//2)
            prog_docs = self.programs_store.similarity_search(query_embedding, k=k//2)
            docs = prof_docs + prog_docs
        
        return docs
    
    def format_context(self, docs: List[Document]) -> str:
        """Format retrieved documents as context string."""
        if not docs:
            return "No relevant information found."
        
        context_parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source', 'Unknown')
            similarity = doc.metadata.get('similarity', 0)
            
            context_parts.append(
                f"[Source {i}: {source}]\n"
                f"{doc.page_content}\n"
                f"[Relevance: {similarity:.3f}]"
            )
        
        return "\n\n---\n\n".join(context_parts)
    
    def answer_question(
        self,
        question: str,
        query_type: str = "general",
        k: int = 5
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG.
        
        Args:
            question: User question
            query_type: Type of query
            k: Number of context documents
            
        Returns:
            Dictionary with answer and sources
        """
        print(f"\n🔍 Processing question: {question}")
        
        # Retrieve context
        docs = self.retrieve_context(question, query_type=query_type, k=k)
        context = self.format_context(docs)
        
        print(f"   Retrieved {len(docs)} relevant documents")
        
        # Build prompt
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are PathWise, an intelligent academic advisor for Columbia Engineering programs.

Your role is to help students understand degree requirements, course options, and professor recommendations.

Guidelines:
1. Answer based ONLY on the provided context
2. Cite sources using [Source X] format
3. If information is not in the context, say "I don't have that information"
4. Be concise and clear
5. Always include a disclaimer to verify with official advisors

Remember: You are a helpful tool, not a replacement for official advising."""),
            ("human", """Context:
{context}

Question: {question}

Please provide a helpful answer based on the context above. Include source citations.""")
        ])
        
        # Create RAG chain
        rag_chain = (
            {
                "context": lambda x: context,
                "question": RunnablePassthrough()
            }
            | prompt_template
            | self.llm
            | StrOutputParser()
        )
        
        # Generate answer
        print("   Generating answer with LLM...")
        answer = rag_chain.invoke(question)
        
        print("   ✅ Answer generated")
        
        return {
            "question": question,
            "answer": answer,
            "sources": [
                {
                    "text": doc.page_content[:200],
                    "metadata": doc.metadata
                }
                for doc in docs
            ],
            "num_sources": len(docs)
        }
    
    def find_best_professors(
        self,
        course_name: str = None,
        min_rating: float = 4.0,
        k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find best-rated professors.
        
        Args:
            course_name: Optional course name to search for
            min_rating: Minimum rating threshold
            k: Number of results
            
        Returns:
            List of professor information
        """
        query = f"highly rated professors {course_name}" if course_name else "best professors"
        
        # Get query embedding
        query_embedding = self.embedder.encode(query)
        
        # Search professor database
        docs = self.prof_store.similarity_search(query_embedding, k=k*2)
        
        # Filter by rating
        results = []
        for doc in docs:
            rating = doc.metadata.get('rating', 0)
            if rating >= min_rating:
                results.append({
                    'professor': doc.metadata.get('professor_name'),
                    'rating': rating,
                    'course': doc.metadata.get('course_code', 'N/A'),
                    'text': doc.page_content
                })
            
            if len(results) >= k:
                break
        
        # Sort by rating
        results.sort(key=lambda x: x['rating'], reverse=True)
        
        return results
    
    def generate_degree_plan(
        self,
        program: str,
        completed_courses: List[str] = None,
        target_semesters: int = 4,
        prefer_high_rated: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a degree plan using RAG.
        
        Args:
            program: Program name (e.g., "MS Computer Science")
            completed_courses: List of completed course codes
            target_semesters: Number of semesters to plan
            prefer_high_rated: Whether to prefer high-rated professors
            
        Returns:
            Dictionary with plan and recommendations
        """
        print(f"\n📅 Generating plan for: {program}")
        
        # Retrieve program requirements
        req_query = f"degree requirements courses for {program}"
        req_docs = self.retrieve_context(req_query, query_type="program", k=8)
        req_context = self.format_context(req_docs)
        
        # Get professor ratings
        prof_query = f"professors teaching courses"
        prof_docs = self.retrieve_context(prof_query, query_type="professor", k=10)
        prof_context = self.format_context(prof_docs)
        
        # Build planning prompt
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are PathWise, an academic planning assistant.

Create a realistic semester-by-semester course plan based on the degree requirements and professor ratings provided.

Guidelines:
1. Follow the degree requirements strictly
2. Suggest 3-4 courses per semester (9-12 credits typical)
3. When professor ratings are available, recommend higher-rated professors
4. Include planning notes and assumptions
5. Format the plan clearly with semesters and courses

Output format:
Semester 1: Fall 2025
- Course 1 (recommended professor if available)
- Course 2
...

Notes:
- List any assumptions or caveats"""),
            ("human", """Program: {program}
Completed courses: {completed}
Target: {semesters} semesters
Preference: {preference}

Program Requirements:
{requirements}

Professor Ratings:
{professors}

Please create a personalized course plan.""")
        ])
        
        # Generate plan
        plan_chain = prompt_template | self.llm | StrOutputParser()
        
        plan = plan_chain.invoke({
            "program": program,
            "completed": ", ".join(completed_courses) if completed_courses else "None",
            "semesters": target_semesters,
            "preference": "Prefer highly-rated professors" if prefer_high_rated else "Balanced",
            "requirements": req_context[:2000],  # Limit context size
            "professors": prof_context[:2000]
        })
        
        print("   ✅ Plan generated")
        
        return {
            "program": program,
            "plan": plan,
            "requirements_sources": len(req_docs),
            "professor_data_sources": len(prof_docs)
        }


# Convenience function
def create_pathwise_rag(
    openai_api_key: str,
    model_name: str = "gpt-4"
) -> PathWiseRAG:
    """
    Create a PathWise RAG instance.
    
    Args:
        openai_api_key: OpenAI API key
        model_name: LLM model name
        
    Returns:
        PathWiseRAG instance
    """
    return PathWiseRAG(
        openai_api_key=openai_api_key,
        model_name=model_name
    )


if __name__ == "__main__":
    # Example usage
    print("PathWise LangChain RAG Example")
    print("="*60)
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n❌ Please set OPENAI_API_KEY environment variable")
        print("   export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Initialize RAG
    rag = create_pathwise_rag(api_key, model_name="gpt-3.5-turbo")
    
    # Test question answering
    print("\n" + "="*60)
    print("TEST 1: Question Answering")
    print("="*60)
    
    result = rag.answer_question(
        "What are the requirements for MS in Computer Science?",
        query_type="program"
    )
    
    print(f"\nQuestion: {result['question']}")
    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nSources used: {result['num_sources']}")
    
    # Test professor search
    print("\n" + "="*60)
    print("TEST 2: Find Best Professors")
    print("="*60)
    
    profs = rag.find_best_professors(min_rating=4.5, k=5)
    
    print(f"\nTop {len(profs)} Professors (rating >= 4.5):")
    for i, prof in enumerate(profs, 1):
        print(f"{i}. {prof['professor']}: {prof['rating']:.2f}/5.0")


