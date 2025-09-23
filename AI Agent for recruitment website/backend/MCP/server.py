import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from mcp.server.fastmcp import FastMCP
from pymongo import MongoClient
from typing import List, Dict, Any
from setting import Settings

# 1️⃣ Tạo server
server = FastMCP("demo-mcp")

# Load settings
settings = Settings.load_settings()

# connect to MongoDB (example, adjust as needed)
mongo_client = MongoClient(settings.DATABASE_HOST)
db = mongo_client[settings.DATABASE_NAME]

# 2️⃣ Định nghĩa tool
@server.tool()
def hello(name: str) -> str:
    """Say hello to a user"""
    return f"Hello, {name}!"

#MongoDB
@server.tool()
def find_documents(collection: str, query: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
    """
    find documents in mongoDB
    Args:
        collection: name of the collection on mongoDB
        query: fillter query (vd: {"name": "Alice"})
    """
    col = db[collection]
    docs = list(col.find(query))
    
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs

# Tool trích xuất đặc trưng từ câu hỏi về JD
@server.tool()
def extract_features_from_question(query: str, prompt_type: str) -> Dict[str, Any]:
    """
    Trích xuất các đặc trưng từ câu hỏi về JD
    Args:
        query: câu hỏi của user
        prompt_type: loại prompt để trích xuất (vd: "extract_features_question_aboout_job")
    Returns:
        dict: các đặc trưng đã trích xuất
    """
    from tool.extract_feature_question_about_jd import ExtractFeatureQuestion
    extractor = ExtractFeatureQuestion(
        model_name=os.getenv("OLLAMA_MODEL", "hf.co/Cactus-Compute/Qwen3-1.7B-Instruct-GGUF:Q4_K_M"),
        validate_response=["title", "skills", "company", "location", "experience"]
    )
    features = extractor.extract(query, prompt_type)
    return features




# 3️⃣ Chạy server qua STDIO
if __name__ == "__main__":
    server.run()
