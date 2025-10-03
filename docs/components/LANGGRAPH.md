# LangGraph Component

## Overview

LangGraph is a library for building stateful, multi-actor applications with LLMs. It extends LangChain with graph-based workflows and state management capabilities.

## Key Features

- **State Management**: Maintain conversation state across interactions
- **Graph-Based Workflows**: Define complex multi-step processes
- **Conditional Routing**: Dynamic flow control based on state
- **Persistence**: Save and restore conversation state
- **Human-in-the-Loop**: Pause for human intervention

## Why LangGraph for RAG Chatbot?

### 1. Conversation State Management
```python
from langgraph.graph import StateGraph
from typing import TypedDict, List

class ConversationState(TypedDict):
    messages: List[dict]
    user_id: int
    session_id: str
    context: List[str]
```

### 2. Multi-Step RAG Pipeline
```
┌─────────────┐
│   Input     │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Contextualize  │
│  Question       │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│   Retrieve      │
│   Documents     │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│   Generate      │
│   Answer        │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│   Output        │
└─────────────────┘
```

## Implementation in Our Application

### Basic State Definition

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """State for the RAG agent"""
    messages: Annotated[Sequence[BaseMessage], "Chat messages"]
    user_id: int
    session_id: str
    retrieved_docs: List[str]
    answer: str
```

### Graph Construction

```python
# Define nodes (functions)
def contextualize_question(state: AgentState):
    """Reformulate question based on history"""
    messages = state["messages"]
    # Contextualization logic
    return {"messages": messages}

def retrieve_documents(state: AgentState):
    """Retrieve relevant documents"""
    query = state["messages"][-1].content
    docs = vector_store.similarity_search(query)
    return {"retrieved_docs": docs}

def generate_answer(state: AgentState):
    """Generate answer from retrieved docs"""
    docs = state["retrieved_docs"]
    query = state["messages"][-1].content
    answer = llm.invoke(f"Context: {docs}\n\nQuestion: {query}")
    return {"answer": answer}

# Build graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("contextualize", contextualize_question)
workflow.add_node("retrieve", retrieve_documents)
workflow.add_node("generate", generate_answer)

