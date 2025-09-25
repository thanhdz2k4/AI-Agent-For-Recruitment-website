"""
Model Manager để cache và quản lý các models tránh load lại nhiều lần
"""
import os
import threading
from typing import Dict, Any, Optional
from tool.embeddings import SentenceTransformerEmbedding, EmbeddingConfig
from tool.semantic_router import SemanticRouter, Route
from tool.semantic_router.sample import Sample
from setting import Settings

class ModelManager:
    """Singleton class để quản lý và cache các models"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.settings = Settings.load_settings()
        self.models_cache: Dict[str, Any] = {}
        self._initialized = True
        
        print("🔧 ModelManager initialized")
    
    def get_embedding_model(self, model_name: str = None) -> SentenceTransformerEmbedding:
        """
        Lấy embedding model từ cache hoặc load mới nếu chưa có
        """
        if model_name is None:
            model_name = "dangvantuan/vietnamese-document-embedding"
            
        cache_key = f"embedding_{model_name}"
        
        if cache_key not in self.models_cache:
            print(f"🚀 Loading embedding model: {model_name}")
            config = EmbeddingConfig(name=model_name)
            embedding_model = SentenceTransformerEmbedding(config)
            self.models_cache[cache_key] = embedding_model
            print(f"✅ Embedding model cached: {model_name}")
        else:
            print(f"📦 Using cached embedding model: {model_name}")
            
        return self.models_cache[cache_key]
    
    def get_semantic_router(self) -> SemanticRouter:
        """
        Lấy semantic router từ cache hoặc tạo mới nếu chưa có
        """
        cache_key = "semantic_router"
        
        if cache_key not in self.models_cache:
            print("🚀 Creating semantic router...")
            
            # Lấy embedding model
            embedding_tool = self.get_embedding_model()
            
            # Tạo các routes
            routes = [
                Route(name="recruitment_incomplete", samples=Sample.recruitment_incomplete),
                Route(name="recruitment_complete", samples=Sample.recruitment_complete),
                Route(name="chitchat", samples=Sample.chitchatSample)
            ]
            
            # Tạo semantic router
            semantic_router = SemanticRouter(embedding=embedding_tool, routes=routes)
            self.models_cache[cache_key] = semantic_router
            print("✅ Semantic router cached")
        else:
            print("📦 Using cached semantic router")
            
        return self.models_cache[cache_key]
    
    def get_llm_model(self, model_name: str = None):
        """
        Lấy LLM model từ cache (có thể extend cho Ollama, etc.)
        """
        if model_name is None:
            model_name = self.settings.RAG_MODEL_ID
            
        cache_key = f"llm_{model_name}"
        
        if cache_key not in self.models_cache:
            print(f"🚀 Loading LLM model: {model_name}")
            # TODO: Implement LLM loading logic
            # Ví dụ cho Ollama client
            from llms.ollama_llms import OllamaLLMs
            llm_model = OllamaLLMs(model_name=model_name)
            self.models_cache[cache_key] = llm_model
            print(f"✅ LLM model cached: {model_name}")
        else:
            print(f"📦 Using cached LLM model: {model_name}")
            
        return self.models_cache[cache_key]
    
    def preload_models(self):
        """
        Preload tất cả models khi khởi động ứng dụng
        """
        print("🚀 Preloading all models...")
        
        # Preload embedding model
        self.get_embedding_model()
        
        # Preload semantic router
        self.get_semantic_router()
        
        # Preload LLM model (optional)
        # self.get_llm_model()
        
        print("✅ All models preloaded successfully!")
    
    def clear_cache(self):
        """
        Xóa cache models (để free memory nếu cần)
        """
        self.models_cache.clear()
        print("🗑️ Model cache cleared")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Lấy thông tin về các models đã cache
        """
        return {
            "cached_models": list(self.models_cache.keys()),
            "cache_size": len(self.models_cache)
        }

# Global instance
model_manager = ModelManager()
