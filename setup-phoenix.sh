#!/bin/bash

# Setup script for RAG Chatbot with local Ollama and LangSmith

set -e

echo "🚀 RAG Chatbot Setup with Local Ollama and Phoenix"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Ollama is running
echo "1️⃣  Checking Ollama..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ollama is running on localhost:11434${NC}"
    echo "   Available models:"
    ollama list | tail -n +2 | awk '{print "   - " $1}'
else
    echo -e "${RED}✗ Ollama is not running${NC}"
    echo "   Please start Ollama first:"
    echo "   - On Mac: Ollama should start automatically"
    echo "   - Or run: ollama serve"
    exit 1
fi

# Check if required model is available
echo ""
echo "2️⃣  Checking for llama3.1:8b model..."
if ollama list | grep -q "llama3.1:8b"; then
    echo -e "${GREEN}✓ llama3.1:8b model is available${NC}"
else
    echo -e "${YELLOW}⚠ llama3.1:8b model not found${NC}"
    echo "   Pulling llama3.1:8b model (this may take a few minutes)..."
    ollama pull llama3.1:8b
    echo -e "${GREEN}✓ llama3.1:8b model downloaded${NC}"
fi

# Start Arize Phoenix server
echo ""
echo "3️⃣  Starting Arize Phoenix server..."
if docker ps | grep -q "phoenix"; then
    echo -e "${YELLOW}⚠ Phoenix is already running${NC}"
else
    docker run -d \
        --name phoenix \
        -p 6006:6006 \
        -p 4317:4317 \
        arizephoenix/phoenix:latest
    
    echo "   Waiting for Phoenix to be ready..."
    sleep 5
    
    if curl -s http://localhost:6006 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Phoenix is running on localhost:6006${NC}"
    else
        echo -e "${YELLOW}⚠ Phoenix is starting... (may take a moment)${NC}"
    fi
fi

# Setup environment file
echo ""
echo "4️⃣  Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file from .env.example${NC}"
else
    echo -e "${YELLOW}⚠ .env file already exists${NC}"
fi

# Start the application
echo ""
echo "5️⃣  Starting application services..."
docker-compose up -d --build

echo ""
echo "   Waiting for services to be ready..."
sleep 10

# Check service health
echo ""
echo "6️⃣  Checking service health..."

# Check database
if docker-compose ps | grep -q "rag_chatbot_db.*Up"; then
    echo -e "${GREEN}✓ Database is running${NC}"
else
    echo -e "${RED}✗ Database failed to start${NC}"
fi

# Check backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is running on localhost:8000${NC}"
else
    echo -e "${YELLOW}⚠ Backend is starting... (check logs if it doesn't start)${NC}"
fi

# Check frontend
if curl -s http://localhost:8501/_stcore/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is running on localhost:8501${NC}"
else
    echo -e "${YELLOW}⚠ Frontend is starting... (check logs if it doesn't start)${NC}"
fi

# Test Ollama connection from backend
echo ""
echo "7️⃣  Testing Ollama connection from backend..."
sleep 2
if docker exec rag_chatbot_backend curl -s http://host.docker.internal:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend can connect to local Ollama${NC}"
else
    echo -e "${RED}✗ Backend cannot connect to local Ollama${NC}"
    echo "   Check if Ollama is running and accessible"
fi

# Test Phoenix connection from backend
echo ""
echo "8️⃣  Testing Phoenix connection from backend..."
if docker exec rag_chatbot_backend curl -s http://host.docker.internal:6006 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend can connect to Phoenix${NC}"
else
    echo -e "${YELLOW}⚠ Backend cannot connect to Phoenix${NC}"
fi

# Summary
echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "🌐 Access your application:"
echo "   Frontend:  http://localhost:8501"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo "   Phoenix:   http://localhost:6006"
echo ""
echo "📊 View traces in Phoenix:"
echo "   1. Open http://localhost:6006"
echo "   2. Upload a document and ask questions"
echo "   3. Watch traces appear in real-time!"
echo "   4. Click on traces to see detailed execution flow"
echo ""
echo "📝 View logs:"
echo "   docker-compose logs -f backend"
echo ""
echo "🛑 Stop everything:"
echo "   docker-compose down"
echo "   docker stop phoenix"
echo ""
