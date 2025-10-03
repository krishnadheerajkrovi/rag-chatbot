# Local Setup with Mac Ollama and LangSmith

Quick guide for running the RAG chatbot with your local Mac Ollama and LangSmith tracing.

## 🎯 What Changed

✅ **Using your local Mac Ollama** (not dockerized)
✅ **LangSmith integration** for tracing and debugging
✅ **Simplified setup** - one script does everything

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Run the setup script
./setup-langsmith.sh
```

This script will:
1. ✅ Check if Ollama is running
2. ✅ Verify llama2 model is available
3. ✅ Start LangSmith local server
4. ✅ Create .env file
5. ✅ Start all services
6. ✅ Test connections

### Option 2: Manual Setup

#### 1. Verify Ollama is Running

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# List models
ollama list

# Pull llama2 if needed
ollama pull llama2
```

#### 2. Start LangSmith

```bash
docker run -d \
  --name langsmith-local \
  -p 1984:1984 \
  langchain/langsmith-local:latest
```

#### 3. Setup Environment

```bash
cp .env.example .env
# The file is already configured correctly
```

#### 4. Start Application

```bash
docker-compose up -d --build
```

## 🔍 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:8501 | User interface |
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Interactive API docs |
| **LangSmith** | http://localhost:1984 | Trace viewer |

## 📊 Using LangSmith

### View Traces

1. Open http://localhost:1984
2. Navigate to project: **rag-chatbot**
3. Use your chatbot (upload docs, ask questions)
4. Watch traces appear in real-time!

### What You'll See

Each query shows:
- **Query Contextualization**: How the question is reformulated
- **Document Retrieval**: Which documents were found
- **LLM Generation**: The actual prompt and response
- **Timing**: How long each step took
- **Tokens**: Token usage per step

### Example Trace

```
User Query: "What about its headquarters?"

Step 1: Contextualize (200ms)
  Input: "What about its headquarters?"
  History: ["What is Tesla?", "Tesla is..."]
  Output: "What about Tesla's headquarters?"

Step 2: Retrieve (150ms)
  Query: "What about Tesla's headquarters?"
  Retrieved: 4 documents
  - Doc 1: "Tesla headquarters in Austin..."
  - Doc 2: "The company moved from..."
  
Step 3: Generate (1500ms)
  Prompt: "Context: [4 docs]... Question: What about Tesla's headquarters?"
  Response: "Tesla's headquarters is located in Austin, Texas..."
```

## 🔧 Configuration Details

### Ollama Connection

**Before (Dockerized)**:
```yaml
OLLAMA_BASE_URL=http://ollama:11434
```

**Now (Local Mac)**:
```yaml
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

The backend container uses `host.docker.internal` to access services running on your Mac.

### LangSmith Configuration

```bash
# Enable tracing
LANGCHAIN_TRACING_V2=true

# Local LangSmith endpoint
LANGCHAIN_ENDPOINT=http://host.docker.internal:1984

# No API key needed for local
LANGCHAIN_API_KEY=

# Project name
LANGCHAIN_PROJECT=rag-chatbot
```

## 🧪 Testing the Setup

### Test Ollama

```bash
# From your Mac
curl http://localhost:11434/api/tags

# From backend container
docker exec rag_chatbot_backend curl http://host.docker.internal:11434/api/tags
```

### Test LangSmith

```bash
# From your Mac
curl http://localhost:1984/health

# From backend container
docker exec rag_chatbot_backend curl http://host.docker.internal:1984/health
```

### Test Full Flow

1. Open http://localhost:8501
2. Register/Login
3. Upload a document
4. Ask a question
5. Check http://localhost:1984 for traces

## 🐛 Troubleshooting

### Ollama Not Accessible

**Problem**: Backend can't connect to Ollama

**Solution**:
```bash
# Check Ollama is running
ollama list

# Test from backend
docker exec rag_chatbot_backend curl http://host.docker.internal:11434/api/tags

# If fails, restart Ollama
killall ollama
ollama serve
```

### LangSmith Not Showing Traces

**Problem**: No traces appearing in LangSmith

**Solution**:
```bash
# Check LangSmith is running
docker ps | grep langsmith

# Check environment variables
docker exec rag_chatbot_backend env | grep LANGCHAIN

# Restart backend
docker-compose restart backend
```

### host.docker.internal Not Working

**Problem**: Docker can't resolve host.docker.internal

**Solution** (Linux users):
```yaml
# In docker-compose.yml, change:
extra_hosts:
  - "host.docker.internal:172.17.0.1"
```

### Port Conflicts

**Problem**: Port already in use

**Solution**:
```bash
# Check what's using the port
lsof -i :1984  # LangSmith
lsof -i :11434 # Ollama
lsof -i :8000  # Backend
lsof -i :8501  # Frontend

# Kill the process or change port in docker-compose.yml
```

## 📝 Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# LangSmith
docker logs -f langsmith-local

# Last 100 lines
docker-compose logs --tail=100 backend
```

## 🛑 Stopping Everything

```bash
# Stop application
docker-compose down

# Stop LangSmith
docker stop langsmith-local
docker rm langsmith-local

# Or use the cleanup script
./cleanup.sh  # If you create one
```

## 🔄 Restarting Services

```bash
# Restart backend only
docker-compose restart backend

# Restart all
docker-compose restart

# Rebuild and restart
docker-compose up -d --build
```

## 📚 Additional Resources

- **[LangSmith Setup Guide](docs/LANGSMITH_SETUP.md)** - Detailed LangSmith documentation
- **[Setup Guide](docs/SETUP.md)** - Full setup instructions
- **[Architecture](docs/ARCHITECTURE.md)** - System architecture
- **[API Guide](docs/API_GUIDE.md)** - API reference

## 💡 Tips

### 1. Use Different Models

```bash
# Pull a different model
ollama pull mistral

# Update .env
DEFAULT_MODEL=mistral

# Restart backend
docker-compose restart backend
```

### 2. Disable Tracing

```bash
# In .env
LANGCHAIN_TRACING_V2=false

# Restart
docker-compose restart backend
```

### 3. Change Project Name

```bash
# In .env
LANGCHAIN_PROJECT=my-custom-project

# Restart
docker-compose restart backend
```

### 4. Monitor Performance

Watch LangSmith to identify:
- Slow steps (> 2 seconds)
- Failed queries
- Token usage patterns
- Retrieval quality

## ✅ Success Checklist

- [ ] Ollama running on Mac (`ollama list`)
- [ ] LangSmith container running (`docker ps | grep langsmith`)
- [ ] Application services running (`docker-compose ps`)
- [ ] Can access frontend (http://localhost:8501)
- [ ] Can access LangSmith (http://localhost:1984)
- [ ] Backend can connect to Ollama (test command above)
- [ ] Traces appearing in LangSmith after queries

## 🎉 You're All Set!

Your RAG chatbot is now running with:
- ✅ Local Mac Ollama (no Docker overhead)
- ✅ LangSmith tracing (debug everything)
- ✅ Full observability (see every step)

Start chatting and watch the magic happen in LangSmith! 🚀
