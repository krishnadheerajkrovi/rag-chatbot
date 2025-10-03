# System Architecture

Complete architectural overview of the Multi-User RAG Chatbot system.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                            │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/WebSocket
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend (Port 8501)               │
│  • User Authentication UI                                       │
│  • Document Upload Interface                                    │
│  • Chat Interface                                               │
│  • Session Management                                           │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Port 8000)                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │  Auth Routes     │  │  Chat Routes     │  │  RAG Service │ │
│  │  • Register      │  │  • Query         │  │  • Document  │ │
│  │  • Login         │  │  • Upload        │  │    Processing│ │
│  │  • Token Verify  │  │  • History       │  │  • Retrieval │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
└────────┬──────────────────────┬──────────────────────┬──────────┘
         │                      │                      │
         ▼                      ▼                      ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐
│   PostgreSQL    │  │  Ollama LLM     │  │   Chroma Vector DB  │
│   (Port 5432)   │  │  (Port 11434)   │  │   (Embedded)        │
│                 │  │                 │  │                     │
│  • Users        │  │  • llama2       │  │  • Document Chunks  │
│  • Documents    │  │  • mistral      │  │  • Embeddings       │
│  • Chat History │  │  • codellama    │  │  • Metadata         │
│  • Sessions     │  │  • phi          │  │                     │
└─────────────────┘  └─────────────────┘  └─────────────────────┘
```

## Component Interaction Flow

### 1. User Registration & Authentication

```
User → Streamlit → FastAPI → PostgreSQL
                      ↓
                   JWT Token
                      ↓
                   Streamlit (Store in Session)
```

**Steps:**
1. User submits registration form
2. Streamlit sends POST to `/auth/register`
3. FastAPI validates data with Pydantic
4. Password hashed with bcrypt
5. User record created in PostgreSQL
6. User logs in with credentials
7. JWT token generated and returned
8. Token stored in Streamlit session state

### 2. Document Upload & Processing

```
User → Streamlit → FastAPI → File System
                      ↓
                   Document Processor
                      ↓
                   Text Splitter
                      ↓
                   Ollama (Embeddings)
                      ↓
                   Chroma Vector Store
                      ↓
                   PostgreSQL (Metadata)
```

**Steps:**
1. User uploads file via Streamlit
2. File sent to `/chat/upload` endpoint
3. File saved to user-specific directory
4. Document metadata saved to PostgreSQL
5. LangChain loader reads document
6. Text splitter creates chunks (1000 chars, 200 overlap)
7. Ollama generates embeddings for each chunk
8. Embeddings stored in Chroma with metadata
9. Document marked as processed

### 3. RAG Query Processing

```
User Query → Streamlit → FastAPI → RAG Service
                                      ↓
                                   History-Aware Retriever
                                      ↓
                            ┌─────────┴─────────┐
                            ▼                   ▼
                    Contextualize Query    Retrieve from Chroma
                    (with chat history)         ↓
                            │              Top K Documents
                            │                   │
                            └─────────┬─────────┘
                                      ▼
                                  Ollama LLM
                                      ↓
                                  Generate Answer
                                      ↓
                            Save to PostgreSQL
                                      ↓
                                  Return to User
```

**Steps:**
1. User sends query via Streamlit
2. Query sent to `/chat/query` with session_id
3. FastAPI retrieves chat history from PostgreSQL
4. RAG Service initializes with user_id
5. History-aware retriever reformulates query with context
6. Chroma performs MMR search for relevant chunks
7. Retrieved documents passed to Ollama with query
8. Ollama generates answer based on context
9. User query and assistant response saved to PostgreSQL
10. Answer returned to Streamlit
11. UI updates with new message

## Data Flow Diagrams

### Document Processing Pipeline

```
┌──────────────┐
│   Raw File   │
│  (PDF/TXT)   │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│  Document Loader │
│  (LangChain)     │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Text Splitter   │
│  (Recursive)     │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Chunks          │
│  [C1, C2, C3...] │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Embedding Gen   │
│  (Ollama)        │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Vector Store    │
│  (Chroma)        │
└──────────────────┘
```

### RAG Query Pipeline

```
┌──────────────────┐
│  User Query      │
│  + Chat History  │
└────────┬─────────┘
         │
         ▼
