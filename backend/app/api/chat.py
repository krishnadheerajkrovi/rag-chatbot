from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
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

def _get_chat_history_helper(db: Session, session_id: str) -> List[dict]:
    """Helper function to get chat history for a session"""
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
        chat_history = _get_chat_history_helper(db, session_id)
        print(f"📜 Chat history for session {session_id}: {len(chat_history)} messages")
        if chat_history:
            print(f"   Last message: {chat_history[-1]['content'][:100]}...")
        
        # Initialize RAG service with user context
        user_display_name = current_user.full_name or current_user.username
        rag_service = RAGService(user_id=current_user.id, user_name=user_display_name)
        
        # Determine folder_id for scoped retrieval
        folder_id = query.folder_id
        if folder_id is None and session.folder_id:
            # Use session's folder if not explicitly provided
            folder_id = session.folder_id
        
        # Query the RAG system with optional folder scope
        result = rag_service.query(query.query, chat_history, folder_id=folder_id)
        
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

@router.post("/sessions", response_model=schemas.ChatSession)
async def create_session(
    session_data: schemas.ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    """Create a new chat session"""
    import uuid
    
    new_session = chat_model.ChatSession(
        session_id=str(uuid.uuid4()),
        title=session_data.title,
        folder_id=session_data.folder_id,
        user_id=current_user.id
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


@router.get("/sessions", response_model=List[schemas.ChatSession])
async def get_sessions(
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    """Get all chat sessions for the current user"""
    sessions = db.query(chat_model.ChatSession).filter(
        chat_model.ChatSession.user_id == current_user.id
    ).order_by(chat_model.ChatSession.updated_at.desc()).all()
    
    return sessions


@router.get("/history/{session_id}", response_model=schemas.ChatHistory)
async def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    """Get chat history for a specific session"""
    # Find the session
    session = db.query(chat_model.ChatSession).filter(
        chat_model.ChatSession.session_id == session_id,
        chat_model.ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    # Get messages
    messages = db.query(chat_model.ChatMessage).filter(
        chat_model.ChatMessage.session_id == session.id
    ).order_by(chat_model.ChatMessage.created_at).all()
    
    return schemas.ChatHistory(
        session_id=session.session_id,
        messages=[schemas.ChatMessage(role=msg.role, content=msg.content) for msg in messages],
        created_at=session.created_at
    )

@router.delete("/sessions/clear")
async def clear_chat_history(
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    """Clear all chat history for the current user"""
    try:
        # Delete all sessions (cascades to messages)
        sessions = db.query(chat_model.ChatSession).filter(
            chat_model.ChatSession.user_id == current_user.id
        ).all()
        
        session_count = len(sessions)
        
        for session in sessions:
            db.delete(session)
        
        db.commit()
        
        return {
            "message": "Chat history cleared successfully",
            "sessions_deleted": session_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload", response_model=schemas.Document)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(None),
    description: str = Form(None),
    folder_id: int = Form(None),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    """Upload and process a document with optional folder assignment"""
    print(f"📤 Upload received: file={file.filename}, folder_id={folder_id}, title={title}")
    try:
        # Validate folder if specified
        if folder_id:
            from ..models import folder as folder_model
            folder = db.query(folder_model.Folder).filter(
                folder_model.Folder.id == folder_id,
                folder_model.Folder.user_id == current_user.id
            ).first()
            if not folder:
                raise HTTPException(status_code=404, detail="Folder not found")
        
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
            folder_id=folder_id,
            is_processed=False
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Process document
        processor = DocumentProcessor()
        chunks = processor.process_document(file_path)
        
        # Add to vector store with user context and folder metadata
        user_display_name = current_user.full_name or current_user.username
        rag_service = RAGService(user_id=current_user.id, user_name=user_display_name)
        rag_service.add_documents(chunks, folder_id=folder_id)
        
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

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    """Delete a document and its embeddings"""
    try:
        # Get the document
        document = db.query(document_model.Document).filter(
            document_model.Document.id == document_id,
            document_model.Document.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete the file
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete from database (cascades to chunks)
        db.delete(document)
        db.commit()
        
        # Check if this was the last document - if so, clear vector store
        remaining_docs = db.query(document_model.Document).filter(
            document_model.Document.user_id == current_user.id
        ).count()
        
        if remaining_docs == 0:
            print(f"🗑️ Last document deleted, clearing vector store for user {current_user.id}")
            try:
                user_display_name = current_user.full_name or current_user.username
                rag_service = RAGService(user_id=current_user.id, user_name=user_display_name)
                rag_service.clear_vector_store()
            except Exception as e:
                print(f"⚠️ Error clearing vector store: {e}")
        
        return {
            "message": "Document deleted successfully",
            "document_id": document_id,
            "vector_store_cleared": remaining_docs == 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/{document_id}/reprocess")
async def reprocess_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    """Reprocess and reindex a document with current settings"""
    try:
        # Get the document
        document = db.query(document_model.Document).filter(
            document_model.Document.id == document_id,
            document_model.Document.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not os.path.exists(document.file_path):
            raise HTTPException(status_code=404, detail="Document file not found")
        
        # Reprocess the document
        processor = DocumentProcessor()
        chunks = processor.process_document(document.file_path)
        
        # Clear old embeddings and add new ones
        user_display_name = current_user.full_name or current_user.username
        rag_service = RAGService(user_id=current_user.id, user_name=user_display_name)
        
        # Note: This adds to existing embeddings. For a clean reindex, 
        # you might want to clear the vector store first
        rag_service.add_documents(chunks)
        
        # Update document status
        document.is_processed = True
        db.commit()
        
        return {
            "message": "Document reprocessed successfully",
            "document_id": document_id,
            "chunks": len(chunks)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/reindex-all")
async def reindex_all_documents(
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    """Clear vector store and reindex all documents with current settings"""
    try:
        # Clear the vector store (always clear cache, even if no documents)
        user_display_name = current_user.full_name or current_user.username
        rag_service = RAGService(user_id=current_user.id, user_name=user_display_name)
        
        try:
            rag_service.clear_vector_store()
            print(f"✅ Cleared vector store for user {current_user.id}")
        except Exception as e:
            print(f"⚠️ Error clearing vector store (may not exist): {e}")
            # Continue anyway - vector store might not exist yet
        
        # Get all documents
        documents = db.query(document_model.Document).filter(
            document_model.Document.user_id == current_user.id
        ).all()
        
        if not documents:
            return {
                "message": "Vector store cleared. No documents to reindex.",
                "documents_reindexed": 0,
                "total_documents": 0,
                "total_chunks": 0
            }
        
        # Reprocess each document
        processor = DocumentProcessor()
        total_chunks = 0
        reindexed_count = 0
        
        for document in documents:
            if os.path.exists(document.file_path):
                try:
                    chunks = processor.process_document(document.file_path)
                    rag_service.add_documents(chunks)
                    total_chunks += len(chunks)
                    reindexed_count += 1
                    document.is_processed = True
                except Exception as e:
                    print(f"❌ Error reprocessing {document.title}: {e}")
                    document.is_processed = False
            else:
                print(f"⚠️ File not found for document: {document.title}")
                document.is_processed = False
        
        db.commit()
        
        return {
            "message": "All documents reindexed successfully" if reindexed_count > 0 else "Vector store cleared",
            "documents_reindexed": reindexed_count,
            "total_documents": len(documents),
            "total_chunks": total_chunks
        }
        
    except Exception as e:
        # Even if there's an error, try to return a meaningful response
        print(f"❌ Reindex error: {e}")
        return {
            "message": f"Reindex completed with errors: {str(e)}",
            "documents_reindexed": 0,
            "total_documents": 0,
            "total_chunks": 0
        }
