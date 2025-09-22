# -*- coding: utf-8 -*-
import pytest
import sys
import os
import logging
from unittest.mock import Mock, patch, MagicMock

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from llms.ollama_llms import OllamaLLMs
from llms.tools import add_two_numbers, get_current_time, search_job_info
from app.chatbot.ChatbotOllama import ChatbotOllama


class TestFunctionCalling:
    """Test cases for function calling functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        # Setup without real Ollama client for unit tests
        pass
    
    

    
 

    


class TestChatbotWithTools:
    """Test ChatbotOllama with function calling"""
    
    def setup_method(self):
        """Setup chatbot for testing"""
        with patch('ollama.Client'):
            self.chatbot = ChatbotOllama(model_name="llama3.1:8b")
    
    def test_get_available_tools(self):
        """Test getting available tools from chatbot"""
        tools = self.chatbot.get_available_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0
    
    @patch.object(OllamaLLMs, 'chat_with_tools')
    def test_chat_with_tools(self, mock_chat_with_tools):
        """Test chatbot chat_with_tools method"""
        mock_response = {
            "final_answer": "I found 2 Python jobs for you!",
            "tool_calls": [
                {
                    "tool_name": "search_job_info",
                    "arguments": {"query": "Python", "job_type": "all"},
                    "result": {"total_found": 2, "jobs": []}
                }
            ],
            "steps": 2
        }
        mock_chat_with_tools.return_value = mock_response
        
        result = self.chatbot.chat_with_tools("Find Python jobs", tools=["search_job_info"])
        
        assert result["final_answer"] == "I found 2 Python jobs for you!"
        assert len(result["tool_calls"]) == 1
        mock_chat_with_tools.assert_called_once()
    
    @patch.object(OllamaLLMs, 'chat_with_tools')
    def test_chat_with_job_tools(self, mock_chat_with_tools):
        """Test chatbot chat_with_job_tools method"""
        mock_response = {
            "final_answer": "Here are the available positions:",
            "tool_calls": [],
            "steps": 1
        }
        mock_chat_with_tools.return_value = mock_response
        
        result = self.chatbot.chat_with_job_tools("What jobs are available?")
        
        assert result["final_answer"] == "Here are the available positions:"
        mock_chat_with_tools.assert_called_once()
        # Verify job-specific tools were used
        call_args = mock_chat_with_tools.call_args
        tools_used = call_args.kwargs['tools']
        assert "search_job_info" in tools_used
        assert "get_current_time" in tools_used


if __name__ == "__main__":
    pytest.main([__file__, "-s"])
