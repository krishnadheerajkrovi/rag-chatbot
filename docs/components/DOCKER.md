# Docker & Docker Compose

## Overview

Docker containerizes our application components, ensuring consistent environments across development and production. Docker Compose orchestrates multiple containers.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              Docker Compose Network                 │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │  Frontend    │  │   Backend    │  │  Ollama  │ │
│  │  Streamlit   │◄─┤   FastAPI    │◄─┤   LLM    │ │
│  │  Port: 8501  │  │  Port: 8000  │  │  Port:   │ │
│  └──────────────┘  └──────┬───────┘  │  11434   │ │
│                            │          └──────────┘ │
│                            ▼                        │
│                    ┌──────────────┐                │
│                    │  PostgreSQL  │                │
│                    │  Port: 5432  │                │
│                    └──────────────┘                │
│                                                     │
│  Volumes:                                          │
│  • postgres_data                                   │
│  • ollama_data                                     │
│  • backend_uploads                                 │
│  • vector_store                                    │
└─────────────────────────────────────────────────────┘
```

## Docker Compose Configuration

### Complete docker-compose.yml

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: rag_chatbot_db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: rag_chatbot
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - rag_network

  # Ollama Service
  ollama:
    image: ollama/ollama:latest
    container_name: rag_chatbot_ollama
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    environment:
      - OLLAMA_HOST=0.0.0.0
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - rag_network

  # FastAPI Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: rag_chatbot_backend
    depends_on:
      db:
        condition: service_healthy
      ollama:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/rag_chatbot
      - OLLAMA_BASE_URL=http://ollama:11434
      - DEFAULT_MODEL=llama2
      - SECRET_KEY=${SECRET_KEY:-your-secret-key-change-this}
      - VECTOR_STORE_PATH=/app/vector_store
    volumes:
      - ./backend/app:/app/app
      - backend_uploads:/app/uploads
      - vector_store:/app/vector_store
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - rag_network

  # Streamlit Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: rag_chatbot_frontend
    depends_on:
      - backend
    environment:
      - API_BASE_URL=http://backend:8000
    volumes:
      - ./frontend/app:/app/app
    ports:
      - "8501:8501"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - rag_network

networks:
  rag_network:
    driver: bridge

volumes:
  postgres_data:
  ollama_data:
  backend_uploads:
  vector_store:
```

## Individual Dockerfiles

### Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app

# Create necessary directories
RUN mkdir -p /app/uploads /app/vector_store

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app

# Expose port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## Docker Commands

### Build and Start

```bash
# Build and start all services
docker-compose up --build

# Start in detached mode
docker-compose up -d

# Build specific service
docker-compose build backend

# Start specific service
docker-compose up backend
```

### Stop and Remove

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v

# Stop specific service
docker-compose stop backend
```

### View Logs

```bash
# View all logs
docker-compose logs

# Follow logs
docker-compose logs -f

# View specific service logs
docker-compose logs backend

# View last 100 lines
docker-compose logs --tail=100
```

### Execute Commands

```bash
# Execute command in running container
docker-compose exec backend bash

# Run one-off command
docker-compose run backend python -c "print('Hello')"

# Pull Ollama model
docker exec -it rag_chatbot_ollama ollama pull llama2
```

### Inspect Services

```bash
# List running services
docker-compose ps

# View service details
docker-compose ps backend

# View resource usage
docker stats
```

## Volume Management

### List Volumes

```bash
# List all volumes
docker volume ls

# Inspect volume
docker volume inspect windsurf-project_postgres_data
```

### Backup Volumes

```bash
# Backup PostgreSQL data
docker run --rm \
  -v windsurf-project_postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz /data

# Backup vector store
docker run --rm \
  -v windsurf-project_vector_store:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/vector_store_backup.tar.gz /data
```

### Restore Volumes

```bash
# Restore PostgreSQL data
docker run --rm \
  -v windsurf-project_postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/postgres_backup.tar.gz -C /
```

## Networking

### Network Commands

```bash
# List networks
docker network ls

# Inspect network
docker network inspect windsurf-project_rag_network

# Connect container to network
docker network connect rag_network my_container
```

### Service Communication

Services communicate using service names:
- Backend → Database: `postgresql://postgres:postgres@db:5432/rag_chatbot`
- Backend → Ollama: `http://ollama:11434`
- Frontend → Backend: `http://backend:8000`

## Health Checks

### Database Health Check

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 10s
  timeout: 5s
  retries: 5
```

### Backend Health Check

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Ollama Health Check

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## Environment Variables

### .env File

```bash
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=rag_chatbot

# Security
SECRET_KEY=your-secret-key-here

# Ollama
DEFAULT_MODEL=llama2

# API
API_BASE_URL=http://localhost:8000
```

### Using in docker-compose.yml

```yaml
services:
  backend:
    environment:
      - SECRET_KEY=${SECRET_KEY:-default-secret}
      - DATABASE_URL=${DATABASE_URL}
    env_file:
      - .env
```

## Production Optimization

### Multi-Stage Builds

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY ./app ./app

ENV PATH=/root/.local/bin:$PATH

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Resource Limits

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### GPU Support (Ollama)

```yaml
ollama:
  image: ollama/ollama:latest
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs backend

# Check if port is in use
lsof -i :8000

# Rebuild without cache
docker-compose build --no-cache backend
```

### Database Connection Issues

```bash
# Check if database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Connect to database
docker-compose exec db psql -U postgres -d rag_chatbot
```

### Volume Permission Issues

```bash
# Fix permissions
docker-compose exec backend chown -R $(id -u):$(id -g) /app/uploads
```

### Network Issues

```bash
# Recreate network
docker-compose down
docker network prune
docker-compose up
```

## Best Practices

### 1. Use .dockerignore

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.git
.gitignore
*.md
.env
.vscode
.idea
```

### 2. Layer Caching

```dockerfile
# Copy requirements first (changes less frequently)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy code last (changes more frequently)
COPY ./app ./app
```

### 3. Security

```yaml
# Don't expose unnecessary ports
# Use secrets for sensitive data
# Run as non-root user

services:
  backend:
    user: "1000:1000"
    secrets:
      - db_password
```

### 4. Logging

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
