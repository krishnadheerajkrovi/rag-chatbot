from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from .api import auth, chat, folders
from .db.base import Base, engine
from .core.logging_config import setup_logging, get_logger
from .middleware.logging_middleware import RequestLoggingMiddleware

# Import all models so SQLAlchemy knows about them

# Setup logging
log_level = os.getenv("LOG_LEVEL", "INFO")
json_logs = os.getenv("JSON_LOGS", "false").lower() == "true"
setup_logging(log_level=log_level, json_logs=json_logs)

logger = get_logger(__name__)

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RAG Chatbot API",
    description="""
    ## Multi-User RAG Chatbot with Folder Organization
    
    ### Features:
    - 🔐 User authentication with JWT
    - 📁 Folder-based organization
    - 💬 Multiple chat sessions per user
    - 📄 Document upload and processing
    - 🔍 Folder-scoped semantic search
    - 📦 Archive/restore functionality
    
    ### Quick Start:
    1. Register: POST /auth/register
    2. Login: POST /auth/token
    3. Create folder: POST /folders/
    4. Upload document: POST /chat/upload
    5. Query: POST /chat/query
    
    ### Documentation:
    - Swagger UI: /docs
    - ReDoc: /redoc
    """,
    version="1.0.0",
    contact={
        "name": "RAG Chatbot Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
    },
)

# Add logging middleware (before CORS)
app.add_middleware(RequestLoggingMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Application middlewares configured")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(folders.router, prefix="/folders", tags=["folders"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to RAG Chatbot API",
        "docs": "/docs",
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
