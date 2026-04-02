from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

from chunking import BaseChunker


class HybridChunker(BaseChunker):
    """
    Hybrid chunking strategy that combines multiple approaches:
    1. Respects document structure (paragraphs, sections)
    2. Uses character-based splitting for size control
    3. Maintains semantic coherence through recursive splitting
    """
    
    def __init__(self):
        super().__init__()
        # Use recursive character splitter with smart separators
        self.splitter = None  # Will be initialized per request
    
    def chunk(
        self, 
        text: str, 
        chunk_size: int = 512, 
        chunk_overlap: int = 50,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Chunk text using a hybrid approach that combines:
        - Structural boundaries (paragraphs, sections)
        - Character limits
        - Recursive splitting for optimal size
        
        This approach tries to keep semantic units together while
        respecting size constraints.
        """
        # Define separators in order of preference
        separators = [
            "\n\n\n",  # Multiple newlines (section breaks)
            "\n\n",    # Paragraph breaks
            "\n",      # Line breaks
            ". ",      # Sentence ends
            "! ",      # Exclamation
            "? ",      # Question
            "; ",      # Semicolon
            ", ",      # Comma
            " ",       # Space
            ""         # Character-level
        ]
        
        # Initialize splitter with current parameters
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
            is_separator_regex=False
        )
        
        # Split the text
        text_chunks = self.splitter.split_text(text)
        
        # Add metadata to each chunk
        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            # Detect chunk type based on content
            chunk_type = self._detect_chunk_type(chunk_text)
            
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "chunk_type": "hybrid",
                    "position": i,
                    "total_chunks": len(text_chunks),
                    "detected_type": chunk_type,
                    "char_count": len(chunk_text),
                    "word_count": len(chunk_text.split())
                }
            })
        
        return chunks
    
    def _detect_chunk_type(self, text: str) -> str:
        """Detect the type of content in a chunk"""
        # Simple heuristics to detect content type
        lines = text.split('\n')
        
        # Check for lists
        list_indicators = sum(1 for line in lines if line.strip().startswith(('-', '*', '•', '1.', '2.')))
        if list_indicators > len(lines) * 0.5:
            return "list"
        
        # Check for code
        code_indicators = text.count('(') + text.count('{') + text.count('[')
        if code_indicators > len(text.split()) * 0.2:
            return "code_or_structured"
        
        # Check for headings (short lines, possibly with special chars)
        if len(lines) > 0 and len(lines[0]) < 100 and lines[0].isupper():
            return "heading"
        
        # Check for table-like structure
        if '|' in text and text.count('|') > 5:
            return "table"
        
        # Default to paragraph
        return "paragraph"
