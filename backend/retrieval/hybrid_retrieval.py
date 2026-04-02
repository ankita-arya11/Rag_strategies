from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings
from rank_bm25 import BM25Okapi
import os
import numpy as np

from retrieval import BaseRetriever


class HybridRetrieval(BaseRetriever):
    """
    Hybrid retrieval combining dense (vector) and sparse (BM25) search.
    Uses weighted combination to rank results.
    """
    
    def __init__(self, qdrant_manager):
        super().__init__(qdrant_manager)
        # OpenAI API key should be set via OPENAI_API_KEY environment variable
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )
        self.dense_weight = 0.7  # Weight for vector search
        self.sparse_weight = 0.3  # Weight for BM25
    
    def retrieve(
        self, 
        query: str, 
        collection_name: Optional[str] = None,
        top_k: int = 5,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Retrieve using hybrid search (dense + sparse).
        
        1. Perform dense vector search using embeddings
        2. Perform sparse BM25 search
        3. Combine and rerank results
        """
        # Get all collections if not specified
        collections = [collection_name] if collection_name else self.qdrant_manager.list_collections()
        
        all_results = []
        
        for collection in collections:
            try:
                # Dense retrieval (vector search)
                query_vector = self.embeddings.embed_query(query)
                dense_results = self.qdrant_manager.search(
                    collection_name=collection,
                    query_vector=query_vector,
                    limit=top_k * 2  # Get more for reranking
                )
                
                # Sparse retrieval (BM25)
                sparse_results = self._bm25_search(collection, query, limit=top_k * 2)
                
                # Combine results
                combined = self._combine_results(dense_results, sparse_results)
                all_results.extend(combined)
                
            except Exception as e:
                print(f"Error searching collection {collection}: {e}")
                continue
        
        # Sort by combined score and take top_k
        all_results.sort(key=lambda x: x['score'], reverse=True)
        return all_results[:top_k]
    
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
            if scores[idx] > 0:  # Only include relevant results
                results.append({
                    'text': all_docs[idx]['text'],
                    'score': float(scores[idx]),
                    'metadata': all_docs[idx].get('metadata', {}),
                    'source': 'bm25'
                })
        
        return results
    
    def _combine_results(
        self, 
        dense_results: List[Dict[str, Any]], 
        sparse_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Combine dense and sparse results with weighted scoring"""
        # Create a map to deduplicate results
        result_map = {}
        
        # Normalize scores for dense results
        max_dense = max([r['score'] for r in dense_results], default=1.0)
        for result in dense_results:
            text = result['text']
            normalized_score = result['score'] / max_dense if max_dense > 0 else 0
            
            if text in result_map:
                result_map[text]['score'] += normalized_score * self.dense_weight
            else:
                result_map[text] = {
                    'text': text,
                    'score': normalized_score * self.dense_weight,
                    'metadata': result.get('metadata', {}),
                    'sources': ['dense']
                }
        
        # Normalize scores for sparse results
        max_sparse = max([r['score'] for r in sparse_results], default=1.0)
        for result in sparse_results:
            text = result['text']
            normalized_score = result['score'] / max_sparse if max_sparse > 0 else 0
            
            if text in result_map:
                result_map[text]['score'] += normalized_score * self.sparse_weight
                result_map[text]['sources'].append('sparse')
            else:
                result_map[text] = {
                    'text': text,
                    'score': normalized_score * self.sparse_weight,
                    'metadata': result.get('metadata', {}),
                    'sources': ['sparse']
                }
        
        # Convert map to list
        combined_results = list(result_map.values())
        
        return combined_results
