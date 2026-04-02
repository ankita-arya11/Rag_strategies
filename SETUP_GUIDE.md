# RAG Strategies Testing Platform - Setup Guide

A comprehensive platform for testing and comparing different chunking and retrieval strategies for Retrieval-Augmented Generation (RAG) systems using Qdrant vector database.

---

## 🎯 Features

### Chunking Strategies
1. **Semantic Chunking**: Groups text based on semantic similarity between sentences using embeddings
2. **Agentic Proposition**: Uses LLM to extract atomic, self-contained propositions
3. **Hybrid Chunking**: Combines structural boundaries with character-based splitting

### Retrieval Strategies
1. **Hybrid Search**: Combines dense vector search with sparse BM25 search
2. **Cross-Encoder Reranking**: Vector search followed by cross-encoder reranking for accuracy
3. **Reciprocal Rank Fusion (RRF)**: Rank-based fusion of multiple retrieval methods

### UI Features
- 📤 Document upload with drag-and-drop
- 📄 Document viewer with full content display
- 📦 Chunk visualization with metadata
- 🔍 Interactive query interface
- ⚡ Real-time latency metrics
- 📊 Performance comparison

---

## 🏗️ Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   React     │─────▶│   FastAPI   │─────▶│   Qdrant    │
│  Frontend   │      │   Backend   │      │   Vector    │
│   (3000)    │      │   (8000)    │      │   DB (6333) │
└─────────────┘      └─────────────┘      └─────────────┘
```

---

## 📋 Prerequisites

- **Docker** and **Docker Compose** installed
- **OpenAI API Key** (for embeddings and LLM)
- At least 4GB RAM available
- Modern web browser

---

## 🚀 Quick Start

### 1. Clone and Navigate
```bash
cd Rag_strategies
```

### 2. Set Up Environment Variables
```bash
# Copy the example environment file
copy .env.example .env

# Edit .env and add your OpenAI API key
# Example: OPENAI_API_KEY=sk-...
```

### 3. Start All Services
```bash
docker-compose up --build
```

This will start three containers:
- **Qdrant** (Vector Database) on port 6333
- **Backend** (FastAPI) on port 8000
- **Frontend** (React) on port 3000

### 4. Access the Application

Once all services are running:

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

---

## 💻 Development Setup (Without Docker)

### Backend Setup

1. **Navigate to backend directory**:
```bash
cd backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set environment variables**:
```bash
# Create .env file in backend directory
echo OPENAI_API_KEY=your_key_here > .env
echo QDRANT_HOST=localhost >> .env
echo QDRANT_PORT=6333 >> .env
```

5. **Run backend**:
```bash
uvicorn main:app --reload
```

### Frontend Setup

1. **Navigate to frontend directory**:
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Set environment variables**:
```bash
# Create .env file in frontend directory
echo REACT_APP_API_URL=http://localhost:8000 > .env
```

4. **Start development server**:
```bash
npm start
```

### Run Qdrant Separately

```bash
docker run -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage qdrant/qdrant:latest
```

---

## 📖 Usage Guide

### Step 1: Upload a Document

1. Navigate to the **Chunking Strategies** page
2. Drag and drop a document (PDF, TXT, or DOCX) or click to upload
3. View the document content in the preview pane

### Step 2: Generate Chunks

1. Select a chunking strategy:
   - **Semantic**: Best for maintaining topic coherence
   - **Agentic Proposition**: Best for extracting discrete facts
   - **Hybrid**: Best for balanced, general-purpose chunking

2. Adjust parameters:
   - **Chunk Size**: 128-2048 characters
   - **Chunk Overlap**: 0-200 characters

3. Click **Generate Chunks**

4. View results:
   - Individual chunks with metadata
   - Latency metrics
   - Chunk statistics (count, size, etc.)

### Step 3: Query and Retrieve

1. Navigate to the **Retrieval Strategies** page

2. Enter your query in the text box

3. Select a retrieval strategy:
   - **Hybrid**: Balanced speed and accuracy
   - **Cross-Encoder**: Best accuracy, slower
   - **RRF**: Robust rank-based fusion

4. Adjust number of results (1-20)

5. Click **Retrieve**

6. View results:
   - Ranked results with relevance scores
   - Metadata and source information
   - Latency metrics

---

## 🔧 Configuration

### Backend Configuration

Edit `backend/main.py` for:
- API endpoints
- CORS settings
- Default parameters

### Chunking Strategy Parameters

Edit individual strategy files in `backend/chunking/`:
- `semantic_chunker.py`: Similarity threshold
- `agentic_proposition.py`: LLM model, prompt template
- `hybrid_chunker.py`: Separator priorities

### Retrieval Strategy Parameters

Edit individual strategy files in `backend/retrieval/`:
- `hybrid_retrieval.py`: Dense/sparse weights
- `cross_encoder.py`: Model selection, candidate count
- `rrf_retrieval.py`: RRF constant (k value)

---

## 📊 API Endpoints

### Documents
- `POST /upload` - Upload a document
- `GET /documents` - List all documents
- `GET /documents/{id}` - Get document by ID

### Chunking
- `POST /chunk` - Chunk a document
- `GET /strategies` - List available strategies

### Retrieval
- `POST /retrieve` - Retrieve relevant chunks
- `GET /metrics` - Get performance metrics

