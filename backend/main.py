from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from pathlib import Path
import time
import uuid
import asyncio

from database.qdrant_manager import QdrantManager
from chunking.semantic_chunker import SemanticChunker
from chunking.agentic_proposition import AgenticPropositionChunker
from chunking.hybrid_chunker import HybridChunker
from retrieval.hybrid_retrieval import HybridRetrieval
from retrieval.cross_encoder import CrossEncoderRetrieval
from retrieval.rrf_retrieval import RRFRetrieval
from utils.metrics import MetricsTracker
from utils.document_processor import DocumentProcessor

app = FastAPI(
    title="RAG Strategies API", 
    version="1.0.0",
    timeout=300  # 5 minutes timeout
)

# CORS middleware
# Allow all origins for ngrok and remote access
# For production, specify exact origins instead of ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows ngrok URLs and all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)

# Initialize components
# Use parent directory for data uploads (project root/data/uploads)
UPLOAD_DIR = Path(__file__).parent.parent / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Qdrant mode: "server" (Docker), "memory" (RAM), or "local" (file)
# Set via environment variable QDRANT_MODE
QDRANT_MODE = os.getenv("QDRANT_MODE", "server")
qdrant_manager = QdrantManager(mode=QDRANT_MODE)
metrics_tracker = MetricsTracker()
doc_processor = DocumentProcessor()

# Chunking strategies
chunking_strategies = {
    "semantic": SemanticChunker(),
    "agentic_proposition": AgenticPropositionChunker(),
    "hybrid": HybridChunker()
}

# Retrieval strategies
retrieval_strategies = {
    "hybrid": HybridRetrieval(qdrant_manager),
    "cross_encoder": CrossEncoderRetrieval(qdrant_manager),
    "rrf": RRFRetrieval(qdrant_manager)
}

# Pydantic models
class ChunkRequest(BaseModel):
    document_id: str
    strategy: str
    chunk_size: Optional[int] = 512
    chunk_overlap: Optional[int] = 50

class RetrievalRequest(BaseModel):
    query: str
    strategy: str
    document_id: Optional[str] = None
    top_k: Optional[int] = 5

class ChunkResponse(BaseModel):
    document_id: str
    strategy: str
    chunks: List[Dict[str, Any]]
    latency_ms: float
    total_chunks: int

class RetrievalResponse(BaseModel):
    query: str
    strategy: str
    results: List[Dict[str, Any]]
    latency_ms: float
    total_results: int


