import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    groq_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    
    llm_provider: Literal["groq", "openai", "anthropic"] = "groq"
    llm_model: str ="llama-3.3-70b-versatile"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    vector_db_type: Literal["chromadb", "faiss"] = "chromadb"
    vector_db_path: str = "./data/storage/vector_db"
    metadata_db_path: str = "./data/storage/metadata/metadata.db"
    
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k_retrieval: int = 5
    confidence_threshold: float = 0.6
    enable_reranking: bool = True
    
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    enable_debug_mode: bool = False
    
    max_retries: int = 3
    timeout_seconds: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Path(self.vector_db_path).mkdir(parents=True, exist_ok=True)
        Path(self.metadata_db_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)

settings = Settings()