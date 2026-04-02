from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseChunker(ABC):
    """Abstract base class for all chunking strategies"""
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    @abstractmethod
    def chunk(
        self, 
        text: str, 
        chunk_size: int = 512, 
        chunk_overlap: int = 50,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Chunk the input text using the specific strategy.
        
        Args:
            text: Input text to chunk
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between consecutive chunks
            **kwargs: Additional strategy-specific parameters
            
        Returns:
            List of chunks, where each chunk is a dict with:
                - text: The chunk text
                - metadata: Additional metadata (position, type, etc.)
        """
        pass
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Return information about this chunking strategy"""
        return {
            "name": self.name,
            "description": self.__doc__ or "No description available"
        }
