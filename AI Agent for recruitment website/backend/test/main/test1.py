import os
import sys
import json
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from llms.ollama_llms import OllamaLLMs
from MCP.server import get_prompt

def test():
    default_url = "http://host.docker.internal:11434" if os.getenv("DOCKER_ENV") == "true" else "http://localhost:11434"
    ollama_url = os.getenv("OLLAMA_URL", default_url)
    model_name = "hf.co/Cactus-Compute/Qwen3-1.7B-Instruct-GGUF:Q4_K_M"

    client = OllamaLLMs(base_url=ollama_url, model_name=model_name)
    
    
    listOfChatToClassificationIntent = [
        " Có việc làm lập trình viên ở Hà Nội không? ",
" Mình muốn tìm việc blockchain lương cao. ",
" Cho mình danh sách các công việc mới nhất tại TP.HCM. ",
" Có công việc nào làm remote cho sinh viên không? ",
" Mình muốn biết các vị trí Data Analyst đang tuyển. ",
" Hướng dẫn mình cách tạo tài khoản trên web. ",
" Làm sao để upload CV lên hệ thống? ",
" Bạn chỉ mình cách đổi mật khẩu với. ",
" Cách ứng tuyển một công việc trên website như thế nào? ",
" Mình không biết cách cập nhật hồ sơ, chỉ giúp mình. ",
" Tìm ứng viên có kinh nghiệm về Unity. ",
" Có ứng viên nào biết Solidity không? ",
" Liệt kê cho mình những ứng viên có CV về Data Science. ",
" Tìm người có kỹ năng Python ở Hà Nội. ",
" Mình cần ứng viên part-time lập trình game. ",
" Mình muốn phản hồi về tính năng tìm kiếm. ",
" Website hơi chậm, mình góp ý chút. ",
" Tôi muốn gửi ý kiến về trải nghiệm đăng ký tài khoản. ",
" Nút ứng tuyển bị lỗi, mình muốn báo cáo. ",
" Cho mình gửi feedback về dịch vụ hỗ trợ. ",
" Bạn có thể xem và góp ý CV của mình không? ",
" Đánh giá CV Data Analyst này giúp mình. ",
" Xem thử CV của mình có điểm gì cần chỉnh. ",
" Nhận xét CV blockchain của mình. ",
" Giúp mình kiểm tra nội dung CV này. ",
" Dựa trên CV này bạn gợi ý công việc phù hợp được không? ",
" Mình có CV về AI, bạn tìm giúp việc phù hợp nhé. ",
" Với kinh nghiệm trong CV, công việc nào hợp với mình? ",
" Bạn có thể gợi ý một số vị trí dựa trên hồ sơ này không? ",
" Xem CV của mình và đề xuất vài công việc thích hợp. ",
" Thông tin về công ty Horus Entertainment. ",
" Công ty ABC có đang tuyển không? ",
" Cho mình biết quy mô của công ty XYZ. ",
" Địa chỉ văn phòng của công ty Unikgate ở đâu? ",
" Công ty nào đang thuộc lĩnh vực blockchain? ",
" Hôm nay trời đẹp quá. ",
" Bạn tên gì thế? ",
" Bạn có mệt không? ",
" Dạo này công việc của bạn ổn chứ? ",
" Nghe nói cuối tuần có bão, bạn biết chưa? ",
    ]
    
    for chat in listOfChatToClassificationIntent:
        prompt_text = get_prompt("classification_chat_intent", user_input=chat)
        messages = [{"role": "user", "content": prompt_text}]
        response = client.generate_content(messages)
        print(f"Chat: {chat}\n=> Intent: {response}\n")



if __name__ == "__main__":
    test()
    
    
