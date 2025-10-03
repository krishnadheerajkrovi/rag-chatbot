# Setup Guide

This guide will help you set up and run the Multi-User RAG Chatbot application.

## Prerequisites

- Docker and Docker Compose installed
- At least 8GB of RAM available
- 10GB of free disk space

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd windsurf-project
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

3. **Start all services**
   ```bash
   docker-compose up --build
   ```

4. **Pull Ollama model** (first time only)
   ```bash
   docker exec -it rag_chatbot_ollama ollama pull llama2
   ```

5. **Access the application**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Service Details

### PostgreSQL Database (Port 5432)
- Stores user accounts, chat history, and document metadata
- Data persisted in Docker volume `postgres_data`

### Ollama Service (Port 11434)
- Local LLM inference server
- Models stored in Docker volume `ollama_data`
- Default model: llama2

### FastAPI Backend (Port 8000)
- RESTful API for authentication and chat
- Handles document processing and RAG pipeline
- Vector store persisted in Docker volume `vector_store`

### Streamlit Frontend (Port 8501)
- User-friendly web interface
- Document upload and management
- Real-time chat interface

## First-Time Setup

### 1. Pull Additional Ollama Models (Optional)

```bash
# For better performance, you can use other models
docker exec -it rag_chatbot_ollama ollama pull mistral
docker exec -it rag_chatbot_ollama ollama pull codellama

# Update DEFAULT_MODEL in .env to use a different model
```

### 2. Create Admin User

Register through the frontend at http://localhost:8501 or use the API:

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "password": "secure_password"
  }'
```

## Troubleshooting

### Services not starting

```bash
# Check service logs
docker-compose logs backend
docker-compose logs ollama
docker-compose logs db

# Restart services
docker-compose restart
```

### Ollama model not found

```bash
# List available models
docker exec -it rag_chatbot_ollama ollama list

# Pull the required model
docker exec -it rag_chatbot_ollama ollama pull llama2
```

### Database connection issues

```bash
# Reset database
docker-compose down -v
docker-compose up --build
```

### Out of memory errors

- Increase Docker memory limit to at least 8GB
- Use a smaller Ollama model (e.g., `phi` instead of `llama2`)

## Development Mode

For development with hot-reload:

```bash
# Backend only
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend only
cd frontend
pip install -r requirements.txt
streamlit run app/main.py
```

## Production Deployment

1. **Update security settings**
   - Change `SECRET_KEY` in .env
   - Use strong passwords
   - Configure CORS properly

2. **Use production database**
   - Replace SQLite with PostgreSQL
   - Set up database backups

3. **Set up reverse proxy**
   - Use Nginx or Traefik
   - Enable HTTPS with SSL certificates

4. **Monitor resources**
   - Set up logging and monitoring
   - Configure resource limits in docker-compose.yml

## Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v
```
