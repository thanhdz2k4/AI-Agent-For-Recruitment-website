from mcp.server.fastmcp import FastMCP

# 1️⃣ Tạo server
server = FastMCP("demo-mcp")

# 2️⃣ Định nghĩa tool
@server.tool()
def hello(name: str) -> str:
    """Say hello to a user"""
    return f"Hello, {name}!"

# 3️⃣ Chạy server qua STDIO
if __name__ == "__main__":
    server.run()
