from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseRetriever(ABC):
    """Abstract base class for all retrieval strategies"""
    
    def __init__(self, qdrant_manager=None):
        self.name = self.__class__.__name__
        self.qdrant_manager = qdrant_manager
    
    @abstractmethod
    def retrieve(
        self, 
        query: str, 
        collection_name: Optional[str] = None,
        top_k: int = 5,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks using the specific strategy.
        
        Args:
            query: Search query
            collection_name: Qdrant collection to search in (None for all)
            top_k: Number of results to return
            **kwargs: Additional strategy-specific parameters
            
        Returns:
            List of retrieved chunks, where each is a dict with:
                - text: The chunk text
                - score: Relevance score
                - metadata: Additional metadata
        """
        pass
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Return information about this retrieval strategy"""
        return {
            "name": self.name,
            "description": self.__doc__ or "No description available"
        }
