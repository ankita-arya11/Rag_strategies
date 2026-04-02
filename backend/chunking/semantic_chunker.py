from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os

from chunking import BaseChunker


class SemanticChunker(BaseChunker):
    """
    Semantic chunking strategy that groups text based on semantic similarity.
    Uses embeddings to determine natural breakpoints in the text.
    """
    
    def __init__(self):
        super().__init__()
        # OpenAI API key should be set via OPENAI_API_KEY environment variable
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )
        self.similarity_threshold = 0.7  # Threshold for semantic similarity
    
    def chunk(
        self, 
        text: str, 
        chunk_size: int = 512, 
        chunk_overlap: int = 50,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Chunk text based on semantic similarity between sentences.
        
        1. Split text into sentences
        2. Embed each sentence
        3. Calculate similarity between consecutive sentences
        4. Group sentences with high similarity
        5. Ensure chunks don't exceed chunk_size
        """
        # Split into sentences first
        sentences = self._split_into_sentences(text)
        
        if not sentences:
            return []
        
        # Get embeddings for sentences
        sentence_embeddings = self.embeddings.embed_documents(sentences)
        
        # Calculate similarity scores
        similarities = []
        for i in range(len(sentence_embeddings) - 1):
            emb1 = np.array(sentence_embeddings[i]).reshape(1, -1)
            emb2 = np.array(sentence_embeddings[i + 1]).reshape(1, -1)
            sim = cosine_similarity(emb1, emb2)[0][0]
            similarities.append(sim)
        
        # Group sentences into chunks based on similarity
        chunks = []
        current_chunk = [sentences[0]]
        current_size = len(sentences[0])
        
        for i, sentence in enumerate(sentences[1:]):
            sentence_len = len(sentence)
            
            # Check if we should start a new chunk
            if (i < len(similarities) and similarities[i] < self.similarity_threshold) or \
               (current_size + sentence_len > chunk_size):
                # Save current chunk
                if current_chunk:
                    chunks.append({
                        "text": " ".join(current_chunk),
                        "metadata": {
                            "chunk_type": "semantic",
                            "sentence_count": len(current_chunk),
                            "avg_similarity": np.mean([similarities[j] for j in range(len(current_chunk)-1)]) if len(current_chunk) > 1 else 1.0
                        }
                    })
                current_chunk = [sentence]
                current_size = sentence_len
            else:
                current_chunk.append(sentence)
                current_size += sentence_len
        
        # Add last chunk
        if current_chunk:
            chunks.append({
                "text": " ".join(current_chunk),
                "metadata": {
                    "chunk_type": "semantic",
                    "sentence_count": len(current_chunk),
                    "avg_similarity": np.mean([similarities[j] for j in range(len(current_chunk)-1)]) if len(current_chunk) > 1 else 1.0
                }
            })
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Simple sentence splitter"""
        import re
        # Split on period, exclamation, or question mark followed by space
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
