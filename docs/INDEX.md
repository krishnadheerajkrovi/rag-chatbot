# Documentation Index

Complete guide to the Multi-User RAG Chatbot documentation.

## 🚀 Getting Started

Start here if you're new to the project:

1. **[README](../README.md)** - Project overview and features
2. **[QUICKSTART](../QUICKSTART.md)** - Get running in 5 minutes
3. **[SETUP Guide](SETUP.md)** - Detailed installation instructions

## 📚 Core Documentation

### System Overview

- **[Architecture](ARCHITECTURE.md)** - Complete system architecture
  - High-level design
  - Component interactions
  - Data flow diagrams
  - Security architecture
  - Scalability considerations

### API Documentation

- **[API Guide](API_GUIDE.md)** - Complete API reference
  - Authentication endpoints
  - Chat endpoints
  - Python client examples
  - cURL examples
  - Error handling

## 🔧 Component Documentation

Deep dive into each technology component:

### Backend Technologies

- **[FastAPI](components/FASTAPI.md)** - Backend framework
  - Application setup
  - Authentication & JWT
  - Database integration
  - API endpoints
  - Middleware & dependencies
  - Testing strategies

- **[Database (PostgreSQL)](components/DATABASE.md)** - Data persistence
  - Schema design
  - SQLAlchemy models
  - CRUD operations
  - Migrations with Alembic
  - Performance optimization
  - Backup & restore

### AI/ML Technologies

- **[Ollama](components/OLLAMA.md)** - Local LLM inference
  - Model management
  - LangChain integration
  - Performance optimization
  - GPU acceleration
  - Troubleshooting

- **[LangChain](components/LANGCHAIN.md)** - RAG framework
  - Document loaders
  - Text splitters
  - Embeddings
  - Vector stores
  - Retrievers
  - RAG chains
  - Best practices

- **[LangGraph](components/LANGGRAPH.md)** - State management
  - State definitions
  - Graph construction
  - Conditional routing
  - Checkpointing
  - Use cases
  - Integration patterns

### Frontend Technologies

- **[Streamlit](components/STREAMLIT.md)** - Web interface
  - Application structure
  - Session state management
  - Authentication UI
  - Chat interface
  - Custom styling
  - Widgets reference
  - Best practices

### Infrastructure

- **[Docker](components/DOCKER.md)** - Containerization
  - Docker Compose setup
  - Individual Dockerfiles
  - Volume management
  - Networking
  - Health checks
  - Production optimization
  - Troubleshooting

## 📖 How-To Guides

### For Users

