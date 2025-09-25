"""
Script khởi động tối ưu cho ứng dụng với preloading models
"""
import sys
import os
import time
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from setting import Settings
from tool.model_manager import model_manager
from llms.ollama_llms import OllamaLLMs

def startup_optimization():
    """
    Thực hiện tối ưu hóa khi khởi động ứng dụng
    """
    print("🚀 Starting AI Agent Recruitment System...")
    
    # Load settings
    settings = Settings.load_settings()
    print("✅ Settings loaded")
    
    if settings.ENABLE_MODEL_PRELOAD:
        print("🔥 Preloading models...")
        start_time = time.time()
        
        # Preload embedding model và semantic router
        model_manager.preload_models()
        
        # Preload và warm-up Ollama model
        try:
            ollama_model = OllamaLLMs(
                base_url=settings.OLLAMA_BASE_URL,
                model_name=settings.RAG_MODEL_ID.split("/")[-1].split(":")[0]  # Extract model name
            )
            # Set keep-alive để model không bị unload
            ollama_model.keep_alive(settings.MODEL_KEEP_ALIVE)
            print(f"✅ Ollama model warmed up: {settings.RAG_MODEL_ID}")
        except Exception as e:
            print(f"⚠️ Ollama warm-up failed: {e}")
        
        elapsed_time = time.time() - start_time
        print(f"✅ All models preloaded in {elapsed_time:.2f} seconds")
    
    print("🎯 System ready for optimal performance!")
    
    # In thông tin cache
    cache_info = model_manager.get_cache_info()
    print(f"📦 Cached models: {cache_info['cached_models']}")
    
    return True

def health_check():
    """
    Kiểm tra sức khỏe của system
    """
    try:
        from server import intent_classification
        
        # Test intent classification
        test_result = intent_classification("Tôi muốn tìm việc")
        print(f"🔍 Health check passed - Intent: {test_result}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 AI Agent Recruitment System")
    print("=" * 50)
    
    # Startup optimization
    startup_optimization()
    
    # Health check
    if health_check():
        print("✅ System is healthy and ready!")
    else:
        print("❌ System health check failed!")
        sys.exit(1)
    
    # Start main server
    print("🌟 Starting main server...")
    from server import server
    server.run()
