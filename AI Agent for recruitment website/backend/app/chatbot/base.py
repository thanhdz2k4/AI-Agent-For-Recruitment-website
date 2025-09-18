
from abc import ABC, abstractmethod
from typing import Dict, List


class BaseChatbot(ABC):
    def __init__(self, model_name: str = None, **kwargs):
        self.model_name = model_name
        self.conversation_history = []
        pass
    
    def add_system_message(self, message: str):
        self.conversation_history.append({"role": "system", "content": message})
        
    def add_user_message(self, message: str):
        self.conversation_history.append({"role": "user", "content": message})
    
    def add_assistant_message(self, message: str):
        self.conversation_history.append({"role": "assistant", "content": message})
        
    @abstractmethod
    def classify_intent(self, message: str) -> str:
        pass
    
    def clear_history(self):
        self.conversation_history = []

    def get_history(self) -> List[Dict[str, str]]:
        return self.conversation_history
    
    @abstractmethod
    def chat(self, message: str, include_history: bool = True) -> str:
        """
        Chat with the bot
        
        Args:
            message: user message
            include_history: whether to include conversation history in the prompt
        Returns:
            response from the bot
        """
        pass
