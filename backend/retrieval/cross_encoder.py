from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings
from sentence_transformers import CrossEncoder
import os

from retrieval import BaseRetriever


class CrossEncoderRetrieval(BaseRetriever):
    """
    Retrieval with Cross-Encoder reranking.
    First retrieves candidates using vector search, then reranks using
    a cross-encoder model for more accurate relevance scoring.
    """
    
    def __init__(self, qdrant_manager):
        super().__init__(qdrant_manager)
        # OpenAI API key should be set via OPENAI_API_KEY environment variable
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )
        # Use a pre-trained cross-encoder for reranking
        self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        self.initial_retrieve_k = 20  # Retrieve more candidates for reranking
    
    def retrieve(
        self, 
        query: str, 
        collection_name: Optional[str] = None,
        top_k: int = 5,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Retrieve using vector search + cross-encoder reranking.
        
        1. Initial retrieval using vector similarity (gets more candidates)
        2. Rerank candidates using cross-encoder
        3. Return top_k results
        """
        # Get all collections if not specified
        collections = [collection_name] if collection_name else self.qdrant_manager.list_collections()
        
        all_candidates = []
        
        # Phase 1: Initial retrieval
        for collection in collections:
            try:
                # Vector search to get candidates
                query_vector = self.embeddings.embed_query(query)
                results = self.qdrant_manager.search(
                    collection_name=collection,
                    query_vector=query_vector,
                    limit=self.initial_retrieve_k
                )
                all_candidates.extend(results)
            except Exception as e:
                print(f"Error searching collection {collection}: {e}")
                continue
        
        if not all_candidates:
            return []
        
        # Phase 2: Rerank using cross-encoder
        reranked_results = self._rerank_with_cross_encoder(query, all_candidates)
        
        # Return top_k
        return reranked_results[:top_k]
    
    def _rerank_with_cross_encoder(
        self, 
        query: str, 
        candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rerank candidates using cross-encoder"""
        # Prepare pairs for cross-encoder
        pairs = [[query, candidate['text']] for candidate in candidates]
        
        # Get cross-encoder scores
        scores = self.cross_encoder.predict(pairs)
        
        # Update scores and metadata
        for i, candidate in enumerate(candidates):
            candidate['score'] = float(scores[i])
            candidate['metadata'] = candidate.get('metadata', {})
            candidate['metadata']['reranked'] = True
            candidate['metadata']['original_score'] = candidate.get('original_score', candidate['score'])
        
        # Sort by new scores
        reranked = sorted(candidates, key=lambda x: x['score'], reverse=True)
        
        return reranked
