# Multi-User RAG Chatbot

A production-ready multi-user chatbot with Retrieval-Augmented Generation (RAG) capabilities, built with FastAPI, Streamlit, Ollama, LangChain, and LangGraph.

## 🚀 Features

- **Multi-User Support**: User authentication with JWT tokens
- **Document Processing**: Upload and process PDF, TXT, MD, and DOCX files
- **RAG Pipeline**: History-aware retrieval with context understanding
- **Local LLM**: Run models locally with Ollama (no API costs)
- **Modern UI**: Clean, responsive Streamlit interface
- **Persistent Storage**: PostgreSQL for data, Chroma for vectors
- **Dockerized**: Complete containerized setup with Docker Compose

## 📋 Prerequisites

- Docker and Docker Compose
- At least 8GB RAM
- 10GB free disk space

## 🏃 Quick Start

### Using Local Mac Ollama (Recommended)

If you have Ollama running locally on your Mac:

```bash
# One-command setup with Phoenix tracing
./setup-phoenix.sh
```

This will:
- ✅ Verify Ollama is running
- ✅ Start Phoenix for tracing
- ✅ Configure and start all services
- ✅ Test connections

**Access Points**:
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Phoenix**: http://localhost:6006 (view traces!)

See **[LOCAL_SETUP.md](LOCAL_SETUP.md)** for detailed instructions.

### Using Dockerized Ollama

If you prefer to use Docker for everything:

1. Uncomment the Ollama service in `docker-compose.yml`
2. Update `OLLAMA_BASE_URL` to `http://ollama:11434`
3. Run:

```bash
docker-compose up --build
docker exec -it rag_chatbot_ollama ollama pull llama2
```

**Access Points**:
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📁 Project Structure

```
windsurf-project/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration & security
│   │   ├── db/             # Database setup
│   │   ├── models/         # SQLAlchemy & Pydantic models
│   │   ├── services/       # Business logic (RAG)
│   │   └── main.py         # Application entry
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/               # Streamlit frontend
│   ├── app/
│   │   ├── main.py        # Main application
│   │   └── auth.py        # Authentication
│   ├── requirements.txt
│   └── Dockerfile
│
├── docs/                   # Documentation
│   ├── SETUP.md           # Setup guide
│   └── components/        # Component documentation
│       ├── OLLAMA.md
│       ├── LANGCHAIN.md
│       ├── LANGGRAPH.md
│       ├── FASTAPI.md
│       ├── STREAMLIT.md
│       ├── DOCKER.md
│       └── DATABASE.md
│
├── docker-compose.yml     # Docker orchestration
├── .env.example          # Environment template
└── README.md             # This file
```

## 🏗️ Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Streamlit  │─────▶│   FastAPI   │─────▶│   Ollama    │
│  Frontend   │      │   Backend   │      │     LLM     │
│  Port: 8501 │      │  Port: 8000 │      │ Port: 11434 │
└─────────────┘      └──────┬──────┘      └─────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │ PostgreSQL  │
                     │   Database  │
                     │  Port: 5432 │
                     └─────────────┘
```

## 🔧 Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Relational database
- **LangChain**: RAG pipeline framework
- **LangGraph**: Conversation state management
- **Chroma**: Vector database for embeddings

### Frontend
- **Streamlit**: Interactive web UI
- **Requests**: HTTP client for API calls

### AI/ML
- **Ollama**: Local LLM inference
- **LangChain**: Document processing and RAG
- **Sentence Transformers**: Text embeddings

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

## 📖 Documentation

Comprehensive documentation for each component:

- **[Setup Guide](docs/SETUP.md)**: Installation and configuration
- **[Ollama](docs/components/OLLAMA.md)**: Local LLM setup and usage
- **[LangChain](docs/components/LANGCHAIN.md)**: RAG pipeline details
- **[LangGraph](docs/components/LANGGRAPH.md)**: State management
- **[FastAPI](docs/components/FASTAPI.md)**: Backend API documentation
- **[Streamlit](docs/components/STREAMLIT.md)**: Frontend UI guide
- **[Docker](docs/components/DOCKER.md)**: Container management
- **[Database](docs/components/DATABASE.md)**: PostgreSQL schema and operations

## 🎯 Usage

### Register a User

1. Navigate to http://localhost:8501
2. Click "Register" tab
3. Fill in your details
4. Click "Register"

### Upload Documents

1. Login to the application
2. Use the sidebar file uploader
3. Select a document (PDF, TXT, MD, or DOCX)
4. Add a title and description
5. Click "Upload & Process"

### Chat with Documents

1. Type your question in the chat input
2. The system will retrieve relevant context
3. Get AI-generated answers based on your documents
4. Continue the conversation with follow-up questions

## 🔐 Security

- JWT-based authentication
- Password hashing with bcrypt
- SQL injection prevention with ORM
- CORS configuration for API security
- Environment-based secrets management

## 🚀 Production Deployment

### Environment Variables

Update `.env` with production values:

```bash
SECRET_KEY=<strong-random-key>
DATABASE_URL=<production-database-url>
OLLAMA_BASE_URL=<ollama-server-url>
```

### Resource Limits

Configure in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
```

### Backup Strategy

```bash
# Backup database
docker exec -t rag_chatbot_db pg_dump -U postgres rag_chatbot > backup.sql

# Backup vector store
docker run --rm -v windsurf-project_vector_store:/data -v $(pwd):/backup alpine tar czf /backup/vectors.tar.gz /data
```

## 🐛 Troubleshooting

### Services Won't Start

```bash
docker-compose logs backend
docker-compose logs ollama
docker-compose restart
```

### Ollama Model Issues

```bash
docker exec -it rag_chatbot_ollama ollama list
docker exec -it rag_chatbot_ollama ollama pull llama2
```

### Database Connection

```bash
docker-compose exec db psql -U postgres -d rag_chatbot
```

See [SETUP.md](docs/SETUP.md) for more troubleshooting tips.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built following best practices from [FutureSmart AI Blog](http://blog.futuresmart.ai/langchain-rag-from-basics-to-production-ready-rag-chatbot)
- Powered by open-source technologies
- Community-driven development

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation in `docs/`
- Review troubleshooting guide in SETUP.md
