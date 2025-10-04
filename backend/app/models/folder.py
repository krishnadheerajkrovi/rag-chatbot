"""
Folder model for organizing chats and documents
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.base import Base


class Folder(Base):
    """Folder for organizing chats and documents"""
    __tablename__ = "folders"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_folder_id = Column(Integer, ForeignKey("folders.id", ondelete="CASCADE"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_archived = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="folders")
    chats = relationship("ChatSession", back_populates="folder", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="folder", cascade="all, delete-orphan")
    
    # Self-referential for nested folders
    subfolders = relationship("Folder", backref="parent_folder", remote_side=[id])
    
    def __repr__(self):
        return f"<Folder(id={self.id}, name='{self.name}', user_id={self.user_id})>"
