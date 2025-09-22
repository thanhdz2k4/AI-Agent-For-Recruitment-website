
import os
import logging
from typing import List, Dict, Union, Callable, Any, Optional
from .base import BaseChatbot
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from llms.ollama_llms import OllamaLLMs
from llms.tools import list_available_tools


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
    
    def chat_with_tools(
        self, 
        message: str, 
        tools: Optional[List[Union[Callable, str]]] = None,
        include_history: bool = True,
        max_steps: int = 3,
        **options
    ) -> Dict[str, Any]:
        """
        Chat with function calling support
        
        Args:
            message: User message
            tools: List of tool functions or tool names to use
            include_history: Whether to include conversation history
            max_steps: Maximum tool calling steps
            **options: Additional options (temperature, etc.)
        
        Returns:
            dict: Response with final answer and tool call information
        """
        # Add user message to history
        self.add_user_message(message)
        
        # Prepare messages for Ollama API
        if include_history:
            messages = self.conversation_history.copy()
        else:
            messages = [{"role": "user", "content": message}]
        
        try:
            # Use the client's chat_with_tools method
            response = self.client.chat_with_tools(
                messages=messages,
                tools=tools,
                max_steps=max_steps,
                **options
            )
            
            # Add assistant response to history
            final_answer = response.get("final_answer", "No response generated")
            self.add_assistant_message(final_answer)
            
            return response
            
        except Exception as e:
            error_msg = f"Error in chat with tools: {str(e)}"
            self.add_assistant_message(error_msg)
            return {
                "final_answer": error_msg,
                "tool_calls": [],
                "steps": 1,
                "error": str(e)
            }
    
    def get_available_tools(self) -> List[str]:
        """
        Get list of available tool names
        
        Returns:
            list: List of available tool names
        """
        return list_available_tools()
    
    def chat_with_job_tools(self, message: str, include_history: bool = True) -> Dict[str, Any]:
        """
        Chat with job-related tools enabled
        
        Args:
            message: User message
            include_history: Whether to include conversation history
        
        Returns:
            dict: Response with job search capabilities
        """
        # Define job-related tools
        job_tools = [
            "search_job_info",
            "get_current_time",
            "format_json_response"
        ]
        
        return self.chat_with_tools(
            message=message,
            tools=job_tools,
            include_history=include_history,
            temperature=0.2  # Lower temperature for more consistent tool usage
        )
    
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
    