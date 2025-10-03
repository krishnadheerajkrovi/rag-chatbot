# LangChain Component

## Overview

LangChain is a framework for developing applications powered by language models. It provides tools for document processing, embeddings, vector stores, and chain composition.

## Key Features

- **Document Loaders**: Load documents from various sources
- **Text Splitters**: Split documents into manageable chunks
- **Embeddings**: Convert text to vector representations
- **Vector Stores**: Store and retrieve embeddings efficiently
- **Chains**: Compose multiple LLM calls and operations

## Architecture in Our Application

```
┌──────────────────┐
│  User Query      │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────┐
│  History-Aware Retriever         │
│  (Reformulates query with        │
│   chat history context)          │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Vector Store Retrieval          │
│  (Chroma DB - MMR Search)        │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Document Chain                  │
│  (Combines retrieved docs        │
│   with query)                    │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  LLM Response                    │
│  (Ollama)                        │
└──────────────────────────────────┘
```

## Components Used

### 1. Document Loaders

```python
from langchain_community.document_loaders import (
    PyPDFLoader,      # PDF files
    TextLoader,       # Plain text
    Docx2txtLoader,   # Word documents
    UnstructuredMarkdownLoader  # Markdown
)

# Example usage
loader = PyPDFLoader("document.pdf")
documents = loader.load()
```

**Supported Formats**:
- PDF (.pdf)
- Text (.txt)
- Markdown (.md)
- Word (.docx)

### 2. Text Splitters

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # Characters per chunk
    chunk_overlap=200,      # Overlap between chunks
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)

chunks = splitter.split_documents(documents)
```

**Why Chunking?**
- LLMs have token limits
- Smaller chunks = more precise retrieval
- Overlap preserves context between chunks

### 3. Embeddings

```python
from langchain_community.embeddings import OllamaEmbeddings

embeddings = OllamaEmbeddings(
    model="llama2",
    base_url="http://ollama:11434"
)

# Convert text to vector
vector = embeddings.embed_query("What is RAG?")
```

**Purpose**:
- Convert text to numerical vectors
- Enable semantic similarity search
- Each vector represents meaning of text

### 4. Vector Store (Chroma)

```python
from langchain_community.vectorstores import Chroma

vector_store = Chroma(
    persist_directory="/app/vector_store",
    embedding_function=embeddings,
    collection_name="user_docs"
)

# Add documents
vector_store.add_texts(
    texts=["Document text..."],
    metadatas=[{"source": "doc.pdf"}]
)

# Search
results = vector_store.similarity_search("query", k=4)
```

**Features**:
- Persistent storage
- Fast similarity search
- Metadata filtering
- MMR (Maximum Marginal Relevance) search

### 5. Retriever

```python
retriever = vector_store.as_retriever(
    search_type="mmr",           # Maximum Marginal Relevance
    search_kwargs={
        "k": 4,                  # Return top 4 results
        "fetch_k": 10            # Fetch 10, then filter to 4
    }
)
```

**Search Types**:
- **similarity**: Pure similarity search
- **mmr**: Balances relevance and diversity
- **similarity_score_threshold**: Filter by score

### 6. History-Aware Retriever

```python
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

contextualize_prompt = ChatPromptTemplate.from_messages([
    ("system", "Reformulate the question based on chat history"),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

history_aware_retriever = create_history_aware_retriever(
    llm,
    retriever,
    contextualize_prompt
)
```

**Purpose**:
- Handles follow-up questions
- Reformulates queries with context
- Example: "What about its headquarters?" → "What about Tesla's headquarters?"

### 7. RAG Chain

```python
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer based on context: {context}"),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

rag_chain = create_retrieval_chain(
    history_aware_retriever,
    question_answer_chain
)

# Use the chain
result = rag_chain.invoke({
    "input": "What is RAG?",
    "chat_history": []
})
```

## RAG Pipeline Flow

### Step 1: Document Processing
```
Document → Loader → Text Splitter → Chunks
```

### Step 2: Embedding & Storage
```
Chunks → Embeddings → Vector Store
```

### Step 3: Query Processing
```
User Query + History → Contextualized Query
```

### Step 4: Retrieval
```
Contextualized Query → Vector Search → Relevant Chunks
```

### Step 5: Generation
```
Relevant Chunks + Query → LLM → Answer
```

## Prompt Templates

### Contextualization Prompt
```python
"""
Given a chat history and the latest user question which might 
reference context in the chat history, formulate a standalone 
question which can be understood without the chat history. 
Do NOT answer the question, just reformulate it if needed.
"""
```

### QA Prompt
```python
"""
You are a helpful AI assistant. Use the following pieces of 
context to answer the user's question. If you don't know the 
answer, just say that you don't know, don't try to make up 
an answer.

Context: {context}
"""
```

## Best Practices

### 1. Chunk Size Selection
- **Small chunks (500)**: Precise retrieval, may lose context
- **Medium chunks (1000)**: Good balance (recommended)
- **Large chunks (2000)**: More context, less precise

### 2. Overlap Configuration
- Use 10-20% of chunk_size as overlap
- Preserves context at chunk boundaries

### 3. Retrieval Parameters
- **k=4**: Good for most use cases
- **fetch_k=10**: Provides diversity with MMR
- Adjust based on document size and query complexity

### 4. Embedding Model
- Use same model for indexing and querying
- Larger models = better semantic understanding
- Trade-off: accuracy vs. speed

### 5. Vector Store Optimization
- Use persistent storage for production
- Separate collections per user
- Regular cleanup of old embeddings

## Advanced Features

### 1. Metadata Filtering
```python
retriever = vector_store.as_retriever(
    search_kwargs={
        "filter": {"source": "important_doc.pdf"},
        "k": 4
    }
)
```

### 2. Custom Prompts
```python
custom_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert in {domain}"),
    ("human", "{input}"),
])
```

### 3. Streaming Responses
```python
for chunk in rag_chain.stream({"input": query}):
    print(chunk, end="", flush=True)
```

## Performance Optimization

1. **Batch Processing**: Process multiple documents at once
2. **Caching**: Cache embeddings for frequently accessed documents
3. **Async Operations**: Use async for concurrent processing
4. **Index Optimization**: Regularly optimize vector store indices

## Troubleshooting

### Issue: Slow retrieval
- Reduce `fetch_k` parameter
- Use smaller embedding model
- Optimize chunk size

### Issue: Poor answer quality
- Increase `k` (retrieve more documents)
- Adjust chunk size and overlap
- Improve prompt templates

### Issue: Out of context errors
- Reduce chunk size
- Check token limits
- Use summarization for long documents

## Resources

- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [LangChain Cookbook](https://github.com/langchain-ai/langchain/tree/master/cookbook)
- [RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)
