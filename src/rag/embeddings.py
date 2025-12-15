"""
Embedding generation module using sentence transformers.
"""

from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings for text using sentence transformers."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.embedding_dim}")
    
    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        show_progress_bar: bool = False
    ) -> np.ndarray:
        """
        Generate embeddings for text(s).
        
        Args:
            texts: Single text string or list of text strings
            batch_size: Batch size for encoding
            show_progress_bar: Whether to show progress bar
            
        Returns:
            Numpy array of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
        
        logger.info(f"Encoding {len(texts)} texts...")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress_bar,
            convert_to_numpy=True
        )
        
        return embeddings
    
    def encode_query(self, query: str) -> np.ndarray:
        """
        Encode a search query.
        
        Args:
            query: Search query string
            
        Returns:
            Numpy array representing the query embedding
        """
        return self.encode(query)[0]
    
    def encode_documents(
        self,
        documents: List[str],
        batch_size: int = 32
    ) -> np.ndarray:
        """
        Encode multiple documents.
        
        Args:
            documents: List of document strings
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of document embeddings
        """
        return self.encode(
            documents,
            batch_size=batch_size,
            show_progress_bar=True
        )
    
    def compute_similarity(
        self,
        query_embedding: np.ndarray,
        document_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Compute cosine similarity between query and documents.
        
        Args:
            query_embedding: Query embedding vector
            document_embeddings: Array of document embedding vectors
            
        Returns:
            Array of similarity scores
        """
        # Normalize embeddings
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        doc_norms = document_embeddings / np.linalg.norm(
            document_embeddings,
            axis=1,
            keepdims=True
        )
        
        # Compute cosine similarity
        similarities = np.dot(doc_norms, query_norm)
        return similarities


# Alternative: OpenAI Embeddings
class OpenAIEmbeddings:
    """Generate embeddings using OpenAI's API."""
    
    def __init__(self, api_key: str, model: str = "text-embedding-ada-002"):
        """
        Initialize OpenAI embeddings.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI embedding model name
        """
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.model = model
            logger.info(f"Initialized OpenAI embeddings with model: {model}")
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings using OpenAI API.
        
        Args:
            texts: Single text or list of texts
            
        Returns:
            Numpy array of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
        
        logger.info(f"Encoding {len(texts)} texts using OpenAI...")
        
        embeddings = []
        # Process in batches to avoid rate limits
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.client.embeddings.create(
                input=batch,
                model=self.model
            )
            batch_embeddings = [item.embedding for item in response.data]
            embeddings.extend(batch_embeddings)
        
        return np.array(embeddings)
    
    def encode_query(self, query: str) -> np.ndarray:
        """Encode a search query."""
        return self.encode(query)[0]


if __name__ == "__main__":
    # Test embedding generation
    embedder = EmbeddingGenerator()
    
    # Test single text
    text = "What are the core courses for MS in Computer Science?"
    embedding = embedder.encode(text)
    print(f"Single text embedding shape: {embedding.shape}")
    
    # Test multiple texts
    texts = [
        "Database systems course requirement",
        "Machine learning elective courses",
        "Software engineering prerequisites"
    ]
    embeddings = embedder.encode_documents(texts)
    print(f"Multiple texts embedding shape: {embeddings.shape}")
    
    # Test similarity
    query = "What database courses are required?"
    query_emb = embedder.encode_query(query)
    similarities = embedder.compute_similarity(query_emb, embeddings)
    print(f"Similarities: {similarities}")