# Add edges
workflow.add_edge("contextualize", "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

# Set entry point
workflow.set_entry_point("contextualize")

# Compile
app = workflow.compile()
```

### Using the Graph

```python
# Initialize state
initial_state = {
    "messages": [HumanMessage(content="What is RAG?")],
    "user_id": 1,
    "session_id": "abc123",
    "retrieved_docs": [],
    "answer": ""
}

# Run the graph
result = app.invoke(initial_state)
print(result["answer"])
```

## Advanced Features

### 1. Conditional Routing

```python
def should_retrieve(state: AgentState) -> str:
    """Decide if we need to retrieve documents"""
    last_message = state["messages"][-1].content
    
    if "hello" in last_message.lower():
        return "respond_directly"
    else:
        return "retrieve_docs"

# Add conditional edge
workflow.add_conditional_edges(
    "contextualize",
    should_retrieve,
    {
        "respond_directly": "generate",
        "retrieve_docs": "retrieve"
    }
)
```

### 2. Checkpointing (State Persistence)

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# Create checkpointer
memory = SqliteSaver.from_conn_string("checkpoints.db")

# Compile with checkpointing
app = workflow.compile(checkpointer=memory)

# Use with thread_id for persistence
config = {"configurable": {"thread_id": "session_123"}}
result = app.invoke(initial_state, config=config)
```

### 3. Human-in-the-Loop

```python
from langgraph.prebuilt import ToolExecutor

def needs_approval(state: AgentState) -> bool:
    """Check if answer needs human approval"""
    return state.get("confidence", 1.0) < 0.7

workflow.add_conditional_edges(
    "generate",
    needs_approval,
    {
        True: "wait_for_approval",
        False: END
    }
)
```

### 4. Streaming Responses

```python
# Stream intermediate steps
for step in app.stream(initial_state):
    print(f"Step: {step}")
    
# Stream with updates
async for chunk in app.astream(initial_state):
    print(chunk)
```

## Use Cases in RAG Chatbot

### 1. Multi-Turn Conversations

```python
class ChatState(TypedDict):
    messages: List[BaseMessage]
    chat_history: List[dict]
    current_topic: str
    
def update_history(state: ChatState):
    """Update conversation history"""
    messages = state["messages"]
    history = state["chat_history"]
    
    # Add latest exchange to history
    history.append({
        "user": messages[-2].content,
        "assistant": messages[-1].content
    })
    
    return {"chat_history": history}
```

### 2. Document Processing Pipeline

```python
class DocumentState(TypedDict):
    file_path: str
    chunks: List[str]
    embeddings: List[List[float]]
    status: str

def load_document(state: DocumentState):
    """Load and parse document"""
    # Loading logic
    return {"chunks": chunks, "status": "loaded"}

def create_embeddings(state: DocumentState):
    """Create embeddings for chunks"""
    # Embedding logic
    return {"embeddings": embeddings, "status": "embedded"}

def store_vectors(state: DocumentState):
    """Store in vector database"""
    # Storage logic
    return {"status": "stored"}
```

### 3. Query Routing

```python
def route_query(state: AgentState) -> str:
    """Route query to appropriate handler"""
    query = state["messages"][-1].content
    
    if "code" in query.lower():
        return "code_handler"
    elif "math" in query.lower():
        return "math_handler"
    else:
        return "general_handler"

workflow.add_conditional_edges(
    "classify",
    route_query,
    {
        "code_handler": "handle_code",
        "math_handler": "handle_math",
        "general_handler": "handle_general"
    }
)
```

## State Management Patterns

### 1. Accumulating State

```python
from operator import add

class AccumulatingState(TypedDict):
    messages: Annotated[List[BaseMessage], add]  # Accumulate messages
    docs: Annotated[List[str], add]              # Accumulate documents
```

### 2. Replacing State

```python
class ReplacingState(TypedDict):
    current_step: str      # Replace with new value
    confidence: float      # Replace with new value
```

### 3. Custom Reducers

```python
def merge_docs(existing: List[str], new: List[str]) -> List[str]:
    """Custom merge logic for documents"""
    return list(set(existing + new))  # Remove duplicates

class CustomState(TypedDict):
    docs: Annotated[List[str], merge_docs]
```

## Integration with LangChain

### Using LangChain Chains in Nodes

```python
from langchain.chains import create_retrieval_chain

def rag_node(state: AgentState):
    """Node using LangChain RAG chain"""
    rag_chain = create_retrieval_chain(retriever, qa_chain)
    
    result = rag_chain.invoke({
        "input": state["messages"][-1].content,
        "chat_history": state.get("chat_history", [])
    })
    
    return {
        "answer": result["answer"],
        "retrieved_docs": result["context"]
    }
```

## Best Practices

### 1. State Design
- Keep state minimal and focused
- Use typed dictionaries for clarity
- Document state transitions

### 2. Node Functions
- Each node should have a single responsibility
- Return partial state updates, not full state
- Handle errors gracefully

### 3. Graph Structure
- Keep graphs simple and readable
- Use conditional edges for complex routing
- Document decision points

### 4. Persistence
- Use checkpointing for long conversations
- Clean up old checkpoints regularly
- Consider database-backed persistence for production

### 5. Error Handling
```python
def safe_node(state: AgentState):
    """Node with error handling"""
    try:
        # Node logic
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
```

## Performance Considerations

### 1. Async Operations
```python
async def async_retrieve(state: AgentState):
    """Async document retrieval"""
    docs = await vector_store.asimilarity_search(query)
    return {"retrieved_docs": docs}
```

### 2. Parallel Execution
```python
# Multiple retrievers in parallel
workflow.add_node("retrieve_docs", retrieve_documents)
workflow.add_node("retrieve_web", retrieve_web_results)

# Both run in parallel
workflow.add_edge("query", "retrieve_docs")
workflow.add_edge("query", "retrieve_web")
```

### 3. Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_retrieval(query: str):
    """Cache retrieval results"""
    return vector_store.similarity_search(query)
```

## Debugging

### 1. Visualization
```python
# Generate graph visualization
from IPython.display import Image

Image(app.get_graph().draw_png())
```

### 2. Logging
```python
import logging

def logged_node(state: AgentState):
    """Node with logging"""
    logging.info(f"Processing state: {state}")
    # Node logic
    logging.info(f"Updated state: {new_state}")
    return new_state
```

### 3. Step-by-Step Execution
```python
# Execute one step at a time
for step in app.stream(initial_state):
    print(f"Current step: {step}")
    input("Press Enter to continue...")
```

## Comparison: LangChain vs LangGraph

| Feature | LangChain | LangGraph |
|---------|-----------|-----------|
| State Management | Limited | Built-in |
| Conditional Logic | Basic | Advanced |
| Persistence | Manual | Automatic |
| Visualization | No | Yes |
| Complexity | Simple chains | Complex workflows |

## When to Use LangGraph

✅ **Use LangGraph when:**
- Building multi-step workflows
- Need conversation state management
- Require conditional routing
- Want to visualize agent flow
- Need human-in-the-loop

❌ **Use LangChain when:**
- Simple question-answering
- Single-step operations
- No state management needed
- Rapid prototyping

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph Examples](https://github.com/langchain-ai/langgraph/tree/main/examples)
- [State Management Guide](https://langchain-ai.github.io/langgraph/concepts/#state)
