#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "Starting Backend Server"
echo "========================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python -m venv venv
fi

# Activate virtual environment
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
    touch venv/.installed
fi

# Check if .env exists in parent directory
if [ ! -f "../.env" ]; then
    echo -e "${YELLOW}Warning: .env file not found in parent directory${NC}"
    echo "Make sure OPENAI_API_KEY is set"
fi

# Start the server
echo -e "${GREEN}Starting FastAPI server on http://localhost:8000${NC}"
echo "API Docs: http://localhost:8000/docs"
echo ""
uvicorn main:app --reload --host 0.0.0.0 --port 8000
