"""
Simple Flask app for AI Recruitment System
"""
from flask import Flask, jsonify, request, render_template, send_from_directory, session
import os
import sys
import time
import uuid
from datetime import datetime

# Add backend to path
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_path)

from llms.ollama_llms import OllamaLLMs
from chatbot.ChatbotOllama import ChatbotOllama
import logging

app = Flask(__name__, template_folder='../templates')
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize LLM client and chatbot with error handling
def initialize_llm_client():
    try:
        # For Docker containers, use host.docker.internal to reach host machine
        default_url = "http://host.docker.internal:11434" if os.getenv("DOCKER_ENV") == "true" else "http://localhost:11434"
        ollama_url = os.getenv("OLLAMA_URL", default_url)
        model_name = os.getenv("OLLAMA_MODEL", "hf.co/Cactus-Compute/Qwen3-1.7B-Instruct-GGUF:Q4_K_M")
        
        logger.info(f"Initializing Ollama client with URL: {ollama_url}, Model: {model_name}")
        
        # Setup environment for ChatbotOllama
        os.environ["OLLAMA_URL"] = ollama_url
        os.environ["OLLAMA_MODEL"] = model_name
        
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
            model_name=os.getenv("OLLAMA_MODEL", "hf.co/Cactus-Compute/Qwen3-1.7B-Instruct-GGUF:Q4_K_M")

        )

llm_client = initialize_llm_client()

# Dictionary to store chatbot instances for each user session
user_chatbots = {}

def get_session_id():
    """Get or create session ID for current user"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session['created_at'] = datetime.now().isoformat()
    return session['session_id']

def get_user_chatbot(session_id):
    """Get or create chatbot instance for specific user session"""
    if session_id not in user_chatbots:
        try:
            chatbot = ChatbotOllama()
            chatbot.add_system_message(
                "Bạn là một trợ lý thân thiện trong lĩnh vực tuyển dụng. "
                "Hãy giúp đỡ ứng viên về việc làm, phỏng vấn và tư vấn nghề nghiệp. "
                "Trả lời ngắn gọn và hữu ích."
            )
            user_chatbots[session_id] = {
                'chatbot': chatbot,
                'created_at': datetime.now(),
                'last_activity': datetime.now()
            }
            logger.info(f"Created new chatbot for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to create chatbot for session {session_id}: {e}")
            return None
    
    # Update last activity
    user_chatbots[session_id]['last_activity'] = datetime.now()
    return user_chatbots[session_id]['chatbot']

def cleanup_inactive_sessions():
    """Remove inactive user sessions (older than 1 hour)"""
    current_time = datetime.now()
    inactive_sessions = []
    
    for session_id, data in user_chatbots.items():
        time_diff = current_time - data['last_activity']
        if time_diff.total_seconds() > 3600:  # 1 hour
            inactive_sessions.append(session_id)
    
    for session_id in inactive_sessions:
        del user_chatbots[session_id]
        logger.info(f"Cleaned up inactive session: {session_id}")
    
    return len(inactive_sessions)


@app.route('/')
def index():
    """Serve the chat interface"""
    return render_template('chat.html')


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "AI Recruitment Agent",
        "version": "1.0.0"
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint for recruitment conversations using ChatbotOllama"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        
        user_message = data['message']
        
        # Get user's session and chatbot
        session_id = get_session_id()
        bot = get_user_chatbot(session_id)
        
        if bot is None:
            return jsonify({
                "error": "Chatbot service is not available. Please ensure Ollama is running.",
                "status": "service_unavailable"
            }), 503
        
        try:
            # Generate response using chatbot
            response = bot.chat(user_message)
            
            # Clean response (remove thinking tags if present)
            if "<think>" in response:
                response = response.split("</think>")[-1].strip()
            
            # Get intent classification
            intent = bot.classify_intent(user_message)
            
            # Cleanup inactive sessions periodically
            if len(user_chatbots) > 10:  # Only cleanup when we have many sessions
                cleanup_inactive_sessions()
            
            return jsonify({
                "response": response,
                "intent": intent,
                "session_id": session_id,
                "status": "success"
            })
            
        except Exception as llm_error:
            logger.error(f"Chatbot error: {llm_error}")
            
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
                    "error": f"Chatbot processing error: {str(llm_error)}",
                    "status": "processing_error"
                }), 500
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500


@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """Get conversation history for current user session"""
    try:
        session_id = get_session_id()
        bot = get_user_chatbot(session_id)
        
        if bot is None:
            return jsonify({
                "error": "Chatbot service is not available",
                "status": "service_unavailable"
            }), 503
        
        history = bot.get_history()
        return jsonify({
            "history": history,
            "total_messages": len(history),
            "session_id": session_id,
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"History endpoint error: {e}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500


@app.route('/api/chat/clear', methods=['POST'])
def clear_chat_history():
    """Clear conversation history for current user session"""
    try:
        session_id = get_session_id()
        bot = get_user_chatbot(session_id)
        
        if bot is None:
            return jsonify({
                "error": "Chatbot service is not available",
                "status": "service_unavailable"
            }), 503
        
        bot.clear_history()
        # Re-add system message
        bot.add_system_message(
            "Bạn là một trợ lý thân thiện trong lĩnh vực tuyển dụng. "
            "Hãy giúp đỡ ứng viên về việc làm, phỏng vấn và tư vấn nghề nghiệp. "
            "Trả lời ngắn gọn và hữu ích."
        )
        
        return jsonify({
            "message": "Conversation history cleared",
            "session_id": session_id,
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Clear history endpoint error: {e}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500


@app.route('/api/sessions', methods=['GET'])
def get_sessions_info():
    """Get information about active sessions (admin endpoint)"""
    try:
        # Cleanup inactive sessions first
        cleaned_up = cleanup_inactive_sessions()
        
        sessions_info = []
        for session_id, data in user_chatbots.items():
            history_length = len(data['chatbot'].get_history())
            sessions_info.append({
                "session_id": session_id[:8] + "...",  # Truncate for privacy
                "created_at": data['created_at'].isoformat(),
                "last_activity": data['last_activity'].isoformat(),
                "history_length": history_length
            })
        
        return jsonify({
            "active_sessions": len(user_chatbots),
            "cleaned_up_sessions": cleaned_up,
            "sessions": sessions_info,
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Sessions info endpoint error: {e}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500


@app.route('/api/session/info', methods=['GET'])
def get_current_session_info():
    """Get current user's session information"""
    try:
        session_id = get_session_id()
        
        if session_id in user_chatbots:
            data = user_chatbots[session_id]
            history_length = len(data['chatbot'].get_history())
            
            return jsonify({
                "session_id": session_id,
                "created_at": data['created_at'].isoformat(),
                "last_activity": data['last_activity'].isoformat(),
                "history_length": history_length,
                "status": "active"
            })
        else:
            return jsonify({
                "session_id": session_id,
                "status": "new",
                "message": "No chatbot instance created yet"
            })
            
    except Exception as e:
        logger.error(f"Session info endpoint error: {e}")
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
