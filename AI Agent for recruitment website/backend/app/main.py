"""
Simple Flask app for AI Recruitment System
"""
from flask import Flask, jsonify, request
import os
import sys

# Add backend to path
backend_path = os.path.dirname(os.path.abspath(__file__))
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
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        model_name = os.getenv("OLLAMA_MODEL", "llama2")
        
        logger.info(f"Initializing Ollama client with URL: {ollama_url}, Model: {model_name}")
        
        client = OllamaLLMs(
            base_url=ollama_url,
            model_name=model_name
        )
        
        # Test connection
        test_response = client.generate_content([
            {"role": "user", "content": "Hello"}
        ])
        logger.info("Ollama client initialized successfully")
        return client
        
    except Exception as e:
        logger.error(f"Failed to initialize Ollama client: {e}")
        return None

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
        # Check if LLM client is available
        if llm_client is None:
            return jsonify({
                "error": "LLM service is not available. Please ensure Ollama is running and accessible.",
                "status": "service_unavailable",
                "suggestion": "Check if Ollama is running at the configured URL"
            }), 503
        
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
        
        # Generate response
        response = llm_client.generate_content(prompt)
        
        return jsonify({
            "response": response,
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500


@app.route('/api/models', methods=['GET'])
def list_models():
    """List available models"""
    if llm_client is None:
        return jsonify({
            "error": "LLM service is not available",
            "status": "service_unavailable"
        }), 503
        
    return jsonify({
        "current_model": llm_client.model_name,
        "base_url": llm_client.base_url,
        "status": "available"
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
