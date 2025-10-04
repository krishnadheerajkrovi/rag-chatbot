"""
API endpoints for folder management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..db.base import get_db
from ..models import user as user_model
from ..models import folder as folder_model
from ..models import schemas
from ..core import security

router = APIRouter()


@router.post("/", response_model=schemas.Folder)
async def create_folder(
    folder: schemas.FolderCreate,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    """Create a new folder"""
    # Validate parent folder if specified
    if folder.parent_folder_id:
        parent = db.query(folder_model.Folder).filter(
            folder_model.Folder.id == folder.parent_folder_id,
            folder_model.Folder.user_id == current_user.id
        ).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent folder not found")
    
    db_folder = folder_model.Folder(
        name=folder.name,
        description=folder.description,
        parent_folder_id=folder.parent_folder_id,
        user_id=current_user.id
    )
    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)
    return db_folder


@router.get("/", response_model=List[schemas.Folder])
async def list_folders(
    include_archived: bool = False,
    parent_id: int = None,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    """List all folders for the current user"""
    print(f"📁 Listing folders for user_id={current_user.id}, username={current_user.username}")
    
    # Query folders, excluding archived by default
    query = db.query(folder_model.Folder).filter(
        folder_model.Folder.user_id == current_user.id
    )
    
    if not include_archived:
        query = query.filter(
            (folder_model.Folder.is_archived.is_(False)) | (folder_model.Folder.is_archived.is_(None))
        )
    
    folders = query.order_by(folder_model.Folder.created_at.desc()).all()
    
    print(f"📁 Found {len(folders)} folders (include_archived={include_archived}): {[f.name for f in folders]}")
    return folders


@router.get("/{folder_id}", response_model=schemas.Folder)
async def get_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    """Get a specific folder"""
    folder = db.query(folder_model.Folder).filter(
        folder_model.Folder.id == folder_id,
        folder_model.Folder.user_id == current_user.id
    ).first()
    
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    return folder


@router.put("/{folder_id}", response_model=schemas.Folder)
async def update_folder(
    folder_id: int,
    folder_update: schemas.FolderUpdate,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    """Update a folder"""
    folder = db.query(folder_model.Folder).filter(
        folder_model.Folder.id == folder_id,
        folder_model.Folder.user_id == current_user.id
    ).first()
    
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # Update fields
    if folder_update.name is not None:
        folder.name = folder_update.name
    if folder_update.description is not None:
        folder.description = folder_update.description
    if folder_update.parent_folder_id is not None:
        # Validate parent folder
        if folder_update.parent_folder_id != folder_id:  # Prevent self-reference
            parent = db.query(folder_model.Folder).filter(
                folder_model.Folder.id == folder_update.parent_folder_id,
                folder_model.Folder.user_id == current_user.id
            ).first()
            if not parent:
                raise HTTPException(status_code=404, detail="Parent folder not found")
            folder.parent_folder_id = folder_update.parent_folder_id
    
    db.commit()
    db.refresh(folder)
    return folder


@router.delete("/{folder_id}")
async def delete_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    """Delete a folder and all its contents"""
    folder = db.query(folder_model.Folder).filter(
        folder_model.Folder.id == folder_id,
        folder_model.Folder.user_id == current_user.id
    ).first()
    
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # Delete folder (cascades to chats and documents)
    db.delete(folder)
    db.commit()
    
    return {"message": "Folder deleted successfully", "folder_id": folder_id}


@router.post("/{folder_id}/archive")
async def archive_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    """Archive a folder (soft delete)"""
    folder = db.query(folder_model.Folder).filter(
        folder_model.Folder.id == folder_id,
        folder_model.Folder.user_id == current_user.id
    ).first()
    
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    folder.is_archived = True
    db.commit()
    
    return {"message": "Folder archived successfully", "folder_id": folder_id}


@router.post("/{folder_id}/unarchive")
async def unarchive_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    """Unarchive a folder"""
    folder = db.query(folder_model.Folder).filter(
        folder_model.Folder.id == folder_id,
        folder_model.Folder.user_id == current_user.id
    ).first()
    
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    folder.is_archived = False
    db.commit()
    
    return {"message": "Folder unarchived successfully", "folder_id": folder_id}
