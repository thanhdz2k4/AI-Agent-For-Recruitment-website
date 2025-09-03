"""
Simple Flask app for AI Recruitment System
"""
from flask import Flask, jsonify, request
import os
import sys
import time

# Add backend to path
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_path)

from llms.ollama_llms import OllamaLLMs
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize LLM client with error handling
def initialize_llm_client():
    try:
        # For Docker containers, use host.docker.internal to reach host machine
        default_url = "http://host.docker.internal:11434" if os.getenv("DOCKER_ENV") == "true" else "http://localhost:11434"
        ollama_url = os.getenv("OLLAMA_URL", default_url)
        model_name = os.getenv("OLLAMA_MODEL", "phi3:mini")
        
        logger.info(f"Initializing Ollama client with URL: {ollama_url}, Model: {model_name}")
        
        client = OllamaLLMs(
            base_url=ollama_url,
            model_name=model_name
        )
        
        # Simple connection test without generating content
        import requests
        response = requests.get(f"{ollama_url}/api/version", timeout=5)
        if response.status_code == 200:
            logger.info("Ollama server is accessible")
            return client
        else:
            logger.warning(f"Ollama server returned status {response.status_code}")
            return client  # Still return client, let individual requests handle errors
        
    except Exception as e:
        logger.warning(f"Failed to verify Ollama connection: {e}")
        # Still create client - it might work later
        return OllamaLLMs(
            base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
            model_name=os.getenv("OLLAMA_MODEL", "phi3:mini")
        )

llm_client = initialize_llm_client()


@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "AI Recruitment Agent",
        "version": "1.0.0"
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint for recruitment conversations"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        
        user_message = data['message']
        
        # Prepare prompt for recruitment context
        prompt = [
            {
                "role": "system", 
                "content": "You are an AI recruitment assistant. Help with job interviews, candidate screening, and recruitment processes."
            },
            {
                "role": "user", 
                "content": user_message
            }
        ]
        
        # Generate response with error handling
        try:
            response = llm_client.generate_content(prompt)
            
            return jsonify({
                "response": response,
                "status": "success"
            })
            
        except Exception as llm_error:
            logger.error(f"LLM generation error: {llm_error}")
            
            # Check if it's a connection error
            if "Connection refused" in str(llm_error) or "Max retries exceeded" in str(llm_error):
                return jsonify({
                    "error": "Ollama service is not available. Please ensure Ollama is running.",
                    "status": "service_unavailable",
                    "suggestion": "Start Ollama service and ensure the correct model is pulled",
                    "technical_details": str(llm_error)
                }), 503
            else:
                return jsonify({
                    "error": f"LLM processing error: {str(llm_error)}",
                    "status": "processing_error"
                }), 500
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500


@app.route('/api/models', methods=['GET'])
def list_models():
    """List available models"""
    try:
        import requests
        ollama_url = llm_client.base_url
        
        # Check if Ollama is accessible
        response = requests.get(f"{ollama_url}/api/version", timeout=5)
        if response.status_code != 200:
            return jsonify({
                "error": "Ollama service is not accessible",
                "status": "service_unavailable",
                "ollama_url": ollama_url
            }), 503
        
        # Try to get list of models
        models_response = requests.get(f"{ollama_url}/api/tags", timeout=10)
        if models_response.status_code == 200:
            models_data = models_response.json()
            available_models = [model["name"] for model in models_data.get("models", [])]
        else:
            available_models = ["Unable to fetch models"]
        
        return jsonify({
            "current_model": llm_client.model_name,
            "base_url": llm_client.base_url,
            "status": "available",
            "available_models": available_models,
            "ollama_version": response.json()
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to check Ollama service: {str(e)}",
            "status": "service_check_failed",
            "current_model": getattr(llm_client, 'model_name', 'unknown'),
            "base_url": getattr(llm_client, 'base_url', 'unknown')
        }), 503


@app.route('/api/health/ollama', methods=['GET'])
def ollama_health():
    """Check Ollama service health"""
    try:
        import requests
        ollama_url = llm_client.base_url
        
        # Test basic connectivity
        start_time = time.time()
        response = requests.get(f"{ollama_url}/api/version", timeout=10)
        response_time = time.time() - start_time
        
        if response.status_code != 200:
            return jsonify({
                "status": "unhealthy",
                "error": f"Ollama returned status {response.status_code}",
                "url": ollama_url,
                "response_time_seconds": response_time
            }), 503
        
        # Test model availability
        try:
            test_prompt = [{"role": "user", "content": "Hello"}]
            llm_response = llm_client.generate_content(test_prompt)
            model_test_success = True
            model_error = None
        except Exception as e:
            model_test_success = False
            model_error = str(e)
        
        return jsonify({
            "status": "healthy" if model_test_success else "degraded",
            "ollama_version": response.json(),
            "url": ollama_url,
            "model": llm_client.model_name,
            "response_time_seconds": response_time,
            "model_test_success": model_test_success,
            "model_error": model_error,
            "timestamp": time.time()
        })
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "url": getattr(llm_client, 'base_url', 'unknown'),
            "timestamp": time.time()
        }), 503


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
