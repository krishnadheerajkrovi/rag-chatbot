# Folders and Chats Feature

## Overview

Hierarchical organization system for chats and documents with folder-scoped document retrieval.

## Architecture

```
User
 ├── Folder 1 (e.g., "Work")
 │   ├── Chat 1.1 (e.g., "Project Alpha")
 │   │   └── Messages
 │   ├── Chat 1.2 (e.g., "Team Meeting Notes")
 │   │   └── Messages
 │   └── Documents (PDFs, TXT files)
 │
 ├── Folder 2 (e.g., "Personal")
 │   ├── Subfolder 2.1 (e.g., "Finance")
 │   │   ├── Chat 2.1.1
 │   │   └── Documents
 │   └── Chat 2.1
 │
 └── Root Chats (no folder)
```

## Database Schema

### New Tables

**folders**
- `id`: Primary key
- `name`: Folder name
- `description`: Optional description
- `user_id`: Owner
- `parent_folder_id`: For nested folders (self-referential)
- `is_archived`: Soft delete flag
- `created_at`, `updated_at`: Timestamps

### Updated Tables

**chat_sessions**
- Added: `folder_id` (nullable, SET NULL on folder delete)

**documents**
- Added: `folder_id` (nullable, SET NULL on folder delete)

## API Endpoints

### Folder Management

```
POST   /folders/                    - Create folder
GET    /folders/                    - List folders (with parent_id filter)
GET    /folders/{id}                - Get folder details
PUT    /folders/{id}                - Update folder
DELETE /folders/{id}                - Delete folder (cascades to chats/docs)
POST   /folders/{id}/archive        - Archive folder
POST   /folders/{id}/unarchive      - Unarchive folder
```

### Chat Management (Updated)

```
POST   /chat/sessions               - Create chat (with optional folder_id)
GET    /chat/sessions               - List chats (filter by folder_id)
PUT    /chat/sessions/{id}          - Update chat (move to folder)
DELETE /chat/sessions/{id}          - Delete chat
```

### Document Upload (Updated)

```
POST   /chat/upload                 - Upload document (with optional folder_id)
```

## Features

### 1. Folder-Scoped Document Retrieval

When querying in a chat that belongs to a folder:
- **Default**: Retrieves from ALL user documents
- **Folder-scoped**: Retrieves ONLY from documents in that folder

```python
# In RAG service
if folder_id:
    # Filter vector store by folder metadata
    retriever = vector_store.as_retriever(
        search_kwargs={
            "filter": {"folder_id": folder_id}
        }
    )
```

### 2. Chat History Isolation

- Each chat maintains its own conversation history
- Moving a chat to a different folder preserves its history
- Deleting a folder deletes all its chats and messages

### 3. Nested Folders

- Folders can have subfolders
- Unlimited nesting depth
- Parent folder deletion cascades to children

### 4. Soft Delete (Archive)

- Folders can be archived instead of deleted
- Archived folders hidden by default
- Can be unarchived later

## Usage Examples

### Create a Folder

```bash
curl -X POST http://localhost:8000/folders/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Work Projects",
    "description": "All work-related documents and chats"
  }'
```

### Create a Chat in a Folder

```bash
curl -X POST http://localhost:8000/chat/sessions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Project Alpha Discussion",
    "folder_id": 1
  }'
```

### Upload Document to Folder

```bash
curl -X POST http://localhost:8000/chat/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@document.pdf" \
  -F "folder_id=1"
```

### Query with Folder Scope

```bash
curl -X POST http://localhost:8000/chat/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the project requirements?",
    "session_id": "abc-123",
    "folder_id": 1
  }'
```

## Frontend Implementation

### Sidebar Structure

```
📁 Work Projects
  💬 Project Alpha
  💬 Team Meeting Notes
  📄 requirements.pdf
  📄 design_doc.pdf

📁 Personal
  📁 Finance
    💬 Tax Questions
    📄 tax_forms.pdf
  💬 General Notes

💬 Untitled Chat 1 (root level)
💬 Untitled Chat 2 (root level)
```

### UI Components Needed

1. **Folder Tree** - Collapsible folder hierarchy
2. **Chat List** - Chats grouped by folder
3. **Context Menu** - Right-click for delete/rename/move
4. **Drag & Drop** - Move chats between folders
5. **Folder Selector** - When creating new chat/uploading doc

## Migration Steps

1. **Run migration**:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

2. **Existing data**:
   - All existing chats will have `folder_id = NULL` (root level)
   - All existing documents will have `folder_id = NULL`
   - Users can organize them later

3. **Backward compatibility**:
   - Chats without folders still work normally
   - Documents without folders are searchable across all chats

## Benefits

✅ **Organization**: Group related chats and documents
✅ **Context**: Folder-scoped retrieval for focused answers
✅ **Privacy**: Separate work/personal/project contexts
✅ **Scalability**: Handle hundreds of chats efficiently
✅ **Flexibility**: Optional feature - works with or without folders

## Next Steps

- [ ] Implement folder-scoped vector store filtering
- [ ] Add frontend folder tree component
- [ ] Implement drag-and-drop for reorganization
- [ ] Add folder sharing (future: multi-user folders)
- [ ] Add folder-level permissions
- [ ] Implement folder search/filter
