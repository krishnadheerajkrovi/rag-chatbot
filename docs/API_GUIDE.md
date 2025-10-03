# API Usage Guide

Complete guide to using the RAG Chatbot API.

## Base URL

```
http://localhost:8000
```

## Authentication

All protected endpoints require a JWT token in the Authorization header.

### Register a New User

```bash
POST /auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "password": "secure_password123"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Login

```bash
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=john_doe&password=secure_password123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Get Current User

```bash
GET /auth/me
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Chat Endpoints

### Send a Query

```bash
POST /chat/query
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "What is machine learning?",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "answer": "Machine learning is a subset of artificial intelligence...",
  "session_id": "abc123-def456",
  "sources": [
    {
      "content": "Machine learning involves...",
      "metadata": {
        "source": "ml_intro.pdf",
        "chunk_id": 0
      }
    }
  ]
}
```

### Get Chat Sessions

```bash
GET /chat/sessions
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "session_id": "abc123-def456",
    "messages": [
      {
        "role": "user",
        "content": "What is machine learning?"
      },
      {
        "role": "assistant",
        "content": "Machine learning is..."
      }
    ],
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### Upload Document

```bash
POST /chat/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file=@document.pdf
title=Machine Learning Introduction
description=Introductory document on ML
```

**Response:**
```json
{
  "id": 1,
  "title": "Machine Learning Introduction",
  "description": "Introductory document on ML",
  "file_path": "/app/uploads/user_1/document.pdf",
  "file_type": ".pdf",
  "file_size": 1024000,
  "is_processed": true,
  "user_id": 1,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Get User Documents

```bash
GET /chat/documents
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "title": "Machine Learning Introduction",
    "description": "Introductory document on ML",
    "file_path": "/app/uploads/user_1/document.pdf",
    "file_type": ".pdf",
    "file_size": 1024000,
    "is_processed": true,
    "user_id": 1,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

## Python Client Example

```python
import requests

class RAGChatbotClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
    
    def register(self, username, email, password, full_name=None):
        """Register a new user"""
        response = requests.post(
            f"{self.base_url}/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "full_name": full_name
            }
        )
        response.raise_for_status()
        return response.json()
    
    def login(self, username, password):
        """Login and store token"""
        response = requests.post(
            f"{self.base_url}/auth/token",
            data={"username": username, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        self.token = data["access_token"]
        return data
    
    def _get_headers(self):
        """Get authorization headers"""
        if not self.token:
            raise ValueError("Not authenticated. Call login() first.")
        return {"Authorization": f"Bearer {self.token}"}
    
    def query(self, question, session_id=None):
        """Send a query to the chatbot"""
        response = requests.post(
            f"{self.base_url}/chat/query",
            json={"query": question, "session_id": session_id},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def upload_document(self, file_path, title=None, description=None):
        """Upload a document"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {}
            if title:
                data['title'] = title
            if description:
                data['description'] = description
            
            response = requests.post(
                f"{self.base_url}/chat/upload",
                files=files,
                data=data,
                headers=self._get_headers()
            )
        response.raise_for_status()
        return response.json()
    
    def get_documents(self):
        """Get all user documents"""
        response = requests.get(
            f"{self.base_url}/chat/documents",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_sessions(self):
        """Get all chat sessions"""
        response = requests.get(
            f"{self.base_url}/chat/sessions",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

# Usage example
if __name__ == "__main__":
    client = RAGChatbotClient()
    
    # Register
    client.register(
        username="test_user",
        email="test@example.com",
        password="password123",
        full_name="Test User"
    )
    
    # Login
    client.login("test_user", "password123")
    
    # Upload document
    doc = client.upload_document(
        "document.pdf",
        title="My Document",
        description="Test document"
    )
    print(f"Uploaded: {doc['title']}")
    
    # Query
    result = client.query("What is this document about?")
    print(f"Answer: {result['answer']}")
    
    # Get documents
    docs = client.get_documents()
    print(f"Total documents: {len(docs)}")
```

