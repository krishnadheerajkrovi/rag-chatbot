import streamlit as st
from streamlit_option_menu import option_menu
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        color: #1a1a1a;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        color: #0d47a1;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
        color: #1b5e20;
    }
    .chat-message strong {
        color: inherit;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

def is_authenticated():
    return st.session_state.token is not None

def get_headers():
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

def login_page():
    st.markdown('<div class="main-header">🤖 RAG Chatbot</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/auth/token",
                        data={"username": username, "password": password}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.token = data["access_token"]
                        st.session_state.user = username
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tab2:
        st.subheader("Register")
        with st.form("register_form"):
            reg_username = st.text_input("Username", key="reg_username")
            reg_email = st.text_input("Email", key="reg_email")
            reg_full_name = st.text_input("Full Name", key="reg_full_name")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            reg_submit = st.form_submit_button("Register")
            
            if reg_submit:
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/auth/register",
                        json={
                            "username": reg_username,
                            "email": reg_email,
                            "full_name": reg_full_name,
                            "password": reg_password
                        }
                    )
                    if response.status_code == 200:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error(f"Registration failed: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

def chat_page():
    st.markdown('<div class="main-header">💬 Chat with Your Documents</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.subheader(f"Welcome, {st.session_state.user}!")
        
        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.session_id = None
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        
        # Document upload
        st.subheader("📄 Upload Documents")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "txt", "md", "docx"]
        )
        
        if uploaded_file:
            title = st.text_input("Document Title", value=uploaded_file.name)
            description = st.text_area("Description (optional)")
            
            if st.button("Upload & Process"):
                with st.spinner("Processing document..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                        data = {"title": title, "description": description}
                        
                        response = requests.post(
                            f"{API_BASE_URL}/chat/upload",
                            files=files,
                            data=data,
                            headers=get_headers()
                        )
                        
                        if response.status_code == 200:
                            st.success("Document uploaded and processed successfully!")
                        else:
                            st.error(f"Upload failed: {response.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        st.divider()
        
        # View documents
        if st.button("View My Documents"):
            try:
                response = requests.get(
                    f"{API_BASE_URL}/chat/documents",
                    headers=get_headers()
                )
                if response.status_code == 200:
                    docs = response.json()
                    if docs:
                        st.subheader("Your Documents")
                        for doc in docs:
                            st.write(f"📄 {doc['title']}")
                            st.caption(f"Type: {doc['file_type']} | Size: {doc['file_size']} bytes")
                    else:
                        st.info("No documents uploaded yet")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Main chat area
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {content}</div>', 
                          unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message"><strong>Assistant:</strong> {content}</div>', 
                          unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("Ask me anything about your documents...")
    
    if user_input:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Send query to API
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/chat/query",
                    json={
                        "query": user_input,
                        "session_id": st.session_state.session_id
                    },
                    headers=get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.session_id = data["session_id"]
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": data["answer"]
                    })
                    st.rerun()
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

def main():
    if not is_authenticated():
        login_page()
    else:
        chat_page()

if __name__ == "__main__":
    main()
