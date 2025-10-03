from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import uuid
import os
import shutil

from ..db.base import get_db
from ..models import user as user_model
from ..models import chat as chat_model
from ..models import document as document_model
from ..models import schemas
from ..core import security
from ..services.rag_service import RAGService, DocumentProcessor
from ..core.config import settings

router = APIRouter()

def get_or_create_session(db: Session, session_id: str, user_id: int):
    """Get existing session or create new one"""
    session = db.query(chat_model.ChatSession).filter(
        chat_model.ChatSession.session_id == session_id
    ).first()
    
    if not session:
        session = chat_model.ChatSession(
            session_id=session_id,
            user_id=user_id,
            title="New Chat"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    return session

def get_chat_history(db: Session, session_id: str) -> List[dict]:
    """Get chat history for a session"""
    session = db.query(chat_model.ChatSession).filter(
        chat_model.ChatSession.session_id == session_id
    ).first()
    
    if not session:
        return []
    
    messages = db.query(chat_model.ChatMessage).filter(
        chat_model.ChatMessage.session_id == session.id
    ).order_by(chat_model.ChatMessage.created_at).all()
    
    return [{"role": msg.role, "content": msg.content} for msg in messages]

def save_message(db: Session, session_id: int, role: str, content: str, model: str = None):
    """Save a chat message"""
    message = chat_model.ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        model=model
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

@router.post("/query", response_model=schemas.ChatResponse)
async def chat_query(
    query: schemas.ChatQuery,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    """Process a chat query with RAG"""
    try:
        # Generate or use existing session ID
        session_id = query.session_id or str(uuid.uuid4())
        
        # Get or create session
        session = get_or_create_session(db, session_id, current_user.id)
        
        # Get chat history
        chat_history = get_chat_history(db, session_id)
        
        # Initialize RAG service with user context
        user_display_name = current_user.full_name or current_user.username
        rag_service = RAGService(user_id=current_user.id, user_name=user_display_name)
        
        # Query the RAG system
        result = rag_service.query(query.query, chat_history)
        
        # Save user message
        save_message(db, session.id, "user", query.query)
        
        # Save assistant response
        save_message(db, session.id, "assistant", result["answer"], settings.DEFAULT_MODEL)
        
        return schemas.ChatResponse(
            answer=result["answer"],
            session_id=session_id,
            sources=[{"content": doc.page_content, "metadata": doc.metadata} 
                    for doc in result.get("source_documents", [])]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions", response_model=List[schemas.ChatHistory])
async def get_sessions(
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    """Get all chat sessions for the current user"""
    sessions = db.query(chat_model.ChatSession).filter(
        chat_model.ChatSession.user_id == current_user.id
    ).order_by(chat_model.ChatSession.updated_at.desc()).all()
    
    result = []
    for session in sessions:
        messages = db.query(chat_model.ChatMessage).filter(
            chat_model.ChatMessage.session_id == session.id
        ).order_by(chat_model.ChatMessage.created_at).all()
        
        result.append(schemas.ChatHistory(
            session_id=session.session_id,
            messages=[schemas.ChatMessage(role=msg.role, content=msg.content) 
                     for msg in messages],
            created_at=session.created_at
        ))
    
    return result

@router.post("/upload", response_model=schemas.Document)
async def upload_document(
    file: UploadFile = File(...),
    title: str = None,
    description: str = None,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    """Upload and process a document"""
    try:
        # Create upload directory if it doesn't exist
        upload_dir = f"/app/uploads/user_{current_user.id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create document record
        document = document_model.Document(
            title=title or file.filename,
            description=description,
            file_path=file_path,
            file_type=os.path.splitext(file.filename)[1],
            file_size=file_size,
            user_id=current_user.id,
            is_processed=False
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Process document
        processor = DocumentProcessor()
        chunks = processor.process_document(file_path)
        
        # Add to vector store with user context
        user_display_name = current_user.full_name or current_user.username
        rag_service = RAGService(user_id=current_user.id, user_name=user_display_name)
        rag_service.add_documents(chunks)
        
        # Update document status
        document.is_processed = True
        db.commit()
        
        return document
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents", response_model=List[schemas.Document])
async def get_documents(
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    """Get all documents for the current user"""
    documents = db.query(document_model.Document).filter(
        document_model.Document.user_id == current_user.id
    ).order_by(document_model.Document.created_at.desc()).all()
    
    return documents
