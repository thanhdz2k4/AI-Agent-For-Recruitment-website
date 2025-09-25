
import os
import logging
from typing import List, Dict, Union, Callable, Any, Optional
from .base import BaseChatbot
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from llms.ollama_llms import OllamaLLMs
from llms.tools import list_available_tools
from MCP.server import server, intent_classification, enhance_question, get_prompt, get_reflection

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
    
    def _set_conversation_state_from_question(self, enhanced_question: str, original_message: str):
        """Set conversation state based on the enhanced question"""
        enhanced_lower = enhanced_question.lower()
        
        if any(word in enhanced_lower for word in ['địa chỉ', 'location', 'nơi làm việc', 'ở đâu', 'khu vực', 'ở thành phố']):
            self.conversation_state = "waiting_for_location"
        elif any(word in enhanced_lower for word in ['kỹ năng', 'skills', 'kinh nghiệm', 'chuyên môn']):
            self.conversation_state = "waiting_for_skills"
        elif any(word in enhanced_lower for word in ['lương', 'salary', 'mức lương', 'thu nhập']):
            self.conversation_state = "waiting_for_salary"
        elif any(word in enhanced_lower for word in ['vị trí', 'position', 'công việc', 'chức danh']):
            self.conversation_state = "waiting_for_position"
        else:
            self.conversation_state = "waiting_for_info"
    
    def _handle_ongoing_conversation(self, message: str, messages: List[Dict]) -> str:
        """Handle conversation when we're waiting for specific information"""
        print("Handling ongoing conversation...")
        
        # Create proper message format for generate_content
        classification_prompt = get_prompt("classification_recruitment_intent", user_input=message)
        classification_messages = [{"role": "user", "content": classification_prompt}]
        
        intent = self.client.generate_content(classification_messages)
        intent = intent.strip().lower()  # Clean up the response
        
        # Extract only the final answer, ignore <think> sections
        if "</think>" in intent:
            intent = intent.split("</think>")[-1].strip()
        
        # Extract the final word/classification
        intent_words = intent.split()
        if intent_words:
            intent = intent_words[-1]  # Get the last word as the classification
        
        print(f"Extracted intent: {intent}")
        
        if intent == "location" or "địa điểm" in intent:
            self.recruitment_context["location"] = message
        elif intent == "skills" or "kỹ năng" in intent:
            self.recruitment_context["skills"] = message
        elif intent == "salary" or "lương" in intent:
            self.recruitment_context["salary"] = message
        elif intent == "position" or "vị trí" in intent:
            self.recruitment_context["position"] = message
            
        print(f"Extracted intent: {intent}")
        
        # Check if we have enough information
        if self._is_recruitment_complete():
            self.conversation_state = "idle"
            # Use reflection to generate comprehensive response
            print(f"Current state: {self.conversation_state}")
            print(f"Current context: {self.recruitment_context}")
            return self._generate_recruitment_response_with_reflection(messages)
        else:
            print(f"Current state: {self.conversation_state}")
            print(f"Current context: {self.recruitment_context}")
            # Continue asking for more information
            return self._ask_for_next_missing_info()
    
    def _is_recruitment_complete(self) -> bool:
        """Check if we have enough information for job search"""
        required_fields = ["location"]  # Minimum required
        optional_fields = ["skills", "position", "salary"]
        
        # Must have at least location
        has_required = all(field in self.recruitment_context for field in required_fields)
        # Should have at least one optional field
        has_optional = any(field in self.recruitment_context for field in optional_fields)
        
        # Count only actual recruitment info fields (exclude initial_query)
        recruitment_info_count = len([k for k in self.recruitment_context.keys() if k != "initial_query"])
        
        return has_required and (has_optional or recruitment_info_count >= 2)
    
    def _ask_for_next_missing_info(self) -> str:
        """Ask for the next missing piece of information"""
        if "skills" not in self.recruitment_context:
            self.conversation_state = "waiting_for_skills"
            return "Bạn có kỹ năng gì hoặc muốn ứng tuyển vị trí nào?"
        elif "salary" not in self.recruitment_context:
            self.conversation_state = "waiting_for_salary"
            return "Bạn mong muốn mức lương như thế nào?"
        else:
            self.conversation_state = "idle"
            return "Cảm ơn! Tôi sẽ tìm kiếm công việc phù hợp cho bạn."
    
    def _generate_recruitment_response_with_reflection(self, messages: List[Dict]) -> str:
        """Generate recruitment response using reflection for better quality"""
        try:
            # Create a comprehensive context for reflection
            context_summary = f"Thông tin tuyển dụng: {self.recruitment_context}"
            
            # # Add context to conversation history for reflection
            # reflection_history = messages.copy()
            # reflection_history.append({
            #     "role": "system", 
            #     "content": f"Context: {context_summary}. Hãy tìm kiếm và đưa ra kết quả công việc phù hợp."
            # })
            
            # # Use reflection to improve the response
            # improved_response = get_reflection(reflection_history)
            # self.add_assistant_message(improved_response)
            
            return context_summary
            
        except Exception as e:
            logging.error(f"Error in reflection: {str(e)}")
            # Fallback to simple response
            fallback_response = f"Cảm ơn bạn! Dựa trên thông tin: {self.recruitment_context}, tôi sẽ tìm kiếm công việc phù hợp."
            self.add_assistant_message(fallback_response)
            return fallback_response

    def chat(self, message: str, include_history: bool = True) -> str:
        # Add user message to history first
        self.add_user_message(message)
        
        # Prepare messages for Ollama API
        if include_history:
            messages = self.conversation_history.copy()
        else:
            messages = [{"role": "user", "content": message}]
        
        try:
            # print("history = ", self.conversation_history)
            print(f"Current state: {self.conversation_state}")
            print(f"Current context: {self.recruitment_context}")
            
            # Check conversation state first - if we're waiting for info, handle it
            if self.conversation_state != "idle":
                return self._handle_ongoing_conversation(message, messages)
            
            # Only classify intent when in idle state
            intent = intent_classification(message)
            print(f"Intent classified as: {intent}")
            
            if intent == "chitchat":
                messages.append({"role": "user", "content": get_prompt("chitchat")}) 
                assistant_response = self.client.generate_content(messages)
                self.add_assistant_message(assistant_response)
                return assistant_response
                
            elif intent == "recruitment_incomplete":
                enhanced_question = enhance_question(message)
                self.add_assistant_message(enhanced_question)
                
                # Store the original query and set conversation state
                self.recruitment_context["initial_query"] = message
                self._set_conversation_state_from_question(enhanced_question, message)
                print(f"State set to: {self.conversation_state}")
                return enhanced_question
                
            elif intent == "recruitment_complete":
                # Use reflection to generate better response
                try:
                    # Add recruitment prompt context
                    messages.append({"role": "user", "content": get_prompt("recruitment_complete")})
                    
                    # Use reflection to improve the response quality
                    #improved_response = get_reflection(messages)
                    return "Recruitment complete intent detected, but reflection temporarily disabled."
                    
                    self.add_assistant_message(improved_response)
                    return improved_response
                    
                except Exception as reflection_error:
                    logging.error(f"Error in reflection: {str(reflection_error)}")
                    # Fallback to normal generation
                    assistant_response = self.client.generate_content(messages)
                    self.add_assistant_message(assistant_response)
                    return assistant_response
            
            # Default fallback
            assistant_response = self.client.generate_content(messages)
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
    