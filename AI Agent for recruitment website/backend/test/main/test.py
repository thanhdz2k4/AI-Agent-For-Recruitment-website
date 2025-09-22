import os
import sys
import requests

# Add backend path to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, backend_path)

from app.chatbot.ChatbotOllama import ChatbotOllama

def chat_with_ollama():
    base_url = "http://localhost:11434"
    model_name = "hf.co/Cactus-Compute/Qwen3-1.7B-Instruct-GGUF:Q4_K_M"

    # Kiểm tra Ollama server
    try:
        r = requests.get(f"{base_url}/api/tags", timeout=3)
        if not r.json().get("models", []):
            print("❌ Chưa có model. Chạy: ollama pull llama2")
            return
    except:
        print("❌ Ollama chưa chạy. Chạy: ollama serve")
        return

    # Thiết lập môi trường
    os.environ["OLLAMA_URL"] = base_url
    os.environ["OLLAMA_MODEL"] = model_name

    # Tạo chatbot
    bot = ChatbotOllama()
    bot.add_system_message(
        "Bạn là một trợ lý AI hữu ích, thân thiện và luôn hỗ trợ người dùng một cách tốt nhất. Chỉ trả lời trong tools nếu được yêu cầu."
    )

    print(f"✅ Chatbot sẵn sàng! Model: {model_name}")
    print("Gõ 'quit' để thoát.\n")
    tools = bot.get_available_tools()
    print(f"🔧 Công cụ sẵn có: {', '.join(tools)}\n")

    while True:
        user = input("👤 You: ").strip()
        if user.lower() in ["quit", "exit"]:
            print("👋 Tạm biệt!")
            break
        if not user:
            continue
        resp = bot.chat_with_tools(user, tools, max_steps = 1)
        # Loại bỏ thẻ <think> nếu có
        if "<think>" in resp:
            resp = resp.split("</think>")[-1].strip()
        print(f"🤖 Bot: {resp}")

if __name__ == "__main__":
    chat_with_ollama()
