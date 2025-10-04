# Frontend Implementation Plan for Folders & Chats

## Current State
- ❌ No folder management UI
- ❌ No chat list/management
- ❌ Single chat session only
- ✅ Document upload works
- ✅ Chat interface works

## Required Features

### 1. Sidebar Layout
```
┌─────────────────────────────┐
│ Welcome, User!       Logout │
├─────────────────────────────┤
│ [+ New Folder] [+ New Chat] │
├─────────────────────────────┤
│ 📁 Work Projects      [🗑️]  │
│   💬 Project Alpha    [🗑️]  │
│   💬 Team Meeting     [🗑️]  │
│   📄 doc1.pdf         [🗑️]  │
│                              │
│ 📁 Personal           [🗑️]  │
│   💬 Notes            [🗑️]  │
│   📄 doc2.pdf         [🗑️]  │
│                              │
│ 💬 Untitled Chat 1    [🗑️]  │
│ 💬 Untitled Chat 2    [🗑️]  │
├─────────────────────────────┤
│ 📤 Upload Document          │
│ 🗑️ Clear All History        │
└─────────────────────────────┘
```

### 2. Main Chat Area
```
┌─────────────────────────────────────┐
│ Current Chat: Project Alpha         │
│ Folder: Work Projects               │
├─────────────────────────────────────┤
│                                     │
│ [Chat messages display here]        │
│                                     │
├─────────────────────────────────────┤
│ [Type your message...]       [Send] │
└─────────────────────────────────────┘
```

## Implementation Steps

### Step 1: Add Session State
```python
if 'current_folder_id' not in st.session_state:
    st.session_state.current_folder_id = None
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None
if 'folders' not in st.session_state:
    st.session_state.folders = []
if 'chats' not in st.session_state:
    st.session_state.chats = []
```

### Step 2: Load Folders and Chats
```python
def load_folders():
    response = requests.get(f"{API_BASE_URL}/folders/", headers=get_headers())
    if response.status_code == 200:
        st.session_state.folders = response.json()

def load_chats():
    response = requests.get(f"{API_BASE_URL}/chat/sessions", headers=get_headers())
    if response.status_code == 200:
        st.session_state.chats = response.json()
```

### Step 3: Create Folder UI
```python
with st.sidebar:
    if st.button("➕ New Folder"):
        st.session_state.show_create_folder = True
    
    if st.session_state.get('show_create_folder'):
        with st.form("create_folder"):
            name = st.text_input("Folder Name")
            submit = st.form_submit_button("Create")
            if submit:
                # Create folder via API
                pass
```

### Step 4: Create Chat UI
```python
with st.sidebar:
    if st.button("➕ New Chat"):
        # Create new chat session
        # Optionally assign to current folder
        pass
```

### Step 5: Folder Tree
```python
for folder in st.session_state.folders:
    if st.button(f"📁 {folder['name']}", key=f"folder_{folder['id']}"):
        st.session_state.current_folder_id = folder['id']
        st.rerun()
    
    # Show chats in this folder
    folder_chats = [c for c in st.session_state.chats if c.get('folder_id') == folder['id']]
    for chat in folder_chats:
        if st.button(f"  💬 {chat['title'] or 'Untitled'}", key=f"chat_{chat['id']}"):
            st.session_state.current_chat_id = chat['session_id']
            st.rerun()
```

### Step 6: Upload to Folder
```python
uploaded_file = st.file_uploader("Upload Document")
folder_select = st.selectbox(
    "Assign to Folder",
    options=[None] + [f['id'] for f in st.session_state.folders],
    format_func=lambda x: "No Folder" if x is None else next(f['name'] for f in st.session_state.folders if f['id'] == x)
)

if st.button("Upload"):
    files = {"file": uploaded_file}
    data = {"folder_id": folder_select}
    response = requests.post(f"{API_BASE_URL}/chat/upload", files=files, data=data, headers=get_headers())
```

### Step 7: Query with Folder Scope
```python
if user_input:
    # Use current folder for scoped retrieval
    response = requests.post(
        f"{API_BASE_URL}/chat/query",
        json={
            "query": user_input,
            "session_id": st.session_state.current_chat_id,
            "folder_id": st.session_state.current_folder_id
        },
        headers=get_headers()
    )
```

## Quick Implementation (Minimal)

For a quick working version, add these to the existing frontend:

1. **Folder selector** in sidebar
2. **Chat selector** in sidebar  
3. **Pass folder_id** when uploading documents
4. **Pass folder_id** when querying

## Full Implementation (Complete)

Create a new `main.py` with:
- Proper folder tree component
- Chat list with folder grouping
- Drag & drop to move chats between folders
- Context menus for rename/delete
- Folder-scoped document upload
- Visual indication of current folder/chat

## Testing Checklist

- [ ] Create folder
- [ ] Create subfolder
- [ ] Create chat in folder
- [ ] Upload document to folder
- [ ] Query in folder (should only search folder docs)
- [ ] Query without folder (should search all docs)
- [ ] Delete chat
- [ ] Delete folder (should delete all contents)
- [ ] Move chat between folders
- [ ] Rename folder
- [ ] Archive folder

## API Endpoints Used

```
POST   /folders/                    - Create folder
GET    /folders/                    - List folders
DELETE /folders/{id}                - Delete folder
POST   /chat/sessions               - Create chat (with folder_id)
GET    /chat/sessions               - List chats
POST   /chat/query                  - Query (with folder_id)
POST   /chat/upload                 - Upload (with folder_id)
```

## Next Steps

1. Decide: Quick minimal update OR full rewrite?
2. If minimal: Add folder/chat selectors to existing UI
3. If full: Create new main.py with proper component structure
4. Test all features
5. Add polish (icons, colors, animations)
