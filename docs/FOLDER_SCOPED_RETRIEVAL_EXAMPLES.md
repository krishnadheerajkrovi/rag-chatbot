# Folder-Scoped Retrieval Examples

## How It Works

Documents uploaded to a folder have `folder_id` added to their metadata in the vector store. When querying, you can filter retrieval to only documents in that folder.

## Example Scenarios

### Scenario 1: Work vs Personal Documents

```
User has:
├── Folder: "Work" (id=1)
│   ├── tesla_requirements.pdf
│   └── project_alpha_design.pdf
└── Folder: "Personal" (id=2)
    ├── tax_documents.pdf
    └── medical_records.pdf
```

**Query in Work folder:**
```bash
curl -X POST http://localhost:8000/chat/query \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "What are the project requirements?",
    "folder_id": 1
  }'
```

**Result:** Only searches `tesla_requirements.pdf` and `project_alpha_design.pdf`

**Query without folder (global search):**
```bash
curl -X POST http://localhost:8000/chat/query \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "What are the project requirements?"
  }'
```

**Result:** Searches ALL documents (work + personal)

### Scenario 2: Chat Inherits Folder Context

```python
# Create chat in "Work" folder
POST /chat/sessions
{
  "title": "Project Discussion",
  "folder_id": 1
}

# Query in this chat (no folder_id needed)
POST /chat/query
{
  "query": "What's the timeline?",
  "session_id": "abc-123"
}
# Automatically uses folder_id=1 from the chat session
```

### Scenario 3: Override Chat's Folder

```python
# Chat is in "Work" folder (id=1)
# But query a different folder
POST /chat/query
{
  "query": "What are my tax deductions?",
  "session_id": "abc-123",
  "folder_id": 2  # Override to search "Personal" folder
}
```

## Vector Store Metadata

### Document Without Folder
```python
{
  "page_content": "Tesla was founded in 2003...",
  "metadata": {
    "source": "tesla.pdf",
    "chunk_id": 0,
    # No folder_id
  }
}
```

### Document With Folder
```python
{
  "page_content": "Project Alpha requirements...",
  "metadata": {
    "source": "requirements.pdf",
    "chunk_id": 0,
    "folder_id": 1  # ← Added during upload
  }
}
```

## Retrieval Filtering

### Without Folder Filter (Default)
```python
retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 8,
        "fetch_k": 20
    }
)
# Returns: All documents matching the query
```

### With Folder Filter
```python
retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 8,
        "fetch_k": 20,
        "filter": {"folder_id": 1}  # ← Only folder 1
    }
)
# Returns: Only documents from folder 1
```

## API Usage

### 1. Create Folder
```bash
curl -X POST http://localhost:8000/folders/ \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Work Projects",
    "description": "All work-related documents"
  }'
# Response: {"id": 1, "name": "Work Projects", ...}
```

### 2. Upload Document to Folder
```bash
curl -X POST http://localhost:8000/chat/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@requirements.pdf" \
  -F "folder_id=1"
```

### 3. Create Chat in Folder
```bash
curl -X POST http://localhost:8000/chat/sessions \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Requirements Discussion",
    "folder_id": 1
  }'
```

### 4. Query with Folder Scope
```bash
# Option A: Explicit folder_id
curl -X POST http://localhost:8000/chat/query \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "What are the requirements?",
    "folder_id": 1
  }'

# Option B: Use chat's folder (automatic)
curl -X POST http://localhost:8000/chat/query \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "What are the requirements?",
    "session_id": "abc-123"
  }'
# Uses folder_id from the chat session
```

## Benefits

✅ **Context Isolation**: Work documents don't interfere with personal queries
✅ **Improved Relevance**: Smaller search space = more relevant results
✅ **Privacy**: Separate sensitive documents by folder
✅ **Flexibility**: Can still do global search when needed
✅ **Performance**: Filtering reduces search space

## Implementation Details

### RAG Service Changes

```python
class RAGService:
    def init_vector_store(self, folder_id: int = None):
        search_kwargs = {"k": 8, "fetch_k": 20}
        
        if folder_id is not None:
            search_kwargs["filter"] = {"folder_id": folder_id}
        
        self.retriever = self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs=search_kwargs
        )
    
    def add_documents(self, documents, folder_id: int = None):
        metadatas = [doc["metadata"] for doc in documents]
        
        if folder_id is not None:
            for metadata in metadatas:
                metadata["folder_id"] = folder_id
        
        self.vector_store.add_texts(texts, metadatas)
    
    def query(self, question, chat_history, folder_id: int = None):
        if folder_id is not None:
            self.init_vector_store(folder_id=folder_id)
        
        return self.rag_chain.invoke(...)
```

### Chat API Changes

```python
@router.post("/query")
async def chat_query(query: ChatQuery, ...):
    # Determine folder scope
    folder_id = query.folder_id
    if folder_id is None and session.folder_id:
        folder_id = session.folder_id
    
    # Query with folder scope
    result = rag_service.query(
        query.query,
        chat_history,
        folder_id=folder_id
    )
```

## Testing

### Test 1: Upload to Different Folders
```bash
# Upload work doc
curl -X POST .../upload -F "file=@work.pdf" -F "folder_id=1"

# Upload personal doc
curl -X POST .../upload -F "file=@personal.pdf" -F "folder_id=2"
```

### Test 2: Query Each Folder
```bash
# Query work folder
curl -X POST .../query -d '{"query": "work content?", "folder_id": 1}'
# Should only find work.pdf content

# Query personal folder
curl -X POST .../query -d '{"query": "personal content?", "folder_id": 2}'
# Should only find personal.pdf content
```

### Test 3: Global Query
```bash
# Query without folder
curl -X POST .../query -d '{"query": "any content?"}'
# Should find content from both folders
```

## Troubleshooting

**Issue**: Folder filter not working
- Check metadata in vector store: `metadata["folder_id"]` must match
- Verify Chroma version supports metadata filtering
- Check filter syntax: `{"folder_id": 1}` not `{"folder_id": "1"}`

**Issue**: Can't find documents
- Ensure documents were uploaded with `folder_id`
- Check if query is using correct `folder_id`
- Verify folder exists and user has access

**Issue**: Getting documents from wrong folder
- Check if `folder_id` is being passed correctly
- Verify RAG chain is being reinitialized with new filter
- Check session's `folder_id` if using automatic scoping
