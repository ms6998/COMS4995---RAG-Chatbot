"""
Retrieval module for the RAG system.
"""

from typing import List, Dict, Any, Optional
import logging
from .embeddings import EmbeddingGenerator
from .vector_store import VectorStore
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProfessorRatingsRetriever:
    """Specialized retriever for professor ratings with input normalization."""
    
    def __init__(self, embedder: EmbeddingGenerator, vector_store: VectorStore):
        self.embedder = embedder
        self.vector_store = vector_store
        logger.info("Initialized ProfessorRatingsRetriever")

    def normalize_course_code(self, course_code: str) -> str:
        """
        Standardizes course codes to 'DEPT ####' format.
        Example: 'coms4995' -> 'COMS 4995'
        """
        # 1. Remove all spaces and convert to uppercase
        clean = course_code.replace(" ", "").upper()
        
        # 2. Use regex to separate letters and numbers
        match = re.match(r"([A-Z]{2,4})(\d{4})", clean)
        if match:
            return f"{match.group(1)} {match.group(2)}"
        
        return course_code  # Return original if pattern doesn't match

    def get_professors_for_course(self, course_code: str, k: int = 5) -> List[Dict[str, Any]]:
        # 1. Generate variations
        raw = course_code.strip()
        no_space = raw.replace(" ", "")
        with_space = re.sub(r"([A-Z]{2,4})(\d{4})", r"\1 \2", no_space.upper())
        
        # 2. Build a flexible filter
        # This checks for: "COMS 4995", "COMS4995", "coms4995", etc.
        flexible_filter = {
            "$or": [
                {"course_code": with_space},           # "COMS 4995"
                {"course_code": no_space.upper()},     # "COMS4995"
                {"course_code": no_space.lower()},     # "coms4995"
                {"course_code": raw}                   # Original input
            ]
        }

        logger.info(f"Searching with flexible filter for: {raw}")
        query_embedding = self.embedder.encode_query(f"professors for {with_space}")
        
        results = self.vector_store.search(
            query_embedding=query_embedding,
            k=k * 2,
            filter_dict=flexible_filter
        )
        
        return sorted(results, key=lambda x: x['metadata'].get('rating', 0), reverse=True)[:k]

