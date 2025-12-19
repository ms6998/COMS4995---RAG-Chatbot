"""
Vector database module for storing and retrieving embeddings
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
        except ImportError:
            raise ImportError("chromadb not installed. Run: pip install chromadb")

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


def create_vector_store(
    store_type: str = "chroma",
    collection_name: str = "default",
    persist_directory: str = "./vector_db"
) -> VectorStore:
    """
    Factory function to create a vector store. Only Chroma is supported
    for the proof-of-concept

    Args:
        store_type: Type of store ('chroma')
        collection_name: Name of the collection
        persist_directory: Directory to persist data

    Returns:
        VectorStore instance
    """
    if store_type.lower() == "chroma":
        return ChromaVectorStore(
            collection_name,
            persist_directory,
        )
    raise ValueError(f"Unknown store type: {store_type}")
