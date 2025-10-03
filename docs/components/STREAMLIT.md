# Streamlit Component

## Overview

Streamlit is a Python framework for building interactive web applications. It's perfect for creating data apps and ML interfaces with minimal code.

## Key Features

- **Simple API**: Write apps in pure Python
- **Reactive**: Automatic UI updates
- **Built-in Widgets**: Forms, sliders, file uploaders, etc.
- **Session State**: Maintain state across reruns
- **Custom Components**: Extend with custom HTML/JS

## Architecture

```
┌─────────────────────────────────────┐
│      Streamlit Frontend             │
│  ┌──────────────────────────────┐   │
│  │   Login/Register Page        │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │   Chat Interface             │   │
│  │   - Message Display          │   │
│  │   - Input Box                │   │
│  │   - Document Upload          │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │   Sidebar                    │   │
│  │   - User Info                │   │
│  │   - Document List            │   │
│  │   - Settings                 │   │
│  └──────────────────────────────┘   │
└────────────┬────────────────────────┘
             │ HTTP Requests
             ▼
┌─────────────────────────────────────┐
│      FastAPI Backend                │
└─────────────────────────────────────┘
```

## Application Structure

```python
import streamlit as st
from streamlit_option_menu import option_menu
import requests

# Page config
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

def main():
    if not is_authenticated():
        login_page()
    else:
        chat_page()

if __name__ == "__main__":
    main()
```

## Core Components

### 1. Session State Management

```python
# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Access session state
token = st.session_state.token
st.session_state.messages.append({"role": "user", "content": "Hello"})

# Check authentication
def is_authenticated():
    return st.session_state.token is not None
```

### 2. Authentication UI

#### Login Form
```python
def login_page():
    st.markdown('<div class="main-header">🤖 RAG Chatbot</div>', 
                unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
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
```

#### Register Form
```python
with tab2:
    st.subheader("Register")
    with st.form("register_form"):
        reg_username = st.text_input("Username", key="reg_username")
        reg_email = st.text_input("Email", key="reg_email")
        reg_full_name = st.text_input("Full Name", key="reg_full_name")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_submit = st.form_submit_button("Register")
        
        if reg_submit:
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
                st.error(f"Registration failed: {response.json().get('detail')}")
```

### 3. Chat Interface

#### Message Display
```python
def display_messages():
    """Display chat messages"""
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            st.markdown(
                f'<div class="chat-message user-message">'
                f'<strong>You:</strong> {content}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="chat-message assistant-message">'
                f'<strong>Assistant:</strong> {content}</div>',
                unsafe_allow_html=True
            )
```

#### Chat Input
```python
def handle_chat_input():
    """Handle user input"""
    user_input = st.chat_input("Ask me anything about your documents...")
    
    if user_input:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Send to API
        with st.spinner("Thinking..."):
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
```

### 4. Sidebar Components

#### User Info
```python
with st.sidebar:
    st.subheader(f"Welcome, {st.session_state.user}!")
    
    if st.button("Logout"):
        st.session_state.token = None
        st.session_state.user = None
        st.session_state.session_id = None
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
```

#### Document Upload
```python
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
            files = {
                "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
            }
            data = {"title": title, "description": description}
            
            response = requests.post(
                f"{API_BASE_URL}/chat/upload",
                files=files,
                data=data,
                headers=get_headers()
            )
            
            if response.status_code == 200:
                st.success("Document uploaded successfully!")
            else:
                st.error(f"Upload failed: {response.json().get('detail')}")
```

#### Document List
```python
if st.button("View My Documents"):
    response = requests.get(
        f"{API_BASE_URL}/chat/documents",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        docs = response.json()
        if docs:
            st.subheader("Your Documents")
            for doc in docs:
                with st.expander(f"📄 {doc['title']}"):
                    st.write(f"**Type:** {doc['file_type']}")
                    st.write(f"**Size:** {doc['file_size']} bytes")
                    st.write(f"**Status:** {'Processed' if doc['is_processed'] else 'Processing'}")
                    if doc['description']:
                        st.write(f"**Description:** {doc['description']}")
        else:
            st.info("No documents uploaded yet")
```

### 5. Custom Styling

```python
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
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)
```

## Advanced Features

### 1. Caching

```python
@st.cache_data
def load_documents():
    """Cache document list"""
    response = requests.get(
        f"{API_BASE_URL}/chat/documents",
        headers=get_headers()
    )
    return response.json()

@st.cache_resource
def get_rag_service():
    """Cache RAG service instance"""
    return RAGService()
```

