"""
Vector database module for storing and retrieving embeddings.
Supports both ChromaDB and FAISS.
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np
import logging
import json
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStore:
    """Base class for vector stores."""
    
    def add_documents(
        self,
        texts: List[str],
        embeddings: np.ndarray,
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ):
        """Add documents to the vector store."""
        raise NotImplementedError

    def count_documents(self):
        """
        How many documents does the store have?
        """
        raise NotImplementedError
    
    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        raise NotImplementedError
    
    def delete_collection(self):
        """Delete the collection."""
        raise NotImplementedError


class ChromaVectorStore(VectorStore):
    """Vector store using ChromaDB."""
    
    def __init__(
        self,
        collection_name: str,
        persist_directory: str = "./vector_db"
    ):
        """
        Initialize ChromaDB vector store.
        
        Args:
            collection_name: Name of the collection
            persist_directory: Directory to persist the database
        """
        try:
            import chromadb
            from chromadb.config import Settings
            
            self.persist_directory = persist_directory
            Path(persist_directory).mkdir(parents=True, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"Initialized ChromaDB collection: {collection_name}")
            logger.info(f"Current document count: {self.collection.count()}")
            
        except ImportError:
            raise ImportError("chromadb not installed. Run: pip install chromadb")
    
    def add_documents(
        self,
        texts: List[str],
        embeddings: np.ndarray,
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ):
        """
        Add documents to ChromaDB.
        
        Args:
            texts: List of text strings
            embeddings: Numpy array of embeddings
            metadatas: List of metadata dictionaries
            ids: Optional list of document IDs
        """
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(texts))]
        
        # Convert numpy array to list for ChromaDB
        embeddings_list = embeddings.tolist() if isinstance(embeddings, np.ndarray) else embeddings
        
        # ChromaDB requires metadata values to be strings, ints, or floats
        processed_metadatas = []
        for metadata in metadatas:
            processed = {}
            for key, value in metadata.items():
                if isinstance(value, (list, dict)):
                    processed[key] = json.dumps(value)
                else:
                    processed[key] = value
            processed_metadatas.append(processed)
        
        self.collection.add(
            documents=texts,
            embeddings=embeddings_list,
            metadatas=processed_metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(texts)} documents to ChromaDB")

    def count_documents(self):
        return self.collection.count()

    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents in ChromaDB.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            filter_dict: Optional metadata filter
            
        Returns:
            List of result dictionaries with text, metadata, and distance
        """
        query_embedding_list = query_embedding.tolist() if isinstance(query_embedding, np.ndarray) else query_embedding
        
        # Build where clause for filtering
        where_clause = None
        if filter_dict:
            items = [{k: v} for k, v in filter_dict.items()]
            if len(items) == 1:
                where_clause = items[0]
            else:
                where_clause = {"$and": items}
        
        results = self.collection.query(
            query_embeddings=[query_embedding_list],
            n_results=k,
            where=where_clause
        )
        
        # Format results
        formatted_results = []
        if results['documents'][0]:
            for i in range(len(results['documents'][0])):
                metadata = results['metadatas'][0][i]
                # Parse JSON strings back to objects
                for key, value in metadata.items():
                    if isinstance(value, str) and (value.startswith('[') or value.startswith('{')):
                        try:
                            metadata[key] = json.loads(value)
                        except:
                            pass
                
                formatted_results.append({
                    'text': results['documents'][0][i],
                    'metadata': metadata,
                    'distance': results['distances'][0][i],
                    'id': results['ids'][0][i]
                })
        
        return formatted_results
    
    def delete_collection(self):
        """Delete the collection."""
        self.client.delete_collection(self.collection.name)
        logger.info(f"Deleted collection: {self.collection.name}")


