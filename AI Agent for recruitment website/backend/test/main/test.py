import os
import sys
import json
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from llms.ollama_llms import OllamaLLMs
from MCP.server import get_prompt


def extract_cv_features(cv_text: str) -> dict:
    """
    Extract features from CV text using LLM
    
    Args:
        cv_text: Raw CV text content
        
    Returns:
        dict: Extracted features in structured format
    """
    # Setup Ollama client
    default_url = "http://host.docker.internal:11434" if os.getenv("DOCKER_ENV") == "true" else "http://localhost:11434"
    ollama_url = os.getenv("OLLAMA_URL", default_url)
    model_name = "hf.co/unsloth/Qwen3-4B-Instruct-2507-GGUF:Q4_K_M"

    client = OllamaLLMs(base_url=ollama_url, model_name=model_name)

    # Create prompt for CV extraction
    prompt_text = get_prompt("extract_features_cv", user_input=cv_text)
    messages = [{"role": "user", "content": prompt_text}]
    
    try:
        # Generate response
        response = client.generate_content(messages)
        print("=== RAW LLM RESPONSE ===")
        print(response)
        print("\n=== PROCESSED OUTPUT ===")
        
        # Extract JSON from response (ignore <think> sections)
        try:
            # Remove <think> sections if present
            if "<think>" in response:
                response = response.split("</think>")[-1].strip()
            
            # Find JSON part (between { and })
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_part = response[start_idx:end_idx]
                parsed_json = json.loads(json_part)
                print("JSON Format:")
                print(json.dumps(parsed_json, indent=2, ensure_ascii=False))
                return parsed_json
            else:
                print("Text Format:")
                print(response)
                return {"raw_text": response}
                
        except json.JSONDecodeError:
            print("Text Format (JSON parse failed):")
            print(response)
            return {"raw_text": response}
            
    except Exception as e:
        print(f"Error during extraction: {str(e)}")
        return {"error": str(e)}


def test_cv_extraction():
    """Test CV extraction with sample CV"""
    
    # Sample CV text (Vietnamese)
    sample_cv = """
 SUMMARY
Hanoi Open University – Software Engineering (2022–2025 expected)
GPA: 3.0 | Merit & Excellence Scholarships
Physics Provincial Consolation Prize (2021)Customer Sentiment Analysis – ML.NET
Built a sentiment classification model from customer textual reviews using ML.NET.
 Performed NLP preprocessing including tokenization, stopword removal, and feature extraction (TF-
IDF).
 Applied feature selection and model tuning to improve classification accuracy.
 Integrated the model into a Blazor Web frontend for real-time sentiment prediction.
Githup: Link
Playable Ads Fresher– Horus Production (Apr 2024 – Jul 2025)Unity Intern Developer – Onechain Technology (Feb 2025 – Apr 2025)As a passionate and responsible student in technology, I aim to specialize in the AI/ML field. I have hands-on
experience in machine learning projects, smart contract deployment, and blockchain-integrated web
development. My goal is to become a practical and creative AI Engineer who never stops learning.NGUYỄN THẾ THÀNH
Hoang Liet, Hoang Mai, Ha Noi | thanhthanh1002004@gmail.com | 0859215819
AI INTERN
     TECHNICAL SKILLS
Programming: Python, C#, JavaScript, Solidity, SQL, HTML/CSS
AI/ML: ML.NET, TensorFlow (basic), Keras, LLM (LLama), Neural Networks, NLP
Blockchain: Solidity, Web3.js, Smart Contract Development, DApp Integration
Application Development: Asp.net Core mvc, ML.net, Android mobile, Winform
Soft Skills: Problem-solving, Adaptability, Teamwork
Smart Contract & DApp Integration
Developed and deployed smart contracts on Ethereum testnet using Solidity. Built a frontend
interface to interact via Web3.js. Integrated blockchain-based token transactions.
Web deploy: Link
Githup: Link
     HIGHLIGHTED PROJECTS
     WORK EXPERIENCE
     EDUCATIONLung Cancer Classification – Google Colab (2025)
Built a CNN model with TensorFlow/Keras to classify lung cancer types from medical images.
Applied preprocessing (resize, normalization, augmentation) to improve robustness.
Achieved 98% accuracy with high precision, recall, and F1-score.
Evaluated using ROC-AUC for reliable medical classification.
Colab Demo: View Project
    """
    
    # Extract features
    result = extract_cv_features(sample_cv)
    
    return result



if __name__ == "__main__":
    # PDF to Text conversion
    pdf_file_path = "C:\\Users\\myth\\Downloads\\NGUYEN THE THANH.pdf"

    print("📖 PDF TO TEXT CONVERTER")
    print("=" * 50)

    result = test_cv_extraction()

    print(f"\n✅ results: {result}")
