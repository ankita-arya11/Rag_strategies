from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings
from rank_bm25 import BM25Okapi
import os
import numpy as np
from collections import defaultdict

from retrieval import BaseRetriever


class RRFRetrieval(BaseRetriever):
    """
    Reciprocal Rank Fusion (RRF) retrieval strategy.
    Combines multiple retrieval methods using rank-based fusion.
    RRF is robust and doesn't require score normalization.
    """
    
    def __init__(self, qdrant_manager):
        super().__init__(qdrant_manager)
        # OpenAI API key should be set via OPENAI_API_KEY environment variable
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )
        self.k = 60  # RRF constant (typically 60)
    
    def retrieve(
        self, 
        query: str, 
        collection_name: Optional[str] = None,
        top_k: int = 5,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Retrieve using Reciprocal Rank Fusion.
        
        RRF formula: score(d) = Σ 1 / (k + rank_i(d))
        where rank_i(d) is the rank of document d in retrieval method i
        
        Combines:
        1. Dense vector search
        2. BM25 sparse search
        Using rank-based fusion
        """
        # Get all collections if not specified
        collections = [collection_name] if collection_name else self.qdrant_manager.list_collections()
        
        # Store ranked lists from different methods
        ranked_lists = []
        
        for collection in collections:
            try:
                # Method 1: Dense vector search
                query_vector = self.embeddings.embed_query(query)
                dense_results = self.qdrant_manager.search(
                    collection_name=collection,
                    query_vector=query_vector,
                    limit=top_k * 3
                )
                ranked_lists.append(('dense', dense_results))
                
                # Method 2: BM25 sparse search
                sparse_results = self._bm25_search(collection, query, limit=top_k * 3)
                ranked_lists.append(('bm25', sparse_results))
                
            except Exception as e:
                print(f"Error searching collection {collection}: {e}")
                continue
        
        if not ranked_lists:
            return []
        
        # Apply RRF
        fused_results = self._reciprocal_rank_fusion(ranked_lists)
        
        # Sort by RRF score and return top_k
        fused_results.sort(key=lambda x: x['score'], reverse=True)
        return fused_results[:top_k]
    
    def _bm25_search(self, collection_name: str, query: str, limit: int) -> List[Dict[str, Any]]:
        """Perform BM25 sparse search"""
        # Get all documents from collection
        all_docs = self.qdrant_manager.get_all_points(collection_name)
        
        if not all_docs:
            return []
        
        # Prepare corpus for BM25
        corpus = [doc['text'] for doc in all_docs]
        tokenized_corpus = [doc.lower().split() for doc in corpus]
        
        # Initialize BM25
        bm25 = BM25Okapi(tokenized_corpus)
        
        # Search
        tokenized_query = query.lower().split()
        scores = bm25.get_scores(tokenized_query)
        
        # Get top results
        top_indices = np.argsort(scores)[::-1][:limit]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append({
                    'text': all_docs[idx]['text'],
                    'score': float(scores[idx]),
                    'metadata': all_docs[idx].get('metadata', {})
                })
        
        return results
    
    def _reciprocal_rank_fusion(
        self, 
        ranked_lists: List[tuple]
    ) -> List[Dict[str, Any]]:
        """
        Apply Reciprocal Rank Fusion to combine multiple ranked lists.
        
        RRF score(d) = Σ 1 / (k + rank_i(d))
        """
        # Dictionary to accumulate RRF scores
        rrf_scores = defaultdict(float)
        # Dictionary to store document details
        doc_details = {}
        # Dictionary to track which methods retrieved each document
        doc_sources = defaultdict(list)
        
        for method_name, ranked_list in ranked_lists:
            for rank, doc in enumerate(ranked_list, start=1):
                doc_text = doc['text']
                
                # Calculate RRF contribution
                rrf_contribution = 1.0 / (self.k + rank)
                rrf_scores[doc_text] += rrf_contribution
                
                # Store document details (first time we see it)
                if doc_text not in doc_details:
                    doc_details[doc_text] = {
                        'text': doc_text,
                        'metadata': doc.get('metadata', {})
                    }
                
                # Track sources
                doc_sources[doc_text].append({
                    'method': method_name,
                    'rank': rank,
                    'original_score': doc.get('score', 0)
                })
        
        # Build final results
        results = []
        for doc_text, rrf_score in rrf_scores.items():
            result = doc_details[doc_text].copy()
            result['score'] = rrf_score
            result['metadata']['rrf_sources'] = doc_sources[doc_text]
            result['metadata']['fusion_method'] = 'reciprocal_rank_fusion'
            results.append(result)
        
        return results
