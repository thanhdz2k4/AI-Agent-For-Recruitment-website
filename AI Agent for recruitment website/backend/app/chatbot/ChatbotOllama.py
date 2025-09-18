
import os
import logging
from .base import BaseChatbot
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from llms.ollama_llms import OllamaLLMs


class ChatbotOllama(BaseChatbot):
    def __init__(self, model_name: str = "hf.co/unsloth/Qwen3-1.7B-GGUF:IQ4_XS", **kwargs):
        super().__init__(model_name=model_name, **kwargs)
        
        default_url = "http://host.docker.internal:11434" if os.getenv("DOCKER_ENV") == "true" else "http://localhost:11434"
        ollama_url = os.getenv("OLLAMA_URL", default_url)
        ollama_model = os.getenv("OLLAMA_MODEL", "hf.co/unsloth/Qwen3-1.7B-GGUF:IQ4_XS")
        
        logging.info(f"Initializing Ollama client with URL: {ollama_url}, Model: {ollama_model}")
        
        self.client = OllamaLLMs(
            base_url=ollama_url,
            model_name=ollama_model
        )
        

   

    def chat(self, message: str, include_history: bool = True) -> str:
        # Add user message to history first
        self.add_user_message(message)
        
        # Prepare messages for Ollama API
        if include_history:
            messages = self.conversation_history.copy()
        else:
            messages = [{"role": "user", "content": message}]
        
        try:
            # Use the client's generate_content method
            assistant_response = self.client.generate_content(messages)
            
            # Add assistant response to history
            self.add_assistant_message(assistant_response)
            
            return assistant_response
            
        except Exception as e:
            error_msg = f"Error communicating with Ollama: {str(e)}"
            self.add_assistant_message(error_msg)
            return error_msg
    
    def classify_intent(self, message: str) -> str:
        """
        Classify the intent of the user message
        """
        # Basic intent classification - can be enhanced
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['job', 'position', 'vacancy', 'opening', 'career']):
            return 'job_inquiry'
        elif any(word in message_lower for word in ['application', 'apply', 'resume', 'cv']):
            return 'application'
        elif any(word in message_lower for word in ['interview', 'schedule', 'meeting']):
            return 'interview'
        elif any(word in message_lower for word in ['salary', 'pay', 'compensation', 'benefits']):
            return 'compensation'
        else:
            return 'general'
    