1. **Getting Started**
   - [Quick Start](../QUICKSTART.md) - 5-minute setup
   - [First Steps](SETUP.md#first-time-setup) - Creating your first chat

2. **Using the Application**
   - Register and login
   - Upload documents
   - Chat with your documents
   - Manage chat sessions

### For Developers

1. **Development Setup**
   ```bash
   # See SETUP.md for detailed instructions
   docker-compose up --build
   ```

2. **Making Changes**
   - Backend: Edit files in `backend/app/`
   - Frontend: Edit files in `frontend/app/`
   - Hot reload enabled in development

3. **Testing**
   - Unit tests: See [FastAPI docs](components/FASTAPI.md#testing)
   - Integration tests: API testing examples
   - Manual testing: Use Swagger UI at `/docs`

4. **Adding Features**
   - New API endpoint: [FastAPI guide](components/FASTAPI.md#api-endpoints)
   - New UI component: [Streamlit guide](components/STREAMLIT.md#components)
   - Database changes: [Database migrations](components/DATABASE.md#migrations-with-alembic)

### For DevOps

1. **Deployment**
   - [Production setup](SETUP.md#production-deployment)
   - [Docker optimization](components/DOCKER.md#production-optimization)
   - [Security hardening](ARCHITECTURE.md#security-architecture)

2. **Monitoring**
   - [Logging setup](components/DOCKER.md#logging)
   - [Health checks](components/DOCKER.md#health-checks)
   - [Performance metrics](ARCHITECTURE.md#monitoring--observability)

3. **Maintenance**
   - [Backup procedures](components/DATABASE.md#backup)
   - [Scaling strategies](ARCHITECTURE.md#scalability-considerations)
   - [Troubleshooting](SETUP.md#troubleshooting)

## 🎯 Use Case Guides

### Basic RAG Chatbot

**Goal**: Chat with your documents

**Steps**:
1. Upload documents (PDF, TXT, MD, DOCX)
2. Ask questions about the content
3. Get AI-powered answers with sources

**Documentation**:
- [LangChain RAG](components/LANGCHAIN.md#rag-pipeline-flow)
- [Chat API](API_GUIDE.md#chat-endpoints)

### Multi-User System

**Goal**: Multiple users with isolated data

**Steps**:
1. User registration and authentication
2. User-specific document storage
3. Isolated vector stores per user

**Documentation**:
- [Authentication](components/FASTAPI.md#authentication)
- [Database schema](components/DATABASE.md#database-schema)
- [Security](ARCHITECTURE.md#security-architecture)

### Conversational AI

**Goal**: Multi-turn conversations with context

**Steps**:
1. Chat history stored in database
2. History-aware retrieval
3. Context-aware responses

**Documentation**:
- [LangChain History](components/LANGCHAIN.md#history-aware-retriever)
- [LangGraph State](components/LANGGRAPH.md#state-management-patterns)
- [Chat Sessions](components/DATABASE.md#chat-sessions-table)

### Custom Model Integration

**Goal**: Use different LLM models

**Steps**:
1. Pull model: `ollama pull <model-name>`
2. Update `.env`: `DEFAULT_MODEL=<model-name>`
3. Restart backend

**Documentation**:
- [Ollama models](components/OLLAMA.md#available-models)
- [Configuration](components/FASTAPI.md#configuration)

## 🔍 Reference

### Configuration

- **Environment Variables**: See `.env.example`
- **Docker Compose**: See `docker-compose.yml`
- **API Settings**: [FastAPI config](components/FASTAPI.md#application-setup)

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | Register new user |
| `/auth/token` | POST | Login and get token |
| `/auth/me` | GET | Get current user |
| `/chat/query` | POST | Send chat query |
| `/chat/upload` | POST | Upload document |
| `/chat/documents` | GET | List documents |
| `/chat/sessions` | GET | List chat sessions |

Full reference: [API Guide](API_GUIDE.md)

### Database Tables

| Table | Purpose |
|-------|---------|
| `users` | User accounts |
| `documents` | Document metadata |
| `document_chunks` | Text chunks |
| `chat_sessions` | Chat sessions |
| `chat_messages` | Chat messages |

Full schema: [Database docs](components/DATABASE.md#database-schema)

### Docker Services

| Service | Port | Purpose |
|---------|------|---------|
| `frontend` | 8501 | Streamlit UI |
| `backend` | 8000 | FastAPI server |
| `db` | 5432 | PostgreSQL |
| `ollama` | 11434 | LLM inference |

Full details: [Docker docs](components/DOCKER.md)

## 🐛 Troubleshooting

### Common Issues

1. **Services won't start**
   - Check: [Docker troubleshooting](components/DOCKER.md#troubleshooting)
   - Logs: `docker-compose logs`

2. **Model not found**
   - Check: [Ollama troubleshooting](components/OLLAMA.md#troubleshooting)
   - Fix: `docker exec -it rag_chatbot_ollama ollama pull llama2`

3. **Database connection**
   - Check: [Database troubleshooting](components/DATABASE.md#database-management)
   - Logs: `docker-compose logs db`

4. **Authentication errors**
   - Check: [Security docs](components/FASTAPI.md#authentication)
   - Verify: Token expiration, credentials

### Getting Help

1. **Check Documentation**: Search this index
2. **View Logs**: `docker-compose logs <service>`
3. **Health Checks**: Visit `/health` endpoints
4. **API Docs**: http://localhost:8000/docs
5. **GitHub Issues**: Report bugs and ask questions

## 📝 Contributing

### Documentation

- All docs in `docs/` directory
- Markdown format
- Include code examples
- Keep up to date with code changes

### Code

- Follow existing patterns
- Add tests for new features
- Update documentation
- Submit pull requests

## 🔗 External Resources

### Technologies

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [LangChain Documentation](https://python.langchain.com/)
- [Ollama Documentation](https://ollama.ai/docs)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Learning Resources

- [RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Docker Tutorial](https://docs.docker.com/get-started/)
- [SQL Tutorial](https://www.postgresql.org/docs/current/tutorial.html)

### Inspiration

- [FutureSmart AI Blog](http://blog.futuresmart.ai/langchain-rag-from-basics-to-production-ready-rag-chatbot)
- [LangChain Cookbook](https://github.com/langchain-ai/langchain/tree/master/cookbook)
- [Awesome RAG](https://github.com/awesome-rag/awesome-rag)

## 📊 Documentation Stats

- **Total Documents**: 12
- **Component Guides**: 7
- **Setup Guides**: 3
- **Reference Docs**: 2

## 🗺️ Documentation Roadmap

### Planned Additions

- [ ] Video tutorials
- [ ] Architecture diagrams (Mermaid)
- [ ] Performance benchmarks
- [ ] Security audit guide
- [ ] Migration guides
- [ ] FAQ section
- [ ] Glossary of terms

### Recent Updates

- ✅ Complete component documentation
- ✅ API reference guide
- ✅ Quick start guide
- ✅ Architecture overview
- ✅ Troubleshooting sections

---

**Last Updated**: 2024-01-01

**Version**: 0.1.0

**Maintainers**: Project Team

**License**: MIT