┌──────────────────────┐
│  Contextualize       │
│  (Reformulate Query) │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  Vector Search       │
│  (MMR, k=4)          │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  Retrieved Docs      │
│  [D1, D2, D3, D4]    │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  Prompt Construction │
│  Context + Query     │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  LLM Generation      │
│  (Ollama)            │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  Answer              │
└──────────────────────┘
```

## Database Schema

### Entity Relationship Diagram

```
┌─────────────┐
│    users    │
│─────────────│
│ id (PK)     │
│ username    │
│ email       │
│ password    │
└──────┬──────┘
       │ 1
       │
       │ N
┌──────┴──────────────┐
│                     │
▼                     ▼
┌─────────────┐   ┌──────────────┐
│  documents  │   │chat_sessions │
│─────────────│   │──────────────│
│ id (PK)     │   │ id (PK)      │
│ user_id(FK) │   │ session_id   │
│ title       │   │ user_id (FK) │
│ file_path   │   │ title        │
└──────┬──────┘   └──────┬───────┘
       │ 1               │ 1
       │                 │
       │ N               │ N
       ▼                 ▼
┌─────────────┐   ┌──────────────┐
│doc_chunks   │   │chat_messages │
│─────────────│   │──────────────│
│ id (PK)     │   │ id (PK)      │
│ doc_id (FK) │   │ session_id   │
│ chunk_text  │   │ role         │
│ embedding_id│   │ content      │
└─────────────┘   └──────────────┘
```

## Security Architecture

### Authentication Flow

```
┌──────────┐                ┌──────────┐
│  Client  │                │  Server  │
└────┬─────┘                └────┬─────┘
     │                           │
     │  1. POST /auth/token      │
     │  (username, password)     │
     │──────────────────────────>│
     │                           │
     │                      2. Verify
     │                      credentials
     │                           │
     │  3. JWT Token             │
     │<──────────────────────────│
     │                           │
     │  4. Subsequent requests   │
     │  Authorization: Bearer    │
     │  <token>                  │
     │──────────────────────────>│
     │                           │
     │                      5. Verify
     │                      token
     │                           │
     │  6. Response              │
     │<──────────────────────────│
     │                           │
```

### Security Layers

1. **Transport Security**: HTTPS in production
2. **Authentication**: JWT tokens with expiration
3. **Password Security**: Bcrypt hashing
4. **SQL Injection**: ORM (SQLAlchemy) parameterized queries
5. **CORS**: Configured for specific origins
6. **Input Validation**: Pydantic schemas
7. **Authorization**: User-specific data isolation

## Scalability Considerations

### Current Architecture (Single Server)

```
┌────────────────────────────────┐
│      Single Docker Host        │
│  ┌──────┐ ┌──────┐ ┌────────┐ │
│  │ Web  │ │ API  │ │  DB    │ │
│  └──────┘ └──────┘ └────────┘ │
└────────────────────────────────┘
```

**Limitations:**
- Single point of failure
- Limited by single machine resources
- No horizontal scaling

### Scalable Architecture (Production)

```
┌─────────────┐
│Load Balancer│
└──────┬──────┘
       │
   ┌───┴───┐
   │       │
   ▼       ▼
┌─────┐ ┌─────┐
│ API │ │ API │  (Multiple instances)
└──┬──┘ └──┬──┘
   │       │
   └───┬───┘
       │
   ┌───┴────────┐
   │            │
   ▼            ▼
