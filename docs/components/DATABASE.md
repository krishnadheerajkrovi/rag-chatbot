# PostgreSQL Database Component

## Overview

PostgreSQL is our relational database for storing user accounts, chat history, and document metadata. It provides ACID compliance, complex queries, and robust data integrity.

## Architecture

```
┌─────────────────────────────────────┐
│        PostgreSQL Database          │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   users                      │  │
│  │   - id (PK)                  │  │
│  │   - username                 │  │
│  │   - email                    │  │
│  │   - hashed_password          │  │
│  └────────┬─────────────────────┘  │
│           │                         │
│           │ 1:N                     │
│           ▼                         │
│  ┌──────────────────────────────┐  │
│  │   documents                  │  │
│  │   - id (PK)                  │  │
│  │   - user_id (FK)             │  │
│  │   - title                    │  │
│  │   - file_path                │  │
│  │   - is_processed             │  │
│  └──────────────────────────────┘  │
│           │                         │
│           │ 1:N                     │
│           ▼                         │
│  ┌──────────────────────────────┐  │
│  │   chat_sessions              │  │
│  │   - id (PK)                  │  │
│  │   - session_id               │  │
│  │   - user_id (FK)             │  │
│  │   - title                    │  │
│  └────────┬─────────────────────┘  │
│           │                         │
│           │ 1:N                     │
│           ▼                         │
│  ┌──────────────────────────────┐  │
│  │   chat_messages              │  │
│  │   - id (PK)                  │  │
│  │   - session_id (FK)          │  │
│  │   - role                     │  │
│  │   - content                  │  │
│  │   - created_at               │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

### Documents Table

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size INTEGER NOT NULL,
    is_processed BOOLEAN DEFAULT FALSE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_is_processed ON documents(is_processed);
```

### Document Chunks Table

```sql
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding_id VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_chunks_embedding_id ON document_chunks(embedding_id);
```

### Chat Sessions Table

```sql
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_sessions_session_id ON chat_sessions(session_id);
```

### Chat Messages Table

```sql
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    model VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_messages_created_at ON chat_messages(created_at);
```

## SQLAlchemy Models

### User Model

```python
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
```

### Document Model

```python
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, JSON

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    is_processed = Column(Boolean, default=False, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
```

### Chat Models

```python
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    model = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("ChatSession", back_populates="messages")
```

## Database Operations

### Connection Setup

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:postgres@db:5432/rag_chatbot"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### CRUD Operations

#### Create
```python
def create_user(db: Session, user: UserCreate):
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

#### Read
```python
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()
```

#### Update
```python
def update_user(db: Session, user_id: int, user_update: UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        for key, value in user_update.dict(exclude_unset=True).items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user
```

#### Delete
```python
def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user
```

### Complex Queries

#### Join Queries
```python
def get_user_with_documents(db: Session, user_id: int):
    return db.query(User)\
        .join(Document)\
        .filter(User.id == user_id)\
        .options(joinedload(User.documents))\
        .first()
```

#### Aggregation
```python
from sqlalchemy import func

def get_user_stats(db: Session, user_id: int):
    return db.query(
        func.count(Document.id).label('document_count'),
        func.count(ChatSession.id).label('session_count')
    ).join(Document, Document.user_id == user_id)\
     .join(ChatSession, ChatSession.user_id == user_id)\
     .first()
```

#### Filtering
```python
def get_processed_documents(db: Session, user_id: int):
    return db.query(Document)\
        .filter(Document.user_id == user_id)\
        .filter(Document.is_processed == True)\
        .order_by(Document.created_at.desc())\
        .all()
```

## Migrations with Alembic

### Setup

```bash
# Initialize Alembic
alembic init alembic

# Configure alembic.ini
sqlalchemy.url = postgresql://postgres:postgres@localhost:5432/rag_chatbot
```

### Create Migration

```bash
# Auto-generate migration
alembic revision --autogenerate -m "Create users table"

# Create empty migration
alembic revision -m "Add index"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade abc123

# Downgrade
alembic downgrade -1
```

### Migration Script Example

```python
"""Create users table

Revision ID: abc123
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_email', 'users', ['email'])

def downgrade():
    op.drop_index('idx_users_email')
    op.drop_index('idx_users_username')
    op.drop_table('users')
```

## Database Management

### Backup

```bash
# Backup database
docker exec -t rag_chatbot_db pg_dump -U postgres rag_chatbot > backup.sql

# Backup with compression
docker exec -t rag_chatbot_db pg_dump -U postgres rag_chatbot | gzip > backup.sql.gz
```

### Restore

```bash
# Restore database
docker exec -i rag_chatbot_db psql -U postgres rag_chatbot < backup.sql

# Restore from compressed backup
gunzip -c backup.sql.gz | docker exec -i rag_chatbot_db psql -U postgres rag_chatbot
```

### Connect to Database

```bash
# Using docker exec
docker exec -it rag_chatbot_db psql -U postgres -d rag_chatbot

# Using psql directly
psql -h localhost -U postgres -d rag_chatbot
```

### Common SQL Commands

```sql
-- List tables
\dt

-- Describe table
\d users

-- List databases
\l

-- Switch database
\c rag_chatbot

-- Show table size
SELECT pg_size_pretty(pg_total_relation_size('users'));

-- Count rows
SELECT COUNT(*) FROM users;

-- Show indexes
\di
```

## Performance Optimization

### Indexing

```sql
-- Create index
CREATE INDEX idx_documents_user_id ON documents(user_id);

-- Create composite index
CREATE INDEX idx_messages_session_created ON chat_messages(session_id, created_at);

-- Create partial index
CREATE INDEX idx_unprocessed_docs ON documents(user_id) WHERE is_processed = FALSE;

-- Create GIN index for JSONB
CREATE INDEX idx_chunks_metadata ON document_chunks USING GIN (metadata);
```

### Query Optimization

```python
# Use select_related for foreign keys
users = db.query(User).options(joinedload(User.documents)).all()

# Use pagination
def get_paginated_documents(db: Session, page: int = 1, per_page: int = 20):
    return db.query(Document)\
        .offset((page - 1) * per_page)\
        .limit(per_page)\
        .all()

# Use exists() for checking existence
exists = db.query(User).filter(User.email == email).exists()
db.query(exists).scalar()
```

### Connection Pooling

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True
)
```

## Security

### SQL Injection Prevention

```python
# ✅ Good - Using ORM
user = db.query(User).filter(User.username == username).first()

# ✅ Good - Using parameters
db.execute("SELECT * FROM users WHERE username = :username", {"username": username})

# ❌ Bad - String concatenation
db.execute(f"SELECT * FROM users WHERE username = '{username}'")
```

### Password Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
hashed = pwd_context.hash("password123")

# Verify password
is_valid = pwd_context.verify("password123", hashed)
```

## Monitoring

### Query Logging

```python
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### Slow Query Log

```sql
-- Enable slow query log
ALTER DATABASE rag_chatbot SET log_min_duration_statement = 1000;

-- View slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

## Best Practices

1. **Use Transactions**: Wrap related operations in transactions
2. **Close Connections**: Always close database sessions
3. **Use Indexes**: Index frequently queried columns
4. **Avoid N+1 Queries**: Use eager loading
5. **Validate Input**: Use Pydantic schemas
6. **Regular Backups**: Automate database backups
7. **Monitor Performance**: Track slow queries
8. **Use Migrations**: Version control schema changes

## Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
