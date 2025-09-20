import sys
import os

# Add the backend directory to the path so we can import from MCP
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from server import server, find_documents


if __name__ == "__main__":
    result = find_documents(collection="job-description")
    print(result)


