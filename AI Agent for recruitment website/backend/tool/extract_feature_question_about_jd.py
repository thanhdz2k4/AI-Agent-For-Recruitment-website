
import os
import json
import re


from llms.ollama_llms import OllamaLLMs
from prompt.promt_config import PromptConfig


class ExtractFeatureQuestion:
    def __init__(self, model_name: str, validate_response: list = ["title", "skills", "company", "location", "experience", "description"]):
        self.valid_fields = validate_response
        default_url = "http://host.docker.internal:11434" if os.getenv("DOCKER_ENV") == "true" else "http://localhost:11434"
        ollama_url = os.getenv("OLLAMA_URL", default_url)
        model_name = os.getenv("OLLAMA_MODEL", "hf.co/Cactus-Compute/Qwen3-1.7B-Instruct-GGUF:Q4_K_M")
        self.llm = OllamaLLMs(base_url=ollama_url, model_name=model_name)


    def extract(self, query: str, prompt_type: str) -> str:
        try:
            response = self._call_llm(query, prompt_type)
            cleaned_response = self._clear_llm_response(response)
            response_dict = json.loads(cleaned_response)
            validated_dict = self._validate_query_fields(response_dict)
            print(f"📝 User input: {query}")
            print(f"🔍 Extracted query: {validated_dict}")
            return validated_dict
        except Exception as e:
            print(f"Error extracting features: {e}")
            return {}

    def _call_llm(self, query: str, prompt_type: str) -> str:
        promptConfig = PromptConfig()
        prompt = promptConfig.get_prompt(prompt_name=prompt_type, user_input=query)
        messages = [
            {"role": "user", "content": prompt}
        ]
        response = self.llm.chat(messages)
        return response
    
    def _clear_llm_response(self, response: str) -> str:
        """
        Clear the LLM response to be a valid JSON object.
        """
        # Tìm JSON trong response
        json_pattern = r'\{[^{}]*\}'
        matches = re.findall(json_pattern, response)
        
        if matches:
            return matches[0]
        
        # Nếu không tìm thấy JSON pattern, thử clean up
        cleaned = response.strip()
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        if cleaned.startswith('```'):
            cleaned = cleaned[3:]
            
        cleaned = cleaned.strip()
        
        # Nếu vẫn không có dấu ngoặc, trả về empty dict
        if not cleaned.startswith('{'):
            return '{}'
            
        return cleaned
    
    def _validate_query_fields(self, query_dict: dict) -> dict:
        """
        Validate và filter các fields hợp lệ
        """
        validated = {}
        
        for key, value in query_dict.items():
            if key in self.valid_fields and value:
                # Clean up value
                if isinstance(value, str):
                    value = value.strip()
                    if value:  # Only add non-empty values
                        validated[key] = value
                else:
                    validated[key] = value
                    
        return validated