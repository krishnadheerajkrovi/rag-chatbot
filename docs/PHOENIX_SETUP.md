# Arize Phoenix Setup Guide

Complete guide for using Arize Phoenix for tracing and debugging your RAG chatbot.

## What is Arize Phoenix?

Phoenix is an **open-source observability platform** for LLM applications:
- ✅ **100% Open Source** - No vendor lock-in
- ✅ **Local-first** - Run entirely on your machine
- ✅ **LangChain Native** - Built-in instrumentation
- ✅ **Beautiful UI** - Clean, intuitive interface
- ✅ **No Authentication** - Simple for development

## Quick Start

### Automated Setup (Recommended)

```bash
./setup-phoenix.sh
```

This will:
1. Check Ollama is running
2. Verify llama3.1:8b model
3. Start Phoenix server
4. Start all application services
5. Test connections

### Manual Setup

#### 1. Start Phoenix

```bash
docker run -d \
  --name phoenix \
  -p 6006:6006 \
  -p 4317:4317 \
  arizephoenix/phoenix:latest
```

**Ports:**
- `6006`: Web UI
- `4317`: OTLP collector (for traces)

#### 2. Verify Phoenix is Running

```bash
# Check container
docker ps | grep phoenix

# Access UI
open http://localhost:6006
```

#### 3. Start Your Application

```bash
docker-compose up -d --build
```

## Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Phoenix UI** | http://localhost:6006 | View traces and analytics |
| **Frontend** | http://localhost:8501 | User interface |
| **Backend** | http://localhost:8000 | API |
| **API Docs** | http://localhost:8000/docs | Interactive docs |

## Using Phoenix

### View Traces

1. Open http://localhost:6006
2. Use your chatbot (upload docs, ask questions)
3. Traces appear automatically in Phoenix

### Trace Details

Each trace shows:

**📊 Overview**
- Total duration
- Number of spans
- Status (success/error)
- Timestamp

**🔍 Detailed View**
- **LLM Calls**: Prompts, responses, tokens
- **Retrievals**: Documents retrieved, scores
- **Chains**: Step-by-step execution
- **Embeddings**: Vector operations
- **Errors**: Full stack traces

### Example Trace

```
RAG Query Trace
├── Duration: 2.3s
├── Status: ✅ Success
│
├── [CHAIN] RAG Chain (2.3s)
│   │
│   ├── [LLM] Contextualize Query (0.2s)
│   │   ├── Input: "What about its headquarters?"
│   │   ├── History: ["What is Tesla?", "Tesla is..."]
│   │   ├── Output: "What about Tesla's headquarters?"
│   │   └── Tokens: 45 input, 12 output
│   │
│   ├── [RETRIEVER] Vector Search (0.1s)
│   │   ├── Query: "What about Tesla's headquarters?"
│   │   ├── Retrieved: 4 documents
│   │   └── Scores: [0.89, 0.85, 0.82, 0.79]
│   │
│   └── [LLM] Generate Answer (2.0s)
│       ├── Context: [4 documents]
│       ├── Prompt: "Context: ... Question: ..."
│       ├── Response: "Tesla's headquarters..."
│       └── Tokens: 512 input, 87 output
```

## Phoenix Features

### 1. Trace Explorer

**Filter traces by:**
- Status (success/error)
- Duration
- Model used
- Time range

**Search:**
- Input text
- Output text
- Metadata

### 2. Analytics

**View metrics:**
- Average latency
- Token usage
- Error rate
- Request volume

**Charts:**
- Latency over time
- Token consumption
- Error trends

### 3. Span Details

Click any span to see:
- Full input/output
- Metadata
- Timing breakdown
- Token counts
- Model parameters

### 4. LLM Insights

**For each LLM call:**
- Exact prompt sent
- Full response received
- Token counts (input/output)
- Model name and version
- Temperature and other params

### 5. Retrieval Analysis

**For vector searches:**
- Query text
- Retrieved documents
- Relevance scores
- Number of results
- Search parameters

## Configuration

### Environment Variables

```bash
# Enable Phoenix tracing
PHOENIX_ENABLED=true

# Phoenix endpoint
PHOENIX_COLLECTOR_ENDPOINT=http://host.docker.internal:6006

# Project name
PHOENIX_PROJECT_NAME=rag-chatbot
```

### Disable Tracing

```bash
# In .env
PHOENIX_ENABLED=false

# Restart backend
docker-compose restart backend
```

### Change Project Name

```bash
# In .env
PHOENIX_PROJECT_NAME=my-custom-project

# Restart backend
docker-compose restart backend
```

## Debugging with Phoenix

### 1. Identify Slow Operations

