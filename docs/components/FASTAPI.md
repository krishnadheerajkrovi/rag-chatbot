# FastAPI Component

## Overview

FastAPI is a modern, fast web framework for building APIs with Python. It provides automatic API documentation, data validation, and async support.

## Key Features

- **Fast Performance**: Built on Starlette and Pydantic
- **Automatic Documentation**: OpenAPI (Swagger) and ReDoc
- **Type Safety**: Python type hints for validation
- **Async Support**: Native async/await support
- **Dependency Injection**: Clean, testable code

## Architecture

```
┌─────────────────────────────────────┐
│         Streamlit Frontend          │
└────────────────┬────────────────────┘
                 │ HTTP/REST
                 ▼
┌─────────────────────────────────────┐
│          FastAPI Backend            │
│  ┌─────────────────────────────┐   │
│  │   Authentication Routes     │   │
│  │   /auth/register            │   │
│  │   /auth/token               │   │
│  │   /auth/me                  │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │   Chat Routes               │   │
│  │   /chat/query               │   │
│  │   /chat/sessions            │   │
│  │   /chat/upload              │   │
│  │   /chat/documents           │   │
│  └─────────────────────────────┘   │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│    PostgreSQL + Ollama + Chroma     │
└─────────────────────────────────────┘
```

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── auth.py          # Authentication endpoints
│   │   └── chat.py          # Chat endpoints
│   ├── core/
│   │   ├── config.py        # Configuration
│   │   └── security.py      # JWT & password handling
│   ├── db/
│   │   └── base.py          # Database setup
│   ├── models/
│   │   ├── user.py          # User model
│   │   ├── chat.py          # Chat models
│   │   ├── document.py      # Document models
│   │   └── schemas.py       # Pydantic schemas
│   ├── services/
│   │   └── rag_service.py   # RAG logic
│   └── main.py              # Application entry
├── requirements.txt
└── Dockerfile
```

## Core Components

### 1. Application Setup

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="RAG Chatbot API",
    description="API for multi-user RAG chatbot",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Authentication

#### JWT Token Generation
```python
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(subject: str, expires_delta: timedelta = None):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

#### Password Hashing
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

#### Protected Routes
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        raise credentials_exception
    
    return user
```

### 3. Database Integration

#### SQLAlchemy Setup
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://user:pass@db:5432/dbname"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### Models
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Relationships
    documents = relationship("Document", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")
```

### 4. Pydantic Schemas

```python
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
```

### 5. API Endpoints

#### Authentication Endpoints

```python
@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    return create_user(db=db, user=user)

@router.post("/token", response_model=schemas.Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """OAuth2 compatible token login"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(subject=user.username)
    return {"access_token": access_token, "token_type": "bearer"}
```

#### Chat Endpoints

```python
@router.post("/query", response_model=schemas.ChatResponse)
async def chat_query(
    query: schemas.ChatQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process a chat query with RAG"""
    # Get or create session
    session_id = query.session_id or str(uuid.uuid4())
    session = get_or_create_session(db, session_id, current_user.id)
    
    # Get chat history
    chat_history = get_chat_history(db, session_id)
    
    # Initialize RAG service
    rag_service = RAGService(user_id=current_user.id)
    
    # Query the RAG system
    result = rag_service.query(query.query, chat_history)
    
    # Save messages
    save_message(db, session.id, "user", query.query)
    save_message(db, session.id, "assistant", result["answer"])
    
    return schemas.ChatResponse(
        answer=result["answer"],
        session_id=session_id,
        sources=result.get("source_documents", [])
    )

@router.post("/upload", response_model=schemas.Document)
async def upload_document(
    file: UploadFile = File(...),
    title: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload and process a document"""
    # Save file
    file_path = save_uploaded_file(file, current_user.id)
    
    # Create document record
    document = create_document_record(db, file_path, title, current_user.id)
    
    # Process document
    processor = DocumentProcessor()
    chunks = processor.process_document(file_path)
    
    # Add to vector store
    rag_service = RAGService(user_id=current_user.id)
    rag_service.add_documents(chunks)
    
    # Update status
    document.is_processed = True
    db.commit()
    
    return document
```

## Middleware

### 1. CORS Middleware
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Custom Logging Middleware
```python
from fastapi import Request
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    print(f"{request.method} {request.url.path} - {process_time:.2f}s")
    return response
```

### 3. Error Handling Middleware
```python
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )
```

## Dependency Injection

### Database Dependency
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

### Authentication Dependency
```python
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Verify token and return user
    return user

@app.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
```

## Async Operations

### Async Endpoints
```python
@app.post("/chat/query")
async def chat_query(query: str):
    # Async operations
    result = await rag_service.aquery(query)
    return result
```

### Background Tasks
```python
from fastapi import BackgroundTasks

def process_document_background(file_path: str):
    # Long-running task
    pass

@app.post("/upload")
async def upload(
    file: UploadFile,
    background_tasks: BackgroundTasks
):
    file_path = save_file(file)
    background_tasks.add_task(process_document_background, file_path)
    return {"status": "processing"}
```

## Testing

### Unit Tests
```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_register():
    response = client.post(
        "/auth/register",
        json={
            "username": "test",
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    assert response.json()["username"] == "test"
```

### Integration Tests
```python
def test_chat_flow():
    # Register
    register_response = client.post("/auth/register", json=user_data)
    
    # Login
    login_response = client.post("/auth/token", data=login_data)
    token = login_response.json()["access_token"]
    
    # Query
    headers = {"Authorization": f"Bearer {token}"}
    query_response = client.post(
        "/chat/query",
        json={"query": "What is RAG?"},
        headers=headers
    )
    assert query_response.status_code == 200
```

## Best Practices

### 1. Error Handling
```python
from fastapi import HTTPException

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### 2. Request Validation
```python
from pydantic import BaseModel, validator

class ChatQuery(BaseModel):
    query: str
    session_id: Optional[str] = None
    
    @validator('query')
    def query_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v
```

### 3. Response Models
```python
@app.get("/users", response_model=List[schemas.User])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

### 4. API Versioning
```python
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
```

## Documentation

Access automatic API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Performance Optimization

### 1. Connection Pooling
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0
)
```

### 2. Caching
```python
from functools import lru_cache

@lru_cache()
def get_settings():
    return Settings()
```

### 3. Async Database
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine(DATABASE_URL)

async def get_async_db():
    async with AsyncSession(engine) as session:
        yield session
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
