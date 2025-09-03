# -*- coding: utf-8 -*-
import requests
from typing import List, Dict
from .base import BaseLLM


class OllamaLLMs(BaseLLM):
    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "llama2", **kwargs):
        """
        Ollama client.
        base_url: URL Ollama server (mặc định: http://localhost:11434)
        model_name: tên model đã pull về trong Ollama
        """
        super().__init__(model_name=model_name, **kwargs)
        self.base_url = base_url.rstrip("/")

    def generate_content(self, prompt: List[Dict[str, str]]) -> str:
        messages = "\n".join([f"{p['role']}: {p['content']}" for p in prompt])

        payload = {
            "model": self.model_name,
            "prompt": messages,
            "stream": False,
        }

        resp = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
        )

        if resp.status_code != 200:
            raise ValueError(f"Ollama request failed: {resp.status_code}, {resp.text}")

        data = resp.json()
        return data.get("response", "")
