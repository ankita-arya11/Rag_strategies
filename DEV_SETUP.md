# 🛠️ Development Setup Guide

This guide helps you run the RAG platform in **development mode** for faster iteration.

---

## 🎯 Development Mode Overview

In development mode:
- ✅ **Only Qdrant runs in Docker** (no rebuilding needed)
- ✅ **Backend runs locally** with hot reload (instant changes)
- ✅ **Frontend runs locally** with hot reload (instant changes)
- ✅ All services still work together seamlessly

---

## 🚀 Quick Start (Development Mode)

### Option 1: Automated Setup (Recommended)

1. **Start Qdrant**:
   ```bash
   dev-start.bat
   ```

2. **In Terminal 1 - Start Backend**:
   ```bash
   cd backend
   run-backend.bat
   ```

3. **In Terminal 2 - Start Frontend**:
   ```bash
   cd frontend
   run-frontend.bat
   ```

### Option 2: Manual Setup

#### Step 1: Start Qdrant Only

```bash
docker-compose -f docker-compose.dev.yml up -d
```

#### Step 2: Setup and Run Backend

```bash
cd backend

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Linux/Mac

# Install dependencies (first time only)
pip install -r requirements.txt

# Run backend with hot reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Step 3: Setup and Run Frontend

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Run frontend with hot reload
npm start
```

---

## 🔌 Access Points

Once all services are running:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

---

## 💡 Development Workflow

### Making Backend Changes

1. Edit any Python file in `backend/`
2. **Save** → Backend automatically reloads ✨
3. Test immediately in browser

### Making Frontend Changes

1. Edit any React file in `frontend/src/`
2. **Save** → Frontend automatically reloads ✨
3. See changes instantly in browser

### Working with Qdrant

- Qdrant runs in Docker and persists data
- No need to restart when changing backend/frontend
- View collections: http://localhost:6333/dashboard

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Make sure you're in the backend directory
cd backend

# Check Python version (should be 3.11+)
python --version

# Recreate virtual environment
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend won't start

```bash
# Make sure you're in the frontend directory
cd frontend

# Clear cache and reinstall
rmdir /s /q node_modules
del package-lock.json
npm install
npm start
```

### Backend can't connect to Qdrant

```bash
# Check if Qdrant is running
docker ps

# Restart Qdrant
docker-compose -f docker-compose.dev.yml restart

# Check Qdrant logs
docker-compose -f docker-compose.dev.yml logs qdrant
```

### Frontend can't connect to Backend

1. Check backend is running on port 8000
2. Check `.env` has `REACT_APP_API_URL=http://localhost:8000`
3. Restart frontend

### "Module not found" errors

**Backend**:
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend**:
```bash
cd frontend
npm install
```

---

## 📁 Environment Variables

Create `.env` in the root directory:

```env
OPENAI_API_KEY=sk-your-key-here
QDRANT_HOST=localhost
QDRANT_PORT=6333
REACT_APP_API_URL=http://localhost:8000
```

---

## 🔄 Switching Between Modes

### Development Mode → Production Mode

```bash
# Stop development services
dev-stop.bat

# Start production (all in Docker)
docker-compose up --build
```

### Production Mode → Development Mode

```bash
# Stop production
docker-compose down

# Start development
dev-start.bat
cd backend && run-backend.bat  # Terminal 1
cd frontend && run-frontend.bat  # Terminal 2
```

---

## 🎨 IDE Setup

### VS Code Recommended Extensions

- Python (Microsoft)
- Pylance
- ESLint
- Prettier
- Docker

### VS Code Settings

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/Scripts/python.exe",
  "python.linting.enabled": true,
  "editor.formatOnSave": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/node_modules": true
  }
}
```

---

## 🧪 Testing Your Changes

### Test Backend Changes

1. Make a change in backend code
2. Save the file
3. Backend auto-reloads
4. Test via:
   - API Docs: http://localhost:8000/docs
   - Frontend UI
   - curl commands

### Test Frontend Changes

1. Make a change in React code
2. Save the file
3. Frontend auto-reloads
4. See changes in browser immediately

---

## 📊 Development vs Production

| Feature | Development | Production |
|---------|------------|------------|
| Backend | Local Python | Docker Container |
| Frontend | Local npm | Docker Container |
| Qdrant | Docker | Docker |
| Hot Reload | ✅ Yes | ❌ No |
| Build Time | ⚡ Instant | 🐢 2-3 minutes |
| Best For | Coding | Deployment |

---

## 🛑 Stopping Services

### Stop Everything

```bash
dev-stop.bat
# Then Ctrl+C in backend terminal
# Then Ctrl+C in frontend terminal
```

### Stop Individual Services

- **Qdrant**: `docker-compose -f docker-compose.dev.yml down`
- **Backend**: Press `Ctrl+C` in backend terminal
- **Frontend**: Press `Ctrl+C` in frontend terminal

---

## 📦 Adding New Dependencies

### Backend (Python)

```bash
cd backend
venv\Scripts\activate
pip install new-package
pip freeze > requirements.txt
```

### Frontend (JavaScript)

```bash
cd frontend
npm install new-package
# package.json automatically updated
```

---

## 🎯 Common Development Tasks

### Clear Qdrant Data

```bash
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
```

### View Backend Logs

Backend logs appear directly in your terminal (advantage of running locally!)

### View Qdrant Logs

```bash
docker-compose -f docker-compose.dev.yml logs -f qdrant
```

### Check System Health

```bash
# Backend health
curl http://localhost:8000/health

# Qdrant health
curl http://localhost:6333
```

---

## ✨ Benefits of Development Mode

1. **⚡ Faster iterations**: No Docker rebuilds
2. **🔍 Better debugging**: Direct access to logs and debuggers
3. **💾 Lower resource usage**: Only Qdrant in Docker
4. **🎯 Hot reload**: Instant feedback on changes
5. **🛠️ Easy testing**: Direct access to all services

---

## 🔗 Useful Commands

```bash
# Check what's running
docker ps                    # Qdrant container
netstat -ano | findstr 8000  # Backend port
netstat -ano | findstr 3000  # Frontend port

# View Qdrant collections
curl http://localhost:6333/collections

# Test backend endpoint
curl http://localhost:8000/strategies

# Install all deps quickly
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
```

---

**Happy Development! 🚀**
