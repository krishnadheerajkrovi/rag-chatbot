# LangSmith Local Setup Guide

This guide explains how to set up LangSmith locally for tracing and debugging your RAG chatbot.

## What is LangSmith?

LangSmith is a platform for debugging, testing, and monitoring LLM applications. It provides:
- **Tracing**: See every step of your RAG pipeline
- **Debugging**: Identify bottlenecks and errors
- **Monitoring**: Track performance metrics
- **Testing**: Evaluate your prompts and chains

## Setup Options

### Option 1: Local LangSmith (Recommended for Development)

Run LangSmith locally without needing a cloud account.

#### 1. Start Local LangSmith Server

```bash
# Pull and run the local LangSmith container
docker run -d \
  --name langsmith-local \
  -p 1984:1984 \
  langchain/langsmith-local:latest

# Verify it's running
curl http://localhost:1984/health
```

#### 2. Configure Your Application

Your `.env` file is already configured:

```bash
# LangSmith Configuration (for local tracing)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=http://host.docker.internal:1984
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=rag-chatbot
```

#### 3. Access LangSmith UI

Open your browser and navigate to:
```
http://localhost:1984
```

You'll see the LangSmith dashboard where you can view all traces.

### Option 2: Cloud LangSmith (For Production)

Use LangChain's hosted LangSmith service.

#### 1. Sign Up

