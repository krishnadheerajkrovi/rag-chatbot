# Quick Start Guide

Get your RAG chatbot running in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- 8GB+ RAM available
- 10GB free disk space

## Step-by-Step Setup

### 1. Clone and Configure (1 minute)

```bash
# Clone the repository
git clone <your-repo-url>
cd windsurf-project

# Copy environment file
cp .env.example .env

# Optional: Edit .env to customize settings
nano .env
```

### 2. Start All Services (2 minutes)

```bash
# Build and start all containers
docker-compose up --build -d

# Check if all services are running
docker-compose ps
```

You should see 4 services running:
- `rag_chatbot_db` (PostgreSQL)
- `rag_chatbot_ollama` (Ollama LLM)
- `rag_chatbot_backend` (FastAPI)
- `rag_chatbot_frontend` (Streamlit)

### 3. Pull LLM Model (2 minutes)

```bash
# Pull the default llama2 model
docker exec -it rag_chatbot_ollama ollama pull llama2

# Verify model is downloaded
docker exec -it rag_chatbot_ollama ollama list
```

**Alternative models:**
```bash
# Faster, smaller model
docker exec -it rag_chatbot_ollama ollama pull phi

# Better reasoning
docker exec -it rag_chatbot_ollama ollama pull mistral

# For code-related queries
docker exec -it rag_chatbot_ollama ollama pull codellama
```

### 4. Access the Application

Open your browser and navigate to:

**Frontend**: http://localhost:8501

**API Documentation**: http://localhost:8000/docs

### 5. First Use

1. **Register a new account**
   - Click the "Register" tab
   - Enter username, email, and password
   - Click "Register"

2. **Login**
   - Switch to "Login" tab
   - Enter your credentials
   - Click "Login"

3. **Upload a document**
   - Use the sidebar file uploader
   - Select a PDF, TXT, MD, or DOCX file
   - Add a title (optional)
   - Click "Upload & Process"
   - Wait for processing to complete

4. **Start chatting**
   - Type your question in the chat input
   - Press Enter or click Send
   - Get AI-powered answers based on your documents!

## Verify Installation

### Check Service Health

```bash
# Check all services
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:8501/_stcore/health

# Check Ollama
curl http://localhost:11434/api/tags
```

### View Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs ollama

# Follow logs in real-time
docker-compose logs -f backend
```

## Common Issues

### Services won't start

```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart

# Rebuild from scratch
docker-compose down -v
docker-compose up --build
```

### Ollama model not found

```bash
# List available models
docker exec -it rag_chatbot_ollama ollama list

# Pull the model again
docker exec -it rag_chatbot_ollama ollama pull llama2
```

### Port already in use

```bash
# Check what's using the port
lsof -i :8000  # Backend
lsof -i :8501  # Frontend
lsof -i :5432  # Database
lsof -i :11434 # Ollama

# Kill the process or change ports in docker-compose.yml
```

### Out of memory

```bash
# Use a smaller model
docker exec -it rag_chatbot_ollama ollama pull phi

# Update .env to use the smaller model
DEFAULT_MODEL=phi

# Restart backend
docker-compose restart backend
```

## Next Steps

### Customize Your Setup

1. **Change the LLM model**
   - Edit `.env`: `DEFAULT_MODEL=mistral`
   - Restart backend: `docker-compose restart backend`

2. **Add more users**
   - Register through the UI
   - Or use the API: see `docs/API_GUIDE.md`

3. **Upload multiple documents**
   - Each user can upload multiple documents
   - Documents are processed and indexed automatically

4. **Explore the API**
   - Visit http://localhost:8000/docs
   - Try the interactive API documentation

### Learn More

- **[Full Setup Guide](docs/SETUP.md)**: Detailed installation instructions
- **[API Guide](docs/API_GUIDE.md)**: Complete API reference
- **[Component Docs](docs/components/)**: Deep dive into each technology

### Production Deployment

For production use:

1. **Update security settings**
   ```bash
   # Generate a strong secret key
   openssl rand -hex 32
   
   # Update .env
   SECRET_KEY=<your-generated-key>
   ```

2. **Use a production database**
   - Set up managed PostgreSQL
   - Update `DATABASE_URL` in `.env`

3. **Enable HTTPS**
   - Set up a reverse proxy (Nginx/Traefik)
   - Get SSL certificates (Let's Encrypt)

4. **Set up monitoring**
   - Add logging
   - Set up health checks
   - Monitor resource usage

## Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove all data (WARNING: deletes everything)
docker-compose down -v
```

## Getting Help

- **Documentation**: Check `docs/` folder
- **Logs**: `docker-compose logs <service-name>`
- **Issues**: Open an issue on GitHub
- **API Docs**: http://localhost:8000/docs

## Success Checklist

- [ ] All 4 services are running (`docker-compose ps`)
- [ ] Ollama model is downloaded (`ollama list`)
- [ ] Can access frontend at http://localhost:8501
- [ ] Can access API docs at http://localhost:8000/docs
- [ ] Successfully registered and logged in
- [ ] Uploaded and processed a document
- [ ] Received an answer to a query

**Congratulations! Your RAG chatbot is ready to use! 🎉**
