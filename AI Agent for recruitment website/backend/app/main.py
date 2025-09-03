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

app = Flask(__name__)

# Initialize LLM client
llm_client = OllamaLLMs(
    base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
    model_name=os.getenv("OLLAMA_MODEL", "llama2")
)


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
        
        # Generate response
        response = llm_client.generate_content(prompt)
        
        return jsonify({
            "response": response,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500


@app.route('/api/models', methods=['GET'])
def list_models():
    """List available models"""
    return jsonify({
        "current_model": llm_client.model_name,
        "base_url": llm_client.base_url
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
