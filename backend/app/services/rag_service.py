from typing import List, Dict, Any
import os
import shutil
from langchain_community.document_loaders import (
    TextLoader,
    Docx2txtLoader,
    UnstructuredMarkdownLoader,
)
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from ..core.config import settings

class DocumentProcessor:
    """Handles document loading and processing for RAG"""
    
    def __init__(self):
        self.embeddings = OllamaEmbeddings(
            model=settings.DEFAULT_MODEL,
            base_url=settings.OLLAMA_BASE_URL
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,  # Larger chunks to capture more context
            chunk_overlap=300,  # More overlap to avoid missing info at boundaries
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""]  # Added period separator
        )

    def load_document(self, file_path: str):
        """Load a document from file path based on file extension"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # Use PyMuPDF for better PDF parsing (preserves formatting better)
        loader_map = {
            '.pdf': PyMuPDFLoader,  # Better PDF parser than PyPDFLoader
            '.txt': TextLoader,
            '.md': UnstructuredMarkdownLoader,
            '.docx': Docx2txtLoader,
        }
        
        if file_extension not in loader_map:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        loader = loader_map[file_extension](file_path)
        documents = loader.load()
        
        # Log the extracted content for debugging
        print(f"📄 Loaded {len(documents)} pages from {os.path.basename(file_path)}")
        if documents:
            print(f"   First 200 chars: {documents[0].page_content[:200]}...")
        
        return documents

    def process_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a document and return chunks with metadata"""
        try:
            documents = self.load_document(file_path)
            docs = self.text_splitter.split_documents(documents)
            
            # Add metadata to each chunk
            for i, doc in enumerate(docs):
                doc.metadata["chunk_id"] = i
                doc.metadata["source"] = os.path.basename(file_path)
                
            return [{"page_content": doc.page_content, "metadata": doc.metadata} 
                   for doc in docs]
                    
        except Exception as e:
            raise Exception(f"Error processing document: {str(e)}")

class RAGService:
    """Production-ready RAG service with history-aware retrieval"""
    
    def __init__(self, user_id: int = None, user_name: str = None):
        self.user_id = user_id
        self.user_name = user_name or f"User {user_id}"
        self.embeddings = OllamaEmbeddings(
            model=settings.DEFAULT_MODEL,
            base_url=settings.OLLAMA_BASE_URL
        )
        self.llm = ChatOllama(
            model=settings.DEFAULT_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0.7
        )
        self.vector_store = None
        self.retriever = None
        self.rag_chain = None
        self._setup_chains()
        
    def _setup_chains(self):
        """Set up the RAG chains with history awareness"""
        # Contextualize question prompt - reformulates questions based on chat history
        contextualize_q_system_prompt = """
        Given a chat history and the latest user question which might reference context 
        in the chat history, formulate a standalone question which can be understood 
        without the chat history. Do NOT answer the question, just reformulate it if 
        needed and otherwise return it as is.
        """
        
        self.contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        # QA system prompt - answers questions based on context with user awareness
        qa_system_prompt = f"""
        You are a helpful AI assistant. You are currently assisting a user named {self.user_name}.
        
        IMPORTANT: When the user asks "what is my name" or "who am I", respond with: "Your name is {self.user_name}."
        
        Use the following pieces of context to answer the user's question. If you don't know the 
        answer based on the context, just say that you don't know, don't try to make up an answer.
        
        You are helping {self.user_name} with their personal documents and queries.
        
        Context: {{context}}
        """
        
        self.qa_prompt = ChatPromptTemplate.from_messages([
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
    def init_vector_store(self, persist_directory: str = None, folder_id: int = None):
        """Initialize or load the vector store with optional folder filtering"""
        if persist_directory is None:
            persist_directory = f"{settings.VECTOR_STORE_PATH}/user_{self.user_id}"
            
        self.vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
            collection_name=f"user_{self.user_id}_docs"
        )
        
        # Build search kwargs with optional folder filter
        search_kwargs = {
            "k": 8,  # Retrieve more documents (was 4)
            "fetch_k": 20,  # Fetch more candidates before MMR (was 10)
            "lambda_mult": 0.5  # Balance between relevance and diversity
        }
        
        # Add folder filter if specified
        if folder_id is not None:
            search_kwargs["filter"] = {"folder_id": folder_id}
        
        self.retriever = self.vector_store.as_retriever(
            search_type="mmr",  # Maximal Marginal Relevance for diversity
            search_kwargs=search_kwargs
        )
        
        # Create history-aware retriever
        history_aware_retriever = create_history_aware_retriever(
            self.llm,
            self.retriever,
            self.contextualize_q_prompt
        )
        
        # Create question-answer chain
        question_answer_chain = create_stuff_documents_chain(
            self.llm,
            self.qa_prompt
        )
        
        # Create the full RAG chain
        self.rag_chain = create_retrieval_chain(
            history_aware_retriever,
            question_answer_chain
        )
    
    def add_documents(self, documents: List[Dict[str, Any]], folder_id: int = None):
        """Add documents to the vector store with optional folder metadata"""
        if not self.vector_store:
            self.init_vector_store()
            
        texts = [doc["page_content"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        
        # Add folder_id to metadata if provided
        if folder_id is not None:
            for metadata in metadatas:
                metadata["folder_id"] = folder_id
        
        self.vector_store.add_texts(
            texts=texts,
            metadatas=metadatas
        )
        
        # Persist the vector store
        self.vector_store.persist()
    
    def _format_chat_history(self, chat_history: List[Dict[str, str]]) -> List:
        """Convert chat history to LangChain message format"""
        formatted_history = []
        for msg in chat_history:
            if msg["role"] == "user" or msg["role"] == "human":
                formatted_history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant" or msg["role"] == "ai":
                formatted_history.append(AIMessage(content=msg["content"]))
        return formatted_history
    
    def query(self, question: str, chat_history: List[Dict[str, str]] = None, folder_id: int = None) -> Dict[str, Any]:
        """Query the RAG system with a question and chat history, optionally scoped to a folder"""
        # Reinitialize if folder_id changes (to update retriever filter)
        if not self.rag_chain or folder_id is not None:
            self.init_vector_store(folder_id=folder_id)
            
        # Format chat history
        formatted_history = self._format_chat_history(chat_history or [])
        
        # Invoke the RAG chain
        result = self.rag_chain.invoke({
            "input": question,
            "chat_history": formatted_history
        })
        
        # Log retrieved documents for debugging
        retrieved_docs = result.get("context", [])
        print(f"\n🔍 Query: {question}")
        print(f"📚 Retrieved {len(retrieved_docs)} documents:")
        for i, doc in enumerate(retrieved_docs[:3]):  # Show first 3
            content_preview = doc.page_content[:150].replace('\n', ' ')
            print(f"   {i+1}. {content_preview}...")
        
        return {
            "answer": result["answer"],
            "source_documents": retrieved_docs,
            "question": question
        }
    
    def clear_vector_store(self):
        """Clear the vector store for this user"""
        # Delete the collection from Chroma
        if self.vector_store:
            try:
                self.vector_store.delete_collection()
            except Exception as e:
                print(f"⚠️ Error deleting collection: {e}")
            
            self.vector_store = None
            self.retriever = None
            self.rag_chain = None
        
        # Also delete the physical directory to ensure complete cleanup
        persist_directory = f"{settings.VECTOR_STORE_PATH}/user_{self.user_id}"
        if os.path.exists(persist_directory):
            try:
                shutil.rmtree(persist_directory)
                print(f"🗑️ Deleted vector store directory: {persist_directory}")
            except Exception as e:
                print(f"⚠️ Error deleting directory: {e}")
