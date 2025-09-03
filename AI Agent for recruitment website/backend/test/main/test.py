import os
import sys

# Minimal test: import class, check /api/tags, optionally call generate
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, backend_path)

import requests
from llms.ollama_llms import OllamaLLMs


def main():
    base_url = "http://localhost:11434"
    print("Minimal OllamaLLMs test")

    try:
        r = requests.get(f"{base_url}/api/tags", timeout=3)
        r.raise_for_status()
        data = r.json()
        models = data.get('models', [])
        print(f"Server reachable, models: {len(models)}")
    except Exception as e:
        print(f"Server not reachable: {e}")
        return 1

    if not models:
        print("No models pulled. Skipping generate test.")
        return 0

    # pick first model name if available
    model_name = models[0].get('name') or None
    print(f"Using model: {model_name}")

    client = OllamaLLMs(base_url=base_url, model_name=model_name)
    resp = client.generate_content([{"role": "user", "content": "Hello"}])
    print("Response:", resp[:200])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())