### Health
- `GET /health` - Check system health

Full API documentation: http://localhost:8000/docs

---

## 🧪 Testing Different Strategies

### Recommended Testing Workflow

1. **Upload the same document**
2. **Test all chunking strategies** with same parameters
3. **Compare metrics**:
   - Number of chunks generated
   - Latency (processing time)
   - Chunk quality (manual inspection)

4. **Test retrieval strategies** with same query
5. **Compare results**:
   - Relevance of retrieved chunks
   - Retrieval latency
   - Score distributions

### Sample Questions to Test

- **Factual**: "What is the main topic of this document?"
- **Specific**: "What are the key statistics mentioned?"
- **Comparative**: "How does X compare to Y?"
- **Abstract**: "What is the overall conclusion?"

---

## 🐛 Troubleshooting

### Common Issues

**1. Docker containers won't start**
```bash
# Check if ports are already in use
netstat -ano | findstr "3000 6333 8000"

# Stop and remove existing containers
docker-compose down -v
docker-compose up --build
```

**2. OpenAI API errors**
```bash
# Verify API key is set
echo %OPENAI_API_KEY%

# Update .env file with valid key
```

**3. Frontend can't connect to backend**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Verify REACT_APP_API_URL in frontend/.env
```

**4. Qdrant connection errors**
```bash
# Check Qdrant is running
curl http://localhost:6333

# Restart Qdrant container
docker restart rag_qdrant
```

**5. Package installation errors**
```bash
# Update pip
pip install --upgrade pip

# Install with no cache
pip install --no-cache-dir -r requirements.txt
```

---

## 📦 Project Structure

```
Rag_strategies/
├── backend/
│   ├── chunking/               # Chunking strategy implementations
│   │   ├── __init__.py        # Base abstract class
│   │   ├── semantic_chunker.py
│   │   ├── agentic_proposition.py
│   │   └── hybrid_chunker.py
│   ├── retrieval/             # Retrieval strategy implementations
│   │   ├── __init__.py        # Base abstract class
│   │   ├── hybrid_retrieval.py
│   │   ├── cross_encoder.py
│   │   └── rrf_retrieval.py
│   ├── database/              # Qdrant integration
│   │   └── qdrant_manager.py
│   ├── utils/                 # Utilities
│   │   ├── metrics.py
│   │   └── document_processor.py
│   ├── main.py                # FastAPI application
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   │   ├── DocumentUploader.js
│   │   │   ├── DocumentViewer.js
│   │   │   ├── ChunkViewer.js
│   │   │   └── MetricsDisplay.js
│   │   ├── pages/            # Main pages
│   │   │   ├── ChunkingStrategies.js
│   │   │   └── RetrievalStrategies.js
│   │   ├── App.js
│   │   ├── api.js            # API client
│   │   └── index.js
│   ├── Dockerfile
│   └── package.json
├── data/uploads/              # Uploaded documents
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 🔒 Security Notes

- Never commit `.env` files with real API keys
- Use environment variables for sensitive data
- Implement authentication for production use
- Limit file upload sizes (currently 10MB)
- Validate and sanitize all user inputs

---

## 🚀 Adding New Strategies

### Adding a New Chunking Strategy

1. Create new file in `backend/chunking/`:
```python
from chunking import BaseChunker

class MyChunker(BaseChunker):
    def chunk(self, text, chunk_size=512, chunk_overlap=50, **kwargs):
        # Your implementation
        return chunks
```

2. Register in `backend/main.py`:
```python
chunking_strategies = {
    "my_strategy": MyChunker(),
    # ... existing strategies
}
```

### Adding a New Retrieval Strategy

1. Create new file in `backend/retrieval/`:
```python
from retrieval import BaseRetriever

class MyRetriever(BaseRetriever):
    def retrieve(self, query, collection_name=None, top_k=5, **kwargs):
        # Your implementation
        return results
```

2. Register in `backend/main.py`:
```python
retrieval_strategies = {
    "my_strategy": MyRetriever(qdrant_manager),
    # ... existing strategies
}
```

---

## 📈 Performance Tips

1. **Use appropriate chunk sizes**: 
   - Larger chunks (1024+) for semantic coherence
   - Smaller chunks (256-512) for precise retrieval

2. **Adjust overlap strategically**:
   - More overlap for better context preservation
   - Less overlap for faster processing

3. **Choose strategy based on content**:
   - Semantic: Narrative, articles, stories
   - Agentic: Technical docs, specifications
   - Hybrid: General purpose, mixed content

4. **Optimize retrieval**:
   - Hybrid: Fast, good for most cases
   - Cross-Encoder: Best quality, slower
   - RRF: Robust, balanced

---

## 🤝 Contributing

To extend this project:

1. Follow the abstract base class pattern
2. Add comprehensive docstrings
3. Include error handling
4. Update this README
5. Add tests (if applicable)

---

## 📝 License

MIT License - feel free to use and modify for your projects.

---

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check Docker logs: `docker-compose logs`

---

## 🎓 Learning Resources

- **Qdrant Documentation**: https://qdrant.tech/documentation/
- **LangChain**: https://python.langchain.com/
- **OpenAI Embeddings**: https://platform.openai.com/docs/guides/embeddings
- **RAG Systems**: Research papers on retrieval-augmented generation

---

**Happy Testing! 🚀**
