"""
Document processing module for extracting and chunking text from various sources.
"""

import re
from typing import List, Dict, Any
from pathlib import Path
import pypdf
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentChunk:
    """Represents a chunk of text with metadata."""
    
    def __init__(
        self,
        text: str,
        metadata: Dict[str, Any],
        chunk_id: str = None
    ):
        self.text = text
        self.metadata = metadata
        self.chunk_id = chunk_id or f"{metadata.get('source', 'unknown')}_{hash(text)}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "metadata": self.metadata
        }


class DocumentProcessor:
    """Process documents and split them into chunks."""
    
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF file."""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            logger.info(f"Extracted {len(text)} characters from {pdf_path}")
            return self.clean_text(text)
        except Exception as e:
            logger.error(f"Error extracting PDF {pdf_path}: {e}")
            return ""
    
    def extract_from_html(self, html_content: str) -> str:
        """Extract text from HTML content."""
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            return self.clean_text(text)
        except Exception as e:
            logger.error(f"Error extracting HTML: {e}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove multiple spaces and newlines
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\-\(\)\[\]\/]', '', text)
        # Fix common PDF extraction issues
        text = text.replace('­', '')  # Remove soft hyphens
        return text.strip()
    
    def chunk_text(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[DocumentChunk]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: The text to chunk
            metadata: Metadata to attach to each chunk
            
        Returns:
            List of DocumentChunk objects
        """
        if not text:
            return []
        
        # Split by sentences for better chunking
        sentences = self._split_into_sentences(text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence.split())
            
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Create a chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append(DocumentChunk(
                    text=chunk_text,
                    metadata=metadata.copy()
                ))
                
                # Start new chunk with overlap
                overlap_words = []
                overlap_length = 0
                for s in reversed(current_chunk):
                    s_len = len(s.split())
                    if overlap_length + s_len <= self.chunk_overlap:
                        overlap_words.insert(0, s)
                        overlap_length += s_len
                    else:
                        break
                
                current_chunk = overlap_words
                current_length = overlap_length
            
            current_chunk.append(sentence)
            current_length += sentence_length
        
        # Add the last chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append(DocumentChunk(
                text=chunk_text,
                metadata=metadata.copy()
            ))
        
        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitter
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def process_degree_requirement_doc(
        self,
        file_path: str,
        program: str,
        degree: str,
        catalog_year: int,
        source_url: str = None
    ) -> List[DocumentChunk]:
        """
        Process a degree requirement document.
        
        Args:
            file_path: Path to the document
            program: Program name (e.g., "MS Computer Science")
            degree: Degree type (e.g., "MS", "BS")
            catalog_year: Academic year
            source_url: URL of the source document
            
        Returns:
            List of DocumentChunk objects
        """
        path = Path(file_path)
        
        # Extract text based on file type
        if path.suffix.lower() == '.pdf':
            text = self.extract_from_pdf(file_path)
        elif path.suffix.lower() in ['.html', '.htm']:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            text = self.extract_from_html(html_content)
        elif path.suffix.lower() == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            text = self.clean_text(text)
        else:
            logger.error(f"Unsupported file type: {path.suffix}")
            return []
        
        # Create metadata
        metadata = {
            "source": file_path,
            "source_url": source_url or "",
            "program": program,
            "degree": degree,
            "catalog_year": catalog_year,
            "doc_type": "degree_requirement"
        }
        
        # Chunk the text
        chunks = self.chunk_text(text, metadata)
        
        # Extract course codes if present
        for chunk in chunks:
            course_codes = self._extract_course_codes(chunk.text)
            if course_codes:
                chunk.metadata["course_codes"] = course_codes
        
        return chunks
    
    def _extract_course_codes(self, text: str) -> List[str]:
        """Extract course codes from text (e.g., COMS 4111, ENGI 6000)."""
        pattern = r'\b[A-Z]{4}\s*\d{4}\b'
        matches = re.findall(pattern, text)
        # Normalize spacing
        codes = [re.sub(r'\s+', ' ', code) for code in matches]
        return list(set(codes))  # Remove duplicates


if __name__ == "__main__":
    # Example usage
    processor = DocumentProcessor(chunk_size=600, chunk_overlap=100)
    
    # Example text
    sample_text = """
    The Master of Science in Computer Science requires 30 credits.
    Students must complete the following core courses: COMS 4111 (Database Systems),
    COMS 4156 (Advanced Software Engineering), and COMS 4701 (Artificial Intelligence).
    Additionally, students must complete 18 credits of electives from approved courses.
    """
    
    chunks = processor.chunk_text(
        sample_text,
        metadata={"program": "MS CS", "catalog_year": 2023}
    )
    
    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i+1} ---")
        print(f"Text: {chunk.text[:100]}...")
        print(f"Metadata: {chunk.metadata}")



