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





# 3️⃣ Chạy server qua STDIO
if __name__ == "__main__":
    server.run()