Visit [smith.langchain.com](https://smith.langchain.com) and create an account.

#### 2. Get API Key

1. Go to Settings → API Keys
2. Create a new API key
3. Copy the key

#### 3. Update Configuration

Update your `.env` file:

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your-api-key-here
LANGCHAIN_PROJECT=rag-chatbot
```

## Using Local Mac Ollama

The configuration has been updated to use your local Ollama installation instead of the dockerized version.

### Configuration Changes

**docker-compose.yml**:
- Ollama service is commented out
- Backend uses `host.docker.internal:11434` to access your Mac's Ollama
- Added `extra_hosts` for proper host resolution

**Backend Configuration**:
- `OLLAMA_BASE_URL=http://host.docker.internal:11434`
- This allows Docker containers to access services on your Mac

### Verify Local Ollama

```bash
# Check if Ollama is running on your Mac
curl http://localhost:11434/api/tags

# List available models
ollama list

# Pull a model if needed
ollama pull llama2
```

## Complete Setup Steps

### 1. Update Environment File

```bash
# Copy the example file
cp .env.example .env

# The file is already configured for local Ollama and LangSmith
# No changes needed unless you want to customize
```

### 2. Start LangSmith (Local)

```bash
# Start local LangSmith server
docker run -d \
  --name langsmith-local \
  -p 1984:1984 \
  langchain/langsmith-local:latest
```

### 3. Verify Ollama is Running

```bash
# Check Ollama status
ollama list

# If not running, start it
# On Mac, Ollama should start automatically
# Or run: ollama serve
```

### 4. Start Your Application

```bash
# Start the application (without Ollama container)
docker-compose up --build -d

# Check logs
docker-compose logs -f backend
```

### 5. Test the Setup

```bash
# Test Ollama connection from backend
docker exec rag_chatbot_backend curl http://host.docker.internal:11434/api/tags

# Test LangSmith connection
docker exec rag_chatbot_backend curl http://host.docker.internal:1984/health
```

## Viewing Traces

### Local LangSmith UI

1. Open http://localhost:1984
2. Navigate to your project: `rag-chatbot`
3. View traces in real-time

### What You'll See

Each trace shows:
- **Input**: User query and chat history
- **Steps**: 
  - Query contextualization
  - Vector search
  - Document retrieval
  - LLM generation
- **Output**: Final answer
- **Timing**: Duration of each step
- **Tokens**: Token usage per step

### Example Trace Structure

```
RAG Chain
├── Contextualize Query (200ms)
│   ├── Input: "What about its headquarters?"
│   ├── Chat History: [...]
│   └── Output: "What about Tesla's headquarters?"
├── Retrieve Documents (150ms)
│   ├── Query Embedding (50ms)
│   ├── Vector Search (80ms)
│   └── Retrieved: 4 documents
└── Generate Answer (1500ms)
    ├── Prompt Construction (10ms)
    ├── LLM Call (1480ms)
    └── Output: "Tesla's headquarters..."
```

## Debugging with LangSmith

### 1. Identify Slow Steps

Look for steps taking too long:
- **Embedding**: Should be < 100ms
- **Vector Search**: Should be < 200ms
- **LLM Generation**: Varies by model (500ms - 3s)

### 2. Check Retrieved Documents

Verify that relevant documents are being retrieved:
- Click on "Retrieve Documents" step
- View the actual document chunks
- Check relevance scores

### 3. Analyze Prompts

View the exact prompts sent to the LLM:
- Click on "Generate Answer" step
- See the full prompt with context
- Identify if context is relevant

### 4. Track Errors

If a chain fails:
- View the error message
- See which step failed
- Check input/output at each step

## Advanced Configuration

### Custom Project Names

Organize traces by feature:

```python
# In your code
os.environ["LANGCHAIN_PROJECT"] = "rag-chatbot-feature-x"
```

### Filtering Traces

In LangSmith UI:
- Filter by status (success/error)
- Filter by duration
- Search by input/output
- Group by model

### Exporting Data

Export traces for analysis:
- Click "Export" in LangSmith UI
- Download as JSON
- Analyze with custom scripts

## Troubleshooting

### LangSmith Not Receiving Traces

**Check connection:**
```bash
# From backend container
docker exec rag_chatbot_backend curl http://host.docker.internal:1984/health
```

**Check environment variables:**
```bash
docker exec rag_chatbot_backend env | grep LANGCHAIN
```

**Verify tracing is enabled:**
```python
# In your code
import os
print(os.environ.get("LANGCHAIN_TRACING_V2"))  # Should be "true"
```

### Ollama Connection Issues

**Test from backend:**
```bash
docker exec rag_chatbot_backend curl http://host.docker.internal:11434/api/tags
```

**Check Ollama on Mac:**
```bash
# On your Mac terminal
curl http://localhost:11434/api/tags
ollama list
```

**Restart Ollama:**
```bash
# On Mac
killall ollama
ollama serve
```

### host.docker.internal Not Resolving

**For Linux users**, add to docker-compose.yml:
```yaml
backend:
  extra_hosts:
    - "host.docker.internal:172.17.0.1"
```

**Or use host network mode:**
```yaml
backend:
  network_mode: "host"
```

## Performance Monitoring

### Key Metrics to Track

1. **End-to-End Latency**
   - Total time from query to answer
   - Target: < 3 seconds

2. **Retrieval Quality**
   - Relevance of retrieved documents
   - Number of documents needed

3. **LLM Performance**
   - Token usage
   - Generation time
   - Answer quality

4. **Error Rate**
   - Failed queries
   - Timeout errors
   - Model errors

### Setting Up Alerts

In LangSmith (cloud version):
- Set latency thresholds
- Configure error rate alerts
- Monitor token usage

## Best Practices

### 1. Use Descriptive Project Names

```bash
LANGCHAIN_PROJECT=rag-chatbot-${ENVIRONMENT}
```

### 2. Tag Important Traces

```python
from langsmith import trace

@trace(tags=["important", "production"])
def my_function():
    pass
```

### 3. Add Metadata

```python
from langchain.callbacks import LangChainTracer

tracer = LangChainTracer(
    project_name="rag-chatbot",
    metadata={"user_id": user_id, "session_id": session_id}
)
```

### 4. Regular Review

- Review traces daily
- Identify patterns in failures
- Optimize slow steps
- Improve prompts based on outputs

## Disabling Tracing

If you want to disable tracing:

```bash
# In .env
LANGCHAIN_TRACING_V2=false
```

Or temporarily:
```bash
# Restart without tracing
LANGCHAIN_TRACING_V2=false docker-compose up
```

## Resources

- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [LangChain Tracing Guide](https://python.langchain.com/docs/langsmith/walkthrough)
- [Debugging LLM Apps](https://blog.langchain.dev/debugging-llm-apps/)

## Quick Reference

### Start Everything

```bash
# 1. Start LangSmith
docker run -d --name langsmith-local -p 1984:1984 langchain/langsmith-local:latest

# 2. Verify Ollama is running on Mac
ollama list

# 3. Start application
docker-compose up -d

# 4. View traces
open http://localhost:1984
```

### Stop Everything

```bash
# Stop application
docker-compose down

# Stop LangSmith
docker stop langsmith-local
docker rm langsmith-local
```

### View Logs

```bash
# Application logs
docker-compose logs -f backend

# LangSmith logs
docker logs -f langsmith-local
```

---

**Note**: The application is now configured to use your local Mac Ollama installation. The dockerized Ollama service has been disabled in docker-compose.yml.