class RAGRetriever:
    """
    Retriever for the RAG system.
    Combines embedding generation and vector search.
    """
    
    def __init__(
        self,
        embedder: EmbeddingGenerator,
        vector_store: VectorStore,
        top_k: int = 5,
        similarity_threshold: float = 0.0
    ):
        """
        Initialize the retriever.
        
        Args:
            embedder: Embedding generator instance
            vector_store: Vector store instance
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity score threshold
        """
        self.embedder = embedder
        self.vector_store = vector_store
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        logger.info(f"Initialized RAGRetriever with top_k={top_k}")
    
    def retrieve(
        self,
        query: str,
        k: Optional[int] = None,
        filter_dict: Optional[Dict[str, Any]] = None,
        min_score: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query string
            k: Number of results to return (overrides default)
            filter_dict: Optional metadata filters
            min_score: Minimum similarity score (overrides default)
            
        Returns:
            List of retrieved documents with metadata and scores
        """
        k = k or self.top_k
        min_score = min_score if min_score is not None else self.similarity_threshold
        
        # Generate query embedding
        logger.info(f"Retrieving documents for query: {query[:100]}...")
        query_embedding = self.embedder.encode_query(query)
        
        # Search vector store
        results = self.vector_store.search(
            query_embedding=query_embedding,
            k=k * 2,  # Get more results to filter
            filter_dict=filter_dict
        )
        
        # Filter by similarity threshold
        filtered_results = []
        for result in results:
            # Convert distance to similarity (assuming cosine distance)
            similarity = 1 - result['distance']
            
            if similarity >= min_score:
                result['similarity'] = similarity
                filtered_results.append(result)
            
            if len(filtered_results) >= k:
                break
        
        logger.info(f"Retrieved {len(filtered_results)} documents above threshold")
        return filtered_results
    
    def retrieve_with_context(
        self,
        query: str,
        user_profile: Optional[Dict[str, Any]] = None,
        k: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Retrieve documents with additional context enhancement.
        
        Args:
            query: Search query
            user_profile: Optional user profile for filtering
            k: Number of results
            
        Returns:
            Dictionary with retrieved documents and metadata
        """
        # Build filter from user profile
        filter_dict = None
        if user_profile:
            filter_dict = {}
            if 'program' in user_profile:
                filter_dict['program'] = user_profile['program']
            if 'catalog_year' in user_profile:
                filter_dict['catalog_year'] = user_profile['catalog_year']
        
        # Retrieve documents
        results = self.retrieve(
            query=query,
            k=k,
            filter_dict=filter_dict
        )
        
        # Format response with context
        return {
            'query': query,
            'results': results,
            'user_profile': user_profile,
            'num_results': len(results)
        }
    
    def format_context_for_llm(
        self,
        retrieved_docs: List[Dict[str, Any]],
        max_context_length: int = 3000
    ) -> str:
        """
        Format retrieved documents into context string for LLM.
        
        Args:
            retrieved_docs: List of retrieved documents
            max_context_length: Maximum length of context in words
            
        Returns:
            Formatted context string
        """
        if not retrieved_docs:
            return "No relevant information found in the knowledge base."
        
        context_parts = []
        current_length = 0
        
        for i, doc in enumerate(retrieved_docs, 1):
            # Format document with metadata
            doc_text = doc['text']
            metadata = doc['metadata']
            similarity = doc.get('similarity', 0)
            
            # Create citation
            source = metadata.get('source', 'Unknown')
            program = metadata.get('program', '')
            catalog_year = metadata.get('catalog_year', '')
            
            doc_header = f"\n[Source {i}: {program} {catalog_year} - {source}]"
            doc_content = f"\n{doc_text}\n"
            doc_footer = f"[Relevance Score: {similarity:.2f}]"
            
            doc_formatted = doc_header + doc_content + doc_footer
            doc_length = len(doc_formatted.split())
            
            # Check if adding this document exceeds limit
            if current_length + doc_length > max_context_length:
                break
            
            context_parts.append(doc_formatted)
            current_length += doc_length
        
        context = "\n---\n".join(context_parts)
        
        preamble = f"Retrieved {len(context_parts)} relevant documents:\n"
        return preamble + context


class ProfessorRatingsRetriever:
    """
    Specialized retriever for professor ratings.
    """
    
    def __init__(
        self,
        embedder: EmbeddingGenerator,
        vector_store: VectorStore
    ):
        """
        Initialize professor ratings retriever.
        
        Args:
            embedder: Embedding generator
            vector_store: Vector store containing professor ratings
        """
        self.embedder = embedder
        self.vector_store = vector_store
        logger.info("Initialized ProfessorRatingsRetriever")
    
    def get_professors_for_course(
        self,
        course_code: str,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get professor ratings for a specific course.
        
        Args:
            course_code: Course code (e.g., "COMS 4111")
            k: Number of professors to return
            
        Returns:
            List of professor rating records sorted by rating
        """
        # Search with course code filter
        query = f"professors teaching {course_code}"
        query_embedding = self.embedder.encode_query(query)
        
        results = self.vector_store.search(
            query_embedding=query_embedding,
            k=k * 2,
            filter_dict={'course_code': course_code}
        )
        
        # Sort by rating (highest first)
        sorted_results = sorted(
            results,
            key=lambda x: x['metadata'].get('rating', 0),
            reverse=True
        )
        
        return sorted_results[:k]
    
    def get_best_professor_for_course(
        self,
        course_code: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the highest-rated professor for a course.
        
        Args:
            course_code: Course code
            
        Returns:
            Professor rating record or None if not found
        """
        professors = self.get_professors_for_course(course_code, k=1)
        return professors[0] if professors else None
    
    def get_professors_for_courses(
        self,
        course_codes: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get professors for multiple courses.
        
        Args:
            course_codes: List of course codes
            
        Returns:
            Dictionary mapping course codes to professor lists
        """
        result = {}
        for course_code in course_codes:
            professors = self.get_professors_for_course(course_code)
            result[course_code] = professors
        return result
    
    def format_professor_info(
        self,
        prof_record: Dict[str, Any]
    ) -> str:
        """
        Format professor information for display.
        
        Args:
            prof_record: Professor rating record
            
        Returns:
            Formatted string
        """
        metadata = prof_record['metadata']
        prof_name = metadata.get('prof_name', 'Unknown')
        rating = metadata.get('rating', 0)
        tags = metadata.get('tags', '')
        course_code = metadata.get('course_code', '')
        
        return (
            f"Prof. {prof_name} ({course_code}): "
            f"Rating {rating}/5.0"
            f"{f' - {tags}' if tags else ''}"
        )


if __name__ == "__main__":
    # Test retriever (requires initialized embedder and vector store)
    from .embeddings import EmbeddingGenerator
    from .vector_store import ChromaVectorStore
    import numpy as np
    
    print("Testing RAGRetriever...")
    
    # Initialize components
    embedder = EmbeddingGenerator()
    vector_store = ChromaVectorStore("test_retrieval", "./test_db")
    
    # Add some test documents
    texts = [
        "The MS in Computer Science requires 30 credits total.",
        "Core courses include COMS 4111 Database Systems and COMS 4701 AI.",
        "Students must maintain a minimum GPA of 3.0.",
        "Technical electives can be chosen from approved 6000-level courses."
    ]
    
    embeddings = embedder.encode_documents(texts)
    metadatas = [
        {"program": "MS CS", "catalog_year": 2023, "source": "bulletin.pdf"},
        {"program": "MS CS", "catalog_year": 2023, "source": "bulletin.pdf"},
        {"program": "MS CS", "catalog_year": 2023, "source": "requirements.pdf"},
        {"program": "MS CS", "catalog_year": 2023, "source": "requirements.pdf"}
    ]
    
    vector_store.add_documents(texts, embeddings, metadatas)
    
    # Initialize retriever
    retriever = RAGRetriever(embedder, vector_store, top_k=3)
    
    # Test retrieval
    query = "What are the core courses for computer science?"
    results = retriever.retrieve(query)
    
    print(f"\nQuery: {query}")
    print(f"Found {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['text']}")
        print(f"   Similarity: {result['similarity']:.4f}")
        print(f"   Source: {result['metadata']['source']}\n")
    
    # Test context formatting
    context = retriever.format_context_for_llm(results)
    print("\nFormatted context for LLM:")
    print(context)



