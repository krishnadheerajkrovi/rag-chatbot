from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "RAG Chatbot"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/rag_chatbot"
    
    # Ollama - Use host.docker.internal to access host machine's Ollama
    OLLAMA_BASE_URL: str = "http://host.docker.internal:11434"
    DEFAULT_MODEL: str = "llama2"
    
    # Vector Store
    VECTOR_STORE_PATH: str = "/app/vector_store"
    
    # Phoenix Configuration (Arize Phoenix for tracing)
    PHOENIX_ENABLED: bool = True
    PHOENIX_COLLECTOR_ENDPOINT: str = "http://host.docker.internal:4317"
    PHOENIX_PROJECT_NAME: str = "rag-chatbot"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Configure Phoenix tracing
if settings.PHOENIX_ENABLED:
    try:
        from phoenix.otel import register
        from openinference.instrumentation.langchain import LangChainInstrumentor
        
        # Register Phoenix as the OTLP endpoint (gRPC)
        tracer_provider = register(
            project_name=settings.PHOENIX_PROJECT_NAME,
            endpoint=settings.PHOENIX_COLLECTOR_ENDPOINT,
        )
        
        # Instrument LangChain
        LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
        
        print(f"✅ Phoenix tracing enabled - sending to {settings.PHOENIX_COLLECTOR_ENDPOINT}")
    except Exception as e:
        print(f"⚠️  Phoenix tracing failed to initialize: {e}")