**Look for:**
- LLM calls > 3s
- Retrieval > 0.5s
- Total chain > 5s

**Fix:**
- Use smaller models
- Optimize chunk size
- Reduce context window

### 2. Check Retrieval Quality

**Verify:**
- Relevant documents retrieved
- Good relevance scores (> 0.7)
- Sufficient context

**Improve:**
- Adjust chunk size/overlap
- Tune retrieval parameters
- Better document preprocessing

### 3. Analyze Prompts

**Review:**
- Actual prompts sent to LLM
- Context included
- System messages

**Optimize:**
- Simplify prompts
- Remove redundant context
- Better prompt templates

### 4. Track Token Usage

**Monitor:**
- Input tokens per query
- Output tokens per response
- Total tokens per session

**Reduce:**
- Smaller context windows
- Fewer retrieved documents
- Shorter system prompts

### 5. Debug Errors

**Phoenix shows:**
- Full error messages
- Stack traces
- Failed span details
- Input that caused error

## Advanced Features

### 1. Export Traces

```python
# Export traces as JSON
# Available in Phoenix UI
```

### 2. Custom Metadata

```python
# Add custom metadata to traces
from opentelemetry import trace

tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("custom_operation") as span:
    span.set_attribute("user_id", user_id)
    span.set_attribute("session_id", session_id)
    # Your code here
```

### 3. Sampling

```python
# Sample traces (e.g., 10%)
# Useful for high-traffic applications
PHOENIX_SAMPLE_RATE=0.1
```

## Comparison: Phoenix vs LangSmith

| Feature | Phoenix | LangSmith |
|---------|---------|-----------|
| **Cost** | Free, open-source | Free tier, paid plans |
| **Hosting** | Self-hosted | Cloud or self-hosted |
| **Setup** | Single Docker container | Requires account |
| **UI** | Clean, modern | Feature-rich |
| **Privacy** | 100% local | Data sent to cloud |
| **Integration** | OpenTelemetry | Native LangChain |
| **Best For** | Development, privacy | Production, teams |

## Troubleshooting

### Phoenix Not Receiving Traces

**Check connection:**
```bash
docker exec rag_chatbot_backend curl http://host.docker.internal:6006
```

**Check environment:**
```bash
docker exec rag_chatbot_backend env | grep PHOENIX
```

**Restart backend:**
```bash
docker-compose restart backend
```

### Phoenix UI Not Loading

**Check container:**
```bash
docker ps | grep phoenix
docker logs phoenix
```

**Restart Phoenix:**
```bash
docker restart phoenix
```

### Traces Not Appearing

**Verify instrumentation:**
```python
# Should see this in backend logs
from openinference.instrumentation.langchain import LangChainInstrumentor
LangChainInstrumentor().instrument()
```

**Check Phoenix logs:**
```bash
docker logs -f phoenix
```

## Performance Tips

### 1. Reduce Trace Overhead

```python
# Sample traces in production
PHOENIX_SAMPLE_RATE=0.1  # 10% of traces
```

### 2. Limit Trace Size

```python
# Truncate large inputs/outputs
MAX_TRACE_SIZE=10000  # characters
```

### 3. Batch Processing

Phoenix handles batches efficiently - no special config needed.

## Best Practices

### 1. Use Descriptive Names

```python
# Good
with tracer.start_as_current_span("retrieve_user_documents"):
    ...

# Bad
with tracer.start_as_current_span("operation"):
    ...
```

### 2. Add Context

```python
span.set_attribute("user_id", user_id)
span.set_attribute("document_count", len(docs))
span.set_attribute("model", model_name)
```

### 3. Regular Review

- Check traces daily
- Identify patterns
- Optimize slow operations
- Fix recurring errors

### 4. Clean Up Old Traces

Phoenix stores traces in memory by default. For long-running instances:

```bash
# Restart Phoenix periodically
docker restart phoenix
```

## Resources

- [Phoenix Documentation](https://docs.arize.com/phoenix)
- [GitHub Repository](https://github.com/Arize-ai/phoenix)
- [OpenTelemetry Docs](https://opentelemetry.io/docs/)

## Quick Reference

### Start Phoenix

```bash
docker run -d --name phoenix -p 6006:6006 -p 4317:4317 arizephoenix/phoenix:latest
```

### Stop Phoenix

```bash
docker stop phoenix
docker rm phoenix
```

### View Logs

```bash
docker logs -f phoenix
```

### Access UI

```
http://localhost:6006
```

### Test Connection

```bash
curl http://localhost:6006
```

---

**Phoenix is now your tracing solution!** 🎉

Open http://localhost:6006 and start exploring your RAG pipeline!