## cURL Examples

### Complete Workflow

```bash
# 1. Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'

# 2. Login
TOKEN=$(curl -X POST http://localhost:8000/auth/token \
  -d "username=test_user&password=password123" \
  | jq -r '.access_token')

# 3. Upload document
curl -X POST http://localhost:8000/chat/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@document.pdf" \
  -F "title=My Document" \
  -F "description=Test document"

# 4. Query
curl -X POST http://localhost:8000/chat/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is this document about?"
  }'

# 5. Get documents
curl -X GET http://localhost:8000/chat/documents \
  -H "Authorization: Bearer $TOKEN"

# 6. Get sessions
curl -X GET http://localhost:8000/chat/sessions \
  -H "Authorization: Bearer $TOKEN"
```

## JavaScript/TypeScript Example

```typescript
class RAGChatbotClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async register(username: string, email: string, password: string, fullName?: string) {
    const response = await fetch(`${this.baseUrl}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username,
        email,
        password,
        full_name: fullName
      })
    });
    return response.json();
  }

  async login(username: string, password: string) {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${this.baseUrl}/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    });
    
    const data = await response.json();
    this.token = data.access_token;
    return data;
  }

  private getHeaders() {
    if (!this.token) {
      throw new Error('Not authenticated');
    }
    return {
      'Authorization': `Bearer ${this.token}`
    };
  }

  async query(question: string, sessionId?: string) {
    const response = await fetch(`${this.baseUrl}/chat/query`, {
      method: 'POST',
      headers: {
        ...this.getHeaders(),
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        query: question,
        session_id: sessionId
      })
    });
    return response.json();
  }

  async uploadDocument(file: File, title?: string, description?: string) {
    const formData = new FormData();
    formData.append('file', file);
    if (title) formData.append('title', title);
    if (description) formData.append('description', description);

    const response = await fetch(`${this.baseUrl}/chat/upload`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: formData
    });
    return response.json();
  }

  async getDocuments() {
    const response = await fetch(`${this.baseUrl}/chat/documents`, {
      headers: this.getHeaders()
    });
    return response.json();
  }
}

// Usage
const client = new RAGChatbotClient();
await client.login('test_user', 'password123');
const result = await client.query('What is machine learning?');
console.log(result.answer);
```

## Error Handling

### Common Error Responses

#### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

#### 400 Bad Request
```json
{
  "detail": "Username already registered"
}
```

#### 404 Not Found
```json
{
  "detail": "User not found"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error message"
}
```

### Error Handling Example

```python
try:
    result = client.query("What is this about?")
    print(result['answer'])
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("Authentication failed. Please login again.")
        client.login(username, password)
    elif e.response.status_code == 500:
        print(f"Server error: {e.response.json()['detail']}")
    else:
        print(f"Error: {e}")
```

## Rate Limiting

Currently, there are no rate limits. For production, consider implementing:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/chat/query")
@limiter.limit("10/minute")
async def chat_query(...):
    ...
```

## Interactive API Documentation

Visit these URLs for interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## WebSocket Support (Future)

For real-time streaming responses:

```python
import websockets
import json

async def stream_chat():
    uri = "ws://localhost:8000/chat/stream"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
            "token": token,
            "query": "What is machine learning?"
        }))
        
        async for message in websocket:
            data = json.loads(message)
            print(data['chunk'], end='', flush=True)
```

## Best Practices

1. **Store tokens securely**: Never hardcode tokens
2. **Handle token expiration**: Implement token refresh logic
3. **Validate responses**: Always check response status codes
4. **Use HTTPS in production**: Encrypt all communications
5. **Implement retries**: Handle transient failures gracefully
6. **Log errors**: Track API usage and errors
7. **Rate limiting**: Respect API limits
8. **Batch operations**: Upload multiple documents efficiently

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Requests Documentation](https://requests.readthedocs.io/)
- [JWT.io](https://jwt.io/) - JWT debugger