### 2. Progress Indicators

```python
# Spinner
with st.spinner("Processing..."):
    result = process_document()

# Progress bar
progress_bar = st.progress(0)
for i in range(100):
    progress_bar.progress(i + 1)
    time.sleep(0.01)

# Status
status = st.status("Processing document...")
status.update(label="Complete!", state="complete")
```

### 3. Columns Layout

```python
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.text_input("Search")

with col2:
    st.button("Filter")

with col3:
    st.button("Sort")
```

### 4. Tabs

```python
tab1, tab2, tab3 = st.tabs(["Chat", "Documents", "Settings"])

with tab1:
    display_chat()

with tab2:
    display_documents()

with tab3:
    display_settings()
```

### 5. Expanders

```python
with st.expander("Advanced Options"):
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    max_tokens = st.number_input("Max Tokens", 100, 4000, 2000)
```

## Widgets Reference

### Input Widgets
```python
# Text input
name = st.text_input("Name")

# Text area
description = st.text_area("Description")

# Number input
age = st.number_input("Age", min_value=0, max_value=120)

# Slider
temperature = st.slider("Temperature", 0.0, 1.0, 0.7)

# Select box
model = st.selectbox("Model", ["llama2", "mistral", "codellama"])

# Multi-select
tags = st.multiselect("Tags", ["python", "ai", "ml"])

# Checkbox
agree = st.checkbox("I agree")

# Radio
choice = st.radio("Choose", ["Option 1", "Option 2"])

# File uploader
file = st.file_uploader("Upload file")

# Date input
date = st.date_input("Date")

# Time input
time = st.time_input("Time")
```

### Display Widgets
```python
# Text
st.write("Hello, world!")
st.markdown("**Bold** text")
st.code("print('Hello')", language="python")

# Data
st.dataframe(df)
st.table(df)
st.json({"key": "value"})

# Media
st.image("image.png")
st.audio("audio.mp3")
st.video("video.mp4")

# Metrics
st.metric("Temperature", "70 °F", "1.2 °F")

# Charts
st.line_chart(data)
st.bar_chart(data)
st.area_chart(data)
```

### Layout Widgets
```python
# Columns
col1, col2 = st.columns(2)

# Tabs
tab1, tab2 = st.tabs(["Tab 1", "Tab 2"])

# Expander
with st.expander("Details"):
    st.write("Hidden content")

# Container
with st.container():
    st.write("Grouped content")

# Sidebar
with st.sidebar:
    st.write("Sidebar content")
```

## Best Practices

### 1. State Management
```python
# Initialize all state variables at the start
def init_session_state():
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.token = None
        st.session_state.messages = []
        st.session_state.session_id = None

init_session_state()
```

### 2. Error Handling
```python
try:
    response = requests.post(url, json=data)
    response.raise_for_status()
    result = response.json()
except requests.exceptions.RequestException as e:
    st.error(f"Request failed: {str(e)}")
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
```

### 3. Loading States
```python
with st.spinner("Loading..."):
    data = fetch_data()

if data:
    display_data(data)
else:
    st.info("No data available")
```

### 4. Form Validation
```python
with st.form("my_form"):
    username = st.text_input("Username")
    email = st.text_input("Email")
    submit = st.form_submit_button("Submit")
    
    if submit:
        if not username:
            st.error("Username is required")
        elif not email:
            st.error("Email is required")
        elif "@" not in email:
            st.error("Invalid email")
        else:
            st.success("Form submitted!")
```

### 5. Rerun Control
```python
# Rerun after state change
if st.button("Refresh"):
    st.rerun()

# Stop execution
if not is_authenticated():
    st.warning("Please login")
    st.stop()
```

## Performance Optimization

### 1. Use Caching
```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def expensive_computation():
    return compute_result()
```

### 2. Lazy Loading
```python
if st.button("Load Data"):
    data = load_large_dataset()
    st.session_state.data = data
```

### 3. Minimize Reruns
```python
# Use forms to batch inputs
with st.form("settings"):
    setting1 = st.slider("Setting 1")
    setting2 = st.slider("Setting 2")
    submit = st.form_submit_button("Apply")
    
    if submit:
        apply_settings(setting1, setting2)
```

## Deployment

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./app ./app

EXPOSE 8501

CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Environment Variables
```python
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
```

## Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Gallery](https://streamlit.io/gallery)
- [Streamlit Components](https://streamlit.io/components)
