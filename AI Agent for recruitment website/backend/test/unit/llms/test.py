import pytest
import requests
from unittest.mock import patch, MagicMock
from llms.ollama_llms import OllamaLLMs

@pytest.fixture
def ollama_client():
    return OllamaLLMs(model_name="llama2", base_url="http://mockserver:11434")


def test_generate_content_success(ollama_client):
    """Test khi API trả về 200 với response hợp lệ"""

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "Hello from Ollama"}

    with patch.object(requests, "post", return_value=mock_response) as mock_post:
        prompt = [{"role": "user", "content": "Say hello"}]
        output = ollama_client.generate_content(prompt)

        assert output == "Hello from Ollama"
        mock_post.assert_called_once()
        # Check URL đúng endpoint
        assert "/api/generate" in mock_post.call_args[0][0]


def test_generate_content_failure(ollama_client):
    """Test khi API trả về lỗi 500"""

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"

    with patch.object(requests, "post", return_value=mock_response):
        prompt = [{"role": "user", "content": "Say hello"}]

        with pytest.raises(ValueError) as excinfo:
            ollama_client.generate_content(prompt)

        assert "Ollama request failed" in str(excinfo.value)


def test_generate_content_empty_response(ollama_client):
    """Test khi API trả về JSON không có key 'response'"""

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    with patch.object(requests, "post", return_value=mock_response):
        prompt = [{"role": "user", "content": "Say hello"}]
        output = ollama_client.generate_content(prompt)

        # Vì không có 'response', sẽ trả về chuỗi rỗng
        assert output == ""
