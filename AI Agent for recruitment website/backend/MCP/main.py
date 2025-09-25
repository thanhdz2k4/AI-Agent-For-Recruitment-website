import sys
import os

# Add the backend directory to the path so we can import from MCP
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from server import server, intent_classification, enhance_question


if __name__ == "__main__":
    result = intent_classification("Tôi muốn tìm việc")
    if(result == "recruitment_incomplete"):
        enhance_question("Tôi muốn tìm việc")
    print(result)


