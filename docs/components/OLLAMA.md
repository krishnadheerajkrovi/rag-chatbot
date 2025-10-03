# Ollama Component

## Overview

Ollama is a local LLM inference server that allows you to run large language models on your own hardware without relying on external APIs.

## Key Features

- **Local Inference**: Run models completely offline
- **Multiple Models**: Support for various open-source models
- **Fast Performance**: Optimized for CPU and GPU inference
- **Easy Model Management**: Simple CLI for downloading and managing models

## Architecture

```
┌─────────────────┐
│   FastAPI App   │
│   (Backend)     │
└────────┬────────┘
         │ HTTP Requests
         ▼
┌─────────────────┐
│  Ollama Server  │
│  Port: 11434    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Models     │
│  (llama2, etc)  │
└─────────────────┘
```

## Configuration

### Environment Variables

```bash
OLLAMA_BASE_URL=http://ollama:11434
DEFAULT_MODEL=llama2
```

### Available Models

| Model | Size | Use Case |
|-------|------|----------|
| llama2 | 7B | General purpose, good balance |
| mistral | 7B | Better reasoning, faster |
| codellama | 7B | Code generation and analysis |
| phi | 2.7B | Lightweight, faster inference |
| neural-chat | 7B | Conversational AI |

## Usage in Application

### 1. LangChain Integration

```python
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings

# Initialize chat model
llm = ChatOllama(
    model="llama2",
    base_url="http://ollama:11434",
    temperature=0.7
)

# Initialize embeddings
embeddings = OllamaEmbeddings(
    model="llama2",
    base_url="http://ollama:11434"
)
```

### 2. Direct API Calls

```python
import requests

# Generate completion
response = requests.post(
    "http://ollama:11434/api/generate",
    json={
        "model": "llama2",
        "prompt": "What is RAG?",
        "stream": False
    }
)
```

## Model Management

### Pull New Models

```bash
# Inside the container
docker exec -it rag_chatbot_ollama ollama pull mistral

# Or from host
curl http://localhost:11434/api/pull -d '{
  "name": "mistral"
}'
```

### List Available Models

```bash
docker exec -it rag_chatbot_ollama ollama list
```

### Remove Models

```bash
docker exec -it rag_chatbot_ollama ollama rm llama2
```

## Performance Optimization

### 1. GPU Acceleration

For NVIDIA GPUs, update docker-compose.yml:

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

### 2. Memory Management

```bash
# Set context window size
OLLAMA_NUM_CTX=4096

# Set number of GPU layers
OLLAMA_NUM_GPU=35
```

### 3. Model Selection

- **Small documents**: Use `phi` (2.7B) for faster responses
- **Complex queries**: Use `mistral` or `llama2` (7B)
- **Code analysis**: Use `codellama` (7B)

## Troubleshooting

### Model Download Issues

```bash
# Check Ollama logs
docker logs rag_chatbot_ollama

# Manually pull model
docker exec -it rag_chatbot_ollama ollama pull llama2
```

### Out of Memory

- Use smaller models (phi instead of llama2)
- Reduce context window: `OLLAMA_NUM_CTX=2048`
- Increase Docker memory limit

### Slow Inference

- Enable GPU acceleration
- Use smaller models
- Reduce batch size in embeddings

## Best Practices

1. **Model Selection**: Choose the smallest model that meets your needs
2. **Caching**: Ollama caches model layers for faster subsequent loads
3. **Concurrent Requests**: Ollama handles multiple requests efficiently
4. **Monitoring**: Track response times and adjust model/parameters accordingly

## API Reference

### Generate Completion

```bash
POST /api/generate
{
  "model": "llama2",
  "prompt": "Your prompt here",
  "stream": false
}
```

### Chat Completion

```bash
POST /api/chat
{
  "model": "llama2",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ]
}
```

### Create Embeddings

```bash
POST /api/embeddings
{
  "model": "llama2",
  "prompt": "Text to embed"
}
```

## Resources

- [Ollama Documentation](https://ollama.ai/docs)
- [Available Models](https://ollama.ai/library)
- [GitHub Repository](https://github.com/ollama/ollama)