┌──────┐   ┌────────┐
│  DB  │   │ Ollama │
│Cluster│  │Cluster │
└──────┘   └────────┘
```

**Improvements:**
- Load balancing across API instances
- Database replication and clustering
- Distributed vector store
- Separate Ollama inference cluster
- Redis for session management
- Message queue for async processing

## Performance Optimization

### Caching Strategy

```
┌──────────┐
│  Query   │
└────┬─────┘
     │
     ▼
┌──────────────┐
│ Check Cache  │
│  (Redis)     │
└────┬─────────┘
     │
  ┌──┴──┐
  │Hit? │
  └──┬──┘
     │
  ┌──┴──────────┐
  │             │
  ▼ Yes         ▼ No
┌──────┐   ┌──────────┐
│Return│   │  Process │
│Cache │   │  Query   │
└──────┘   └────┬─────┘
                │
                ▼
           ┌──────────┐
           │  Store   │
           │  Cache   │
           └──────────┘
```

### Optimization Techniques

1. **Database**
   - Connection pooling
   - Indexed queries
   - Query optimization

2. **Vector Search**
   - MMR for diversity
   - Batch processing
   - Index optimization

3. **LLM Inference**
   - Model quantization
   - GPU acceleration
   - Batch inference

4. **Caching**
   - Query result caching
   - Embedding caching
   - Session caching

## Monitoring & Observability

### Metrics to Track

1. **Application Metrics**
   - Request rate
   - Response time
   - Error rate
   - Active users

2. **Database Metrics**
   - Query performance
   - Connection pool usage
   - Storage usage

3. **LLM Metrics**
   - Inference time
   - Token usage
   - Model performance

4. **System Metrics**
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network I/O

### Logging Architecture

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Frontend │  │ Backend  │  │ Database │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │              │
     │ Logs        │ Logs         │ Logs
     │             │              │
     └─────────────┴──────────────┘
                   │
                   ▼
            ┌──────────────┐
            │ Log Aggregator│
            │  (ELK Stack)  │
            └──────┬────────┘
                   │
                   ▼
            ┌──────────────┐
            │  Dashboard   │
            │  (Grafana)   │
            └──────────────┘
```

## Deployment Architecture

### Development

```
docker-compose up
```

### Production

```
┌─────────────────────────────────────┐
│         Cloud Provider              │
│  ┌──────────────────────────────┐  │
│  │   Kubernetes Cluster         │  │
│  │  ┌────────┐  ┌────────┐     │  │
│  │  │  Pod   │  │  Pod   │     │  │
│  │  │ (API)  │  │ (API)  │     │  │
│  │  └────────┘  └────────┘     │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │   Managed Services           │  │
│  │  • PostgreSQL (RDS)          │  │
│  │  • Redis (ElastiCache)       │  │
│  │  • S3 (File Storage)         │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

## Technology Decisions

### Why These Technologies?

| Component | Choice | Reason |
|-----------|--------|--------|
| **Backend** | FastAPI | Fast, modern, automatic docs |
| **Frontend** | Streamlit | Rapid development, Python-native |
| **Database** | PostgreSQL | Robust, ACID compliant |
| **LLM** | Ollama | Local, no API costs, privacy |
| **RAG** | LangChain | Mature ecosystem, flexibility |
| **State** | LangGraph | Conversation management |
| **Vectors** | Chroma | Easy setup, good performance |
| **Container** | Docker | Consistency, portability |

## Future Enhancements

1. **WebSocket Support**: Real-time streaming responses
2. **Multi-modal**: Support images and audio
3. **Advanced RAG**: Hybrid search, re-ranking
4. **Analytics**: Usage dashboards and insights
5. **API Rate Limiting**: Protect against abuse
6. **Caching Layer**: Redis for performance
7. **Message Queue**: Async document processing
8. **Multi-tenancy**: Organization support
9. **Fine-tuning**: Custom model training
10. **Mobile App**: Native mobile clients

## Resources

- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [LangChain Architecture](https://python.langchain.com/docs/get_started/introduction)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