class FAISSVectorStore(VectorStore):
    """Vector store using FAISS."""
    
    def __init__(
        self,
        collection_name: str,
        embedding_dim: int,
        persist_directory: str = "./vector_db"
    ):
        """
        Initialize FAISS vector store.
        
        Args:
            collection_name: Name of the collection
            embedding_dim: Dimension of embeddings
            persist_directory: Directory to persist the database
        """
        try:
            import faiss
            
            self.collection_name = collection_name
            self.embedding_dim = embedding_dim
            self.persist_directory = Path(persist_directory)
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            
            self.index_path = self.persist_directory / f"{collection_name}.faiss"
            self.metadata_path = self.persist_directory / f"{collection_name}_metadata.pkl"
            
            # Initialize or load index
            if self.index_path.exists():
                self.index = faiss.read_index(str(self.index_path))
                with open(self.metadata_path, 'rb') as f:
                    self.documents = pickle.load(f)
                logger.info(f"Loaded existing FAISS index with {self.index.ntotal} vectors")
            else:
                # Create new index (using inner product for cosine similarity)
                self.index = faiss.IndexFlatIP(embedding_dim)
                self.documents = []
                logger.info(f"Created new FAISS index")
            
        except ImportError:
            raise ImportError("faiss not installed. Run: pip install faiss-cpu")
    
    def add_documents(
        self,
        texts: List[str],
        embeddings: np.ndarray,
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ):
        """
        Add documents to FAISS.
        
        Args:
            texts: List of text strings
            embeddings: Numpy array of embeddings (should be normalized for cosine similarity)
            metadatas: List of metadata dictionaries
            ids: Optional list of document IDs
        """
        if ids is None:
            ids = [f"doc_{len(self.documents) + i}" for i in range(len(texts))]
        
        # Normalize embeddings for cosine similarity
        embeddings_normalized = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Add to index
        self.index.add(embeddings_normalized.astype('float32'))
        
        # Store documents with metadata
        for text, metadata, doc_id in zip(texts, metadatas, ids):
            self.documents.append({
                'id': doc_id,
                'text': text,
                'metadata': metadata
            })
        
        # Persist
        self._persist()
        logger.info(f"Added {len(texts)} documents to FAISS index")
    
    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents in FAISS.
        
        Args:
            query_embedding: Query embedding vector (should be normalized)
            k: Number of results to return
            filter_dict: Optional metadata filter
            
        Returns:
            List of result dictionaries
        """
        # Normalize query embedding
        query_normalized = query_embedding / np.linalg.norm(query_embedding)
        query_normalized = query_normalized.reshape(1, -1).astype('float32')
        
        # Search
        distances, indices = self.index.search(query_normalized, min(k * 2, len(self.documents)))
        
        # Filter results based on metadata
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx == -1 or idx >= len(self.documents):
                continue
            
            doc = self.documents[idx]
            
            # Apply metadata filter if provided
            if filter_dict:
                match = all(
                    doc['metadata'].get(key) == value
                    for key, value in filter_dict.items()
                )
                if not match:
                    continue
            
            results.append({
                'text': doc['text'],
                'metadata': doc['metadata'],
                'distance': float(distance),
                'id': doc['id']
            })
            
            if len(results) >= k:
                break
        
        return results
    
    def _persist(self):
        """Persist index and metadata to disk."""
        import faiss
        faiss.write_index(self.index, str(self.index_path))
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.documents, f)
    
    def delete_collection(self):
        """Delete the collection files."""
        if self.index_path.exists():
            self.index_path.unlink()
        if self.metadata_path.exists():
            self.metadata_path.unlink()
        logger.info(f"Deleted collection: {self.collection_name}")


def create_vector_store(
    store_type: str = "chroma",
    collection_name: str = "default",
    embedding_dim: int = None,
    persist_directory: str = "./vector_db"
) -> VectorStore:
    """
    Factory function to create a vector store.
    
    Args:
        store_type: Type of store ('chroma' or 'faiss')
        collection_name: Name of the collection
        embedding_dim: Embedding dimension (required for FAISS)
        persist_directory: Directory to persist data
        
    Returns:
        VectorStore instance
    """
    if store_type.lower() == 'chroma':
        return ChromaVectorStore(collection_name, persist_directory)
    elif store_type.lower() == 'faiss':
        if embedding_dim is None:
            raise ValueError("embedding_dim is required for FAISS")
        return FAISSVectorStore(collection_name, embedding_dim, persist_directory)
    else:
        raise ValueError(f"Unknown store type: {store_type}")
