from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Document Schemas
class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: int
    file_path: str
    file_type: str
    file_size: int
    is_processed: bool
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Chat Schemas
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatQuery(BaseModel):
    query: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    session_id: str
    sources: Optional[List[dict]] = []

class ChatHistory(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    created_at: datetime

    class Config:
        from_attributes = True
