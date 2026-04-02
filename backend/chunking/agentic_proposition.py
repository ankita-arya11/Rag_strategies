from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import os
import json

from chunking import BaseChunker


class AgenticPropositionChunker(BaseChunker):
    """
    Agentic proposition chunking strategy that uses an LLM to identify
    and extract atomic propositions (self-contained facts) from text.
    Each chunk represents a complete, standalone proposition.
    """
    
    def __init__(self):
        super().__init__()
        # OpenAI API key should be set via OPENAI_API_KEY environment variable
        # Using gpt-3.5-turbo-16k for larger context window (16k tokens)
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo-16k",
            temperature=0,
            max_tokens=4000  # Max tokens for response
        )
        
        self.proposition_prompt = PromptTemplate(
            input_variables=["text"],
            template="""Extract atomic propositions from the following text. 
Each proposition should be:
1. A self-contained fact or statement
2. Understandable without additional context
3. As concise as possible while maintaining complete meaning

Text: {text}

Return a JSON array of propositions. Example format:
["Proposition 1", "Proposition 2", "Proposition 3"]

Important: Return ONLY the JSON array, no additional text.

Propositions:"""
        )
    
    def chunk(
        self, 
        text: str, 
        chunk_size: int = 512, 
        chunk_overlap: int = 50,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Chunk text by extracting atomic propositions using LLM.
        
        1. Split text into manageable segments
        2. Use LLM to extract propositions from each segment
        3. Group related propositions if they're small
        4. Return propositions as chunks
        """
        # Split text into larger segments for processing
        # Using 12000 chars (~3000 tokens) to maximize context window usage
        # This reduces API calls significantly (e.g., 163k chars = ~14 calls instead of 82)
        segments = self._split_into_segments(text, max_segment_size=12000)
        
        all_propositions = []
        
        print(f"📝 Processing {len(segments)} segments (reduced API calls)")
        
        for segment_idx, segment in enumerate(segments):
            # Extract propositions using LLM
            print(f"   Segment {segment_idx + 1}/{len(segments)} ({len(segment)} chars)...")
            try:
                prompt = self.proposition_prompt.format(text=segment)
                response = self.llm.invoke(prompt)
                
                # Parse response
                propositions = self._parse_propositions(response.content)
                
                # Add metadata
                for prop in propositions:
                    all_propositions.append({
                        "text": prop,
                        "metadata": {
                            "chunk_type": "agentic_proposition",
                            "segment_index": segment_idx,
                            "extraction_method": "llm"
                        }
                    })
            except Exception as e:
                # Fallback: treat segment as single chunk
                all_propositions.append({
                    "text": segment,
                    "metadata": {
                        "chunk_type": "agentic_proposition",
                        "segment_index": segment_idx,
                        "extraction_method": "fallback",
                        "error": str(e)
                    }
                })
        
        # Group small propositions together
        chunks = self._group_propositions(all_propositions, chunk_size)
        
        return chunks
    
    def _split_into_segments(self, text: str, max_segment_size: int = 12000) -> List[str]:
        """
        Split text into segments for LLM processing.
        Now using larger segments (12k chars ~= 3k tokens) to reduce API calls.
        
        For 163k char document: 12k segments = ~14 API calls vs 2k segments = ~82 calls
        Cost savings: ~83% fewer API calls!
        """
        # Split by paragraphs first for better semantic boundaries
        paragraphs = text.split('\n\n')
        segments = []
        current_segment = []
        current_size = 0
        
        for para in paragraphs:
            para_size = len(para) + 2  # +2 for \n\n
            if current_size + para_size > max_segment_size and current_segment:
                segments.append('\n\n'.join(current_segment))
                current_segment = [para]
                current_size = para_size
            else:
                current_segment.append(para)
                current_size += para_size
        
        if current_segment:
            segments.append('\n\n'.join(current_segment))
        
        return segments
    
    def _parse_propositions(self, response: str) -> List[str]:
        """Parse LLM response to extract propositions"""
        try:
            # Try to parse as JSON
            response = response.strip()
            if response.startswith("```"):
                # Remove markdown code blocks
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            
            propositions = json.loads(response.strip())
            
            if isinstance(propositions, list):
                return [str(p).strip() for p in propositions if p]
            else:
                return [str(propositions)]
        except:
            # Fallback: split by newlines
            lines = [line.strip() for line in response.split('\n') if line.strip()]
            # Remove numbering and bullet points
            cleaned = []
            for line in lines:
                line = line.lstrip('0123456789.-) ')
                if line and len(line) > 10:  # Filter out very short lines
                    cleaned.append(line)
            return cleaned if cleaned else [response]
    
    def _group_propositions(
        self, 
        propositions: List[Dict[str, Any]], 
        max_chunk_size: int
    ) -> List[Dict[str, Any]]:
        """Group small propositions together to create optimal chunks"""
        chunks = []
        current_texts = []
        current_size = 0
        current_metadata = []
        
        for prop in propositions:
            prop_size = len(prop["text"])
            
            if current_size + prop_size > max_chunk_size and current_texts:
                # Save current chunk
                chunks.append({
                    "text": " ".join(current_texts),
                    "metadata": {
                        "chunk_type": "agentic_proposition",
                        "proposition_count": len(current_texts),
                        "combined": True
                    }
                })
                current_texts = [prop["text"]]
                current_size = prop_size
            else:
                current_texts.append(prop["text"])
                current_size += prop_size
        
        # Add last chunk
        if current_texts:
            chunks.append({
                "text": " ".join(current_texts),
                "metadata": {
                    "chunk_type": "agentic_proposition",
                    "proposition_count": len(current_texts),
                    "combined": True
                }
            })
        
        return chunks
