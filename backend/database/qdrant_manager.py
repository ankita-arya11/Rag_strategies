from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_openai import OpenAIEmbeddings
from typing import List, Dict, Any, Optional
import os
import uuid
from dotenv import load_dotenv

load_dotenv()
class QdrantManager:
    """Manager for Qdrant vector database operations"""
    
    def __init__(self):
        qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
        
        self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        # OpenAI API key should be set via OPENAI_API_KEY environment variable
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )
        # OpenAI text-embedding-3-small has 1536 dimensions
        self.vector_size = 1536
    
    def health_check(self) -> Dict[str, Any]:
        """Check if Qdrant is accessible"""
        try:
            collections = self.client.get_collections()
            return {
                "status": "healthy",
                "collections_count": len(collections.collections)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def create_collection(self, collection_name: str, force_recreate: bool = False):
        """Create a new collection in Qdrant"""
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            exists = any(c.name == collection_name for c in collections)
            
            if exists and force_recreate:
                self.client.delete_collection(collection_name)
                exists = False
            
            if not exists:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                return {"status": "created", "collection": collection_name}
            else:
                return {"status": "exists", "collection": collection_name}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def add_chunks(
        self, 
        collection_name: str, 
        chunks: List[Dict[str, Any]], 
        document_id: str
    ):
        """Add chunks to a collection with embeddings"""
        try:
            # Extract text from chunks
            texts = [chunk["text"] for chunk in chunks]
            
            # Generate embeddings
            embeddings = self.embeddings.embed_documents(texts)
            
            # Create points for Qdrant
            points = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "text": chunk["text"],
                        "metadata": chunk.get("metadata", {}),
                        "document_id": document_id,
                        "chunk_index": i
                    }
                )
                points.append(point)
            
            # Upload to Qdrant
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            return {
                "status": "success",
                "chunks_added": len(points),
                "collection": collection_name
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def search(
        self, 
        collection_name: str, 
        query_vector: List[float], 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors in a collection"""
        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit
            )
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "text": result.payload.get("text", ""),
                    "score": result.score,
                    "metadata": result.payload.get("metadata", {}),
                    "document_id": result.payload.get("document_id", ""),
                    "chunk_index": result.payload.get("chunk_index", 0)
                })
            
            return formatted_results
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def get_all_points(self, collection_name: str) -> List[Dict[str, Any]]:
        """Get all points from a collection"""
        try:
            # Scroll through all points
            points, _ = self.client.scroll(
                collection_name=collection_name,
                limit=10000  # Adjust as needed
            )
            
            formatted_points = []
            for point in points:
                formatted_points.append({
                    "id": point.id,
                    "text": point.payload.get("text", ""),
                    "metadata": point.payload.get("metadata", {}),
                    "document_id": point.payload.get("document_id", ""),
                    "chunk_index": point.payload.get("chunk_index", 0)
                })
            
            return formatted_points
        except Exception as e:
            print(f"Error getting points: {e}")
            return []
    
    def list_collections(self) -> List[str]:
        """List all collection names"""
        try:
            collections = self.client.get_collections().collections
            return [c.name for c in collections]
        except Exception as e:
            print(f"Error listing collections: {e}")
            return []
    
    def delete_collection(self, collection_name: str):
        """Delete a collection"""
        try:
            self.client.delete_collection(collection_name)
            return {"status": "deleted", "collection": collection_name}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a collection"""
        try:
            info = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status
            }
        except Exception as e:
            return {"error": str(e)}