@app.get("/")
async def root():
    return {"message": "RAG Strategies API", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    qdrant_status = qdrant_manager.health_check()
    return {
        "status": "healthy",
        "qdrant": qdrant_status
    }


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document for processing"""
    file_path = None
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        
        # Validate file extension
        allowed_extensions = ['.pdf', '.txt', '.docx', '.doc']
        if file_extension.lower() not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not supported. Allowed: {', '.join(allowed_extensions)}"
            )
        
        file_path = UPLOAD_DIR / f"{doc_id}{file_extension}"
        
        # Save file in chunks to handle large files
        print(f"📁 Uploading file: {file.filename}")
        
        try:
            content = await asyncio.wait_for(file.read(), timeout=60.0)
        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail="File upload timeout")
        except asyncio.CancelledError:
            print("⚠️ Upload cancelled by client")
            raise HTTPException(status_code=499, detail="Upload cancelled")
        
        # Check file size (max 50MB)
        if len(content) > 50 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large (max 50MB)")
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        print(f"✅ File saved: {file_path}")
        
        # Extract text content
        try:
            text_content = doc_processor.extract_text(str(file_path))
        except Exception as e:
            print(f"❌ Text extraction failed: {e}")
            if file_path.exists():
                file_path.unlink()  # Delete file if extraction fails
            raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")
        
        if not text_content or len(text_content.strip()) == 0:
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=400, detail="No text content extracted from file")
        
        print(f"✅ Extracted {len(text_content)} characters")
        
        return {
            "document_id": doc_id,
            "filename": file.filename,
            "file_size": len(content),
            "text_length": len(text_content),
            "preview": text_content[:500] + "..." if len(text_content) > 500 else text_content
        }
    except asyncio.CancelledError:
        print("⚠️ Upload cancelled")
        if file_path and file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=499, detail="Upload cancelled")
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Upload error: {e}")
        if file_path and file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/documents")
async def list_documents():
    """List all uploaded documents"""
    documents = []
    for file_path in UPLOAD_DIR.glob("*"):
        if file_path.is_file() and file_path.name != ".gitkeep":
            doc_id = file_path.stem
            documents.append({
                "document_id": doc_id,
                "filename": file_path.name,
                "size": file_path.stat().st_size,
                "uploaded_at": file_path.stat().st_mtime
            })
    return {"documents": documents}


@app.get("/documents/{document_id}")
async def get_document(document_id: str):
    """Get document details and content"""
    file_paths = list(UPLOAD_DIR.glob(f"{document_id}.*"))
    
    if not file_paths:
        raise HTTPException(status_code=404, detail="Document not found")
    
    file_path = file_paths[0]
    text_content = doc_processor.extract_text(str(file_path))
    
    return {
        "document_id": document_id,
        "filename": file_path.name,
        "content": text_content,
        "length": len(text_content)
    }


@app.post("/chunk", response_model=ChunkResponse)
async def chunk_document(request: ChunkRequest):
    """Chunk document using specified strategy"""
    try:
        # Get document
        file_paths = list(UPLOAD_DIR.glob(f"{request.document_id}.*"))
        if not file_paths:
            raise HTTPException(status_code=404, detail="Document not found")
        
        file_path = file_paths[0]
        text_content = doc_processor.extract_text(str(file_path))
        
        # Get chunking strategy
        if request.strategy not in chunking_strategies:
            raise HTTPException(status_code=400, detail=f"Invalid strategy: {request.strategy}")
        
        strategy = chunking_strategies[request.strategy]
        
        # Chunk document with timing
        start_time = time.time()
        chunks = strategy.chunk(
            text_content, 
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap
        )
        latency = (time.time() - start_time) * 1000  # Convert to ms
        
        # Store chunks in Qdrant
        collection_name = f"{request.document_id}_{request.strategy}"
        
        # Create collection
        collection_result = qdrant_manager.create_collection(collection_name)
        if collection_result.get("status") == "error":
            raise HTTPException(status_code=500, detail=f"Failed to create collection: {collection_result.get('error')}")
        
        # Add chunks to collection
        add_result = qdrant_manager.add_chunks(collection_name, chunks, request.document_id)
        if add_result.get("status") == "error":
            raise HTTPException(status_code=500, detail=f"Failed to add chunks: {add_result.get('error')}")
        
        print(f"✓ Stored {add_result.get('chunks_added', 0)} chunks in collection: {collection_name}")
        
        # Format chunks for response
        formatted_chunks = [
            {
                "id": i,
                "text": chunk["text"],
                "metadata": chunk.get("metadata", {}),
                "char_count": len(chunk["text"]),
                "word_count": len(chunk["text"].split()),
                "chunk_index": i
            }
            for i, chunk in enumerate(chunks)
        ]
        
        # Track metrics
        metrics_tracker.record_chunking(request.strategy, latency, len(chunks))
        
        return ChunkResponse(
            document_id=request.document_id,
            strategy=request.strategy,
            chunks=formatted_chunks,
            latency_ms=round(latency, 2),
            total_chunks=len(chunks)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chunking failed: {str(e)}")


@app.post("/retrieve", response_model=RetrievalResponse)
async def retrieve_documents(request: RetrievalRequest):
    """Retrieve documents using specified strategy"""
    try:
        # Get retrieval strategy
        if request.strategy not in retrieval_strategies:
            raise HTTPException(status_code=400, detail=f"Invalid strategy: {request.strategy}")
        
        strategy = retrieval_strategies[request.strategy]
        
        # Determine collection name
        if request.document_id:
            # Get all collections for this document
            collections = qdrant_manager.list_collections()
            doc_collections = [c for c in collections if c.startswith(request.document_id)]
            if not doc_collections:
                raise HTTPException(status_code=404, detail="No chunks found for document")
            collection_name = doc_collections[0]  # Use first available
        else:
            # Use all collections
            collection_name = None
        
        # Retrieve with timing
        start_time = time.time()
        results = strategy.retrieve(
            query=request.query,
            collection_name=collection_name,
            top_k=request.top_k
        )
        latency = (time.time() - start_time) * 1000  # Convert to ms
        
        # Track metrics
        metrics_tracker.record_retrieval(request.strategy, latency, len(results))
        
        return RetrievalResponse(
            query=request.query,
            strategy=request.strategy,
            results=results,
            latency_ms=round(latency, 2),
            total_results=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")


@app.get("/metrics")
async def get_metrics():
    """Get performance metrics"""
    return metrics_tracker.get_summary()


@app.get("/metrics/recent")
async def get_recent_metrics(limit: int = 10):
    """Get recent operations with latency details"""
    recent = metrics_tracker.get_recent_operations(limit)
    return {
        "recent_operations": recent,
        "count": len(recent)
    }


@app.get("/metrics/compare")
async def compare_strategies():
    """Compare latency across different strategies"""
    summary = metrics_tracker.get_summary()
    
    comparison = {
        "chunking_comparison": [],
        "retrieval_comparison": []
    }
    
    # Compare chunking strategies
    for strategy, stats in summary.get("chunking", {}).items():
        comparison["chunking_comparison"].append({
            "strategy": strategy,
            "avg_latency_ms": round(stats["avg_latency_ms"], 2),
            "min_latency_ms": round(stats["min_latency_ms"], 2),
            "max_latency_ms": round(stats["max_latency_ms"], 2),
            "operations_count": stats["count"],
            "avg_chunks_created": round(stats["avg_chunks"], 1)
        })
    
    # Compare retrieval strategies
    for strategy, stats in summary.get("retrieval", {}).items():
        comparison["retrieval_comparison"].append({
            "strategy": strategy,
            "avg_latency_ms": round(stats["avg_latency_ms"], 2),
            "min_latency_ms": round(stats["min_latency_ms"], 2),
            "max_latency_ms": round(stats["max_latency_ms"], 2),
            "operations_count": stats["count"],
            "avg_results_returned": round(stats["avg_results"], 1)
        })
    
    # Sort by average latency
    comparison["chunking_comparison"].sort(key=lambda x: x["avg_latency_ms"])
    comparison["retrieval_comparison"].sort(key=lambda x: x["avg_latency_ms"])
    
    return comparison


@app.post("/metrics/reset")
async def reset_metrics():
    """Reset all metrics"""
    metrics_tracker.reset()
    return {"status": "success", "message": "Metrics reset successfully"}


@app.get("/strategies")
async def get_strategies():
    """Get available chunking and retrieval strategies"""
    return {
        "chunking": list(chunking_strategies.keys()),
        "retrieval": list(retrieval_strategies.keys())
    }


@app.get("/collections")
async def list_collections():
    """List all Qdrant collections"""
    try:
        collections = qdrant_manager.list_collections()
        collection_info = []
        
        for col_name in collections:
            # Get collection details
            points = qdrant_manager.get_all_points(col_name)
            collection_info.append({
                "name": col_name,
                "chunks_count": len(points)
            })
        
        return {"collections": collection_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list collections: {str(e)}")


@app.get("/collections/{collection_name}/chunks")
async def get_collection_chunks(collection_name: str):
    """Get all chunks from a specific collection"""
    try:
        points = qdrant_manager.get_all_points(collection_name)
        return {
            "collection": collection_name,
            "total_chunks": len(points),
            "chunks": points
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chunks: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        timeout_keep_alive=300,  # 5 minutes
        timeout_notify=300,  # 5 minutes
        limit_max_requests=10000,
        limit_concurrency=100
    )
