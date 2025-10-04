import streamlit as st
import requests
import os
from streamlit_cookies_manager import EncryptedCookieManager

API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")

st.set_page_config(page_title="RAG Chatbot", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# Cookie manager for persistent login
cookies = EncryptedCookieManager(prefix="rag_chatbot_", password=os.getenv("COOKIE_PASSWORD", "change-this-secret-key"))
if not cookies.ready():
    st.stop()

# Session state with cookie persistence
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.logged_out = False
    
    # Try to restore from cookies only if not logged out and cookies exist
    if not st.session_state.get('logged_out', False):
        if 'token' in cookies and cookies['token'] and cookies['token'].strip():
            st.session_state.token = cookies['token']
            st.session_state.user = cookies.get('user', 'User')
    
    for key, default in [
        ('token', None), ('user', None), ('folders', []), ('chats', []), ('documents', []),
        ('current_folder_id', None), ('current_chat_id', None), ('messages', [])
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}

def load_data():
    if not st.session_state.token:
        return
    try:
        r = requests.get(f"{API_BASE_URL}/folders/", headers=get_headers())
        if r.status_code == 200:
            st.session_state.folders = r.json()
        else:
            st.sidebar.error(f"Folders API error: {r.status_code}")
            st.session_state.folders = []
        
        r = requests.get(f"{API_BASE_URL}/chat/sessions", headers=get_headers())
        st.session_state.chats = r.json() if r.status_code == 200 else []
        
        r = requests.get(f"{API_BASE_URL}/chat/documents", headers=get_headers())
        st.session_state.documents = r.json() if r.status_code == 200 else []
    except Exception as e:
        st.sidebar.error(f"Load error: {str(e)}")

def login_page():
    st.title("🤖 RAG Chatbot")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                try:
                    r = requests.post(f"{API_BASE_URL}/auth/token", data={"username": username, "password": password})
                    if r.status_code == 200:
                        st.session_state.token = r.json()["access_token"]
                        st.session_state.user = username
                        # Save to cookies
                        cookies['token'] = st.session_state.token
                        cookies['user'] = username
                        cookies.save()
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                except Exception as e:
                    st.error(str(e))
    
    with tab2:
        with st.form("register"):
            email = st.text_input("Email")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            full_name = st.text_input("Full Name")
            if st.form_submit_button("Register"):
                try:
                    r = requests.post(f"{API_BASE_URL}/auth/register", json={
                        "email": email, "username": username, "password": password, "full_name": full_name
                    })
                    if r.status_code == 200:
                        st.success("Registered! Please login.")
                    else:
                        st.error(r.json().get('detail', 'Registration failed'))
                except Exception as e:
                    st.error(str(e))

def chat_page():
    if st.session_state.token:
        load_data()
    
    # Top bar with menu
    col1, col2 = st.columns([6, 1])
    with col2:
        with st.popover("⋮", use_container_width=True):
            st.write(f"👤 **{st.session_state.user}**")
            if st.button("🚪 Logout", use_container_width=True):
                # Failproof logout - clear everything
                try:
                    # Clear cookies
                    for key in list(cookies.keys()):
                        del cookies[key]
                    cookies.save()
                except:
                    pass
                
                # Set logout flag before clearing session
                st.session_state.logged_out = True
                
                # Clear session state
                st.session_state.token = None
                st.session_state.user = None
                st.session_state.folders = []
                st.session_state.chats = []
                st.session_state.documents = []
                st.session_state.messages = []
                st.session_state.current_chat_id = None
                st.session_state.current_folder_id = None
                
                st.rerun()
    
    # Sidebar
    with st.sidebar:
        # New Chat button at top
        if st.button("➕ New chat", key="add_chat_btn", use_container_width=True):
            try:
                r = requests.post(f"{API_BASE_URL}/chat/sessions", 
                                json={"title": "New Chat"}, 
                                headers=get_headers())
                if r.status_code == 200:
                    st.session_state.current_chat_id = r.json()['session_id']
                    st.session_state.current_folder_id = None
                    st.session_state.messages = []
                    st.session_state.loaded_chat_id = st.session_state.current_chat_id
                    load_data()
                    st.rerun()
            except Exception as e:
                st.error(str(e))
        
        st.divider()
        # New Folder Dialog
        if st.session_state.get('show_new_folder'):
            with st.form("new_folder"):
                name = st.text_input("Folder Name")
                if st.form_submit_button("Create"):
                    if name:
                        try:
                            r = requests.post(f"{API_BASE_URL}/folders/", json={"name": name}, headers=get_headers())
                            if r.status_code == 200:
                                st.success(f"Created folder: {name}")
                                st.session_state.show_new_folder = False
                                st.rerun()
                            else:
                                st.error(f"Failed: {r.json().get('detail', 'Unknown error')}")
                        except Exception as e:
                            st.error(str(e))
                    else:
                        st.warning("Please enter a folder name")
        
        # Projects Section
        st.caption("Projects")
        
        # New project button
        if st.button("📁 New project", key="add_folder_btn", use_container_width=True):
            st.session_state.show_new_folder = True
        
        # List folders
        for folder in st.session_state.folders:
            is_current_folder = st.session_state.current_folder_id == folder['id']
            
            col1, col2 = st.columns([5, 1])
            with col1:
                folder_label = f"📁 {folder['name']}"
                button_type = "primary" if is_current_folder else "secondary"
                if st.button(folder_label, key=f"folder_btn_{folder['id']}", type=button_type, use_container_width=True):
                    if is_current_folder:
                        st.session_state.current_folder_id = None
                    else:
                        st.session_state.current_folder_id = folder['id']
                    st.rerun()
            with col2:
                with st.popover("⋮", use_container_width=True):
                    if st.button("➕ New chat", key=f"nc{folder['id']}", use_container_width=True):
                        try:
                            r = requests.post(f"{API_BASE_URL}/chat/sessions", 
                                            json={"title": "New Chat", "folder_id": folder['id']}, 
                                            headers=get_headers())
                            if r.status_code == 200:
                                st.session_state.current_chat_id = r.json()['session_id']
                                st.session_state.current_folder_id = folder['id']
                                st.session_state.messages = []
                                st.session_state.loaded_chat_id = st.session_state.current_chat_id
                                load_data()
                                st.rerun()
                        except Exception as e:
                            st.error(str(e))
                    if st.button("📦 Archive", key=f"af{folder['id']}", use_container_width=True):
                        requests.post(f"{API_BASE_URL}/folders/{folder['id']}/archive", headers=get_headers())
                        load_data()
                        st.rerun()
                    if st.button("🗑️ Delete", key=f"df{folder['id']}", use_container_width=True):
                        requests.delete(f"{API_BASE_URL}/folders/{folder['id']}", headers=get_headers())
                        load_data()
                        st.rerun()
            
            # Show chats in expanded folder
            if is_current_folder:
                folder_chats = [c for c in st.session_state.chats if c.get('folder_id') == folder['id']]
                for chat in folder_chats:
                    is_selected = st.session_state.current_chat_id == chat['session_id']
                    
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        chat_label = f"  💬 {chat.get('title') or 'Untitled'}"
                        if st.button(chat_label, key=f"c{chat['id']}", type="primary" if is_selected else "secondary", use_container_width=True):
                            st.session_state.current_chat_id = chat['session_id']
                            st.session_state.current_folder_id = folder['id']
                            try:
                                r = requests.get(f"{API_BASE_URL}/chat/history/{chat['session_id']}", headers=get_headers())
                                if r.status_code == 200:
                                    history = r.json()
                                    st.session_state.messages = [{"role": msg["role"], "content": msg["content"]} for msg in history.get("messages", [])]
                                    st.session_state.loaded_chat_id = chat['session_id']
                            except:
                                st.session_state.messages = []
                            st.rerun()
                    with col2:
                        with st.popover("⋮", use_container_width=True):
                            if st.button("✏️ Rename", key=f"rename{chat['id']}", use_container_width=True):
                                st.session_state.show_rename_chat = chat['id']
                                st.rerun()
                            if st.button("🗑️ Delete", key=f"delchat{chat['id']}", use_container_width=True):
                                requests.delete(f"{API_BASE_URL}/chat/sessions/{chat['session_id']}", headers=get_headers())
                                load_data()
                                st.rerun()
        
        st.divider()
        
        # Chats Section
        st.caption("Chats")
        
        # List chats without folders
        no_folder_chats = [c for c in st.session_state.chats if not c.get('folder_id')]
        for chat in no_folder_chats:
            is_selected = st.session_state.current_chat_id == chat['session_id']
            
            col1, col2 = st.columns([5, 1])
            with col1:
                chat_label = f"💬 {chat.get('title') or 'Untitled'}"
                if st.button(chat_label, key=f"chat_{chat['id']}", type="primary" if is_selected else "secondary", use_container_width=True):
                    st.session_state.current_chat_id = chat['session_id']
                    st.session_state.current_folder_id = None
                    try:
                        r = requests.get(f"{API_BASE_URL}/chat/history/{chat['session_id']}", headers=get_headers())
                        if r.status_code == 200:
                            history = r.json()
                            st.session_state.messages = [{"role": msg["role"], "content": msg["content"]} for msg in history.get("messages", [])]
                            st.session_state.loaded_chat_id = chat['session_id']
                    except:
                        st.session_state.messages = []
                    st.rerun()
            with col2:
                with st.popover("⋮", use_container_width=True):
                    if st.button("✏️ Rename", key=f"rename_nf{chat['id']}", use_container_width=True):
                        st.session_state.show_rename_chat = chat['id']
                        st.rerun()
                    if st.button("🗑️ Delete", key=f"del_nf{chat['id']}", use_container_width=True):
                        requests.delete(f"{API_BASE_URL}/chat/sessions/{chat['session_id']}", headers=get_headers())
                        load_data()
                        st.rerun()
        

        # View Archived Folders
        if st.button("📦 View Archived", use_container_width=True):
            st.session_state.show_archived = not st.session_state.get('show_archived', False)
            if st.session_state.show_archived:
                try:
                    r = requests.get(f"{API_BASE_URL}/folders/?include_archived=true", headers=get_headers())
                    if r.status_code == 200:
                        archived = [f for f in r.json() if f.get('is_archived')]
                        st.session_state.archived_folders = archived
                except:
                    st.session_state.archived_folders = []
            st.rerun()
        
        if st.session_state.get('show_archived'):
            st.caption("📦 Archived Folders:")
            for folder in st.session_state.get('archived_folders', []):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text(f"📁 {folder['name']}")
                with col2:
                    if st.button("↩️", key=f"unarch{folder['id']}", help="Unarchive"):
                        requests.post(f"{API_BASE_URL}/folders/{folder['id']}/unarchive", headers=get_headers())
                        st.session_state.show_archived = False
                        load_data()
                        st.rerun()
        
        st.divider()
        
        # Upload
        st.subheader("📤 Upload")
        uploaded_file = st.file_uploader("Document", type=["pdf", "txt", "md", "docx"])
        if uploaded_file:
            folder_opts = [None] + [f['id'] for f in st.session_state.folders]
            folder_names = ["No Folder"] + [f['name'] for f in st.session_state.folders]
            folder_id = st.selectbox("To Folder", folder_opts, format_func=lambda x: folder_names[folder_opts.index(x)])
            if st.button("Upload"):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    data = {"folder_id": folder_id} if folder_id else {}
                    r = requests.post(f"{API_BASE_URL}/chat/upload", files=files, data=data, headers=get_headers())
                    if r.status_code == 200:
                        st.success("Uploaded!")
                    else:
                        st.error("Upload failed")
                except Exception as e:
                    st.error(str(e))
    
    # Main chat area
    current_chat = next((c for c in st.session_state.chats if c['session_id'] == st.session_state.current_chat_id), None)
    
    # Load chat history if we have a chat but no messages loaded yet
    if current_chat and not st.session_state.get('loaded_chat_id') == st.session_state.current_chat_id:
        try:
            r = requests.get(f"{API_BASE_URL}/chat/history/{current_chat['session_id']}", headers=get_headers())
            if r.status_code == 200:
                history = r.json()
                st.session_state.messages = [{"role": msg["role"], "content": msg["content"]} for msg in history.get("messages", [])]
                st.session_state.loaded_chat_id = st.session_state.current_chat_id
        except:
            st.session_state.messages = []
    
    # Header with attachment button
    col1, col2 = st.columns([5, 1])
    with col1:
        if current_chat:
            st.markdown(f"### {current_chat.get('title') or 'Untitled Chat'}")
            if current_chat.get('folder_id'):
                folder = next((f for f in st.session_state.folders if f['id'] == current_chat['folder_id']), None)
                if folder:
                    st.caption(f"📂 {folder['name']}")
            else:
                st.caption("💬 General chat")
        else:
            st.markdown("### Start a new conversation")
            st.caption("Create or select a chat from the sidebar")
    
    with col2:
        if st.button("📎 Attach", use_container_width=True):
            st.session_state.show_upload_dialog = not st.session_state.get('show_upload_dialog', False)
    
    # Upload dialog in chat
    if st.session_state.get('show_upload_dialog'):
        with st.expander("📎 Upload Document", expanded=True):
            uploaded_file = st.file_uploader("Choose file", type=["pdf", "txt", "md", "docx"], key="chat_upload")
            if uploaded_file:
                # Auto-detect folder from current chat
                folder_id = current_chat.get('folder_id') if current_chat else None
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Upload to Current Folder" if folder_id else "Upload (No Folder)", use_container_width=True):
                        try:
                            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                            data = {}
                            if folder_id:
                                data["folder_id"] = str(folder_id)
                            r = requests.post(f"{API_BASE_URL}/chat/upload", files=files, data=data, headers=get_headers())
                            if r.status_code == 200:
                                st.success("✅ Uploaded!")
                                st.session_state.show_upload_dialog = False
                                load_data()
                                st.rerun()
                        except Exception as e:
                            st.error(str(e))
                with col2:
                    if st.button("Cancel", use_container_width=True):
                        st.session_state.show_upload_dialog = False
                        st.rerun()
    
    st.divider()
    
    # Messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # Input - only show if we have a chat or can create one
    if prompt := st.chat_input("Ask anything..." if st.session_state.current_chat_id else "Create a chat to start..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    r = requests.post(f"{API_BASE_URL}/chat/query", json={
                        "query": prompt,
                        "session_id": st.session_state.current_chat_id,
                        "folder_id": st.session_state.current_folder_id
                    }, headers=get_headers())
                    if r.status_code == 200:
                        answer = r.json()["answer"]
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        st.write(answer)
                        st.session_state.current_chat_id = r.json()["session_id"]
                    else:
                        st.error("Query failed")
                except Exception as e:
                    st.error(str(e))

# Main
if not st.session_state.token:
    login_page()
else:
    chat_page()
