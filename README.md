# RAG Strategies Testing Platform

> **Complete implementation of a RAG testing platform with multiple chunking and retrieval strategies**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB?style=flat&logo=react)](https://reactjs.org/)
[![Qdrant](https://img.shields.io/badge/Qdrant-latest-DC244C?style=flat)](https://qdrant.tech/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python)](https://www.python.org/)

---

## ✨ What's Included

This is a **production-ready RAG testing platform** with:

### 🎨 Frontend (React)
- 📤 Document upload with drag-and-drop
- 📊 Two dedicated pages: Chunking & Retrieval
- 📦 Real-time chunk visualization
- ⚡ Live latency metrics and performance indicators
- 🎯 Interactive query interface

### ⚙️ Backend (FastAPI)
- 🏗️ Abstract base classes for extensibility
- 📝 **3 Chunking Strategies**:
  - Semantic (similarity-based)
  - Agentic Proposition (LLM-extracted facts)
  - Hybrid (structural + character)
- 🔍 **3 Retrieval Strategies**:
  - Hybrid Search (dense + sparse)
  - Cross-Encoder Reranking
  - Reciprocal Rank Fusion (RRF)
- 💾 Full Qdrant integration
- 📈 Performance tracking

### 🐳 Infrastructure
- Docker Compose with 3 containers
- Qdrant vector database
- Volume persistence
- Health checks

---

## 🚀 Quick Start (2 Minutes)

### Prerequisites
- Docker & Docker Compose
- OpenAI API Key

### Steps

1. **Set up environment**:
   ```bash
   copy .env.example .env
   # Edit .env and add: OPENAI_API_KEY=your_key_here
   ```

2. **Start everything**:
   ```bash
   docker-compose up --build
   ```
   
   OR use the quick start script:
   ```bash
   start.bat
   ```

3. **Access the application**:
   - **Frontend**: http://localhost:3000
   - **API Docs**: http://localhost:8000/docs
   - **Qdrant**: http://localhost:6333/dashboard

That's it! 🎉

---

## 📖 Full Documentation

See **[SETUP_GUIDE.md](SETUP_GUIDE.md)** for:
- Detailed setup instructions
- Development setup (without Docker)
- Usage guide with examples
- API reference
- Troubleshooting
- Adding custom strategies
- Performance tips

---

## 🎯 How to Use

### 1️⃣ Test Chunking Strategies

1. Go to **Chunking Strategies** page
2. Upload a document (PDF, TXT, DOCX)
3. Select a strategy and adjust parameters
4. Generate chunks and view:
   - Individual chunks with metadata
   - Latency metrics
   - Chunk statistics

### 2️⃣ Test Retrieval Strategies

1. Go to **Retrieval Strategies** page
2. Enter your query
3. Select a retrieval strategy
4. View ranked results with:
   - Relevance scores
   - Retrieved chunks
   - Latency comparison

---

## 🏗️ Project Structure

```
Rag_strategies/
├── backend/              # FastAPI + Python
│   ├── chunking/        # 3 chunking strategies + base class
│   ├── retrieval/       # 3 retrieval strategies + base class
│   ├── database/        # Qdrant manager
│   ├── utils/           # Metrics, document processor
│   └── main.py          # FastAPI app
├── frontend/            # React app
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Chunking & Retrieval pages
│   │   └── api.js       # API client
│   └── public/
├── data/uploads/        # Document storage
├── docker-compose.yml   # Orchestration
└── start.bat            # Quick start script
```

---

## 🧩 Architecture Highlights

### Abstract Base Classes
Easy to extend with new strategies:

```python
# Chunking
class BaseChunker(ABC):
    @abstractmethod
    def chunk(self, text, chunk_size, chunk_overlap, **kwargs):
        pass

# Retrieval  
class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(self, query, collection_name, top_k, **kwargs):
        pass
```

### API Design
RESTful endpoints with full OpenAPI docs:
- `POST /upload` - Upload documents
- `POST /chunk` - Process with any strategy
- `POST /retrieve` - Query with any strategy
- `GET /metrics` - Performance analytics

---

## 🔧 Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | React + React Router |
| Backend | FastAPI (async) |
| Vector DB | Qdrant |
| Embeddings | OpenAI text-embedding-3-small |
| LLM | GPT-3.5-turbo (agentic strategy) |
| Reranking | Cross-Encoder models |
| Containerization | Docker Compose |

---

## 📊 Strategies Explained

### Chunking

| Strategy | Best For | Speed |
|----------|----------|-------|
| **Semantic** | Articles, narratives | Medium |
| **Agentic** | Technical docs, facts | Slow (LLM) |
| **Hybrid** | General purpose | Fast |

### Retrieval

| Strategy | Best For | Accuracy | Speed |
|----------|----------|----------|-------|
| **Hybrid** | Balanced use | Good | Fast |
| **Cross-Encoder** | Maximum accuracy | Best | Slow |
| **RRF** | Robust fusion | Good | Medium |

---

## 🎨 UI Features

- ✅ Responsive design
- ✅ Real-time metrics with color indicators
- ✅ Document preview
- ✅ Expandable chunks
- ✅ Metadata display
- ✅ Loading states
- ✅ Error handling

---

## 🔒 Environment Variables

Required in `.env`:
```env
OPENAI_API_KEY=sk-...        # OpenAI API key (required)
QDRANT_HOST=qdrant           # Host (default: qdrant)
QDRANT_PORT=6333             # Port (default: 6333)
```

---

## 🛠️ Commands

```bash
# Start all services
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Clean everything (including volumes)
docker-compose down -v
```

---

## 🧪 Testing Example

1. Upload a research paper
2. Try all 3 chunking strategies with same settings
3. Compare:
   - Number of chunks
   - Processing latency
   - Chunk quality
4. Query: "What is the main conclusion?"
5. Try all 3 retrieval strategies
6. Compare results and latency

---

## 📈 Metrics Tracked

- ⏱️ Chunking latency (ms)
- ⏱️ Retrieval latency (ms)
- 📦 Number of chunks generated
- 🔍 Number of results retrieved
- 📊 Performance indicators (Excellent/Good/Fair/Slow)

---

## 🚧 Troubleshooting

**Services won't start?**
```bash
docker-compose down -v
docker-compose up --build
```

**OpenAI errors?**
- Check `.env` has valid `OPENAI_API_KEY`

**Frontend can't connect?**
- Verify backend is on port 8000: `curl http://localhost:8000/health`

**More issues?** See [SETUP_GUIDE.md](SETUP_GUIDE.md) troubleshooting section.

---

## 🎓 Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [LangChain](https://python.langchain.com/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)

---

## 🤝 Extending the Platform

Want to add a new strategy? It's easy:

1. Inherit from `BaseChunker` or `BaseRetriever`
2. Implement the abstract method
3. Register in `main.py`
4. That's it! UI automatically updates

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed examples.

---

## 📝 License

MIT License - Free to use and modify

---

## 🎉 You're All Set!

This is a **complete, production-ready** RAG testing platform. Everything is configured and ready to use.

**Next steps**:
1. Run `start.bat` or `docker-compose up --build`
2. Open http://localhost:3000
3. Upload a document and start testing!

**Questions?** Check [SETUP_GUIDE.md](SETUP_GUIDE.md) for comprehensive documentation.

---

Made with ❤️ for RAG developers
