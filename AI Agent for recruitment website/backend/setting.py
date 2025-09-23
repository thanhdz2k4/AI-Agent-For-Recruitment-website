from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # MongoDB settings
    DATABASE_HOST: str = "mongodb+srv://thanhthanh10012004:dH4KeOCy74suqJLk@rag-cluster.ssgkce4.mongodb.net/?retryWrites=true&w=majority&appName=rag-cluster"
    DATABASE_NAME: str = "rag"
    COLLECTION_JOB: str = ""

    # Qdrant settings
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION_NAME: str = "recruitment_vectors"
    QDRANT_VECTOR_SIZE: int = 384  # for all-MiniLM-L6-v2

    # LLM and Embedding settings
    TEXT_EMBEDDING_MODEL_ID: str = "sentence-transformers/all-MiniLM-L6-v2"
    RERANKING_CROSS_ENCODER_MODEL_ID: str = "cross-encoder/ms-marco-MiniLM-L-4-v2"
    RAG_MODEL_DEVICE: str = "cpu"
    RAG_MODEL_ID: str = "hf.co/unsloth/Qwen3-1.7B-GGUF:IQ4_XS"
    
    
    @classmethod
    def load_settings(cls) -> "Settings":
        """
        Tries to load settings from environment variables and .env file
        """
        try:
            settings = cls()
            logger.info("Settings loaded successfully")
            return settings
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            raise