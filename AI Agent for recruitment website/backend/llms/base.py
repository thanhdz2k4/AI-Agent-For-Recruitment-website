# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import List, Dict


class BaseLLM(ABC):
    def __init__(self, model_name: str = None, **kwargs):
        """
        Base class for all LLM clients.
        model_name: Tên model (có thể None nếu không cần).
        kwargs: cấu hình thêm cho subclass.
        """
        self.model_name = model_name

    @abstractmethod
    def generate_content(self, prompt: List[Dict[str, str]]) -> str:
        """
        Sinh output từ model dựa trên prompt.
        prompt: [{"role": "user", "content": "..."}]
        return: output text
        """
        pass
