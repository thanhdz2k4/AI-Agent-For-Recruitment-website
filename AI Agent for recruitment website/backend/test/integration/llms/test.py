import pytest
import os
from llms.ollama_llms import OllamaLLMs


@pytest.fixture
def ollama_client():
    # Sử dụng model nhỏ hơn trong CI/CD
    model_name = "tinyllama:latest" if os.getenv("CI") else "llama2"
    return OllamaLLMs(model_name=model_name, base_url="http://localhost:11434")


def test_generate_content_real_server(ollama_client):
    """Integration test: gọi thật vào Ollama server"""

    prompt = [{"role": "user", "content": "Say hello in one short sentence."}]
    output = ollama_client.generate_content(prompt)

    # Kết quả không rỗng
    assert isinstance(output, str)
    assert len(output) > 0

    print("\nOllama real output:", output)
