"""
Indexing module for building and managing vector indices.
"""

from typing import List, Dict, Any
from pathlib import Path
import json
import logging
from tqdm import tqdm

from .document_processor import DocumentProcessor, DocumentChunk
from .embeddings import EmbeddingGenerator
from .vector_store import VectorStore, create_vector_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentIndexer:
    """
    Indexer for processing documents and building vector indices.
    """
    
    def __init__(
        self,
        document_processor: DocumentProcessor,
        embedder: EmbeddingGenerator,
        vector_store: VectorStore
    ):
        """
        Initialize the indexer.
        
        Args:
            document_processor: Document processor instance
            embedder: Embedding generator instance
            vector_store: Vector store instance
        """
        self.processor = document_processor
        self.embedder = embedder
        self.vector_store = vector_store
        logger.info("Initialized DocumentIndexer")
    
    def index_degree_requirements(
        self,
        documents: List[Dict[str, Any]],
        batch_size: int = 32
    ):
        """
        Index degree requirement documents.
        
        Args:
            documents: List of document info dicts with keys:
                - file_path: Path to document
                - program: Program name
                - degree: Degree type
                - catalog_year: Academic year
                - source_url: Optional URL
            batch_size: Batch size for embedding generation
        """
        logger.info(f"Indexing {len(documents)} degree requirement documents...")
        
        all_chunks = []
        
        # Process all documents
        for doc_info in tqdm(documents, desc="Processing documents"):
            chunks = self.processor.process_degree_requirement_doc(
                file_path=doc_info['file_path'],
                program=doc_info['program'],
                degree=doc_info['degree'],
                catalog_year=doc_info['catalog_year'],
                source_url=doc_info.get('source_url', '')
            )
            all_chunks.extend(chunks)
        
        if not all_chunks:
            logger.warning("No chunks generated from documents")
            return
        
        logger.info(f"Generated {len(all_chunks)} chunks")
        
        # Extract texts and metadata
        texts = [chunk.text for chunk in all_chunks]
        metadatas = [chunk.metadata for chunk in all_chunks]
        ids = [chunk.chunk_id for chunk in all_chunks]
        
        # Generate embeddings in batches
        logger.info("Generating embeddings...")
        embeddings = self.embedder.encode_documents(texts, batch_size=batch_size)
        
        # Add to vector store
        logger.info("Adding to vector store...")
        self.vector_store.add_documents(
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info("Indexing complete!")
    
    def index_professor_ratings(
        self,
        ratings_file: str,
        batch_size: int = 32
    ):
        """
        Index professor ratings from a CSV or JSON file.
        
        Args:
            ratings_file: Path to ratings file (CSV or JSON)
            batch_size: Batch size for embedding
        """
        logger.info(f"Indexing professor ratings from {ratings_file}...")
        
        # Load ratings data
        ratings_path = Path(ratings_file)
        
        if ratings_path.suffix == '.json':
            with open(ratings_path, 'r') as f:
                ratings_data = json.load(f)
        elif ratings_path.suffix == '.csv':
            import pandas as pd
            df = pd.read_csv(ratings_path)
            ratings_data = df.to_dict('records')
        else:
            raise ValueError(f"Unsupported file format: {ratings_path.suffix}")
        
        logger.info(f"Loaded {len(ratings_data)} professor ratings")
        
        # Format each rating as text for embedding
        texts = []
        metadatas = []
        ids = []
        
        for i, rating in enumerate(ratings_data):
            course_code = rating['course_code']
            prof_name = rating['prof_name']
            rating_score = rating['rating']
            tags = rating.get('tags', '')
            
            # Create text representation
            text = (
                f"{course_code} taught by Professor {prof_name}. "
                f"Rating: {rating_score}/5.0. "
                f"Student feedback: {tags}"
            )
            
            texts.append(text)
            metadatas.append({
                'course_code': course_code,
                'prof_name': prof_name,
                'rating': float(rating_score),
                'tags': tags,
                'doc_type': 'professor_rating'
            })
            ids.append(f"prof_{course_code}_{prof_name}_{i}")
        
        # Generate embeddings
        logger.info("Generating embeddings...")
        embeddings = self.embedder.encode_documents(texts, batch_size=batch_size)
        
        # Add to vector store
        logger.info("Adding to vector store...")
        self.vector_store.add_documents(
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info("Professor ratings indexed!")
    
    def update_index(
        self,
        new_chunks: List[DocumentChunk],
        batch_size: int = 32
    ):
        """
        Update index with new chunks.
        
        Args:
            new_chunks: List of new DocumentChunk objects
            batch_size: Batch size for embedding
        """
        if not new_chunks:
            return
        
        logger.info(f"Updating index with {len(new_chunks)} new chunks...")
        
        texts = [chunk.text for chunk in new_chunks]
        metadatas = [chunk.metadata for chunk in new_chunks]
        ids = [chunk.chunk_id for chunk in new_chunks]
        
        embeddings = self.embedder.encode_documents(texts, batch_size=batch_size)
        
        self.vector_store.add_documents(
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info("Index updated!")


def build_indices_from_config(config_path: str):
    """
    Build indices from a configuration file.
    
    Config file should be JSON with structure:
    {
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "vector_db": {
            "type": "chroma",
            "persist_directory": "./vector_db"
        },
        "degree_requirements": {
            "collection_name": "degree_requirements",
            "documents": [
                {
                    "file_path": "data/raw/ms_cs_requirements.pdf",
                    "program": "MS Computer Science",
                    "degree": "MS",
                    "catalog_year": 2023,
                    "source_url": "https://..."
                }
            ]
        },
        "professor_ratings": {
            "collection_name": "professor_ratings",
            "ratings_file": "data/sample/prof_ratings.csv"
        }
    }
    
    Args:
        config_path: Path to configuration JSON file
    """
    logger.info(f"Building indices from config: {config_path}")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Initialize components
    processor = DocumentProcessor(
        chunk_size=config.get('chunk_size', 600),
        chunk_overlap=config.get('chunk_overlap', 100)
    )
    
    embedder = EmbeddingGenerator(
        model_name=config.get('embedding_model', 'sentence-transformers/all-MiniLM-L6-v2')
    )
    
    # Build degree requirements index
    if 'degree_requirements' in config:
        req_config = config['degree_requirements']
        req_store = create_vector_store(
            store_type=config['vector_db']['type'],
            collection_name=req_config['collection_name'],
            embedding_dim=embedder.embedding_dim,
            persist_directory=config['vector_db']['persist_directory']
        )
        
        req_indexer = DocumentIndexer(processor, embedder, req_store)
        req_indexer.index_degree_requirements(req_config['documents'])
    
    # Build professor ratings index
    if 'professor_ratings' in config:
        prof_config = config['professor_ratings']
        prof_store = create_vector_store(
            store_type=config['vector_db']['type'],
            collection_name=prof_config['collection_name'],
            embedding_dim=embedder.embedding_dim,
            persist_directory=config['vector_db']['persist_directory']
        )
        
        prof_indexer = DocumentIndexer(processor, embedder, prof_store)
        prof_indexer.index_professor_ratings(prof_config['ratings_file'])
    
    logger.info("All indices built successfully!")


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
        build_indices_from_config(config_path)
    else:
        print("Usage: python indexer.py <config_file.json>")
        print("\nExample config structure:")
        example_config = {
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "chunk_size": 600,
            "chunk_overlap": 100,
            "vector_db": {
                "type": "chroma",
                "persist_directory": "./vector_db"
            },
            "degree_requirements": {
                "collection_name": "degree_requirements",
                "documents": [
                    {
                        "file_path": "data/raw/ms_cs_requirements.pdf",
                        "program": "MS Computer Science",
                        "degree": "MS",
                        "catalog_year": 2023
                    }
                ]
            },
            "professor_ratings": {
                "collection_name": "professor_ratings",
                "ratings_file": "data/sample/prof_ratings.csv"
            }
        }
        print(json.dumps(example_config, indent=2))

